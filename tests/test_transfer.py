import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from transfer import ImageTransfer
from slideshow import Slideshow


def main():
    """Test the image transfer/processing pipeline"""
    print("=" * 50)
    print("Testing Image Transfer")
    print("=" * 50)
    
    # Create components
    slideshow = Slideshow()
    transfer = ImageTransfer()
    
    # Scan for images
    print("\n1. Scanning for images...")
    count = slideshow.scan_images()
    print(f"Found {count} images")
    
    if count == 0:
        print("\nNo images found! Add some images to images/queue/")
        return
    
    # Process first image
    print("\n2. Processing first image...")
    img_path = slideshow.get_next_image()
    print(f"Processing: {os.path.basename(img_path)}")
    
    processed = transfer.get_processed_image(img_path)
    print(f"Processed image: {processed.size}, mode: {processed.mode}")
    
    # Process again (should use cache)
    print("\n3. Processing same image again (should use cache)...")
    processed2 = transfer.get_processed_image(img_path)
    print(f"Second load: {processed2.size}, mode: {processed2.mode}")
    
    # Check cache
    print(f"\n4. Cache location: images/processed/")
    import os
    cache_files = os.listdir('images/processed')
    print(f"Cached files: {len(cache_files)}")
    for f in cache_files[:5]:  # Show first 5
        print(f"  - {f}")
    
    print("\n" + "=" * 50)
    print("Transfer test complete!")
    print("=" * 50)


if __name__ == '__main__':
    main()