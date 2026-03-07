#!/usr/bin/env python3
"""
Assembles changelog fragments into CHANGELOG.md.
No external dependencies.
"""

import os
import re
import glob
import sys
from datetime import date

FRAGMENT_DIR = '.changelog/fragments'
CHANGELOG_FILE = 'CHANGELOG.md'
MARKER = '<!-- towncrier release notes start -->'

SECTION_ORDER = ['added', 'changed', 'fixed', 'removed', 'config']
SECTION_NAMES = {
    'added':   'Added',
    'changed': 'Changed',
    'fixed':   'Fixed',
    'removed': 'Removed',
    'config':  'Config Changes',
}

def collect_fragments():
    sections = {t: [] for t in SECTION_ORDER}
    pattern = os.path.join(FRAGMENT_DIR, '*.*.md')
    files = sorted(glob.glob(pattern))

    if not files:
        print("ERROR: No changelog fragments found in .changelog/fragments/")
        print("Did you forget to fill in the Changelog section in your feature PR descriptions?")
        sys.exit(1)

    for filepath in files:
        filename = os.path.basename(filepath)
        parts = filename.rsplit('.', 2)
        if len(parts) != 3:
            print(f"WARNING: Skipping malformed fragment filename: {filename}")
            continue

        _, ftype, _ = parts
        if ftype not in sections:
            print(f"WARNING: Unknown fragment type '{ftype}' in {filename}, skipping")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            if not line.startswith('- '):
                line = f'- {line}'
            sections[ftype].append(line)

        print(f"  Read fragment: {filename}")

    return sections

def build_entry(version, sections):
    today = date.today().strftime('%Y-%m-%d')
    lines = [f'## [{version}] - {today}', '']

    for ftype in SECTION_ORDER:
        bullets = sections[ftype]
        if not bullets:
            continue
        lines.append(f'### {SECTION_NAMES[ftype]}')
        lines.extend(bullets)
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'

def update_changelog(version, entry):
    if not os.path.exists(CHANGELOG_FILE):
        print(f"ERROR: {CHANGELOG_FILE} not found")
        sys.exit(1)

    with open(CHANGELOG_FILE, 'r', encoding='utf-8', newline='') as f:
        content = f.read()

    content = content.replace('\r\n', '\n').replace('\r', '\n')

    if MARKER not in content:
        print(f"ERROR: Marker not found in {CHANGELOG_FILE}")
        print(f"CHANGELOG.md must contain exactly: {MARKER}")
        sys.exit(1)

    if f'## [{version}]' in content:
        print(f"ERROR: Version {version} already exists in CHANGELOG.md")
        print("Bump the version number.")
        sys.exit(1)

    new_content = content.replace(MARKER, MARKER + '\n\n' + entry)

    with open(CHANGELOG_FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)

    print(f"Updated {CHANGELOG_FILE}")

def delete_fragments():
    pattern = os.path.join(FRAGMENT_DIR, '*.*.md')
    files = glob.glob(pattern)
    for f in files:
        os.remove(f)
        print(f"  Deleted: {f}")

def extract_entry_for_version(version):
    with open(CHANGELOG_FILE, 'r', encoding='utf-8', newline='') as f:
        content = f.read()

    content = content.replace('\r\n', '\n').replace('\r', '\n')

    match = re.search(
        rf'(## \[{re.escape(version)}\].*?)(?=\n## \[|\Z)',
        content, re.DOTALL
    )

    if match:
        return match.group(1).strip()
    return f'See CHANGELOG.md for v{version} release notes.'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 build-changelog.py <version>")
        print("Example: python3 build-changelog.py 1.2.0")
        sys.exit(1)

    version = sys.argv[1].lstrip('v')
    print(f"Building changelog for v{version}...")

    sections = collect_fragments()
    entry = build_entry(version, sections)

    print(f"\nGenerated entry:\n{entry}")

    update_changelog(version, entry)
    delete_fragments()

    with open('/tmp/version.txt', 'w') as f:
        f.write(version)

    full_entry = extract_entry_for_version(version)
    with open('/tmp/changelog_body.txt', 'w', encoding='utf-8') as f:
        f.write(full_entry)

    print("\nDone.")