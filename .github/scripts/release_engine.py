#!/usr/bin/env python3
import os
import re
import sys
import json
import subprocess
from datetime import date

CHANGELOG_FILE = 'CHANGELOG.md'
MANIFEST_FILE = 'fxmanifest.lua'
MARKER = '<!-- release notes start -->'

def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, errors='ignore')
    if result.returncode != 0: return None
    return result.stdout.strip()

def get_last_tag():
    tag = run_cmd(['git', 'describe', '--tags', '--abbrev=0'])
    if not tag:
        tag = run_cmd(['git', 'rev-list', '--max-parents=0', 'HEAD'])
    return tag

def get_merged_prs(last_tag):
    """Gathers PRs merged into main, staging, or develop since the last tag."""
    all_prs = []
    env = os.environ.copy()
    if 'GH_TOKEN' not in env and 'GITHUB_TOKEN' in env:
        env['GH_TOKEN'] = env['GITHUB_TOKEN']

    # We fetch a slightly larger limit to ensure we don't miss chain PRs
    for base in ['develop', 'staging', 'main']:
        cmd = ['gh', 'pr', 'list', '--state', 'merged', '--base', base, '--limit', '1000', '--json', 'number,title,body,mergeCommit']
        result = subprocess.run(cmd, capture_output=True, text=True, errors='ignore', env=env)
        if result.returncode == 0:
            try:
                all_prs.extend(json.loads(result.stdout))
            except json.JSONDecodeError:
                continue

    # Deduplicate by PR number
    unique_prs_map = {pr['number']: pr for pr in all_prs}
    
    # Identify the cutoff timestamp from the last tag
    try:
        tag_timestamp = run_cmd(['git', 'log', '-1', '--format=%at', last_tag])
        is_initial = len(last_tag) >= 40 
    except:
        tag_timestamp = "0"
        is_initial = True

    if not tag_timestamp: tag_timestamp = "0"

    final_prs = []
    for pr_num in sorted(unique_prs_map.keys()):
        pr = unique_prs_map[pr_num]
        if not pr.get('mergeCommit'): continue
        
        merge_commit = pr['mergeCommit']['oid']
        merge_timestamp = run_cmd(['git', 'log', '-1', '--format=%at', merge_commit])
        
        if is_initial or (merge_timestamp and int(merge_timestamp) > int(tag_timestamp)):
            # Skip PRs that are just automated syncs if they don't have unique notes
            if "sync main to" in pr['title'].lower() or "sync develop to" in pr['title'].lower():
                notes = extract_changelog(pr['body'])
                if not notes or notes.lower() == 'none':
                    continue
            final_prs.append(pr)

    return final_prs

def extract_changelog(pr_body):
    if not pr_body: return None
    match = re.search(r'## Changelog\s*\n(.*?)(?=\n## |\Z)', pr_body, re.DOTALL)
    if not match: return None
    
    # Remove HTML comments (<!-- ... -->)
    content = re.sub(r'<!--.*?-->', '', match.group(1), flags=re.DOTALL).strip()
    if not content or content.lower() == 'none': return None
        
    lines = []
    for line in content.split('\n'):
        line = line.strip()
        if not line: continue
        if not line.startswith('- '): line = f'- {line}'
        lines.append(line)
    
    return '\n'.join(lines)

def build_full_changelog(version, prs):
    today = date.today().strftime('%Y-%m-%d')
    entry = [f'## [{version}] - {today}', '']
    
    seen_notes = set()
    found_any = False
    
    for pr in prs:
        notes = extract_changelog(pr['body'])
        if notes and notes not in seen_notes:
            entry.append(f'#### PR #{pr["number"]}: {pr["title"]}')
            entry.append(notes)
            entry.append('')
            seen_notes.add(notes)
            found_any = True
            
    if not found_any:
        entry.append('- Internal updates and stability improvements.')
        entry.append('')
        
    return '\n'.join(entry)

def update_manifest(version):
    if not os.path.exists(MANIFEST_FILE): return False
    with open(MANIFEST_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Quote-agnostic replacement
    new_content = re.sub(
        r"^(\s*version\s+)(['\"])[^'\"]*(['\"])", 
        r"\1\2" + version + r"\3", 
        content, 
        flags=re.M
    )

    if new_content == content:
        return False

    with open(MANIFEST_FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)
    return True

def update_changelog_file(version, entry):
    if not os.path.exists(CHANGELOG_FILE):
        with open(CHANGELOG_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# Changelog\n\n{MARKER}\n")
            
    with open(CHANGELOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    if MARKER not in content:
        content = f"# Changelog\n\n{MARKER}\n\n" + content

    version_header = f"## [{version}]"
    if version_header in content:
        return
        
    new_content = content.replace(MARKER, f"{MARKER}\n\n{entry.strip()}\n", 1)
    
    with open(CHANGELOG_FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)

if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(1)
    version = sys.argv[1].lstrip('v')
    
    last_tag = get_last_tag()
    prs = get_merged_prs(last_tag)
    entry = build_full_changelog(version, prs)
    
    if os.environ.get('DRY_RUN') == 'true':
        print(entry)
    else:
        update_manifest(version)
        update_changelog_file(version, entry)
        with open('release_notes.txt', 'w', encoding='utf-8') as f:
            f.write(entry)
