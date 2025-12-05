#!/usr/bin/env python3
"""
Test script to verify M3U and XMLTV channel ID matching.
This script validates that the channel IDs in the XMLTV file match the tvg-id format
expected by M3U playlists (particularly for the UHF app on Apple devices).
"""

import re
import sys
import xml.etree.ElementTree as ET


def extract_m3u_info(m3u_content):
    """Extract channel information from M3U playlist."""
    channels = []
    lines = m3u_content.strip().split('\n')

    for i, line in enumerate(lines):
        if line.startswith('#EXTINF:'):
            # Parse the EXTINF line to extract tvg-id and other info
            extinf = line[8:]  # Remove #EXTINF:

            # Extract tvg-id
            tvg_id_match = re.search(r'tvg-id="([^"]*)"', extinf)
            tvg_id = tvg_id_match.group(1) if tvg_id_match else None

            # Extract tvg-name
            tvg_name_match = re.search(r'tvg-name="([^"]*)"', extinf)
            tvg_name = tvg_name_match.group(1) if tvg_name_match else None

            # Get channel name from next line
            if i + 1 < len(lines):
                channel_name = lines[i + 1].strip()
                channels.append({
                    'tvg_id': tvg_id,
                    'tvg_name': tvg_name,
                    'channel_name': channel_name
                })

    return channels

def extract_xmltv_channels(xmltv_file_path: str) -> dict:
    """Extract channel information from XMLTV file."""
    tree = ET.parse(xmltv_file_path)
    root = tree.getroot()

    channels = {}
    for channel in root.findall('channel'):
        channel_id = channel.get('id')
        display_name = None
        for element in channel:
            if element.tag == 'display-name':
                display_name = element.text
                break
        channels[channel_id] = display_name

    return channels

def validate_m3u_xmltv_matching(m3u_file_path: str, xmltv_file_path: str) -> bool:
    """Validate that M3U tvg-id values match XMLTV channel IDs."""
    print("=" * 70)
    print("M3U and XMLTV Channel ID Matching Validation")
    print("=" * 70)

    # Read M3U file
    try:
        with open(m3u_file_path, encoding='utf-8') as f:
            m3u_content = f.read()
    except FileNotFoundError:
        print(f"ERROR: M3U file not found: {m3u_file_path}")
        return False

    # Extract M3U channels
    m3u_channels = extract_m3u_info(m3u_content)
    print(f"\nFound {len(m3u_channels)} channels in M3U playlist")

    # Extract XMLTV channels
    try:
        xmltv_channels = extract_xmltv_channels(xmltv_file_path)
    except FileNotFoundError:
        print(f"ERROR: XMLTV file not found: {xmltv_file_path}")
        return False

    print(f"Found {len(xmltv_channels)} channels in XMLTV file")

    # Check for matches
    print("\n" + "-" * 70)
    print("Channel Matching Results:")
    print("-" * 70)

    matched = 0
    unmatched = []

    for m3u_channel in m3u_channels:
        tvg_id = m3u_channel.get('tvg_id')
        if tvg_id in xmltv_channels:
            matched += 1
            xmltv_name = xmltv_channels[tvg_id]
            m3u_name = m3u_channel.get('channel_name', 'N/A')
            print(f"✓ MATCH: tvg-id '{tvg_id}'")
            print(f"  M3U Channel: {m3u_name}")
            print(f"  XMLTV Name:  {xmltv_name}")
        else:
            unmatched.append(m3u_channel)
            print(f"✗ NO MATCH: tvg-id '{tvg_id}' not found in XMLTV")
            print(f"  M3U Channel: {m3u_channel.get('channel_name', 'N/A')}")

    print("\n" + "-" * 70)
    print("Summary:")
    print("-" * 70)
    print(f"Total M3U channels: {len(m3u_channels)}")
    print(f"Matched channels: {matched}")
    print(f"Unmatched channels: {len(unmatched)}")
    print(f"Match rate: {(matched/len(m3u_channels)*100):.1f}%" if m3u_channels else "N/A")

    if unmatched:
        print("\nUnmatched M3U channels:")
        for ch in unmatched:
            print(f"  - {ch.get('channel_name')} (tvg-id: {ch.get('tvg_id')})")

    print("\nAvailable XMLTV channel IDs:")
    for channel_id in sorted(xmltv_channels.keys())[:10]:  # Show first 10
        print(f"  - {channel_id} ({xmltv_channels[channel_id]})")
    if len(xmltv_channels) > 10:
        print(f"  ... and {len(xmltv_channels) - 10} more")

    print("=" * 70)

    success = len(unmatched) == 0
    if success:
        print("✓ SUCCESS: All M3U channels match XMLTV!")
    else:
        print("✗ FAILURE: Some M3U channels don't match XMLTV")

    return success

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_m3u_xmltv_matching.py <m3u_file> <xmltv_file>")
        print("\nExample:")
        print("  python test_m3u_xmltv_matching.py playlist.m3u epg.xml")
        sys.exit(1)

    input_m3u_file = sys.argv[1]
    input_xmltv_file = sys.argv[2]

    is_success = validate_m3u_xmltv_matching(input_m3u_file, input_xmltv_file)
    sys.exit(0 if is_success else 1)
