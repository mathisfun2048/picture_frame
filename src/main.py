import sys
import os
import json
import time
import signal
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from display_controller import EInkDisplay
from image_processor import ImageProcessor
from slideshow import Slideshow
from transfer import ImageTransfer
from button_handler import ButtonHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('picture_frame.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class PictureFrame:
    """
    Main picture frame application
    Coordinates all components to display a slideshow on e-ink
    """
    
    def __init__(self, config_path='config/settings.json'):
        """
        Initialize the picture frame
        
        Args:
            config_path: Path to configuration file
        """
        logger.info("=" * 60)
        logger.info("E-Ink Picture Frame Starting")
        logger.info("=" * 60)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Get project root
        project_root = Path(__file__).parent.parent
        
        # Initialize components
        queue_dir = project_root / self.config['directories']['queue']
        processed_dir = project_root / self.config['directories']['processed']
        
        self.slideshow = Slideshow(
            image_dir=str(queue_dir),
            loop=self.config['display']['loop']
        )
        
        self.transfer = ImageTransfer(
            queue_dir=str(queue_dir),
            processed_dir=str(processed_dir),
            dither_mode=self.config['processing']['dither_mode'],
            contrast=self.config['processing']['contrast'],
            brightness=self.config['processing']['brightness'],
            sharpness=self.config['processing']['sharpness']
        )
        
        self.display = EInkDisplay()
        
        # Initialize button handler
        self.button = ButtonHandler(
            button_pin=18,
            pull_up=True,  # CHANGE THIS if your button connects to 3.3V instead of GND
            debounce_ms=300
        )
        
        self.running = False
        self.interval = self.config['display']['interval_seconds']
        self.skip_to_next = False  # Flag to skip current wait
        
        # Setup signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Picture frame initialized")
    
    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            # Get absolute path relative to project root
            project_root = Path(__file__).parent.parent
            config_file = project_root / config_path
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    def _button_pressed(self):
        """Callback when button is pressed - skip to next image"""
        logger.info("Button press detected - skipping to next image")
        self.skip_to_next = True
    
    def start(self):
        """Start the picture frame slideshow"""
        try:
            # Initialize display
            logger.info("Initializing display...")
            self.display.init()
            
            if self.config['startup']['clear_display_on_start']:
                logger.info("Clearing display...")
                self.display.clear()
            
            # Initialize button
            logger.info("Setting up button...")
            #self.button.setup(self._button_pressed)
            
            # Scan for images
            logger.info("Scanning for images...")
            image_count = self.slideshow.scan_images()
            logger.info(f"Found {image_count} images in queue")
            
            if image_count == 0:
                logger.error("No images found in queue. Add images and restart.")
                self.display.sleep()
                return
            
            # Optional: Preprocess all images on startup
            if self.config['startup']['preprocess_on_start']:
                logger.info("Preprocessing all images...")
                all_images = [
                    self.slideshow.get_next_image() 
                    for _ in range(image_count)
                ]
                self.slideshow.reset()
                self.transfer.preprocess_all(all_images)
            
            # Start slideshow loop
            self.running = True
            self._run_slideshow()
            
        except Exception as e:
            logger.error(f"Error starting picture frame: {e}", exc_info=True)
            self.shutdown()
    
    def _run_slideshow(self):
        """Main slideshow loop"""
        logger.info("Starting slideshow loop")
        logger.info(f"Image interval: {self.interval} seconds")
        logger.info("Press button on GPIO 18 to skip to next image")
        
        while self.running:
            try:
                # Get next image
                image_path = self.slideshow.get_next_image()
                
                if not image_path:
                    logger.warning("No more images, stopping")
                    break
                
                logger.info(f"Displaying: {Path(image_path).name}")
                
                # Process image
                processed_img = self.transfer.get_processed_image(image_path)
                
                # Display on e-ink
                self.display.display_image(processed_img)
                
                logger.info(f"Image {self.slideshow.get_current_index()}/{self.slideshow.get_image_count()} displayed")
                logger.info(f"Waiting {self.interval} seconds until next image (or press button to skip)...")
                
                # Reset skip flag
                self.skip_to_next = False
                
                # Wait for next image (check skip flag and running flag frequently)
                for _ in range(self.interval):
                    if not self.running or self.skip_to_next:
                        if self.skip_to_next:
                            logger.info("Skipping to next image...")
                        break
                    time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Error in slideshow loop: {e}", exc_info=True)
                logger.info("Waiting 10 seconds before retry...")
                time.sleep(10)
        
        self.shutdown()
    
    def shutdown(self):
        """Clean shutdown of picture frame"""
        logger.info("Shutting down picture frame...")
        self.running = False
        
        try:
            self.button.cleanup()
            logger.info("Button cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up button: {e}")
        
        try:
            self.display.sleep()
            logger.info("Display put to sleep")
        except Exception as e:
            logger.error(f"Error during display shutdown: {e}")
        
        logger.info("=" * 60)
        logger.info("Picture frame stopped")
        logger.info("=" * 60)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}")
        self.shutdown()
        sys.exit(0)


def main():
    """Entry point for picture frame application"""
    try:
        frame = PictureFrame()
        frame.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()