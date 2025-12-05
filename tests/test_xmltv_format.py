#!/usr/bin/env python3
"""
Test script to verify XMLTV format and channel ID matching.
This validates that channel IDs are in the correct format for M3U tvg-id matching.
"""

import xml.etree.ElementTree as ET
import sys

def validate_xmltv_format(xmltv_file: str) -> bool:
    """Test that XMLTV file has correct channel ID format."""
    try:
        tree = ET.parse(xmltv_file)
        root = tree.getroot()
        
        print("✓ XMLTV file is valid XML")
        
        # Check channels
        channels = root.findall('channel')
        print(f"\n✓ Found {len(channels)} channels")
        
        if len(channels) == 0:
            print("✗ ERROR: No channels found in XMLTV file")
            return False
        
        print("\nChannel IDs (for use in M3U tvg-id):")
        print("-" * 60)
        
        channel_ids = {}
        all_valid = True
        
        for channel in channels:
            channel_id = channel.get('id')
            display_names = channel.findall('display-name')
            display_name = display_names[0].text if display_names else "Unknown"
            
            channel_ids[channel_id] = display_name
            
            # Validate channel ID format: should be "hdhomerun.{number}"
            if channel_id and not channel_id.startswith('hdhomerun.'):
                print(f"✗ INVALID: {channel_id} (expected format: hdhomerun.X)")
                all_valid = False
            else:
                print(f"✓ {channel_id:30} → {display_name}")
        
        # Check programmes reference valid channels
        programmes = root.findall('programme')
        print(f"\n✓ Found {len(programmes)} programmes")
        
        if len(programmes) > 0:
            print("\nVerifying programme channel references...")
            invalid_refs = set()
            valid_count = 0
            
            for programme in programmes:
                prog_channel_id = programme.get('channel')
                if prog_channel_id not in channel_ids:
                    invalid_refs.add(prog_channel_id)
                else:
                    valid_count += 1
            
            if invalid_refs:
                print(f"✗ ERROR: Found {len(invalid_refs)} programmes with invalid channel references:")
                for ref in list(invalid_refs)[:5]:  # Show first 5
                    print(f"  - {ref}")
                all_valid = False
            else:
                print(f"✓ All {valid_count} programmes reference valid channels")
        
        print("\n" + "=" * 60)
        print("M3U Example (for use with UHF or other IPTV apps):")
        print("=" * 60)
        print("#EXTM3U\n")
        for i, (channel_id, display_name) in enumerate(list(channel_ids.items())[:5]):
            tuner_num = i
            print(f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{display_name}" group-title="Live TV",{display_name}')
            print(f"http://your-hdhomerun-ip:5004/tuner{tuner_num}\n")
        
        if len(channel_ids) > 5:
            print(f"# ... and {len(channel_ids) - 5} more channels\n")
        
        print("=" * 60)
        if all_valid:
            print("✓ SUCCESS: XMLTV format is valid and compatible with M3U playlists")
            return True
        else:
            print("✗ FAILURE: XMLTV format has issues - see above")
            return False
            
    except ET.ParseError as e:
        print(f"✗ ERROR: Failed to parse XMLTV file: {e}")
        return False
    except (KeyError, AttributeError) as e:
        print(f"✗ ERROR: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_xmltv_format.py <xmltv_file>")
        print("\nExample: python test_xmltv_format.py epg.xml")
        sys.exit(1)
    
    input_xmltv_file = sys.argv[1]
    success = validate_xmltv_format(input_xmltv_file)
    sys.exit(0 if success else 1)
