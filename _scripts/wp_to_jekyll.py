#!/usr/bin/env python3
"""
WordPress to Jekyll Migration Script

This script converts WordPress export XML files to Jekyll blog posts,
preserving metadata, content, and downloading associated images.

Usage:
    python wp_to_jekyll.py --xml-file <wordpress_export.xml> --media-dir <media_directory> [--output-dir <jekyll_posts_dir>] [--post-ids id1,id2,id3] [--date-after YYYY-MM-DD] [--date-before YYYY-MM-DD]

Requirements:
    - beautifulsoup4
    - html2markdown
    - python-dateutil
"""

import argparse
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import html
from datetime import datetime
from urllib.parse import urlparse, unquote
from pathlib import Path

try:
    from bs4 import BeautifulSoup
    import html2markdown
    import dateutil.parser
except ImportError:
    print("Required packages missing. Install with: pip install beautifulsoup4 html2markdown python-dateutil")
    sys.exit(1)

# Define XML namespaces used in WordPress export
NAMESPACES = {
    'wp': 'http://wordpress.org/export/1.2/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
}

class WordPressToJekyllConverter:
    def __init__(self, xml_file, media_dir, output_dir=None, post_ids=None, date_after=None, date_before=None):
        """Initialize the converter with file paths and filters."""
        self.xml_file = xml_file
        self.media_dir = Path(media_dir)
        
        # Default to Jekyll _posts directory if not specified
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # Find Jekyll root directory (parent of _posts)
            script_dir = Path(__file__).resolve().parent
            jekyll_root = script_dir.parent
            self.output_dir = jekyll_root / '_posts'
        
        # Get Jekyll root directory (parent of output_dir)
        if output_dir:
            jekyll_root = Path(output_dir).parent
        else:
            jekyll_root = script_dir.parent
            
        # Create images directory for copied images
        self.jekyll_images_dir = jekyll_root / 'images'
        self.jekyll_images_dir.mkdir(exist_ok=True)
        
        # Store attachment URL to file path mapping
        self.attachment_map = {}
        
        # Parse post IDs for filtering
        self.post_ids = set(post_ids) if post_ids else None
        
        # Parse dates for filtering
        self.date_after = datetime.strptime(date_after, '%Y-%m-%d') if date_after else None
        self.date_before = datetime.strptime(date_before, '%Y-%m-%d') if date_before else None
        
        # Regular expression to find image references in HTML
        self.img_pattern = re.compile(r'<img[^>]+src="([^"]+)"[^>]*>')
        
        # Map of post IDs to attachments
        self.post_attachments = {}

    def parse_wordpress_export(self):
        """Parse the WordPress export XML file."""
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
            channel = root.find('channel')
            
            # First pass: build post parent to attachment mapping
            for item in channel.findall('item'):
                post_type = item.find('.//wp:post_type', NAMESPACES)
                if post_type is not None and post_type.text == 'attachment':
                    self.process_attachment_mapping(item)
            
            # Second pass: Find and process all attachments to build the attachment map
            for item in channel.findall('item'):
                post_type = item.find('.//wp:post_type', NAMESPACES)
                if post_type is not None and post_type.text == 'attachment':
                    self.process_attachment(item)
            
            # Count posts for reporting
            total_posts = 0
            converted_posts = 0
            
            # Process all posts based on filters
            for item in channel.findall('item'):
                post_type = item.find('.//wp:post_type', NAMESPACES)
                if post_type is not None and post_type.text == 'post':
                    post_status = item.find('.//wp:status', NAMESPACES)
                    if post_status is not None and post_status.text == 'publish':
                        total_posts += 1
                        if self.should_process_post(item):
                            if self.convert_post_to_jekyll(item):
                                converted_posts += 1
            
            print(f"Conversion complete. Processed {converted_posts} of {total_posts} posts.")
            print(f"Jekyll posts saved to {self.output_dir}")
            
        except Exception as e:
            print(f"Error parsing WordPress export: {e}")
            sys.exit(1)
    
    def should_process_post(self, item):
        """Determine if post should be processed based on filters."""
        # Check post ID filter
        if self.post_ids:
            post_id = item.find('.//wp:post_id', NAMESPACES).text
            if post_id not in self.post_ids:
                return False
        
        # Check date filters
        if self.date_after or self.date_before:
            post_date = item.find('.//wp:post_date', NAMESPACES).text
            date_obj = datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S')
            
            if self.date_after and date_obj < self.date_after:
                return False
                
            if self.date_before and date_obj > self.date_before:
                return False
        
        return True
    
    def process_attachment_mapping(self, item):
        """Build mapping of post parents to attachment IDs."""
        post_parent = item.find('.//wp:post_parent', NAMESPACES)
        if post_parent is not None and post_parent.text:
            parent_id = post_parent.text
            attachment_id = item.find('.//wp:post_id', NAMESPACES).text
            
            if parent_id not in self.post_attachments:
                self.post_attachments[parent_id] = []
            
            self.post_attachments[parent_id].append(attachment_id)
    
    def process_attachment(self, item):
        """Process an attachment item and add it to the attachment map."""
        try:
            attachment_url = item.find('.//wp:attachment_url', NAMESPACES).text
            attachment_id = item.find('.//wp:post_id', NAMESPACES).text
            
            # Parse URL to get filename
            parsed_url = urlparse(attachment_url)
            filename = unquote(os.path.basename(parsed_url.path))
            
            # Check if file exists in media directory
            year_month_pattern = re.compile(r'/(\d{4})/(\d{2})/')
            year_month_match = year_month_pattern.search(parsed_url.path)
            
            if year_month_match:
                year, month = year_month_match.groups()
                # Search for the file in the media directory structure
                potential_paths = [
                    self.media_dir / year / month / filename,
                    self.media_dir / f"{year}-{month}" / filename,
                    self.media_dir / year / filename,
                ]
                
                for path in potential_paths:
                    if path.exists():
                        self.attachment_map[attachment_url] = path
                        self.attachment_map[attachment_id] = path  # Also map by ID
                        break
            
            # If not found, try a more general search
            if attachment_url not in self.attachment_map:
                for root, _, files in os.walk(self.media_dir):
                    if filename in files:
                        path = Path(root) / filename
                        self.attachment_map[attachment_url] = path
                        self.attachment_map[attachment_id] = path  # Also map by ID
                        break
            
        except Exception as e:
            print(f"Error processing attachment: {e}")
    
    def convert_post_to_jekyll(self, item):
        """Convert a WordPress post to a Jekyll post."""
        try:
            # Extract post metadata
            title = item.find('title').text
            if title is None:
                title = "Untitled Post"
            
            post_id = item.find('.//wp:post_id', NAMESPACES).text
            
            # Get post date
            post_date = item.find('.//wp:post_date', NAMESPACES).text
            date_obj = datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S')
            
            # Format date for Jekyll filename and front matter
            date_str = date_obj.strftime('%Y-%m-%d')
            datetime_str = date_obj.strftime('%Y-%m-%d %H:%M:%S +0100')  # Adjust timezone if needed
            
            # Get content
            content_element = item.find('.//content:encoded', NAMESPACES)
            content = content_element.text if content_element is not None and content_element.text else ""
            
            # Get excerpt
            excerpt_element = item.find('.//excerpt:encoded', NAMESPACES)
            excerpt = excerpt_element.text if excerpt_element is not None and excerpt_element.text else ""
            
            # Get categories and tags
            categories = []
            tags = []
            
            for cat in item.findall('category'):
                domain = cat.get('domain', '')
                if domain == 'category':
                    categories.append(cat.text)
                elif domain == 'post_tag':
                    tags.append(cat.text)
            
            # Process content: replace image URLs and convert to Markdown
            content = self.process_content(content, date_obj, post_id)
            
            # Create Jekyll front matter
            front_matter = self.create_front_matter(title, datetime_str, categories, tags, excerpt)
            
            # Create Jekyll post filename
            post_name = item.find('.//wp:post_name', NAMESPACES).text
            if not post_name:
                # Generate slug from title
                post_name = title.lower().replace(' ', '-')
                post_name = re.sub(r'[^a-z0-9-]', '', post_name)
            
            filename = f"{date_str}-{post_name}.md"
            post_path = self.output_dir / filename
            
            # Write Jekyll post
            with open(post_path, 'w', encoding='utf-8') as f:
                f.write(front_matter)
                f.write('\n\n')
                f.write(content)
            
            print(f"Created Jekyll post: {filename}")
            return True
            
        except Exception as e:
            print(f"Error converting post '{title if 'title' in locals() else 'unknown'}': {e}")
            return False
    
    def process_content(self, content, post_date, post_id):
        """Process post content: handle images, galleries, and convert to Markdown."""
        if not content:
            return ""
        
        # Create a year-month folder for this post's images
        year_month = post_date.strftime('%Y-%m-%d')
        post_images_dir = self.jekyll_images_dir / year_month
        post_images_dir.mkdir(exist_ok=True)
        
        # Replace gallery shortcodes with actual images
        content = self.process_galleries(content, post_id, post_images_dir, year_month)
        
        # Process inline images
        content = self.process_images(content, post_images_dir, year_month)
        
        # Convert HTML to Markdown (optional)
        try:
            content = html2markdown.convert(content)
        except Exception as e:
            print(f"Markdown conversion failed: {e}")
            # If conversion fails, keep HTML
            pass
        
        return content
    
    def process_galleries(self, content, post_id, post_images_dir, year_month):
        """Replace gallery shortcodes with actual images."""
        if post_id not in self.post_attachments:
            return content
        
        # First, handle the special case of Jetpack tiled gallery
        jetpack_pattern = re.compile(r'<!-- wp:jetpack/tiled-gallery \{.*?"ids":\[([^\]]+)\].*? /-->')
        jetpack_matches = jetpack_pattern.findall(content)
        
        # Also check for simple format
        if not jetpack_matches:
            simple_pattern = re.compile(r'<!-- wp:jetpack/tiled-gallery \{"ids":\[([^\]]+)\].*? /-->')
            jetpack_matches = simple_pattern.findall(content)
        
        for ids_str in jetpack_matches:
            # Get the full shortcode - try different patterns
            shortcode = None
            
            # Try to find the exact shortcode in the content
            patterns = [
                r'<!-- wp:jetpack/tiled-gallery \{"ids":\[' + re.escape(ids_str) + r'\].*? /-->',
                r'<!-- wp:jetpack/tiled-gallery \{.*?"ids":\[' + re.escape(ids_str) + r'\].*? /-->'
            ]
            
            for pattern in patterns:
                shortcode_pattern = re.compile(pattern)
                shortcode_match = shortcode_pattern.search(content)
                if shortcode_match:
                    shortcode = shortcode_match.group(0)
                    break
            
            # If we still can't find it, use a more general approach
            if not shortcode:
                # Just find any Jetpack tiled gallery shortcode
                general_pattern = re.compile(r'<!-- wp:jetpack/tiled-gallery .*? /-->')
                shortcode_match = general_pattern.search(content)
                if shortcode_match:
                    shortcode = shortcode_match.group(0)
            
            if shortcode:
                # Clean up the IDs string (remove quotes and spaces)
                ids_str = ids_str.replace('"', '').replace(' ', '')
                attachment_ids = ids_str.split(',')
                print(f"Found Jetpack gallery attachment IDs: {attachment_ids}")
                
                # Build image HTML for these attachments
                gallery_html = "<div class='gallery'>\n"
                for attachment_id in attachment_ids:
                    if attachment_id in self.attachment_map:
                        source_path = self.attachment_map[attachment_id]
                        filename = source_path.name
                        
                        # Copy image to Jekyll images dir
                        target_path = post_images_dir / filename
                        try:
                            shutil.copy2(source_path, target_path)
                            print(f"Copied gallery image: {filename} to {target_path}")
                            
                            # Add image to gallery HTML
                            gallery_html += f"<img src='/images/{year_month}/{filename}' alt='{filename}' />\n"
                        except Exception as e:
                            print(f"Error copying gallery image {source_path}: {e}")
                            
                    # Try to find the image by ID in the WP export
                    else:
                        print(f"Looking for attachment ID {attachment_id} for post {post_id}...")
                        # Search for image URL in content
                        img_id_pattern = re.compile(f'wp-image-{attachment_id}"[^>]*src="([^"]+)"')
                        img_id_match = img_id_pattern.search(content)
                        
                        if img_id_match:
                            img_url = img_id_match.group(1)
                            print(f"Found image URL: {img_url}")
                            
                            # Parse URL to get filename
                            parsed_url = urlparse(img_url)
                            filename = unquote(os.path.basename(parsed_url.path))
                            
                            # Look for the file in the media directory
                            for root, _, files in os.walk(self.media_dir):
                                if filename in files:
                                    source_path = Path(root) / filename
                                    # Add to attachment map for future use
                                    self.attachment_map[attachment_id] = source_path
                                    self.attachment_map[img_url] = source_path
                                    
                                    # Copy image to Jekyll images dir
                                    target_path = post_images_dir / filename
                                    try:
                                        shutil.copy2(source_path, target_path)
                                        print(f"Copied gallery image: {filename} to {target_path}")
                                        
                                        # Add image to gallery HTML
                                        gallery_html += f"<img src='/images/{year_month}/{filename}' alt='{filename}' />\n"
                                        break
                                    except Exception as e:
                                        print(f"Error copying gallery image {source_path}: {e}")
                
                gallery_html += "</div>"
                
                # Replace gallery shortcode with actual images
                content = content.replace(shortcode, gallery_html)
        
        # Now handle standard gallery shortcodes
        gallery_pattern = re.compile(r'\[gallery([^\]]*)\]')
        gallery_matches = gallery_pattern.findall(content)
        
        for gallery_attrs in gallery_matches:
            shortcode = f"[gallery{gallery_attrs}]"
            
            # Parse gallery attributes to get IDs
            ids_pattern = re.compile(r'ids="([^"]+)"')
            ids_match = ids_pattern.search(gallery_attrs)
            
            attachment_ids = []
            if ids_match:
                # Use specified IDs
                ids_str = ids_match.group(1)
                # Clean up the IDs string (remove quotes and spaces)
                ids_str = ids_str.replace('"', '').replace(' ', '')
                attachment_ids = ids_str.split(',')
                print(f"Found gallery attachment IDs: {attachment_ids}")
            else:
                # Use all attachments for this post
                attachment_ids = self.post_attachments[post_id]
            
            # Build image HTML for these attachments
            gallery_html = "<div class='gallery'>\n"
            for attachment_id in attachment_ids:
                if attachment_id in self.attachment_map:
                    source_path = self.attachment_map[attachment_id]
                    filename = source_path.name
                    
                    # Copy image to Jekyll images dir
                    target_path = post_images_dir / filename
                    try:
                        shutil.copy2(source_path, target_path)
                        print(f"Copied gallery image: {filename} to {target_path}")
                        
                        # Add image to gallery HTML
                        gallery_html += f"<img src='/images/{year_month}/{filename}' alt='{filename}' />\n"
                    except Exception as e:
                        print(f"Error copying gallery image {source_path}: {e}")
                        
                # Try to find the image by ID in the WP export
                elif post_id in self.post_attachments:
                    print(f"Looking for attachment ID {attachment_id} for post {post_id}...")
                    # Search for image URL in content
                    img_id_pattern = re.compile(f'wp-image-{attachment_id}"[^>]*src="([^"]+)"')
                    img_id_match = img_id_pattern.search(content)
                    
                    if img_id_match:
                        img_url = img_id_match.group(1)
                        print(f"Found image URL: {img_url}")
                        
                        # Parse URL to get filename
                        parsed_url = urlparse(img_url)
                        filename = unquote(os.path.basename(parsed_url.path))
                        
                        # Look for the file in the media directory
                        for root, _, files in os.walk(self.media_dir):
                            if filename in files:
                                source_path = Path(root) / filename
                                # Add to attachment map for future use
                                self.attachment_map[attachment_id] = source_path
                                self.attachment_map[img_url] = source_path
                                
                                # Copy image to Jekyll images dir
                                target_path = post_images_dir / filename
                                try:
                                    shutil.copy2(source_path, target_path)
                                    print(f"Copied gallery image: {filename} to {target_path}")
                                    
                                    # Add image to gallery HTML
                                    gallery_html += f"<img src='/images/{year_month}/{filename}' alt='{filename}' />\n"
                                    break
                                except Exception as e:
                                    print(f"Error copying gallery image {source_path}: {e}")
            
            gallery_html += "</div>"
            
            # Replace gallery shortcode with actual images
            content = content.replace(shortcode, gallery_html)
        
        return content
    
    def process_images(self, content, post_images_dir, year_month):
        """Process images in content and copy them to Jekyll images directory."""
        if not content:
            return ""
        
        # Find all image references
        soup = BeautifulSoup(content, 'html.parser')
        for img in soup.find_all('img'):
            src = img.get('src', '')
            
            if src in self.attachment_map:
                # We have this image locally
                source_path = self.attachment_map[src]
                
                # Get filename and copy to Jekyll images dir
                filename = source_path.name
                target_path = post_images_dir / filename
                
                try:
                    shutil.copy2(source_path, target_path)
                    print(f"Copied image: {filename} to {target_path}")
                    
                    # Update image src to Jekyll path
                    img['src'] = f"/images/{year_month}/{filename}"
                except Exception as e:
                    print(f"Error copying image {source_path}: {e}")
            else:
                # Try to find the image in the media directory by filename
                try:
                    # Parse URL to get filename
                    parsed_url = urlparse(src)
                    filename = unquote(os.path.basename(parsed_url.path))
                    
                    # Only proceed if filename has an extension (is likely an image)
                    if '.' in filename:
                        print(f"Looking for image: {filename}")
                        
                        # Extract post date for directory matching
                        post_date = dateutil.parser.parse(date)
                        year_month_path = post_date.strftime('%Y/%m')
                        year_path = post_date.strftime('%Y')
                        
                        # Priority search order: exact date match > year match > any match
                        search_paths = [
                            self.media_dir / year_month_path,        # e.g., 2011/03/
                            self.media_dir / year_path,              # e.g., 2011/
                            self.media_dir                           # fallback: search all
                        ]
                        
                        found = False
                        for search_path in search_paths:
                            if search_path.exists():
                                for root, _, files in os.walk(search_path):
                                    if filename in files:
                                        source_path = Path(root) / filename
                                        # Add to attachment map for future use
                                        self.attachment_map[src] = source_path
                                        
                                        # Copy image to Jekyll images dir
                                        target_path = post_images_dir / filename
                                        try:
                                            shutil.copy2(source_path, target_path)
                                            print(f"Copied image: {filename} to {target_path} (from {root})")
                                            
                                            # Update image src to Jekyll path
                                            img['src'] = f"/images/{year_month}/{filename}"
                                            found = True
                                            break
                                        except Exception as e:
                                            print(f"Error copying image {source_path}: {e}")
                                
                                if found:
                                    break
                        
                        if not found:
                            print(f"Warning: Image {filename} not found in any date-appropriate directory")
                except Exception as e:
                    print(f"Error processing image URL {src}: {e}")
        
        # Clean WordPress-specific image markup
        soup = self.clean_image_markup(soup)
        
        # Group consecutive images for better layout
        soup = self.group_consecutive_images(soup)
        
        return str(soup)
    
    def clean_image_markup(self, soup):
        """Clean WordPress-specific image markup and improve layout"""
        
        # Find all img tags
        images = soup.find_all('img')
        
        for img in images:
            # Remove WordPress-specific classes
            wp_classes = ['alignnone', 'alignleft', 'alignright', 'aligncenter', 
                         'size-medium', 'size-large', 'size-full', 'wp-image-']
            
            if img.get('class'):
                img['class'] = [cls for cls in img['class'] 
                              if not any(wp_cls in cls for wp_cls in wp_classes)]
                if not img['class']:
                    del img['class']
            
            # Remove WordPress-specific attributes
            for attr in ['title', 'width', 'height']:
                if img.get(attr):
                    del img[attr]
            
            # Add Jekyll-friendly styling with !important to override theme CSS
            img['style'] = 'width: 200px !important; margin: 10px !important; display: inline-block !important; vertical-align: top !important; float: none !important;'
            
            # Improve alt text if generic
            if not img.get('alt') or img.get('alt') == '':
                img['alt'] = f"Image from post"
            
            # Remove wrapping <a> tags if they point to WordPress media
            parent = img.parent
            if (parent and parent.name == 'a' and 
                parent.get('href') and 
                'files.wordpress.com' in parent.get('href', '')):
                parent.unwrap()
        
        return soup
    
    def group_consecutive_images(self, soup):
        """Group consecutive images for better layout"""
        
        # Find sequences of img tags that are siblings
        for parent in soup.find_all():
            children = list(parent.children)
            img_groups = []
            current_group = []
            
            for child in children:
                if hasattr(child, 'name') and child.name == 'img':
                    current_group.append(child)
                else:
                    if len(current_group) > 1:
                        img_groups.append(current_group)
                    current_group = []
            
            # Handle final group
            if len(current_group) > 1:
                img_groups.append(current_group)
            
            # Wrap groups in divs for better styling with left alignment
            for group in img_groups:
                if len(group) > 1:
                    wrapper = soup.new_tag('div', style='text-align: left !important; margin: 20px 0; display: block !important;')
                    group[0].insert_before(wrapper)
                    for img in group:
                        wrapper.append(img)
        
        return soup
    
    def create_front_matter(self, title, date, categories, tags, excerpt):
        """Create Jekyll front matter in YAML format."""
        lines = [
            '---',
            f'title: "{title}"',
            f'date: {date}',
        ]
        
        if categories:
            categories_str = ', '.join(f'"{cat}"' for cat in categories)
            lines.append(f'categories: [{categories_str}]')
        
        if tags:
            tags_str = ', '.join(f'"{tag}"' for tag in tags)
            lines.append(f'tags: [{tags_str}]')
        
        if excerpt:
            # Clean up excerpt and limit length
            excerpt = excerpt.replace('\n', ' ').strip()
            excerpt = re.sub(r'\s+', ' ', excerpt)
            if len(excerpt) > 160:
                excerpt = excerpt[:157] + '...'
            lines.append(f'description: "{excerpt}"')
        
        lines.append('layout: post')
        lines.append('---')
        
        return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='Convert WordPress export to Jekyll posts')
    parser.add_argument('--xml-file', required=True, help='WordPress export XML file')
    parser.add_argument('--media-dir', required=True, help='WordPress media export directory')
    parser.add_argument('--output-dir', help='Jekyll posts directory (default: _posts)')
    parser.add_argument('--post-ids', help='Comma-separated list of post IDs to convert')
    parser.add_argument('--date-after', help='Only convert posts after this date (YYYY-MM-DD)')
    parser.add_argument('--date-before', help='Only convert posts before this date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Parse post IDs if provided
    post_ids = args.post_ids.split(',') if args.post_ids else None
    
    converter = WordPressToJekyllConverter(
        xml_file=args.xml_file,
        media_dir=args.media_dir,
        output_dir=args.output_dir,
        post_ids=post_ids,
        date_after=args.date_after,
        date_before=args.date_before
    )
    
    converter.parse_wordpress_export()

if __name__ == "__main__":
    main()