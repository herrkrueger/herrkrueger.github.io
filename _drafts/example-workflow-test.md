---
author: Arne Krueger
categories:
- Development
- Tools
date: 2025-06-09 12:24:32 +0100
description: A blog post about setting up an efficient blogging workflow with bear
  and jekyll
tags:
- python
- jekyll
- automation
title: Setting Up an Efficient Blogging Workflow with Bear and Jekyll
---

As a tech consultant running mtc.berlin, I needed a streamlined way to go from idea to published blog post. After trying various solutions, I've settled on a workflow that combines Bear for writing with Jekyll for publishing.

This post shares the complete setup and workflow that now powers my content creation process.

## The Challenge

Writing technical blog posts involves several steps:
- Drafting and editing content
- Formatting for Jekyll
- Adding proper metadata 
- Optimizing for SEO
- Publishing and deployment

Most solutions either overcomplicate the writing process or require too much manual formatting work.

## The Solution: Bear + Jekyll + Automation

My workflow now looks like this:

1. **Write in Bear** - Clean, distraction-free writing environment
2. **Export to _drafts** - Simple markdown export
3. **Ask Claude for help** - Automated processing and optimization
4. **Review and publish** - One-click publishing to Jekyll

### Why Bear?

Bear offers several advantages for technical writing:
- Excellent markdown support
- Great organizational features with hashtags
- Seamless sync across devices
- Clean, focused writing interface

### Automation Scripts

I've created several Python scripts to automate the tedious parts:

```python
# Process a draft from Bear export
python _scripts/process_draft.py _drafts/my-post.md

# Validate formatting and content
python _scripts/validate_post.py _drafts/my-post.md

# Publish to Jekyll
python _scripts/publish_post.py _drafts/my-post.md
```

## The Complete Workflow

### Step 1: Writing in Bear
I start by creating a new note in Bear. The hashtag system helps organize ideas by topic.

### Step 2: Export and Process
When ready to publish, I export the note as markdown to my Jekyll site's `_drafts` folder, then run the processing script.

### Step 3: Review and Optimize
The validation script checks for:
- Proper front matter
- SEO optimization
- Content structure
- Link validation

### Step 4: Publish
The publish script handles:
- Proper Jekyll filename format
- Final content formatting
- Moving to `_posts` directory

## Results

This workflow has dramatically improved my content creation efficiency:
- Writing time reduced by focusing only on content
- Zero manual formatting work
- Consistent post structure and SEO optimization
- Automated quality checks

## What's Next

I'm considering adding:
- Automated image optimization
- Social media post generation
- Analytics integration for content performance

The key insight is that great content workflows separate the creative process from the technical implementation. By automating the technical parts, writers can focus on what matters most: creating valuable content.

What's your content creation workflow? I'd love to hear about tools and processes that work for you.