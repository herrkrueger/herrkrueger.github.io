# Claude Blogging Workflow for herrkrueger.github.io

This document describes the automated blogging workflow for Arne Krueger's Jekyll site using Bear notes and Claude assistance.

## Workflow Overview

1. **Write in Bear**: Draft your posts in Bear app
2. **Export to _drafts**: Export as Markdown to `_drafts/` folder
3. **Ask Claude**: Request formatting, optimization, and publishing help
4. **Review & Publish**: Claude processes and moves to `_posts/` with proper Jekyll formatting

## Bear Export Instructions

### Recommended Bear Export Format
- **Format**: Markdown
- **Location**: `_drafts/` folder in your Jekyll repo
- **Filename**: Use descriptive names like `my-awesome-post-idea.md`

### Bear Export Settings
1. In Bear, select your post
2. File → Export → Markdown
3. Save to: `~/Documents/github_repos/herrkrueger.github.io/_drafts/`
4. Keep original Bear formatting and hashtags

## Claude Workflow Commands

When you have a draft ready, use these commands:

### Basic Commands
- `claude process draft [filename]` - Format and optimize a draft
- `claude review draft [filename]` - Review content and suggest improvements  
- `claude publish draft [filename]` - Move to _posts with proper Jekyll front matter
- `claude check drafts` - List all drafts and their status

### Content Enhancement
- `claude seo optimize [filename]` - Optimize for SEO
- `claude add tags [filename]` - Suggest and add relevant tags
- `claude generate excerpt [filename]` - Create compelling excerpt
- `claude check links [filename]` - Validate all links in post

## Jekyll Post Requirements (Chirpy Theme)

### Required Front Matter
```yaml
---
title: "Your Post Title"
date: YYYY-MM-DD HH:MM:SS +0100
categories: [Category1, Category2]
tags: [tag1, tag2, tag3]
description: "Brief description for SEO and social sharing"
---
```

### Chirpy-Specific Features
- **Table of Contents**: Automatically generated if post has headers
- **Code Blocks**: Use fenced code blocks with language specification
- **Images**: Place in `/images/` folder, reference as `/images/filename.jpg`
- **Math**: Supports MathJax for mathematical expressions
- **Mermaid**: Supports diagrams and flowcharts

## File Structure

```
herrkrueger.github.io/
├── _drafts/              # Bear exports go here
│   ├── draft-post-1.md
│   └── another-idea.md
├── _posts/               # Published posts
├── _scripts/             # Helper scripts
│   ├── process_draft.py
│   ├── validate_post.py
│   └── publish_post.py
├── images/               # Post images
└── CLAUDE.md            # This file
```

## Content Guidelines

### Writing Style
- **Tone**: Professional but approachable, matching mtc.berlin brand
- **Length**: Aim for 800-2000 words for substantial posts
- **Structure**: Use clear headings, bullet points, and short paragraphs
- **Code**: Include practical examples and well-commented code blocks

### SEO Best Practices
- **Title**: 50-60 characters, include primary keyword
- **Description**: 150-160 characters, compelling and descriptive
- **Headers**: Use H2, H3 hierarchy for better structure
- **Internal Links**: Link to relevant previous posts
- **Images**: Include alt text and descriptive filenames

### Technical Content
- **Code Examples**: Always test code before publishing
- **Screenshots**: Use high-quality images, optimize for web
- **Links**: Prefer HTTPS, check for broken links
- **Updates**: Add update notes for time-sensitive content

## Helper Scripts

### Available Scripts
- `_scripts/process_draft.py` - Convert Bear export to Jekyll format
- `_scripts/validate_post.py` - Check post formatting and requirements
- `_scripts/publish_post.py` - Move draft to _posts with proper filename
- `_scripts/optimize_images.py` - Compress and optimize images
- `_scripts/check_links.py` - Validate all external links

### Usage Examples
```bash
# Process a new draft from Bear
python _scripts/process_draft.py _drafts/my-new-post.md

# Validate before publishing
python _scripts/validate_post.py _drafts/my-new-post.md

# Publish when ready
python _scripts/publish_post.py _drafts/my-new-post.md
```

## Quality Checklist

Before publishing, ensure:
- [ ] Front matter is complete and accurate
- [ ] Title is SEO-optimized and engaging
- [ ] Categories and tags are relevant and consistent
- [ ] All code examples work and are well-formatted
- [ ] Images are optimized and have alt text
- [ ] External links work and open appropriately
- [ ] Grammar and spelling are correct
- [ ] Post structure is clear with good headings
- [ ] Excerpt is compelling and informative

## Categories and Tags Strategy

### Main Categories
- `Technology` - General tech topics
- `Development` - Programming and development
- `Business` - mtc.berlin business insights
- `Tools` - Software tools and productivity
- `Tutorials` - Step-by-step guides

### Common Tags
- Programming languages: `python`, `javascript`, `ruby`
- Technologies: `jekyll`, `github`, `docker`, `aws`
- Concepts: `automation`, `productivity`, `security`, `performance`
- Business: `entrepreneurship`, `consulting`, `strategy`

## Deployment Process

1. **Local Testing**: Always test locally with `bundle exec jekyll serve`
2. **Git Workflow**: Commit and push to trigger GitHub Actions
3. **Monitoring**: Check GitHub Actions for successful deployment
4. **Verification**: Visit live site to confirm post appears correctly

## Backup and Version Control

- **Bear Backups**: Keep original Bear notes as backup
- **Git History**: All changes tracked in git repository
- **Draft Preservation**: _drafts folder maintains work-in-progress posts
- **Image Management**: All images committed to git for versioning

---

*Last Updated: June 9, 2025*
*This workflow is designed to maximize efficiency while maintaining high-quality content standards.*