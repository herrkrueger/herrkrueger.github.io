#!/usr/bin/env python3
"""
WordPress Export Posts Lister

This script lists all posts from WordPress export XML files with their
post ID, date, title, and number of images referenced in the content.

Usage:
    python list_wordpress_posts.py --xml-file <wordpress_export.xml> [--output <output.csv>]
"""

import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Define XML namespaces used in WordPress export
NAMESPACES = {
    'wp': 'http://wordpress.org/export/1.2/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
}

def count_images_in_content(content):
    """Count the number of images referenced in the post content."""
    if not content:
        return 0
    
    # Count img tags
    img_pattern = re.compile(r'<img[^>]+src="([^"]+)"[^>]*>')
    img_matches = img_pattern.findall(content)
    
    # Count gallery shortcodes
    gallery_pattern = re.compile(r'\[gallery[^\]]*\]')
    gallery_matches = gallery_pattern.findall(content)
    
    return len(img_matches) + len(gallery_matches)

def list_wordpress_posts(xml_file, output_file=None):
    """List all posts from the WordPress export XML file."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        channel = root.find('channel')
        
        posts = []
        
        # Process all posts
        for item in channel.findall('item'):
            post_type = item.find('.//wp:post_type', NAMESPACES)
            if post_type is not None and post_type.text == 'post':
                post_status = item.find('.//wp:status', NAMESPACES)
                if post_status is not None and post_status.text == 'publish':
                    # Extract post data
                    post_id = item.find('.//wp:post_id', NAMESPACES).text
                    title_elem = item.find('title')
                    title = title_elem.text if title_elem is not None and title_elem.text else "Untitled Post"
                    
                    # Get post date
                    post_date = item.find('.//wp:post_date', NAMESPACES).text
                    date_obj = datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S')
                    date_str = date_obj.strftime('%Y-%m-%d')
                    
                    # Get categories and tags
                    categories = []
                    tags = []
                    
                    for cat in item.findall('category'):
                        domain = cat.get('domain', '')
                        if domain == 'category':
                            categories.append(cat.text)
                        elif domain == 'post_tag':
                            tags.append(cat.text)
                    
                    # Get content and count images
                    content_element = item.find('.//content:encoded', NAMESPACES)
                    content = content_element.text if content_element is not None and content_element.text else ""
                    image_count = count_images_in_content(content)
                    
                    # Get permalink
                    link_elem = item.find('link')
                    link = link_elem.text if link_elem is not None else ""
                    
                    # Get post slug
                    post_name = item.find('.//wp:post_name', NAMESPACES)
                    post_slug = post_name.text if post_name is not None else ""
                    
                    posts.append({
                        'post_id': post_id,
                        'date': date_str,
                        'title': title,
                        'categories': ', '.join(categories),
                        'tags': ', '.join(tags),
                        'image_count': image_count,
                        'link': link,
                        'post_slug': post_slug
                    })
        
        # Sort posts by date (newest first)
        posts.sort(key=lambda x: x['date'], reverse=True)
        
        # Print to console and/or write to CSV
        if output_file:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['post_id', 'date', 'title', 'categories', 'tags', 'image_count', 'link', 'post_slug'])
                writer.writeheader()
                writer.writerows(posts)
            print(f"Found {len(posts)} posts. Results saved to {output_file}")
        else:
            print(f"Found {len(posts)} posts:")
            print("-" * 80)
            for post in posts:
                print(f"{post['post_id']}\t{post['date']}\t{post['title']} ({post['image_count']} images)")
                print(f"  Categories: {post['categories']}")
                print(f"  Tags: {post['tags']}")
                print(f"  URL: {post['link']}")
                print("-" * 80)
        
        return posts
        
    except Exception as e:
        print(f"Error processing WordPress export: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='List WordPress export posts')
    parser.add_argument('--xml-file', required=True, help='WordPress export XML file')
    parser.add_argument('--output', help='Output CSV file')
    
    args = parser.parse_args()
    
    list_wordpress_posts(args.xml_file, args.output)

if __name__ == "__main__":
    main()