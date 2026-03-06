#!/bin/bash
# Run this before opening a PR to develop.
# Creates changelog fragment files from your input.
# Usage: bash .github/scripts/add-fragment.sh

set -e

BRANCH=$(git branch --show-current)
SAFE_NAME=$(echo "$BRANCH" | sed 's/feature\///' | sed 's/[^a-zA-Z0-9_-]/-/g')

echo "Creating changelog fragment for branch: $BRANCH"
echo ""
echo "Available types: added, changed, fixed, removed, config"
echo ""

create_fragment() {
  local TYPE=$1
  local MESSAGE=$2
  local FILENAME=".changelog/fragments/${SAFE_NAME}.${TYPE}.md"

  if [ -f "$FILENAME" ]; then
    echo "- $MESSAGE" >> "$FILENAME"
  else
    echo "- $MESSAGE" > "$FILENAME"
  fi

  echo "Written: $FILENAME"
}

while true; do
  read -p "Type (or press Enter to finish): " TYPE

  if [ -z "$TYPE" ]; then
    break
  fi

  case "$TYPE" in
    added|changed|fixed|removed|config) ;;
    *)
      echo "Invalid type. Must be one of: added, changed, fixed, removed, config"
      continue
      ;;
  esac

  read -p "Message: " MESSAGE

  if [ -z "$MESSAGE" ]; then
    echo "Message cannot be empty"
    continue
  fi

  create_fragment "$TYPE" "$MESSAGE"
done

FRAGMENTS=$(find .changelog/fragments -name "*.md" ! -name ".gitkeep" 2>/dev/null)

if [ -z "$FRAGMENTS" ]; then
  echo ""
  echo "No fragments created."
  exit 0
fi

echo ""
echo "Staging fragment files..."
git add .changelog/fragments/

echo ""
echo "Done. Your fragments:"
echo "$FRAGMENTS"
echo ""
echo "Commit and push, then open your PR to develop."