#!/usr/bin/env python3
"""
UHF EPG Diagnostic Tool

This script analyzes the XMLTV and M3U files to help diagnose why UHF might
be showing the same program data for all channels except one.

**NOTE:** This is a diagnostic/troubleshooting tool only. The main generation
scripts (HDHomeRunEPG_To_XmlTv.py and generate_m3u_from_xmltv.py) automatically
create correctly formatted files. Use this script only if you're experiencing
issues with your IPTV app and need to troubleshoot the file formats.

Usage:
    python uhf_epg_diagnostic.py lineup_fixed.m3u output/epg.xml
"""

import argparse
import xml.etree.ElementTree as ET
from datetime import datetime


def parse_m3u(m3u_file):
    """Parse M3U file and return channel list."""
    channels = []
    try:
        with open(m3u_file, encoding='utf-8') as f:
            lines = f.readlines()

        current_channel = None
        for line in lines:
            line = line.strip()
            if line.startswith('#EXTINF:-1') and 'tvg-id=' in line:
                # Extract tvg-id
                tvg_id_start = line.find('tvg-id="') + 8
                tvg_id_end = line.find('"', tvg_id_start)
                tvg_id = line[tvg_id_start:tvg_id_end]

                # Extract tvg-name
                tvg_name = ""
                if 'tvg-name=' in line:
                    name_start = line.find('tvg-name="') + 10
                    name_end = line.find('"', name_start)
                    tvg_name = line[name_start:name_end]

                current_channel = {'tvg_id': tvg_id, 'tvg_name': tvg_name}

            elif line and not line.startswith('#') and current_channel is not None:
                current_channel['url'] = line
                channels.append(current_channel)
                current_channel = None

    except (OSError, FileNotFoundError) as e:
        print(f"Error parsing M3U: {e}")
        return []

    return channels


def analyze_xmltv(xmltv_file):
    """Analyze XMLTV file and show sample program data."""
    try:
        tree = ET.parse(xmltv_file)
        root = tree.getroot()

        # Get all channels
        channels = {}
        for channel in root.findall('channel'):
            channel_id = channel.get('id')
            display_name = channel.find('display-name')
            if display_name is not None:
                channels[channel_id] = display_name.text

        print(f"Found {len(channels)} channels in XMLTV")

        # Analyze programs for sample channels
        program_counts = {}
        sample_programs = {}

        for programme in root.findall('programme'):
            channel_id = programme.get('channel')
            if channel_id not in program_counts:
                program_counts[channel_id] = 0
                sample_programs[channel_id] = []

            program_counts[channel_id] += 1

            # Store first few programs for analysis
            if len(sample_programs[channel_id]) < 3:
                title_elem = programme.find('title')
                start_time = programme.get('start')
                title = title_elem.text if title_elem is not None else "Unknown"

                sample_programs[channel_id].append({
                    'title': title,
                    'start': start_time
                })

        return channels, program_counts, sample_programs

    except (OSError, ET.ParseError, FileNotFoundError) as e:
        print(f"Error parsing XMLTV: {e}")
        return {}, {}, {}


def main():
    parser = argparse.ArgumentParser(description='Diagnose UHF EPG issues')
    parser.add_argument('m3u_file', help='Path to M3U playlist file')
    parser.add_argument('xmltv_file', help='Path to XMLTV EPG file')

    args = parser.parse_args()

    print("=" * 70)
    print("UHF EPG DIAGNOSTIC REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Parse M3U
    print("1. M3U PLAYLIST ANALYSIS")
    print("-" * 30)
    m3u_channels = parse_m3u(args.m3u_file)
    print(f"M3U File: {args.m3u_file}")
    print(f"Total channels in M3U: {len(m3u_channels)}")

    if m3u_channels:
        print("\nFirst 10 M3U channels:")
        for i, ch in enumerate(m3u_channels[:10]):
            print(f"  {i+1:2d}. tvg-id: {ch['tvg_id']} | name: {ch['tvg_name']}")
    print()

    # Parse XMLTV
    print("2. XMLTV EPG ANALYSIS")
    print("-" * 30)
    xmltv_channels, program_counts, sample_programs = analyze_xmltv(args.xmltv_file)
    print(f"XMLTV File: {args.xmltv_file}")
    print(f"Total channels with EPG: {len(xmltv_channels)}")

    # Show program counts
    if program_counts:
        print("\nProgram counts per channel:")
        sorted_counts = sorted(program_counts.items(), key=lambda x: x[1], reverse=True)
        for channel_id, count in sorted_counts[:15]:
            channel_name = xmltv_channels.get(channel_id, "Unknown")
            print(f"  {channel_id:<20} | {count:3d} programs | {channel_name}")
    print()

    # Channel matching analysis
    print("3. CHANNEL MATCHING ANALYSIS")
    print("-" * 30)
    matched = 0
    unmatched_m3u = []
    unmatched_xmltv = []

    m3u_ids = {ch['tvg_id'] for ch in m3u_channels}
    xmltv_ids = set(xmltv_channels.keys())

    for ch in m3u_channels:
        if ch['tvg_id'] in xmltv_channels:
            matched += 1
        else:
            unmatched_m3u.append(ch['tvg_id'])

    for xmltv_id in xmltv_ids:
        if xmltv_id not in m3u_ids:
            unmatched_xmltv.append(xmltv_id)

    print(f"Matched channels: {matched}/{len(m3u_channels)} ({100*matched/len(m3u_channels):.1f}%)")

    if unmatched_m3u:
        print(f"\nM3U channels without XMLTV data ({len(unmatched_m3u)}):")
        for ch_id in unmatched_m3u[:10]:
            print(f"  - {ch_id}")
        if len(unmatched_m3u) > 10:
            print(f"  ... and {len(unmatched_m3u)-10} more")

    if unmatched_xmltv:
        print(f"\nXMLTV channels not in M3U ({len(unmatched_xmltv)}):")
        for ch_id in unmatched_xmltv[:10]:
            print(f"  - {ch_id}")
        if len(unmatched_xmltv) > 10:
            print(f"  ... and {len(unmatched_xmltv)-10} more")
    print()

    # Sample program analysis
    print("4. SAMPLE PROGRAM DATA")
    print("-" * 30)
    print("Showing first 3 programs for first 5 channels:\n")

    sample_channel_ids = list(sample_programs.keys())[:5]
    for channel_id in sample_channel_ids:
        channel_name = xmltv_channels.get(channel_id, "Unknown")
        programs = sample_programs[channel_id]

        print(f"Channel: {channel_id} ({channel_name})")
        for i, prog in enumerate(programs):
            print(f"  {i+1}. {prog['start']} - {prog['title']}")
        print()

    # UHF-specific diagnostics
    print("5. UHF TROUBLESHOOTING SUGGESTIONS")
    print("-" * 30)

    if matched == len(m3u_channels):
        print("✓ All M3U channels have matching XMLTV data")
        print("\nIf UHF is still showing duplicate programs:")
        print("1. Clear UHF cache: Settings → Clear Cache")
        print("2. Force refresh EPG: Settings → EPG → Refresh EPG Data")
        print("3. Restart UHF app completely")
        print("4. Check UHF EPG update interval settings")
        print("5. Verify both URLs are accessible:")
        print("   - Test M3U URL in browser")
        print("   - Test XMLTV URL downloads the file")
        print("6. Check UHF logs for parsing errors")
        print("\nPossible UHF issues:")
        print("- UHF cached old EPG data")
        print("- UHF parsing error with XMLTV format")
        print("- UHF network timeout during EPG download")
        print("- UHF incorrectly associating all channels with one program set")
    else:
        print("⚠ Some M3U channels don't have XMLTV data")
        print("This could cause UHF to show duplicate or missing programs")

    print("6. VALIDATION COMMANDS")
    print("-" * 30)
    print("Run these to verify your setup:")
    print("1. Validate M3U format:")
    print("   curl -s 'http://192.168.50.33/lineup_fixed.m3u' | head -20")
    print("2. Validate XMLTV format:")
    print("   curl -s 'http://192.168.50.197:8888/epg.xml' | head -50")
    print("3. Test channel matching:")
    print("   python test_m3u_xmltv_matching.py lineup_fixed.m3u output/epg.xml")

    print("\n" + "=" * 70)
    print("END DIAGNOSTIC REPORT")
    print("=" * 70)


if __name__ == "__main__":
    main()
