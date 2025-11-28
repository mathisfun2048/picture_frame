import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Slideshow:
    """
    Manages image queue and rotation for the picture frame
    """
    
    def __init__(self, image_dir='images/queue', loop=True):
        """
        Initialize the slideshow manager
        
        Args:
            image_dir: Directory containing images to display
            loop: Loop back to start when reaching the end
        """
        self.image_dir = Path(image_dir)
        self.loop = loop
        self.image_list = []
        self.current_index = 0
        
        logger.info(f"Slideshow initialized: dir={image_dir}, loop={loop}")
    
    def scan_images(self):
        """
        Scan the image directory and build the image list
        
        Returns:
            Number of images found
        """
        # Valid image extensions
        valid_extensions = {'.jpg', '.jpeg', '.png', '.heic'}
        
        # Ensure directory exists
        if not self.image_dir.exists():
            logger.warning(f"Image directory does not exist: {self.image_dir}")
            self.image_dir.mkdir(parents=True, exist_ok=True)
            return 0
        
        # Find all image files
        self.image_list = [
            f for f in self.image_dir.iterdir()
            if f.is_file() and f.suffix.lower() in valid_extensions
        ]
        
        # Sort alphabetically
        self.image_list.sort()
        
        logger.info(f"Scanned {len(self.image_list)} images from {self.image_dir}")
        
        return len(self.image_list)
    
    
    
    def get_next_image(self):
        """
        Get the path to the next image to display
        
        Returns:
            Path to next image (str), or None if no images available
        """
        # Check if we need to scan
        if not self.image_list:
            self.scan_images()
        
        # No images available
        if not self.image_list:
            logger.warning("No images available in queue")
            return None
        
        # Get current image
        image_path = str(self.image_list[self.current_index])
        
        # Increment index
        self.current_index += 1
        
        # Handle end of list
        if self.current_index >= len(self.image_list):
            if self.loop:
                logger.info("Reached end of slideshow, looping back to start")
                self.scan_images()
                self.current_index = 0
            else:
                logger.info("Reached end of slideshow")
                return None
        
        return image_path
    
    def reset(self):
        """Reset to beginning of slideshow"""
        self.current_index = 0
        logger.info("Slideshow reset to beginning")
    
    def get_image_count(self):
        """Get total number of images"""
        return len(self.image_list)
    
    def get_current_index(self):
        """Get current position in slideshow"""
        return self.current_index