#!/usr/bin/env python3
"""
Test script for image_collector.py

This script tests the core functionality without downloading thousands of images.
"""

import sys
import os
from pathlib import Path
from PIL import Image
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from image_collector import ImageCollector


def create_test_image(width=800, height=600, color=(255, 0, 0)):
    """Create a test image in memory"""
    img = Image.new('RGB', (width, height), color)
    return img


def test_resize_and_crop():
    """Test resize and crop functionality"""
    print("Testing resize_and_crop...")
    
    collector = ImageCollector("test", "test_output")
    
    # Test 1: Large landscape image
    img = create_test_image(1920, 1080)
    processed = collector.resize_and_crop(img, target_size=500)
    assert processed.size[0] <= 500 and processed.size[1] <= 500
    assert processed.size[0] == processed.size[1]  # Should be square after crop
    print(f"  ✓ Large landscape image: {img.size} -> {processed.size}")
    
    # Test 2: Large portrait image
    img = create_test_image(1080, 1920)
    processed = collector.resize_and_crop(img, target_size=500)
    assert processed.size[0] <= 500 and processed.size[1] <= 500
    assert processed.size[0] == processed.size[1]
    print(f"  ✓ Large portrait image: {img.size} -> {processed.size}")
    
    # Test 3: Small image (should not upscale)
    img = create_test_image(300, 300)
    processed = collector.resize_and_crop(img, target_size=500)
    assert processed.size == (300, 300)
    print(f"  ✓ Small image: {img.size} -> {processed.size}")
    
    # Test 4: Square image
    img = create_test_image(1000, 1000)
    processed = collector.resize_and_crop(img, target_size=500)
    assert processed.size == (500, 500)
    print(f"  ✓ Square image: {img.size} -> {processed.size}")
    
    print("✓ All resize_and_crop tests passed!\n")


def test_save_with_size_limit():
    """Test save with size limit functionality"""
    print("Testing save_image_with_size_limit...")
    
    # Create temporary test directory
    test_dir = Path("/tmp/test_images")
    test_dir.mkdir(exist_ok=True)
    
    collector = ImageCollector("test", test_dir)
    
    # Test: Large image should be reduced to under 50KB
    img = create_test_image(1000, 1000, color=(128, 128, 255))
    filepath = test_dir / "test_large.jpg"
    
    success = collector.save_image_with_size_limit(img, filepath, max_size_kb=50, initial_quality=80)
    
    assert success, "Failed to save image"
    assert filepath.exists(), "File was not created"
    
    file_size_kb = filepath.stat().st_size / 1024
    assert file_size_kb <= 50, f"File size {file_size_kb:.2f}KB exceeds 50KB limit"
    
    print(f"  ✓ Large image saved under 50KB: {file_size_kb:.2f}KB")
    
    # Cleanup
    filepath.unlink()
    
    print("✓ All save_with_size_limit tests passed!\n")


def test_image_formats():
    """Test handling of different image formats"""
    print("Testing different image formats...")
    
    collector = ImageCollector("test", "test_output")
    
    # Test RGBA image
    img = Image.new('RGBA', (500, 500), (255, 0, 0, 128))
    processed = collector.resize_and_crop(img)
    assert processed.mode == 'RGB'
    print("  ✓ RGBA image converted to RGB")
    
    # Test grayscale image
    img = Image.new('L', (500, 500), 128)
    processed = collector.resize_and_crop(img)
    assert processed.mode == 'RGB'
    print("  ✓ Grayscale image converted to RGB")
    
    print("✓ All format conversion tests passed!\n")


def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Image Collector Tests")
    print("=" * 60 + "\n")
    
    try:
        test_resize_and_crop()
        test_save_with_size_limit()
        test_image_formats()
        
        print("=" * 60)
        print("All tests passed successfully!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
