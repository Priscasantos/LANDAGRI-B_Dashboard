#!/usr/bin/env python3
"""Test CONAB JSON loading"""

import json
from pathlib import Path

# Load CONAB initiative data
initiative_file = Path("data/json/conab_detailed_initiative.jsonc")
if initiative_file.exists():
    try:
        with open(initiative_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Remove JSONC comments
            lines = content.split('\n')
            clean_lines = [line for line in lines if not line.strip().startswith('//')]
            clean_content = '\n'.join(clean_lines)
            data = json.loads(clean_content)
            
        print("✅ CONAB Initiative data loaded successfully!")
        print(f"📊 Top-level keys: {list(data.keys())}")
        
        if "CONAB Crop Monitoring Initiative" in data:
            initiative = data["CONAB Crop Monitoring Initiative"]
            print(f"🏢 Provider: {initiative.get('provider', 'N/A')}")
            print(f"📍 Coverage: {initiative.get('coverage', 'N/A')}")
            print(f"🎯 Accuracy: {initiative.get('overall_accuracy', 'N/A')}%")
            
            if "detailed_crop_coverage" in initiative:
                crops = list(initiative["detailed_crop_coverage"].keys())
                print(f"🌾 Crops available: {crops}")
                
                # Show sample crop data
                if crops:
                    sample_crop = crops[0]
                    crop_data = initiative["detailed_crop_coverage"][sample_crop]
                    print(f"📋 Sample crop '{sample_crop}':")
                    print(f"   States: {crop_data.get('regions', [])}")
    except Exception as e:
        print(f"❌ Error loading initiative data: {e}")

# Load CONAB calendar data
calendar_file = Path("data/json/conab_crop_calendar.jsonc")
if calendar_file.exists():
    try:
        with open(calendar_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Remove JSONC comments
            lines = content.split('\n')
            clean_lines = [line for line in lines if not line.strip().startswith('//')]
            clean_content = '\n'.join(clean_lines)
            data = json.loads(clean_content)
            
        print("\n✅ CONAB Calendar data loaded successfully!")
        print(f"📊 Top-level keys: {list(data.keys())}")
        
        if "states" in data:
            states = data["states"]
            print(f"🇧🇷 States available: {len(states)} states")
            print(f"📍 Sample states: {list(states.keys())[:5]}")
            
            # Show sample state data
            sample_state = list(states.keys())[0]
            state_data = states[sample_state]
            print(f"📋 Sample state '{sample_state}':")
            print(f"   Name: {state_data.get('name', 'N/A')}")
            print(f"   Region: {state_data.get('region', 'N/A')}")
    except Exception as e:
        print(f"❌ Error loading calendar data: {e}")

print("\n🔄 JSON loading test completed!")
