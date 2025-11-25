import os
from pathlib import Path
import logging
import hashlib
from PIL import Image

# Register HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False
    logging.warning("pillow-heif not installed, HEIC files will not be supported")

from image_processor import ImageProcessor

logger = logging.getLogger(__name__)


class ImageTransfer:
    """
    Manages transfer and processing of images from queue to processed folder
    Caches processed images to avoid reprocessing
    """
    
    def __init__(self, queue_dir='images/queue', processed_dir='images/processed',
                 dither_mode='atkinson', contrast=1.2, brightness=1.0, sharpness=1.0):
        """
        Initialize the image transfer manager
        
        Args:
            queue_dir: Directory containing source images
            processed_dir: Directory to store processed images
            dither_mode: Dithering algorithm to use
            contrast: Contrast adjustment
            brightness: Brightness adjustment
            sharpness: Sharpness adjustment
        """
        self.queue_dir = Path(queue_dir)
        self.processed_dir = Path(processed_dir)
        self.processor = ImageProcessor()
        
        # Processing settings
        self.dither_mode = dither_mode
        self.contrast = contrast
        self.brightness = brightness
        self.sharpness = sharpness
        
        # Create processed directory if it doesn't exist
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ImageTransfer initialized: queue={queue_dir}, processed={processed_dir}")
    
    def get_processed_image(self, source_path):
        """
        Get processed version of an image (from cache or by processing)
        
        Args:
            source_path: Path to source image
            
        Returns:
            PIL Image object ready for display
        """
        source_path = Path(source_path)
        
        # Generate cache filename based on source file hash
        cache_filename = self._get_cache_filename(source_path)
        cache_path = self.processed_dir / cache_filename
        
        # Check if processed version exists and is up to date
        if cache_path.exists():
            # Check if source has been modified since cache was created
            source_mtime = source_path.stat().st_mtime
            cache_mtime = cache_path.stat().st_mtime
            
            if cache_mtime >= source_mtime:
                logger.info(f"Using cached processed image: {cache_filename}")
                return Image.open(cache_path)
            else:
                logger.info(f"Cache outdated, reprocessing: {source_path.name}")
        else:
            logger.info(f"Processing new image: {source_path.name}")
        
        # Process the image
        processed_img = self.processor.process_image(
            str(source_path),
            dither_mode=self.dither_mode,
            contrast=self.contrast,
            brightness=self.brightness,
            sharpness=self.sharpness
        )
        
        # Save to cache
        processed_img.save(cache_path)
        logger.info(f"Cached processed image: {cache_filename}")
        
        return processed_img
    
    def _get_cache_filename(self, source_path):
        """
        Generate a cache filename based on source file
        
        Args:
            source_path: Path to source image
            
        Returns:
            Cache filename (str)
        """
        # Create a hash of the source filename for uniqueness
        source_name = source_path.name
        name_hash = hashlib.md5(source_name.encode()).hexdigest()[:8]
        
        # Use original stem + hash + png extension
        cache_name = f"{source_path.stem}_{name_hash}.png"
        
        return cache_name
    
    def clear_cache(self):
        """
        Clear all cached processed images
        """
        count = 0
        for cache_file in self.processed_dir.glob('*.png'):
            cache_file.unlink()
            count += 1
        
        logger.info(f"Cleared {count} cached images")
        return count
    
    def preprocess_all(self, image_paths):
        """
        Preprocess a list of images (useful for startup)
        
        Args:
            image_paths: List of image paths to preprocess
        """
        logger.info(f"Preprocessing {len(image_paths)} images...")
        
        for i, img_path in enumerate(image_paths):
            try:
                logger.info(f"Preprocessing {i+1}/{len(image_paths)}: {Path(img_path).name}")
                self.get_processed_image(img_path)
            except Exception as e:
                logger.error(f"Failed to preprocess {img_path}: {e}")
        
        logger.info("Preprocessing complete")