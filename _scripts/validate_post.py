#!/usr/bin/env python3
"""
Validate Jekyll post formatting and requirements
Usage: python _scripts/validate_post.py _drafts/my-post.md
"""

import sys
import os
import re
import yaml
import requests
from pathlib import Path
from urllib.parse import urlparse

def validate_frontmatter(content):
    """Validate Jekyll front matter"""
    issues = []
    
    if not content.startswith('---\n'):
        issues.append("❌ Missing front matter delimiter at start")
        return issues, None
    
    # Extract front matter
    try:
        end_idx = content.find('\n---\n', 4)
        if end_idx == -1:
            issues.append("❌ Missing front matter closing delimiter")
            return issues, None
        
        fm_content = content[4:end_idx]
        frontmatter = yaml.safe_load(fm_content)
        
    except yaml.YAMLError as e:
        issues.append(f"❌ Invalid YAML in front matter: {e}")
        return issues, None
    
    # Required fields
    required_fields = ['title', 'date', 'categories', 'tags']
    for field in required_fields:
        if field not in frontmatter:
            issues.append(f"❌ Missing required field: {field}")
    
    # Validate specific fields
    if 'title' in frontmatter:
        title = frontmatter['title']
        if len(title) < 10:
            issues.append("⚠️  Title might be too short (< 10 chars)")
        if len(title) > 60:
            issues.append("⚠️  Title might be too long for SEO (> 60 chars)")
    
    if 'description' in frontmatter:
        desc = frontmatter['description']
        if len(desc) > 160:
            issues.append("⚠️  Description too long for SEO (> 160 chars)")
    
    if 'categories' in frontmatter:
        cats = frontmatter['categories']
        if len(cats) > 3:
            issues.append("⚠️  Too many categories (> 3), consider consolidating")
    
    if 'tags' in frontmatter:
        tags = frontmatter['tags']
        if len(tags) > 8:
            issues.append("⚠️  Too many tags (> 8), consider reducing")
    
    return issues, frontmatter

def validate_content_structure(content):
    """Validate content structure and formatting"""
    issues = []
    
    # Check for headers
    headers = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
    if len(headers) < 2:
        issues.append("⚠️  Consider adding more headers for better structure")
    
    # Check for very long paragraphs
    paragraphs = content.split('\n\n')
    long_paragraphs = [p for p in paragraphs if len(p) > 500 and not p.startswith('```')]
    if long_paragraphs:
        issues.append(f"⚠️  {len(long_paragraphs)} paragraphs are very long (>500 chars)")
    
    # Check for code blocks
    code_blocks = re.findall(r'```(\w+)?\n', content)
    for i, block in enumerate(code_blocks):
        if not block:
            issues.append(f"⚠️  Code block {i+1} missing language specification")
    
    # Check for images without alt text
    images = re.findall(r'!\[(.*?)\]\(.+?\)', content)
    for img_alt in images:
        if not img_alt.strip():
            issues.append("⚠️  Image found without alt text")
    
    return issues

def validate_links(content):
    """Validate external links (basic check)"""
    issues = []
    
    # Find all links
    links = re.findall(r'\[.*?\]\((https?://[^\)]+)\)', content)
    
    for link in links:
        try:
            # Basic URL validation
            parsed = urlparse(link)
            if not parsed.scheme or not parsed.netloc:
                issues.append(f"⚠️  Invalid URL format: {link}")
        except Exception:
            issues.append(f"⚠️  Could not parse URL: {link}")
    
    if len(links) > 10:
        issues.append("⚠️  Many external links (>10), consider if all are necessary")
    
    return issues

def estimate_reading_time(content):
    """Estimate reading time"""
    # Remove front matter and markdown formatting for word count
    text_content = re.sub(r'^---.*?---\n', '', content, flags=re.DOTALL)
    text_content = re.sub(r'[#*`\[\]()_-]', '', text_content)
    words = len(text_content.split())
    
    reading_time = max(1, round(words / 200))  # 200 words per minute
    return words, reading_time

def validate_post(file_path):
    """Main validation function"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"🔍 Validating: {file_path}")
    print("=" * 50)
    
    all_issues = []
    
    # Validate front matter
    fm_issues, frontmatter = validate_frontmatter(content)
    all_issues.extend(fm_issues)
    
    # Validate content structure
    content_issues = validate_content_structure(content)
    all_issues.extend(content_issues)
    
    # Validate links
    link_issues = validate_links(content)
    all_issues.extend(link_issues)
    
    # Content statistics
    words, reading_time = estimate_reading_time(content)
    
    # Report results
    if not all_issues:
        print("✅ All validations passed!")
    else:
        print("Issues found:")
        for issue in all_issues:
            print(f"  {issue}")
    
    print(f"\n📊 Content Statistics:")
    print(f"   📝 Word count: {words}")
    print(f"   ⏱️  Estimated reading time: {reading_time} min")
    
    if frontmatter and 'title' in frontmatter:
        print(f"   📖 Title: {frontmatter['title']}")
        print(f"   🏷️  Categories: {', '.join(frontmatter.get('categories', []))}")
        print(f"   🔖 Tags: {', '.join(frontmatter.get('tags', []))}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if words < 300:
        print("   📝 Consider expanding content (< 300 words)")
    elif words > 2000:
        print("   ✂️  Consider breaking into multiple posts (> 2000 words)")
    else:
        print("   ✅ Good content length")
    
    severity_count = len([i for i in all_issues if i.startswith('❌')])
    warning_count = len([i for i in all_issues if i.startswith('⚠️')])
    
    print(f"\n📈 Validation Summary:")
    print(f"   ❌ Errors: {severity_count}")
    print(f"   ⚠️  Warnings: {warning_count}")
    
    if severity_count == 0:
        print(f"\n🎉 Post is ready for publishing!")
        print(f"   Run: python _scripts/publish_post.py {file_path}")
        return True
    else:
        print(f"\n🔧 Please fix errors before publishing")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python _scripts/validate_post.py _drafts/my-post.md")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = validate_post(file_path)
    sys.exit(0 if success else 1)