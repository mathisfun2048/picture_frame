import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from image_processor import ImageProcessor
from PIL import Image, ImageDraw
import time


def create_test_image():
    """Create a test image with gradients for testing dithering"""
    img = Image.new('RGB', (800, 600), 'white')
    draw = ImageDraw.Draw(img)
    
    # Create gradient
    for i in range(256):
        gray = i
        draw.rectangle([(i*3, 0), (i*3+3, 200)], fill=(gray, gray, gray))
    
    # Add some text
    draw.text((50, 250), 'Dithering Test Image', fill='black')
    
    # Add shapes
    draw.ellipse([(50, 300), (250, 500)], fill='gray')
    draw.rectangle([(300, 300), (500, 500)], fill='darkgray')
    
    # Save it
    test_img_path = os.path.join(os.path.dirname(__file__), '..', 'images', 'test_gradient.png')
    os.makedirs(os.path.dirname(test_img_path), exist_ok=True)
    img.save(test_img_path)
    return test_img_path


def main():
    """Test the image processor with different dithering modes"""
    print("=" * 50)
    print("Testing ImageProcessor")
    print("=" * 50)
    
    # Create processor
    processor = ImageProcessor()
    
    # Create or use test image
    print("\n1. Creating test image...")
    test_img = create_test_image()
    print(f"Test image created: {test_img}")
    
    # Test different dithering modes
    dither_modes = ['floyd-steinberg', 'atkinson', 'ordered', 'threshold']
    
    for mode in dither_modes:
        print(f"\n2. Testing {mode} dithering...")
        try:
            processed = processor.process_image(
                test_img,
                dither_mode=mode,
                contrast=1.3,
                brightness=1.1,
                sharpness=1.2
            )
            
            # Save processed image
            output_path = os.path.join(
                os.path.dirname(__file__), '..', 'images', 
                f'processed_{mode}.png'
            )
            processed.save(output_path)
            print(f"Saved: {output_path}")
            print(f"Size: {processed.size}, Mode: {processed.mode}")
            
        except Exception as e:
            print(f"Failed with {mode}: {e}")
    
    print("\n" + "=" * 50)
    print("Test complete! Check images/ folder for results")
    print("=" * 50)


if __name__ == '__main__':
    main()