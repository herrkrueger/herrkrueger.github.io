#!/bin/bash

# WordPress to Jekyll Import Script
# This script helps to migrate WordPress blog posts to Jekyll format

# Default paths - adjust as needed
WP_EXPORT_DIR="/Users/arnekrueger/Documents/github_repos/herrkrueger_old_blog/herrkrueger.wordpress.com-2023-02-22-15_06_07"
WP_MEDIA_DIR="/Users/arnekrueger/Documents/github_repos/herrkrueger_old_blog/media-export-3815432-from-0-to-20073"
JEKYLL_DRAFTS_DIR="/Users/arnekrueger/Documents/github_repos/herrkrueger.github.io/_drafts"
SCRIPT_DIR="$(dirname "$0")"

# Function to display help message
function show_help {
  echo "WordPress to Jekyll Migration Helper"
  echo ""
  echo "Usage:"
  echo "  $0 [command] [options]"
  echo ""
  echo "Commands:"
  echo "  list              List all WordPress posts to a CSV file"
  echo "  import            Import posts by ID"
  echo "  import-date       Import posts by date range"
  echo "  help              Show this help message"
  echo ""
  echo "Options for 'list':"
  echo "  --output FILE     CSV file to save post list (default: wp_posts.csv)"
  echo ""
  echo "Options for 'import':"
  echo "  --ids ID1,ID2,... Comma-separated list of post IDs to import"
  echo ""
  echo "Options for 'import-date':"
  echo "  --after YYYY-MM-DD   Import posts published after this date"
  echo "  --before YYYY-MM-DD  Import posts published before this date"
  echo ""
  echo "Examples:"
  echo "  $0 list --output my_posts.csv"
  echo "  $0 import --ids 123,456,789"
  echo "  $0 import-date --after 2010-01-01 --before 2010-12-31"
}

# Ensure required packages are installed
function check_requirements {
  echo "Installing required Python packages..."
  pip install beautifulsoup4 html2markdown python-dateutil
}

# Function to list all WordPress posts
function list_posts {
  local output_file="${1:-wp_posts.csv}"
  
  echo "Listing all WordPress posts..."
  python3 "$SCRIPT_DIR/list_wordpress_posts.py" \
    --xml-file "$WP_EXPORT_DIR/arnekrueger.wordpress.2023-02-22.000.xml" \
    --output "$output_file"
  
  # If there's a second XML file, process it too
  if [ -f "$WP_EXPORT_DIR/arnekrueger.wordpress.2023-02-22.001.xml" ]; then
    echo "Processing second XML file..."
    python3 "$SCRIPT_DIR/list_wordpress_posts.py" \
      --xml-file "$WP_EXPORT_DIR/arnekrueger.wordpress.2023-02-22.001.xml" \
      --output "${output_file%.csv}_part2.csv"
  fi
  
  echo "Post list saved to $output_file"
  echo "You can now review the CSV file and decide which posts to import."
}

# Function to import posts by ID
function import_posts_by_id {
  local post_ids="$1"
  
  if [ -z "$post_ids" ]; then
    echo "Error: No post IDs provided. Use --ids option."
    exit 1
  fi
  
  echo "Importing posts with IDs: $post_ids"
  python3 "$SCRIPT_DIR/wp_to_jekyll.py" \
    --xml-file "$WP_EXPORT_DIR/arnekrueger.wordpress.2023-02-22.000.xml" \
    --media-dir "$WP_MEDIA_DIR" \
    --output-dir "$JEKYLL_DRAFTS_DIR" \
    --post-ids "$post_ids"
  
  # If there's a second XML file, process it too
  if [ -f "$WP_EXPORT_DIR/arnekrueger.wordpress.2023-02-22.001.xml" ]; then
    echo "Processing second XML file..."
    python3 "$SCRIPT_DIR/wp_to_jekyll.py" \
      --xml-file "$WP_EXPORT_DIR/arnekrueger.wordpress.2023-02-22.001.xml" \
      --media-dir "$WP_MEDIA_DIR" \
      --output-dir "$JEKYLL_DRAFTS_DIR" \
      --post-ids "$post_ids"
  fi
  
  echo "Import complete!"
}

# Function to import posts by date range
function import_posts_by_date {
  local date_after="$1"
  local date_before="$2"
  
  if [ -z "$date_after" ] && [ -z "$date_before" ]; then
    echo "Error: No date range provided. Use --after and/or --before options."
    exit 1
  fi
  
  echo "Importing posts by date range..."
  
  # Build command arguments
  local date_args=""
  if [ -n "$date_after" ]; then
    date_args="--date-after $date_after"
  fi
  
  if [ -n "$date_before" ]; then
    date_args="$date_args --date-before $date_before"
  fi
  
  python3 "$SCRIPT_DIR/wp_to_jekyll.py" \
    --xml-file "$WP_EXPORT_DIR/arnekrueger.wordpress.2023-02-22.000.xml" \
    --media-dir "$WP_MEDIA_DIR" \
    --output-dir "$JEKYLL_DRAFTS_DIR" \
    $date_args
  
  # If there's a second XML file, process it too
  if [ -f "$WP_EXPORT_DIR/arnekrueger.wordpress.2023-02-22.001.xml" ]; then
    echo "Processing second XML file..."
    python3 "$SCRIPT_DIR/wp_to_jekyll.py" \
      --xml-file "$WP_EXPORT_DIR/arnekrueger.wordpress.2023-02-22.001.xml" \
      --media-dir "$WP_MEDIA_DIR" \
      --output-dir "$JEKYLL_DRAFTS_DIR" \
      $date_args
  fi
  
  echo "Import complete!"
}

# Parse command line arguments
if [ $# -eq 0 ]; then
  show_help
  exit 0
fi

# Check for required packages
check_requirements

# Process commands
case "$1" in
  list)
    shift
    output_file="wp_posts.csv"
    while [ $# -gt 0 ]; do
      case "$1" in
        --output)
          output_file="$2"
          shift 2
          ;;
        *)
          echo "Unknown option: $1"
          exit 1
          ;;
      esac
    done
    list_posts "$output_file"
    ;;
    
  import)
    shift
    post_ids=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --ids)
          post_ids="$2"
          shift 2
          ;;
        *)
          echo "Unknown option: $1"
          exit 1
          ;;
      esac
    done
    import_posts_by_id "$post_ids"
    ;;
    
  import-date)
    shift
    date_after=""
    date_before=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --after)
          date_after="$2"
          shift 2
          ;;
        --before)
          date_before="$2"
          shift 2
          ;;
        *)
          echo "Unknown option: $1"
          exit 1
          ;;
      esac
    done
    import_posts_by_date "$date_after" "$date_before"
    ;;
    
  help)
    show_help
    ;;
    
  *)
    echo "Unknown command: $1"
    show_help
    exit 1
    ;;
esac

exit 0