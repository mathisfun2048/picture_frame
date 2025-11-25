# src/display_controller.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from waveshare_epd import epd4in2_V2
from PIL import Image
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EInkDisplay:
    """
    Clean wrapper for Waveshare 4.2" e-Paper display
    Handles all the low-level hardware communication
    """
    
    def __init__(self):
        """Initialize the display controller"""
        self.epd = None
        self.width = 400
        self.height = 300
        self.initialized = False
        logger.info("EInkDisplay controller created")
    
    def init(self):
        """
        Initialize the e-paper display hardware
        """
        try:
            if not self.epd:
                self.epd = epd4in2_V2.EPD()
            
            logger.info("Initializing e-paper display...")
            self.epd.init()
            self.initialized = True
            logger.info("Display initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            raise
    
    def clear(self):
        """
        Clear the display to white
        """
        try:
            # Make sure we're initialized first
            if not self.initialized:
                logger.warning("Display not initialized, initializing now...")
                self.init()
            
            logger.info("Clearing display...")
            self.epd.Clear()
            logger.info("Display cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear display: {e}")
            raise
    
    def display_image(self, pil_image):
        """
        Display a PIL Image on the e-paper
        
        Args:
            pil_image: PIL Image object (should be 400x300, will be converted to 1-bit)
        """
        try:
            # Make sure we're initialized
            if not self.initialized:
                logger.warning("Display not initialized, initializing now...")
                self.init()
            
            # Check image size
            if pil_image.size != (self.width, self.height):
                logger.warning(
                    f"Image size {pil_image.size} doesn't match display size "
                    f"({self.width}x{self.height}). Image should be resized first."
                )
                # You could resize here, but it's better to handle in image_processor
                raise ValueError(
                    f"Image must be {self.width}x{self.height}, got {pil_image.size}"
                )
            
            # Ensure image is in 1-bit mode (black and white)
            if pil_image.mode != '1':
                logger.info(f"Converting image from {pil_image.mode} to 1-bit")
                pil_image = pil_image.convert('1')
            
            # Get buffer and display
            logger.info("Sending image to display...")
            buffer = self.epd.getbuffer(pil_image)
            self.epd.display(buffer)
            logger.info("Image displayed successfully")
            
        except Exception as e:
            logger.error(f"Failed to display image: {e}")
            raise
    
    def sleep(self):
        """
        Put the display into low power sleep mode
        """
        try:
            if self.epd and self.initialized:
                logger.info("Putting display to sleep...")
                self.epd.sleep()
                self.initialized = False
                logger.info("Display is now sleeping")
            else:
                logger.warning("Display not initialized, nothing to sleep")
                
        except Exception as e:
            logger.error(f"Failed to sleep display: {e}")
            raise
    
    def __del__(self):
        """
        Cleanup when object is destroyed
        Ensures display is properly shut down
        """
        try:
            # Put display to sleep if still active
            if self.initialized:
                logger.info("Cleaning up display in destructor...")
                self.sleep()
            
            # Clean up GPIO and SPI
            if self.epd:
                epd4in2_V2.epdconfig.module_exit(cleanup=True)
                logger.info("Display cleanup complete")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")