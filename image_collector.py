#!/usr/bin/env python3
"""
Automated Image Dataset Collection and Processing System

This script automatically searches for images online, downloads them,
and processes them according to specified requirements.
"""

import os
import sys
import time
import argparse
import json
from urllib.parse import urljoin, quote
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO


class ImageCollector:
    """Handles image search, download, and processing"""
    
    def __init__(self, keyword, output_dir="images", max_images=5000, min_images=3000):
        """
        Initialize the ImageCollector
        
        Args:
            keyword: Search keyword for images
            output_dir: Directory to save downloaded images
            max_images: Maximum number of images to collect
            min_images: Minimum number of images to collect
        """
        self.keyword = keyword
        self.output_dir = Path(output_dir)
        self.max_images = max_images
        self.min_images = min_images
        self.metadata = []
        self.downloaded_count = 0
        self.failed_count = 0
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def search_images_bing(self, num_pages=50):
        """
        Search images using Bing Image Search
        
        Args:
            num_pages: Number of pages to scrape
            
        Returns:
            List of dictionaries containing image URLs and alt text
        """
        print(f"Searching for '{self.keyword}' on Bing Images...")
        image_data = []
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for page in range(num_pages):
            try:
                # Bing uses 'first' parameter for pagination
                offset = page * 35
                url = f"https://www.bing.com/images/search?q={quote(self.keyword)}&first={offset}"
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find image elements
                img_elements = soup.find_all('a', class_='iusc')
                
                for img in img_elements:
                    try:
                        # Parse the m attribute which contains JSON data
                        m_json = img.get('m')
                        if m_json:
                            m_data = json.loads(m_json)
                            img_url = m_data.get('murl')
                            alt_text = m_data.get('t', '')
                            
                            if img_url:
                                image_data.append({
                                    'url': img_url,
                                    'alt': alt_text
                                })
                                
                                if len(image_data) >= self.max_images:
                                    print(f"Reached maximum {self.max_images} images")
                                    return image_data
                    except (json.JSONDecodeError, AttributeError):
                        continue
                
                print(f"Page {page + 1}: Found {len(image_data)} images so far")
                
                # Be respectful with requests
                time.sleep(1)
                
            except requests.RequestException as e:
                print(f"Error fetching page {page + 1}: {e}")
                continue
        
        return image_data
    
    def download_image(self, url, filename):
        """
        Download an image from URL
        
        Args:
            url: Image URL
            filename: Local filename to save
            
        Returns:
            PIL Image object or None if failed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Open image from bytes
            img = Image.open(BytesIO(response.content))
            return img
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return None
    
    def resize_and_crop(self, img, target_size=500):
        """
        Resize and center-crop image to target size
        
        Args:
            img: PIL Image object
            target_size: Maximum dimension (width or height)
            
        Returns:
            Processed PIL Image object
        """
        # Convert to RGB if necessary (handle RGBA, grayscale, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get original dimensions
        width, height = img.size
        
        # Calculate scale to fit within target_size
        scale = min(target_size / width, target_size / height)
        
        # If image is smaller than target, don't upscale
        if scale > 1:
            scale = 1
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize image
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Center crop to square if one dimension is larger
        if new_width > new_height:
            # Crop width
            left = (new_width - new_height) // 2
            img = img.crop((left, 0, left + new_height, new_height))
        elif new_height > new_width:
            # Crop height
            top = (new_height - new_width) // 2
            img = img.crop((0, top, new_width, top + new_width))
        
        return img
    
    def save_image_with_size_limit(self, img, filepath, max_size_kb=50, initial_quality=80):
        """
        Save image as JPEG with size constraint
        
        Args:
            img: PIL Image object
            filepath: Path to save image
            max_size_kb: Maximum file size in KB
            initial_quality: Initial JPEG quality (50-80)
            
        Returns:
            True if saved successfully, False otherwise
        """
        quality = initial_quality
        current_size = img.size
        
        # Try different strategies to reduce file size
        while quality >= 50:
            # Save to buffer first to check size
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            size_kb = buffer.tell() / 1024
            
            if size_kb <= max_size_kb:
                # Size is acceptable, save to file
                with open(filepath, 'wb') as f:
                    f.write(buffer.getvalue())
                return True
            
            # If still too large, reduce quality
            quality -= 5
        
        # If quality reduction isn't enough, reduce dimensions
        scale_factor = 0.9
        while True:
            new_width = int(current_size[0] * scale_factor)
            new_height = int(current_size[1] * scale_factor)
            
            if new_width < 50 or new_height < 50:
                # Image is too small, give up
                return False
            
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Try with quality 60
            buffer = BytesIO()
            resized_img.save(buffer, format='JPEG', quality=60, optimize=True)
            size_kb = buffer.tell() / 1024
            
            if size_kb <= max_size_kb:
                with open(filepath, 'wb') as f:
                    f.write(buffer.getvalue())
                return True
            
            scale_factor -= 0.05
    
    def process_and_save_image(self, img_data, index):
        """
        Process and save a single image
        
        Args:
            img_data: Dictionary with 'url' and 'alt' keys
            index: Image index for filename
            
        Returns:
            True if successful, False otherwise
        """
        url = img_data['url']
        alt = img_data['alt']
        
        # Download image
        img = self.download_image(url, f"image_{index}")
        if img is None:
            self.failed_count += 1
            return False
        
        # Resize and crop
        try:
            processed_img = self.resize_and_crop(img)
            
            # Save with size limit
            filename = f"image_{index:05d}.jpg"
            filepath = self.output_dir / filename
            
            success = self.save_image_with_size_limit(processed_img, filepath)
            
            if success:
                self.downloaded_count += 1
                self.metadata.append({
                    'filename': filename,
                    'original_url': url,
                    'alt_text': alt,
                    'size': os.path.getsize(filepath)
                })
                return True
            else:
                self.failed_count += 1
                return False
                
        except Exception as e:
            print(f"Error processing image {index}: {e}")
            self.failed_count += 1
            return False
    
    def collect_images(self):
        """
        Main method to collect and process images
        """
        print(f"Starting image collection for keyword: '{self.keyword}'")
        print(f"Target: {self.min_images}-{self.max_images} images")
        print(f"Output directory: {self.output_dir}")
        print("-" * 60)
        
        # Search for images
        image_data = self.search_images_bing(num_pages=100)
        
        print(f"\nFound {len(image_data)} image URLs")
        print("Starting download and processing...")
        print("-" * 60)
        
        # Process images
        for i, img_data in enumerate(image_data):
            if self.downloaded_count >= self.max_images:
                break
            
            print(f"Processing image {i + 1}/{len(image_data)}: {img_data['url'][:50]}...")
            self.process_and_save_image(img_data, i + 1)
            
            # Progress update every 100 images
            if (i + 1) % 100 == 0:
                print(f"\nProgress: {self.downloaded_count} downloaded, {self.failed_count} failed")
                print("-" * 60)
            
            # Small delay to be respectful
            time.sleep(0.1)
        
        # Save metadata
        metadata_file = self.output_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print collection summary"""
        print("\n" + "=" * 60)
        print("COLLECTION SUMMARY")
        print("=" * 60)
        print(f"Keyword: {self.keyword}")
        print(f"Output directory: {self.output_dir}")
        print(f"Successfully downloaded: {self.downloaded_count} images")
        print(f"Failed downloads: {self.failed_count} images")
        
        if self.downloaded_count >= self.min_images:
            print(f"✓ Met minimum requirement of {self.min_images} images")
        else:
            print(f"✗ Did not meet minimum requirement of {self.min_images} images")
        
        if self.metadata:
            total_size = sum(img['size'] for img in self.metadata)
            avg_size = total_size / len(self.metadata)
            print(f"Average file size: {avg_size / 1024:.2f} KB")
            print(f"Total dataset size: {total_size / (1024 * 1024):.2f} MB")
        
        print(f"\nMetadata saved to: {self.output_dir / 'metadata.json'}")
        print("=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Automated Image Dataset Collection and Processing'
    )
    parser.add_argument(
        'keyword',
        type=str,
        help='Search keyword for images'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='images',
        help='Output directory for images (default: images)'
    )
    parser.add_argument(
        '--max-images',
        type=int,
        default=5000,
        help='Maximum number of images to collect (default: 5000)'
    )
    parser.add_argument(
        '--min-images',
        type=int,
        default=3000,
        help='Minimum number of images required (default: 3000)'
    )
    
    args = parser.parse_args()
    
    # Create collector and run
    collector = ImageCollector(
        keyword=args.keyword,
        output_dir=args.output,
        max_images=args.max_images,
        min_images=args.min_images
    )
    
    try:
        collector.collect_images()
    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user")
        collector.print_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during collection: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
