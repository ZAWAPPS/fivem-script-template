#!/bin/bash
# ZAWAPPS Resource Template Setup Script
# Run this once after creating a new repo from this template.
# Usage: bash .github/scripts/setup-new-repo.sh

set -e

REPO_NAME=$(gh repo view --json name -q .name 2>/dev/null || echo "my-new-script")
REPO_URL=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")

echo "------------------------------------------------"
echo "[*] Initializing ZAWAPPS Resource: $REPO_NAME"
echo "------------------------------------------------"

# 0. Pre-flight Checks
echo "[*] Checking environment..."

# Detect Python
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
elif command -v py &>/dev/null; then
    PYTHON_CMD="py"
else
    echo "[!] Error: Python not found. Please install Python 3."
    exit 1
fi
echo "[+] Python found: $PYTHON_CMD"

# Check GH CLI
if ! command -v gh &>/dev/null; then
    echo "[!] Error: GitHub CLI (gh) is not installed."
    exit 1
fi

if ! gh auth status &>/dev/null; then
    echo "[!] Error: You are not logged into GitHub CLI. Run 'gh auth login' first."
    exit 1
fi

# 1. Update fxmanifest.lua
echo "[*] Updating fxmanifest.lua..."
echo "Enter SCRIPT_NAME (Leave empty to use $REPO_NAME):"
read INPUT_NAME
[ -n "$INPUT_NAME" ] && REPO_NAME=$INPUT_NAME

echo "Enter SCRIPT_DESCRIPTION:"
read SCRIPT_DESCRIPTION
echo "Enter SCRIPT_AUTHOR (Leave empty for 'ZAWAPPS'):"
read SCRIPT_AUTHOR
[ -z "$SCRIPT_AUTHOR" ] && SCRIPT_AUTHOR="ZAWAPPS"
echo "Enter INITIAL_VERSION (e.g. 1.0.0):"
read INITIAL_VERSION

# Use Python for safe replacement to avoid sed delimiter collisions
export REPO_NAME SCRIPT_DESCRIPTION INITIAL_VERSION SCRIPT_AUTHOR
$PYTHON_CMD <<'EOF'
import os

repo = os.environ.get('REPO_NAME', 'SCRIPT_NAME')
desc = os.environ.get('SCRIPT_DESCRIPTION', 'SCRIPT_DESCRIPTION')
ver = os.environ.get('INITIAL_VERSION', '1.0.0')
author = os.environ.get('SCRIPT_AUTHOR', 'ZAWAPPS')

path = 'fxmanifest.lua'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    import re
    content = re.sub(r"name\s+'[^']+'", f"name '{repo}'", content)
    content = re.sub(r"description\s+'[^']+'", f"description '{desc}'", content)
    content = re.sub(r"version\s+'[^']+'", f"version '{ver}'", content)
    content = re.sub(r"author\s+'[^']+'", f"author '{author}'", content)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
EOF

# 2. Setup Local Environment
echo "[*] Setting up local files..."
if [ -f "shared/config.dist.lua" ] && [ ! -f "shared/config.lua" ]; then
    cp shared/config.dist.lua shared/config.lua
    echo "[+] Created shared/config.lua from template."
    fi

    echo "[*] Initializing NUI (web) dependencies..."
    if [ -f "web/package.json" ]; then
        cd web
        if command -v npm &>/dev/null; then
            npm install
            echo "[+] NUI dependencies installed successfully."
        else
            echo "[!] Warning: npm not found. Skipping NUI setup."
        fi
        cd ..
    else
        echo "[i] No web/package.json found. Skipping NUI setup."
    fi

    echo "[*] Setting up Luacheck & Git Hooks..."
    # Try to install via pip as it's common on Windows/macOS/Linux
    if ! command -v luacheck &>/dev/null; then
        echo "[*] Luacheck not found. Attempting to install via pip..."
        $PYTHON_CMD -m pip install luacheck 2>/dev/null || echo "[!] Could not install luacheck automatically. Please install it manually: 'pip install luacheck' or 'luarocks install luacheck'"
    fi

    if [ -f ".github/hooks/pre-commit" ]; then
        cp .github/hooks/pre-commit .git/hooks/pre-commit
        chmod +x .git/hooks/pre-commit
        echo "[+] Installed non-blocking Luacheck pre-commit hook."
    fi

# 3. Configure Branches
echo "[*] Setting up branches..."
git checkout -B main
git checkout -B develop
git push -u origin develop --force

git checkout -B staging
git push -u origin staging --force

git checkout develop

# 3. Configure Repository Settings
echo "[*] Configuring GitHub repository settings..."
gh repo edit "$REPO_URL" --enable-issues --enable-projects=false --enable-wiki=false

echo "[*] Creating repository labels..."
# Ensure the validation label exists so the workflow doesn't crash
gh label create "FAILED VALIDATION" --color "D93F0B" --description "PR failed CI checks" --force 2>/dev/null || true

# 4. Set Secrets
echo "[*] Setting up Secrets..."
echo "Paste PUBLIC Discord Webhook URL (or press Enter to skip):"
read -s PUBLIC_WEBHOOK
if [ -n "$PUBLIC_WEBHOOK" ]; then
    gh secret set DISCORD_WEBHOOK_URL --body "$PUBLIC_WEBHOOK"
fi

echo "Paste STAGING Discord Webhook URL (or press Enter to skip):"
read -s STAGING_WEBHOOK
if [ -n "$STAGING_WEBHOOK" ]; then
    gh secret set DISCORD_STAGING_WEBHOOK_URL --body "$STAGING_WEBHOOK"
fi

echo "------------------------------------------------"
echo "[!] MANDATORY: GitHub Personal Access Token (GH_PAT)"
echo "On GitHub Free, this is REQUIRED for automated branch sync."
echo "The token needs 'repo' and 'workflow' scopes."
echo "------------------------------------------------"
while [ -z "$GH_PAT_TOKEN" ]; do
    echo "Paste GH_PAT (Required):"
    read -s GH_PAT_TOKEN
done

gh secret set GH_PAT --body "$GH_PAT_TOKEN"
echo "[+] GH_PAT set successfully."

# 5. Final Commit
echo "[*] Committing initial configuration..."
git add fxmanifest.lua
git commit -m "chore: initial repository setup" || echo "Nothing to commit"
git push origin develop

echo "------------------------------------------------"
echo "[+] $REPO_NAME is ready for development!"
echo "Current branch: develop"
echo "Next steps:"
echo "  1. Verify fxmanifest.lua details."
echo "  2. Update README.md with script documentation."
echo "  3. Start coding!"
echo "------------------------------------------------"
