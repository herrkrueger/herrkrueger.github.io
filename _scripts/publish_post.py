#!/usr/bin/env python3
"""
Publish draft to _posts with proper Jekyll filename
Usage: python _scripts/publish_post.py _drafts/my-post.md
"""

import sys
import os
import re
import yaml
import shutil
from datetime import datetime
from pathlib import Path

def extract_frontmatter(content):
    """Extract and parse front matter"""
    if not content.startswith('---\n'):
        return None, content
    
    end_idx = content.find('\n---\n', 4)
    if end_idx == -1:
        return None, content
    
    try:
        fm_content = content[4:end_idx]
        frontmatter = yaml.safe_load(fm_content)
        post_content = content[end_idx + 5:]
        return frontmatter, post_content
    except yaml.YAMLError:
        return None, content

def create_jekyll_filename(title, date_str):
    """Create Jekyll post filename format: YYYY-MM-DD-title.md"""
    # Parse date
    try:
        date_obj = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
    except (ValueError, AttributeError):
        date_obj = datetime.now()
    
    # Clean title for filename
    clean_title = re.sub(r'[^\w\s-]', '', title)
    clean_title = re.sub(r'[-\s]+', '-', clean_title)
    clean_title = clean_title.strip('-').lower()
    
    filename = f"{date_obj.strftime('%Y-%m-%d')}-{clean_title}.md"
    return filename

def update_frontmatter_for_publishing(frontmatter):
    """Update front matter for publishing"""
    # Ensure we have a proper date
    if 'date' not in frontmatter or not frontmatter['date']:
        frontmatter['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S +0100')
    
    # Add author if missing
    if 'author' not in frontmatter:
        frontmatter['author'] = 'Arne Krueger'
    
    # Ensure categories and tags are lists
    if 'categories' in frontmatter and isinstance(frontmatter['categories'], str):
        frontmatter['categories'] = [frontmatter['categories']]
    
    if 'tags' in frontmatter and isinstance(frontmatter['tags'], str):
        frontmatter['tags'] = [frontmatter['tags']]
    
    return frontmatter

def publish_post(draft_path):
    """Main publishing function"""
    if not os.path.exists(draft_path):
        print(f"❌ Draft not found: {draft_path}")
        return False
    
    # Read draft
    with open(draft_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract front matter
    frontmatter, post_content = extract_frontmatter(content)
    if not frontmatter:
        print("❌ No valid front matter found. Run process_draft.py first.")
        return False
    
    # Validate required fields
    required_fields = ['title', 'date']
    for field in required_fields:
        if field not in frontmatter:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Update front matter for publishing
    frontmatter = update_frontmatter_for_publishing(frontmatter)
    
    # Create Jekyll filename
    filename = create_jekyll_filename(frontmatter['title'], frontmatter['date'])
    posts_path = Path('_posts') / filename
    
    # Check if post already exists
    if posts_path.exists():
        response = input(f"⚠️  Post {filename} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Publishing cancelled")
            return False
    
    # Create final content
    final_frontmatter = "---\n" + yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True) + "---\n\n"
    final_content = final_frontmatter + post_content
    
    # Ensure _posts directory exists
    Path('_posts').mkdir(exist_ok=True)
    
    # Write published post
    with open(posts_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"✅ Published post: {posts_path}")
    print(f"📝 Title: {frontmatter['title']}")
    print(f"📅 Date: {frontmatter['date']}")
    print(f"🏷️  Categories: {', '.join(frontmatter.get('categories', []))}")
    print(f"🔖 Tags: {', '.join(frontmatter.get('tags', []))}")
    
    # Ask if user wants to remove draft
    response = input(f"\n🗑️  Remove draft {draft_path}? (y/N): ")
    if response.lower() == 'y':
        os.remove(draft_path)
        print(f"✅ Removed draft: {draft_path}")
    
    print(f"\n🎉 Next steps:")
    print(f"   1. Review the published post: {posts_path}")
    print(f"   2. Test locally: bundle exec jekyll serve")
    print(f"   3. Commit and push to deploy:")
    print(f"      git add {posts_path}")
    print(f"      git commit -m 'Add new post: {frontmatter['title']}'")
    print(f"      git push origin master")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python _scripts/publish_post.py _drafts/my-post.md")
        sys.exit(1)
    
    draft_path = sys.argv[1]
    success = publish_post(draft_path)
    sys.exit(0 if success else 1)