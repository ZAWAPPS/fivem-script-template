import urllib.request
import json
import os
import sys

# Official FiveM Natives URL
URL = "https://runtime.fivem.net/doc/natives.json"
OUTPUT = ".github/scripts/natives_defs.lua"

def sync():
    print(f"🌐 Fetching latest FiveM natives from {URL}...")
    try:
        # Use a short timeout to prevent hanging the pipeline
        with urllib.request.urlopen(URL, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            # Use a set for performance and to handle duplicates across categories
            native_names = set()
            for category in data.values():
                for native in category.values():
                    name = native.get('name')
                    # Ignore hashes/internal names (e.g. _0x...)
                    if name and not name.startswith('_0x'):
                        # Convert to CamelCase if it's snake_case (optional, but 
                        # FiveM supports both, so we just add the name as provided)
                        native_names.add(name)
            
            os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
            with open(OUTPUT, "w", encoding='utf-8') as f:
                f.write("-- AUTOMATED GENERATED FILE - DO NOT EDIT\n")
                f.write("-- This file provides global definitions for Luacheck\n\n")
                # We define them as globals so Luacheck 'reads' them
                for name in sorted(native_names):
                    f.write(f"function {name}() end\n")
            
            print(f"✅ Successfully synced {len(native_names)} natives to {OUTPUT}")
    except Exception as e:
        print(f"⚠️ Warning: Failed to fetch natives ({e}). Creating fallback...")
        os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
        with open(OUTPUT, "w") as f:
            f.write("-- Fallback empty definitions\n")

if __name__ == "__main__":
    sync()
