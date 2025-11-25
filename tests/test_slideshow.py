import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from slideshow import Slideshow


def main():
    """Test the slideshow manager"""
    print("=" * 50)
    print("Testing Slideshow Manager")
    print("=" * 50)
    
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    queue_dir = os.path.join(project_root, 'images', 'queue')
    
    # Create slideshow with absolute path
    slideshow = Slideshow(
        image_dir=queue_dir,
        loop=True
    )
    
    # Scan for images
    print(f"\n1. Scanning for images in {queue_dir}...")
    count = slideshow.scan_images()
    print(f"Found {count} images")
    
    if count == 0:
        print(f"\nNo images found in {queue_dir}")
        print("Supported formats: jpg, png, heic")
        return
    
    # Test getting next images
    print("\n2. Testing image iteration...")
    for i in range(min(count + 2, 10)):  # Test a few iterations including loop
        img_path = slideshow.get_next_image()
        print(f"  Image {i+1}/{count}: {os.path.basename(img_path)}")
    
    # Test reset
    print("\n3. Testing reset...")
    slideshow.reset()
    img_path = slideshow.get_next_image()
    print(f"  After reset: {os.path.basename(img_path)}")
    
    print(f"\n4. Current position: {slideshow.get_current_index()} of {slideshow.get_image_count()}")
    
    print("\n" + "=" * 50)
    print("Slideshow test complete!")
    print("=" * 50)


if __name__ == '__main__':
    main()