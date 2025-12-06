#!/usr/bin/env python3
"""
Generate a correct M3U playlist from XMLTV file.

This script reads the generated XMLTV file and creates a properly formatted M3U
playlist with tvg-id values that match the XMLTV channel IDs. This ensures that
IPTV apps like UHF can correctly link the playlist channels to EPG data.

Usage:
    python generate_m3u_from_xmltv.py epg.xml output.m3u [--server-url http://your-server:8000]

Example:
    python generate_m3u_from_xmltv.py epg.xml playlist.m3u --server-url http://192.168.1.100:8000
"""

import argparse
import sys
import xml.etree.ElementTree as ET


def extract_channel_info(xmltv_file: str) -> list:
    """Extract channel information from XMLTV file."""
    channels = []

    try:
        tree = ET.parse(xmltv_file)
    except FileNotFoundError:
        print(f"ERROR: XMLTV file not found: {xmltv_file}")
        sys.exit(1)
    except ET.ParseError as e:
        print(f"ERROR: Invalid XMLTV file: {e}")
        sys.exit(1)

    root = tree.getroot()

    for channel in root.findall('channel'):
        channel_id = channel.get('id')
        display_name = None
        icon_url = None

        for element in channel:
            if element.tag == 'display-name':
                display_name = element.text
            elif element.tag == 'icon':
                icon_url = element.get('src')

        if channel_id and display_name:
            channels.append({
                'id': channel_id,
                'name': display_name,
                'icon': icon_url
            })

    return channels


def extract_channel_number(channel_id: str) -> str:
    """Extract the channel number from the channel ID for URL use."""
    # channel_id format: "hdhomerun.X.Y" or "hdhomerun.XXX"
    # We want to extract everything after "hdhomerun."
    if channel_id.startswith("hdhomerun."):
        return channel_id[10:]  # Remove "hdhomerun." prefix
    return channel_id


def generate_m3u(channels: list, server_url: str, output_file: str) -> None:
    """Generate M3U playlist file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write M3U header (matching HDHomeRun native format)
            f.write("#EXTM3U\n")

            # Write channels
            for channel in channels:
                channel_id = channel['id']
                channel_name = channel['name']
                channel_number = extract_channel_number(channel_id)

                # Build EXTINF line (matching HDHomeRun native format)
                print(f"DEBUG: channel_id={channel_id}, channel_number={channel_number}")
                extinf_line = f'#EXTINF:-1 tvg-id="{channel_number}" channel-id="{channel_number}" channel-number="{channel_number}" tvg-name="{channel_name}"'

                # Add icon if available
                if channel['icon']:
                    extinf_line += f' tvg-logo="{channel["icon"]}"'

                # Add group title for favorites (HDHomeRun uses this for favorited channels)
                extinf_line += ' group-title="Channels"'

                # Channel display name with number prefix (matching HDHomeRun format)
                extinf_line += f',{channel_number} {channel_name}\n'
                f.write(extinf_line)

                # Write URL on next line (HDHomeRun format - no blank line between EXTINF and URL)
                url = f"{server_url}/auto/v{channel_number}\n"
                f.write(url)

        print(f"✓ Successfully generated M3U playlist: {output_file}")
        print(f"  - Total channels: {len(channels)}")
        print(f"  - Server URL: {server_url}")
        print("\nNext steps:")
        print(f"1. Verify the playlist looks correct: less {output_file}")
        print(f"2. Test channel matching: python test_m3u_xmltv_matching.py {output_file} epg.xml")
        print("3. Upload to your server and add to UHF app settings")

    except OSError as e:
        print(f"ERROR: Could not write M3U file: {e}")
        sys.exit(1)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate M3U playlist from XMLTV file with correct tvg-id matching"
    )
    parser.add_argument(
        "xmltv_file",
        help="Path to the XMLTV file (e.g., epg.xml)"
    )
    parser.add_argument(
        "output_file",
        help="Path to the output M3U file (e.g., playlist.m3u)"
    )
    parser.add_argument(
        "--server-url",
        default="http://127.0.0.1:8000",
        help="Base URL for streaming (default: http://127.0.0.1:8000)"
    )

    args = parser.parse_args()

    # Extract channels from XMLTV
    print(f"Reading XMLTV file: {args.xmltv_file}")
    channels = extract_channel_info(args.xmltv_file)
    print(f"Found {len(channels)} channels")

    # Generate M3U
    print("\nGenerating M3U playlist...")
    generate_m3u(channels, args.server_url, args.output_file)


if __name__ == "__main__":
    main()
