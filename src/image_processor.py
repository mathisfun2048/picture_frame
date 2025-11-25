from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Processes images for optimal e-ink display
    Handles resizing, dithering, and aesthetic adjustments
    """
    
    def __init__(self, target_width=400, target_height=300):
        """
        Initialize the image processor
        
        Args:
            target_width: Display width in pixels
            target_height: Display height in pixels
        """
        self.width = target_width
        self.height = target_height
        logger.info(f"ImageProcessor initialized for {self.width}x{self.height} display")
    
    def process_image(self, image_path, dither_mode='floyd-steinberg', 
                     contrast=1.2, brightness=1.0, sharpness=1.0):
        """
        Process an image for e-ink display
        
        Args:
            image_path: Path to the source image file
            dither_mode: Dithering algorithm to use:
                        'floyd-steinberg' (default, smooth gradients)
                        'atkinson' (retro Mac look)
                        'ordered' (pattern-based)
                        'threshold' (no dithering, pure B&W)
            contrast: Contrast adjustment (1.0 = no change, >1.0 = more contrast)
            brightness: Brightness adjustment (1.0 = no change, >1.0 = brighter)
            sharpness: Sharpness adjustment (1.0 = no change, >1.0 = sharper)
        
        Returns:
            PIL Image object (1-bit, 400x300) ready for display
        """
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Load image
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            img = Image.open(image_path)
            logger.info(f"Loaded image: {img.size}, mode: {img.mode}")
            
            # Convert to RGB if needed (handles RGBA, P, etc.)
            if img.mode not in ('RGB', 'L'):
                logger.info(f"Converting from {img.mode} to RGB")
                img = img.convert('RGB')
            
            # Resize to fit display while maintaining aspect ratio
            img = self._resize_maintain_aspect(img)
            logger.info(f"Resized to {img.size}")
            
            # Apply enhancements before dithering
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)
                logger.info(f"Applied contrast: {contrast}")
            
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)
                logger.info(f"Applied brightness: {brightness}")
            
            if sharpness != 1.0:
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(sharpness)
                logger.info(f"Applied sharpness: {sharpness}")
            
            # Convert to grayscale
            img = img.convert('L')
            logger.info("Converted to grayscale")
            
            # Apply dithering
            img = self._apply_dithering(img, dither_mode)
            logger.info(f"Applied {dither_mode} dithering")
            
            logger.info("Image processing complete")
            return img
            
        except Exception as e:
            logger.error(f"Failed to process image: {e}")
            raise
    
    def _resize_maintain_aspect(self, img):
        """
        Resize image to fit display while maintaining aspect ratio
        Centers the image on a white background if needed
        
        Args:
            img: PIL Image object
            
        Returns:
            PIL Image object (400x300)
        """
        # Calculate aspect ratios
        img_ratio = img.width / img.height
        target_ratio = self.width / self.height
        
        if img_ratio > target_ratio:
            # Image is wider - fit to width
            new_width = self.width
            new_height = int(self.width / img_ratio)
        else:
            # Image is taller - fit to height
            new_height = self.height
            new_width = int(self.height * img_ratio)
        
        # Resize with high-quality resampling
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Create white canvas and paste centered image
        canvas = Image.new('RGB', (self.width, self.height), 'white')
        offset_x = (self.width - new_width) // 2
        offset_y = (self.height - new_height) // 2
        canvas.paste(img, (offset_x, offset_y))
        
        return canvas
    
    def _apply_dithering(self, img, dither_mode):
        """
        Apply dithering algorithm to grayscale image
        
        Args:
            img: PIL Image in 'L' (grayscale) mode
            dither_mode: Dithering algorithm name
            
        Returns:
            PIL Image in '1' (1-bit B&W) mode
        """
        if dither_mode == 'floyd-steinberg':
            # Built-in Floyd-Steinberg dithering (smooth, natural)
            return img.convert('1', dither=Image.FLOYDSTEINBERG)
        
        elif dither_mode == 'atkinson':
            # Atkinson dithering (retro Mac aesthetic)
            return self._atkinson_dither(img)
        
        elif dither_mode == 'ordered':
            # Ordered dithering (pattern-based)
            return img.convert('1', dither=Image.ORDERED)
        
        elif dither_mode == 'threshold':
            # No dithering, pure threshold
            return img.convert('1', dither=Image.NONE)
        
        else:
            logger.warning(f"Unknown dither mode '{dither_mode}', using floyd-steinberg")
            return img.convert('1', dither=Image.FLOYDSTEINBERG)
    
    def _atkinson_dither(self, img):
        """
        Apply Atkinson dithering algorithm
        Creates a distinctive retro look (like old Macintosh computers)
        
        Args:
            img: PIL Image in 'L' (grayscale) mode
            
        Returns:
            PIL Image in '1' (1-bit B&W) mode
        """
        # Convert to numpy array for pixel manipulation
        img_array = np.array(img, dtype=float)
        height, width = img_array.shape
        
        # Atkinson dithering distributes error to 6 neighboring pixels
        # Pattern:
        #     X   1/8 1/8
        # 1/8 1/8 1/8
        #     1/8
        
        for y in range(height - 2):
            for x in range(1, width - 2):
                old_pixel = img_array[y, x]
                new_pixel = 255 if old_pixel > 128 else 0
                img_array[y, x] = new_pixel
                
                # Calculate quantization error
                error = (old_pixel - new_pixel) / 8  # Atkinson divides by 8
                
                # Distribute error to neighboring pixels
                if x + 1 < width:
                    img_array[y, x + 1] += error
                if x + 2 < width:
                    img_array[y, x + 2] += error
                
                if y + 1 < height:
                    if x - 1 >= 0:
                        img_array[y + 1, x - 1] += error
                    img_array[y + 1, x] += error
                    if x + 1 < width:
                        img_array[y + 1, x + 1] += error
                
                if y + 2 < height:
                    img_array[y + 2, x] += error
        
        # Clip values and convert back to PIL Image
        img_array = np.clip(img_array, 0, 255).astype('uint8')
        return Image.fromarray(img_array).convert('1')