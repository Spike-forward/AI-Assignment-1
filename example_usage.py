#!/usr/bin/env python3
"""
Example usage of the image collector

This demonstrates how to use the ImageCollector class programmatically.
"""

from image_collector import ImageCollector


def example_basic_usage():
    """Basic usage example"""
    print("Example 1: Basic usage")
    print("-" * 60)
    
    # Create collector with default settings
    collector = ImageCollector(
        keyword="cat",
        output_dir="example_images",
        max_images=10,  # Small number for demonstration
        min_images=5
    )
    
    # Note: In a real scenario, you would call collector.collect_images()
    # For this example, we just show the setup
    print(f"Keyword: {collector.keyword}")
    print(f"Output directory: {collector.output_dir}")
    print(f"Target: {collector.min_images}-{collector.max_images} images")
    print()


def example_custom_settings():
    """Example with custom settings"""
    print("Example 2: Custom settings")
    print("-" * 60)
    
    collector = ImageCollector(
        keyword="landscape photography",
        output_dir="landscapes",
        max_images=5000,
        min_images=3000
    )
    
    print(f"Keyword: {collector.keyword}")
    print(f"Output directory: {collector.output_dir}")
    print(f"Target: {collector.min_images}-{collector.max_images} images")
    print()


def example_programmatic_usage():
    """Example of using individual methods"""
    print("Example 3: Programmatic usage")
    print("-" * 60)
    
    from PIL import Image
    from io import BytesIO
    import os
    
    collector = ImageCollector("test", "/tmp/test_demo")
    
    # Create a test image
    test_img = Image.new('RGB', (1920, 1080), (100, 150, 200))
    
    # Demonstrate resize and crop
    processed = collector.resize_and_crop(test_img, target_size=500)
    print(f"Original size: {test_img.size}")
    print(f"Processed size: {processed.size}")
    
    # Save with size limit
    output_path = "/tmp/test_demo/example.jpg"
    os.makedirs("/tmp/test_demo", exist_ok=True)
    success = collector.save_image_with_size_limit(
        processed, 
        output_path, 
        max_size_kb=50
    )
    
    if success:
        size_kb = os.path.getsize(output_path) / 1024
        print(f"Saved successfully: {size_kb:.2f}KB")
    
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Image Collector - Usage Examples")
    print("=" * 60)
    print()
    
    example_basic_usage()
    example_custom_settings()
    example_programmatic_usage()
    
    print("=" * 60)
    print("For actual image collection, run:")
    print('  python image_collector.py "your_keyword"')
    print("=" * 60)
