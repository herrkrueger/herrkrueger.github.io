# WordPress to Jekyll Migration Tool

This set of scripts helps you migrate content from your WordPress export to Jekyll format, preserving posts, metadata, and images.

## Overview

The migration process happens in three main steps:

1. **List all WordPress posts** to a CSV file so you can review and select which ones to import
2. **Import selected posts** by ID or date range to the `_drafts` directory
3. **Process the drafts** using your existing Bear/Jekyll workflow for final publishing

## Prerequisites

- Python 3.6 or higher
- WordPress export files (XML)
- WordPress media export files

The scripts will automatically install these Python packages if needed:
- beautifulsoup4
- html2markdown
- python-dateutil

## Scripts Included

- `list_wordpress_posts.py`: Lists all posts from WordPress export files
- `wp_to_jekyll.py`: Converts WordPress posts to Jekyll format
- `import_wordpress.sh`: User-friendly wrapper script to simplify the process

## How to Use

### Step 1: List All Posts

Generate a CSV file of all WordPress posts to review:

```bash
./_scripts/import_wordpress.sh list --output my_posts.csv
```

This will create a CSV file with the following information for each post:
- Post ID
- Publication date
- Title
- Categories
- Tags
- Number of images
- Original URL
- Post slug

The lists are already created and are in /Users/arnekrueger/Documents/github_repos/herrkrueger_old_blog/* in this directory there are also the xml export and the exported media files.

### Step 2: Import Selected Posts

After reviewing the CSV, you can import posts in two ways:

#### Import by Post ID

```bash
./_scripts/import_wordpress.sh import --ids 123,456,789
```

This imports the posts with the specified IDs.

#### Import by Date Range

```bash
# Import posts from 2010
./_scripts/import_wordpress.sh import-date --after 2010-01-01 --before 2010-12-31

# Import posts from a specific date
./_scripts/import_wordpress.sh import-date --after 2010-05-01 --before 2010-05-02

# Import all posts after a certain date
./_scripts/import_wordpress.sh import-date --after 2015-01-01
```

## Features

- **Preserves metadata**: Categories, tags, publication dates
- **Handles images**: Copies images to Jekyll's image directory and updates references
- **Processes galleries**: Extracts images from WordPress gallery shortcodes
- **Converts to Markdown**: Attempts to convert HTML content to Markdown
- **Selective import**: Import only the posts you want
- **Draft workflow**: Imports posts to _drafts for processing with existing Bear workflow
- **Jekyll integration**: Works with your Chirpy theme formatting requirements

## Limitations and Notes

1. **Gallery Handling**: The script attempts to extract images from gallery shortcodes, but complex gallery plugins may not be fully supported.

2. **Image Finding**: Images will be located in the media export directory. If an image cannot be found, its reference in the post will remain unchanged.

3. **Manual Review**: Always review the imported posts to ensure content was migrated correctly.

4. **Multiple XML Files**: If your WordPress export is split across multiple XML files, the script will process all files in the specified directory.

## Integration with Bear Workflow

After importing posts to the `_drafts` directory, you can process them using your existing Bear/Jekyll workflow:

1. The imported posts will be available in the `_drafts` directory with proper Jekyll front matter
2. You can use your existing scripts to process and optimize these drafts:
   ```bash
   python _scripts/process_draft.py _drafts/imported-wordpress-post.md
   ```
3. When ready to publish, use your publish script:
   ```bash
   python _scripts/publish_post.py _drafts/imported-wordpress-post.md
   ```

This workflow allows you to review and enhance the imported content before publishing it to your Jekyll site.

## Troubleshooting

- **Missing Images**: Check that the media directory path is correct and contains the WordPress media export files
- **Conversion Errors**: Review the script output for any error messages related to specific posts
- **HTML in Posts**: If Markdown conversion fails, the HTML content will be preserved
- **Draft Processing**: If the draft format doesn't match your Bear workflow expectations, you may need to adjust the front matter

## Advanced Usage

You can also run the Python scripts directly for more control:

```bash
# List posts
python3 _scripts/list_wordpress_posts.py --xml-file /path/to/wordpress.xml --output posts.csv

# Import posts to drafts
python3 _scripts/wp_to_jekyll.py \
  --xml-file /path/to/wordpress.xml \
  --media-dir /path/to/media \
  --output-dir _drafts \
  --post-ids 123,456,789
```

For help with script options:

```bash
python3 _scripts/list_wordpress_posts.py --help
python3 _scripts/wp_to_jekyll.py --help
```