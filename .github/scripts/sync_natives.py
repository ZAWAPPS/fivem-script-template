import urllib.request
import json
import os
import re

# Official FiveM Natives URL
URL = "https://runtime.fivem.net/doc/natives.json"
OUTPUT = ".natives.lua"

def to_pascal_case(snake_str):
    if not snake_str:
        return ""
    # Remove leading underscores (like _ADD_BLIP...)
    clean_name = snake_str.lstrip('_')
    # Split by underscores, capitalize each part, and join
    return "".join(word.capitalize() for word in clean_name.lower().split('_'))

def sync():
    print(f"[*] Fetching latest FiveM natives from {URL}...")
    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            
            native_names = set()
            for category in data.values():
                for native in category.values():
                    name = native.get('name')
                    if name:
                        # Convert to PascalCase (AddBlipForArea)
                        pascal = to_pascal_case(name)
                        if pascal:
                            native_names.add(pascal)
            
            with open(OUTPUT, "w", encoding='utf-8') as f:
                f.write("-- FIVE-M NATIVES DEFINITIONS\n")
                f.write("-- This file provides global definitions for Luacheck\n")
                f.write("-- Generated from official natives.json\n\n")
                # Add a few core FiveM globals that might not be in the JSON
                core_globals = [
                    "Citizen", "AddEventHandler", "RegisterNetEvent", "TriggerEvent",
                    "TriggerServerEvent", "TriggerClientEvent", "RegisterServerEvent",
                    "GetConvar", "GetConvarInt", "GetResourceMetadata", "GetCurrentResourceName",
                    "Wait", "SetTimeout", "exports", "LocalPlayer", "GlobalState", "Entity", "Player",
                    "vec3", "vec2", "vec4", "quat", "CreateThread", "SetTick", "CancelEvent"
                ]
                for g in core_globals:
                    native_names.add(g)

                for name in sorted(native_names):
                    f.write(f"function {name}() end\n")
            
            print(f"[+] Successfully synced {len(native_names)} natives to {OUTPUT}")
    except Exception as e:
        print(f"[!] Error syncing natives: {e}")

if __name__ == "__main__":
    sync()
