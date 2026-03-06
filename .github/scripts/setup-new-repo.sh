#!/bin/bash
# Run this once after creating a new repo from this template.
# Requirements: GitHub CLI installed and authenticated.
# Usage: bash .github/scripts/setup-new-repo.sh

set -e

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "Setting up $REPO..."

# Create branches
echo ""
echo "Creating branches..."
git checkout -b develop 2>/dev/null || git checkout develop
git push -u origin develop

git checkout -b staging 2>/dev/null || git checkout staging
git push -u origin staging

git checkout main
git push -u origin main

# Configure merge settings (squash only)
echo "Configuring merge settings..."
gh api \
  --method PATCH \
  -H "Accept: application/vnd.github+json" \
  /repos/$REPO \
  -f allow_squash_merge=true \
  -f allow_merge_commit=false \
  -f allow_rebase_merge=false

# Enable issues
echo "Enabling issues..."
gh repo edit --enable-issues

# Set repository secrets
echo ""
echo "Setting repository secrets..."
echo "Paste your PUBLIC Discord webhook URL (release announcements), then press Enter:"
read -s DISCORD_WEBHOOK
echo "Paste your STAGING Discord webhook URL (internal builds), then press Enter:"
read -s DISCORD_STAGING_WEBHOOK

gh secret set DISCORD_WEBHOOK_URL --body "$DISCORD_WEBHOOK"
gh secret set DISCORD_STAGING_WEBHOOK_URL --body "$DISCORD_STAGING_WEBHOOK"
echo "Secrets set."

# Branch protection: main
echo ""
echo "Setting up branch protection: main..."
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/$REPO/branches/main/protection \
  -f required_status_checks='{"strict":true,"contexts":["validate"]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"required_approving_review_count":0}' \
  -f restrictions=null

# Branch protection: staging
echo "Setting up branch protection: staging..."
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/$REPO/branches/staging/protection \
  -f required_status_checks='{"strict":true,"contexts":["validate"]}' \
  -f enforce_admins=false \
  -f required_pull_request_reviews='{"required_approving_review_count":0}' \
  -f restrictions=null

# Branch protection: develop
echo "Setting up branch protection: develop..."
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/$REPO/branches/develop/protection \
  -f required_status_checks='{"strict":true,"contexts":["validate"]}' \
  -f enforce_admins=false \
  -f required_pull_request_reviews='{"required_approving_review_count":0}' \
  -f restrictions=null

echo ""
echo "✅ $REPO is ready."
echo ""
echo "Next steps:"
echo "  1. Update fxmanifest.lua with your script name, description and author"
echo "  2. Replace README.md with your script documentation"
echo "  3. Add your config options to shared/config.dist.lua"
echo "  4. Start coding: git checkout develop && git checkout -b feature/your-feature"