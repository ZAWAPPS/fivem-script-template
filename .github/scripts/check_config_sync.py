#!/usr/bin/env python3
import re
import sys
import os
import glob

def extract_config_keys_from_content(content):
    keys = set()
    # Regex to handle:
    # 1. Config.Key, Config.Sub.Key
    # 2. Config['Key'], Config["Key"]
    # 3. Table definitions: Key = value, ["Key"] = value (when inside a Config-like table)
    
    # Pattern 1: Direct access (Config.Key or Config['Key'])
    pattern_access = re.compile(r"Config(?:\.([a-zA-Z0-9_]+)|\[['\"]([a-zA-Z0-9_]+)['\"]\])")
    for m in pattern_access.finditer(content):
        key = m.group(1) or m.group(2)
        if key: keys.add(key)
        
    # Pattern 2: Table definitions (e.g. Key = true), IGNORING local variables
    # We use a negative lookbehind (?<!local\s) to ensure 'local Key =' is skipped
    pattern_def = re.compile(r"(?<!local\s)(?:^|[\s,{])([a-zA-Z0-9_]+)\s*=\s*")
    for m in pattern_def.finditer(content):
        keys.add(m.group(1))
        
    return keys

def get_keys_used_in_code():
    """Scans all Lua files for Config.Key usage."""
    used_keys = set()
    pattern = re.compile(r"Config(?:\.([a-zA-Z0-9_]+)|\[['\"]([a-zA-Z0-9_]+)['\"]\])")
    
    for root, _, files in os.walk('.'):
        if 'node_modules' in root or '.github' in root or 'dist' in root:
            continue
        for file in files:
            if file.endswith('.lua') and not file.endswith('.dist.lua') and file != 'config.lua':
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    content = re.sub(r'--.*', '', content) # Remove comments
                    for m in pattern.finditer(content):
                        key = m.group(1) or m.group(2)
                        if key: used_keys.add(key)
    return used_keys

def check_all_configs():
    print("[*] Scanning repository for configuration integrity...")
    # Only scan for config.dist.lua to avoid catching locale files or other templates
    dist_files = glob.glob("**/config.dist.lua", recursive=True)
    
    if not dist_files:
        print("[i] No config.dist.lua files found. Skipping check.")
        return True

    all_synced = True
    code_used_keys = get_keys_used_in_code()
    print(f"[*] Found {len(code_used_keys)} unique Config keys used in code.")

    for dist_path in dist_files:
        print(f"[*] Validating: {dist_path}")
        with open(dist_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            content = re.sub(r'--.*', '', content)
            dist_keys = extract_config_keys_from_content(content)
        
        # Check if code uses keys that are missing in DIST
        # We only check this if the dist file is likely the main config (shared/config.dist.lua)
        if "config.dist.lua" in dist_path:
            missing_in_dist = code_used_keys - dist_keys
            if missing_in_dist:
                print(f"  [!] MISSING KEYS in {dist_path} (Used in code but not defined):")
                for key in sorted(missing_in_dist):
                    print(f"    - Missing: Config.{key}")
                all_synced = False

        # If there's a local config.lua (only happens in local dev, not CI), 
        # we can still compare it if it exists.
        source_path = dist_path.replace(".dist.lua", ".lua")
        if os.path.exists(source_path):
            print(f"  [~] Comparing with local {source_path}...")
            with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                content = re.sub(r'--.*', '', content)
                source_keys = extract_config_keys_from_content(content)
            
            diff = source_keys ^ dist_keys
            if diff:
                print(f"  [!] Local {source_path} is out of sync with {dist_path}!")
                all_synced = False

        if all_synced:
            print(f"  [+] {dist_path} looks good.")

    return all_synced

if __name__ == "__main__":
    if not check_all_configs():
        print("\n[!] Error: Configuration integrity check failed.")
        sys.exit(1)
    print("\n[+] All configurations are valid and synchronized.")
    sys.exit(0)
