# tests/test_display.py
import sys
import os
# Add lib to path so we can import waveshare_epd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from waveshare_epd import epd4in2_V2
from PIL import Image, ImageDraw, ImageFont
import time

def main():
    print("Initializing e-paper display...")
    
    # Create display object
    epd = epd4in2_V2.EPD()
    
    try:
        # Initialize and clear
        epd.init()
        print("Clearing display...")
        epd.Clear()
        time.sleep(1)
        
        # Create a new image (400x300 for this display)
        # '1' means 1-bit (black and white)
        # 255 is white background
        print("Creating test image...")
        image = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(image)
        
        # Draw some test elements
        # Text (using default font since we might not have Font.ttc)
        draw.text((10, 10), 'E-Ink Display Test', fill=0)
        draw.text((10, 40), 'Picture Frame v0.1', fill=0)
        draw.text((10, 70), '400x300 pixels', fill=0)
        
        # Draw a rectangle
        draw.rectangle((10, 100, 100, 150), outline=0, width=2)
        
        # Draw a circle (using arc)
        draw.ellipse((120, 100, 170, 150), outline=0, width=2)
        
        # Draw a line
        draw.line((10, 170, 150, 170), fill=0, width=3)
        
        print("Displaying image...")
        epd.display(epd.getbuffer(image))
        
        print("Display test complete! Image will stay for 5 seconds...")
        time.sleep(5)
        
        # Put display to sleep to save power
        print("Putting display to sleep...")
        epd.sleep()
        print("Test finished successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        epd.sleep()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean shutdown
        epd4in2_V2.epdconfig.module_exit(cleanup=True)

if __name__ == '__main__':
    main()