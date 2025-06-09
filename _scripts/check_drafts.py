#!/usr/bin/env python3
"""
Check and list all drafts with their status
Usage: python _scripts/check_drafts.py
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime

def extract_frontmatter(content):
    """Extract front matter from content"""
    if not content.startswith('---\n'):
        return None
    
    end_idx = content.find('\n---\n', 4)
    if end_idx == -1:
        return None
    
    try:
        fm_content = content[4:end_idx]
        return yaml.safe_load(fm_content)
    except yaml.YAMLError:
        return None

def analyze_draft(file_path):
    """Analyze a single draft file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}
    
    frontmatter = extract_frontmatter(content)
    
    # Basic stats
    words = len(content.split())
    lines = len(content.splitlines())
    
    # Check for images
    images = len(re.findall(r'!\[.*?\]\(.+?\)', content))
    
    # Check for code blocks
    code_blocks = len(re.findall(r'```', content)) // 2
    
    # Status assessment
    status = "🔴 Needs Processing"
    if frontmatter:
        required_fields = ['title', 'date', 'categories', 'tags']
        if all(field in frontmatter for field in required_fields):
            status = "🟢 Ready to Publish"
        else:
            missing = [f for f in required_fields if f not in frontmatter]
            status = f"🟡 Missing: {', '.join(missing)}"
    
    return {
        'frontmatter': frontmatter,
        'words': words,
        'lines': lines,
        'images': images,
        'code_blocks': code_blocks,
        'status': status,
        'size': os.path.getsize(file_path)
    }

def check_drafts():
    """Main function to check all drafts"""
    drafts_dir = Path('_drafts')
    
    if not drafts_dir.exists():
        print("📁 No _drafts directory found. Creating it...")
        drafts_dir.mkdir()
        print("✅ Created _drafts directory")
        return
    
    draft_files = list(drafts_dir.glob('*.md'))
    
    if not draft_files:
        print("📝 No drafts found in _drafts directory")
        print("💡 Export your Bear notes as Markdown to _drafts/ to get started!")
        return
    
    print(f"📚 Found {len(draft_files)} draft(s)")
    print("=" * 80)
    
    for draft_file in sorted(draft_files):
        print(f"\n📄 {draft_file.name}")
        print("-" * 50)
        
        analysis = analyze_draft(draft_file)
        
        if 'error' in analysis:
            print(f"❌ Error reading file: {analysis['error']}")
            continue
        
        print(f"Status: {analysis['status']}")
        print(f"📊 Stats: {analysis['words']} words, {analysis['lines']} lines, {analysis['size']} bytes")
        
        if analysis['images']:
            print(f"🖼️  Images: {analysis['images']}")
        
        if analysis['code_blocks']:
            print(f"💻 Code blocks: {analysis['code_blocks']}")
        
        if analysis['frontmatter']:
            fm = analysis['frontmatter']
            if 'title' in fm:
                print(f"📝 Title: {fm['title']}")
            if 'date' in fm:
                print(f"📅 Date: {fm['date']}")
            if 'categories' in fm:
                print(f"🏷️  Categories: {', '.join(fm.get('categories', []))}")
            if 'tags' in fm:
                print(f"🔖 Tags: {', '.join(fm.get('tags', []))}")
        else:
            print("⚠️  No front matter found")
        
        # Suggestions
        if analysis['status'] == "🔴 Needs Processing":
            print(f"💡 Next: python _scripts/process_draft.py {draft_file}")
        elif analysis['status'].startswith("🟡"):
            print(f"💡 Next: Edit front matter, then validate")
        elif analysis['status'] == "🟢 Ready to Publish":
            print(f"💡 Next: python _scripts/validate_post.py {draft_file}")
    
    print("\n" + "=" * 80)
    print("🛠️  Available commands:")
    print("   python _scripts/process_draft.py _drafts/filename.md")
    print("   python _scripts/validate_post.py _drafts/filename.md")
    print("   python _scripts/publish_post.py _drafts/filename.md")

if __name__ == "__main__":
    check_drafts()