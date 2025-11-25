import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from display_controller import EInkDisplay
from PIL import Image, ImageDraw
import time


def main():
    """Test the display controller"""
    print("=" * 50)
    print("Testing EInkDisplay Controller")
    print("=" * 50)
    
    # Create display controller
    display = EInkDisplay()
    
    try:
        # Initialize
        print("\n1. Initializing display...")
        display.init()
        
        # Clear
        print("\n2. Clearing display...")
        display.clear()
        time.sleep(2)
        
        # Create test image
        print("\n3. Creating test image...")
        img = Image.new('1', (400, 300), 255)  # White background
        draw = ImageDraw.Draw(img)
        
        # Draw some test content
        draw.text((10, 10), 'Display Controller Test', fill=0)
        draw.text((10, 40), 'Class methods working!', fill=0)
        draw.rectangle((10, 70, 150, 120), outline=0, width=2)
        draw.ellipse((170, 70, 270, 120), outline=0, width=2)
        draw.line((10, 140, 270, 140), fill=0, width=3)
        
        # Display it
        print("\n4. Displaying test image...")
        display.display_image(img)
        
        print("\n5. Image will display for 5 seconds...")
        time.sleep(5)
        
        # Sleep
        print("\n6. Putting display to sleep...")
        display.sleep()
        
        print("\n" + "=" * 50)
        print("Test completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure cleanup
        if display.initialized:
            display.sleep()


if __name__ == '__main__':
    main()