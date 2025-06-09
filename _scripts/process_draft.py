#!/usr/bin/env python3
"""
Process Bear-exported draft into Jekyll-ready format
Usage: python _scripts/process_draft.py _drafts/my-post.md
"""

import sys
import os
import re
import yaml
from datetime import datetime
from pathlib import Path

def extract_title_from_content(content):
    """Extract title from first H1 or use filename"""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return None

def clean_bear_content(content):
    """Clean up Bear-specific formatting"""
    # Remove Bear hashtags that aren't meant to be markdown headers
    content = re.sub(r'^#(\w+)\s*$', r'', content, flags=re.MULTILINE)
    
    # Clean up multiple newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Fix image paths if they reference local Bear images
    content = re.sub(r'!\[(.*?)\]\(bear://.*?\)', r'![Image: \1]()', content)
    
    return content.strip()

def suggest_categories_and_tags(content, title):
    """Suggest categories and tags based on content"""
    content_lower = content.lower()
    title_lower = title.lower() if title else ""
    
    # Common categories for mtc.berlin blog
    categories = []
    if any(word in content_lower for word in ['python', 'javascript', 'code', 'programming', 'development']):
        categories.append('Development')
    if any(word in content_lower for word in ['business', 'client', 'consulting', 'strategy']):
        categories.append('Business')
    if any(word in content_lower for word in ['tool', 'software', 'app', 'productivity']):
        categories.append('Tools')
    if any(word in content_lower for word in ['tutorial', 'how to', 'guide', 'step']):
        categories.append('Tutorials')
    if not categories:
        categories.append('Technology')
    
    # Extract potential tags
    tags = []
    tech_keywords = ['python', 'javascript', 'jekyll', 'github', 'docker', 'aws', 'automation', 'ai', 'machine learning']
    for keyword in tech_keywords:
        if keyword in content_lower or keyword in title_lower:
            tags.append(keyword)
    
    return categories[:2], tags[:5]  # Limit to reasonable numbers

def create_jekyll_frontmatter(title, categories, tags, description=""):
    """Create Jekyll front matter"""
    now = datetime.now()
    frontmatter = {
        'title': title,
        'date': now.strftime('%Y-%m-%d %H:%M:%S +0100'),
        'categories': categories,
        'tags': tags,
        'description': description or f"A blog post about {title.lower()}",
        'author': 'Arne Krueger'
    }
    
    return "---\n" + yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True) + "---\n\n"

def process_draft(draft_path):
    """Main processing function"""
    if not os.path.exists(draft_path):
        print(f"Error: File {draft_path} not found")
        return False
    
    # Read the draft
    with open(draft_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title
    title = extract_title_from_content(content)
    if not title:
        filename = Path(draft_path).stem
        title = filename.replace('-', ' ').replace('_', ' ').title()
    
    # Clean content
    cleaned_content = clean_bear_content(content)
    
    # Remove the first H1 if it matches the title (avoid duplication)
    if cleaned_content.startswith(f"# {title}"):
        cleaned_content = cleaned_content[len(f"# {title}"):].lstrip('\n')
    
    # Suggest categories and tags
    categories, tags = suggest_categories_and_tags(cleaned_content, title)
    
    # Create front matter
    frontmatter = create_jekyll_frontmatter(title, categories, tags)
    
    # Combine everything
    final_content = frontmatter + cleaned_content
    
    # Write back to file
    with open(draft_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"✅ Processed draft: {draft_path}")
    print(f"📝 Title: {title}")
    print(f"🏷️  Categories: {', '.join(categories)}")
    print(f"🔖 Tags: {', '.join(tags)}")
    print(f"\n📋 Next steps:")
    print(f"   1. Review and edit the processed draft")
    print(f"   2. Add/modify categories and tags as needed")
    print(f"   3. Add images to /images/ if needed")
    print(f"   4. Run: python _scripts/validate_post.py {draft_path}")
    print(f"   5. When ready: python _scripts/publish_post.py {draft_path}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python _scripts/process_draft.py _drafts/my-post.md")
        sys.exit(1)
    
    draft_path = sys.argv[1]
    success = process_draft(draft_path)
    sys.exit(0 if success else 1)