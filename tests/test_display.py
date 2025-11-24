# tests/test_display.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from waveshare_epd import epd4in2_V2
from PIL import Image, ImageDraw, ImageFont
import time
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("Initializing e-paper display...")
    
    epd = epd4in2_V2.EPD()
    
    try:
        # Initialize and clear
        logging.info("init and Clear")
        epd.init()
        epd.Clear()
        
        # Create a new image
        logging.info("Creating test image...")
        image = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(image)
        
        # Use default font (no external font file needed)
        # If you want a specific font, we'll add it later
        draw.text((10, 10), 'E-Ink Display Test', fill=0)
        draw.text((50, 200), 'Hey Calista!', fill=0)
        draw.text((10, 70), '400x300 pixels', fill=0)
        
        # Draw shapes
        '''
        draw.rectangle((10, 100, 100, 150), outline=0)
        draw.ellipse((120, 100, 170, 150), outline=0)
        draw.line((10, 170, 150, 170), fill=0, width=3)
        '''
        
        logging.info("Displaying image...")
        epd.display(epd.getbuffer(image))
        
        print("Display test complete! Image will stay for 5 seconds...")
        time.sleep(5)
        # epd.Clear()
        
        logging.info("Putting display to sleep...")
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
        epd4in2_V2.epdconfig.module_exit(cleanup=True)

if __name__ == '__main__':
    main()