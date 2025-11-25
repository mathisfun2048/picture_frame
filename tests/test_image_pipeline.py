import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from display_controller import EInkDisplay
from image_processor import ImageProcessor
import time


def main():
    """Test the full pipeline: process image -> display on e-ink"""
    print("=" * 50)
    print("Testing Full Pipeline")
    print("=" * 50)
    
    # Get a test image (you'll need to put an image in images/ folder)
    image_path = os.path.join(os.path.dirname(__file__), '..', 'images', 'test.jpg')
    
    if not os.path.exists(image_path):
        print(f"\nError: Please put a test image at {image_path}")
        print("Use any jpg or png file")
        return
    
    # Create components
    processor = ImageProcessor()
    display = EInkDisplay()
    
    try:
        # Process image
        print("\n1. Processing image...")
        processed_img = processor.process_image(
            image_path,
            dither_mode='atkinson',  # Try the retro look!
            contrast=1.3,
            brightness=1.1
        )
        
        # Display it
        print("\n2. Initializing display...")
        display.init()
        display.clear()
        
        print("\n3. Displaying processed image...")
        display.display_image(processed_img)
        
        print("\n4. Image will display for 10 seconds...")
        time.sleep(10)
        
        print("\n5. Cleaning up...")
        display.sleep()
        
        print("\n" + "=" * 50)
        print("Pipeline test complete!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if display.initialized:
            display.sleep()


if __name__ == '__main__':
    main()