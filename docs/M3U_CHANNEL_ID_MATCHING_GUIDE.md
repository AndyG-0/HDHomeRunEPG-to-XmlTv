# HDHomeRun EPG to XMLTV - M3U Channel ID Matching Guide

## The Problem

If UHF app (or other IPTV apps) is not matching M3U playlist channels with XMLTV EPG data, it's likely because **the tvg-id values in your M3U don't match the channel IDs in your XMLTV file**.

This typically happens when:
1. The documentation examples show simple channel numbers (501, 502, etc.)
2. Your actual HDHomeRun device uses RF channel numbers with sub-channel notation (3.1, 3.2, 10.1, etc.)
3. The channel IDs don't match, so the IPTV app can't link the playlist to the EPG

## Solution: Find Your Actual Channel IDs

### Step 1: Generate Your XMLTV File

Run the HDHomeRunEPG_to_XmlTv script:

```bash
uv run python HDHomeRunEPG_To_XmlTv.py --host your-hdhomerun-ip
```

This creates an `epg.xml` file with the actual channel IDs from your device.

### Step 2: Extract Your Channel Numbers

Open the generated `epg.xml` file and look at the channel IDs. They will be in the format:

```xml
<channel id="hdhomerun.X.Y">
  <display-name>Channel Name</display-name>
  ...
</channel>
```

Where:
- `X` = RF Channel number (e.g., 3, 5, 10, 12, 15)
- `Y` = Sub-channel number (e.g., 1, 2, 3, 4, 5)

**Examples from a real HDHomeRun device:**
- `hdhomerun.3.1` → KTVK-HD (RF Channel 3, Sub-channel 1)
- `hdhomerun.3.2` → Comet (RF Channel 3, Sub-channel 2)
- `hdhomerun.5.1` → KPHO-HD (RF Channel 5, Sub-channel 1)
- `hdhomerun.10.1` → KSAZ-TV (RF Channel 10, Sub-channel 1)
- `hdhomerun.10.2` → KSAZ HD (RF Channel 10, Sub-channel 2)

### Step 3: Create Your M3U Playlist

Create an M3U file using the **exact channel IDs** from your XMLTV file:

```m3u
#EXTM3U

#EXTINF:-1 tvg-id="hdhomerun.3.1" tvg-name="KTVK-HD" group-title="Broadcast",KTVK-HD
http://192.168.1.100:5004/tuner0

#EXTINF:-1 tvg-id="hdhomerun.3.2" tvg-name="Comet" group-title="Broadcast",Comet
http://192.168.1.100:5004/tuner0

#EXTINF:-1 tvg-id="hdhomerun.5.1" tvg-name="KPHO-HD" group-title="Broadcast",KPHO-HD
http://192.168.1.100:5004/tuner0

#EXTINF:-1 tvg-id="hdhomerun.10.1" tvg-name="KSAZ-TV" group-title="Broadcast",KSAZ-TV
http://192.168.1.100:5004/tuner1
```

**Key Points:**
- The `tvg-id` MUST exactly match the channel ID from your XMLTV file (including the dot notation)
- Copy the channel IDs directly from the `epg.xml` file
- Don't use examples from documentation - use YOUR actual channel numbers

### Step 4: Test the Matching

Use the included test script to verify your M3U matches your XMLTV:

```bash
python3 test_m3u_xmltv_matching.py your_playlist.m3u epg.xml
```

You should see:
```
✓ MATCH: tvg-id 'hdhomerun.3.1'
✓ MATCH: tvg-id 'hdhomerun.3.2'
... (all channels should match)

✓ SUCCESS: All M3U channels match XMLTV!
```

If you see "NO MATCH" messages, the channel ID format doesn't match. Compare carefully:
- What's in your M3U's tvg-id
- What's in the XMLTV's channel id

## Why Are the Numbers Different?

HDHomeRun devices use **RF (radio frequency) channels** to identify broadcast channels:
- RF channels are the physical broadcast frequencies (3, 5, 10, 12, 15, etc. in the US)
- Sub-channels are digital subdivisions of the RF channel (1, 2, 3, 4, 5, etc.)

The documentation examples showing simple numbers (501, 502, etc.) were:
- Either from different devices/regions that use different numbering
- Or hypothetical examples that don't reflect your actual HDHomeRun device

**Your actual device's numbering format is always `RF.Subchannel` (e.g., 3.1, 3.2, 10.1)**

## Common Issues & Solutions

### Issue 1: Documentation Examples Don't Match
**Symptom:** Examples show `hdhomerun.501` but your XMLTV has `hdhomerun.3.1`

**Solution:** Always extract your actual channel numbers from your XMLTV file, don't copy examples.

### Issue 2: Partial Matches
**Symptom:** Some channels match but others don't

**Solution:** Check each tvg-id carefully against the XMLTV. They must match exactly, including dots and numbers.

### Issue 3: Channels Are Numbers Only
**Symptom:** Your XMLTV has `hdhomerun.501` but M3U uses `hdhomerun.501.1`

**Solution:** Your device is using a different numbering scheme. Use the exact format from your XMLTV file.

## Automated M3U Generation

If you're generating M3U files programmatically, here's how to extract channel IDs from XMLTV:

```python
import xml.etree.ElementTree as ET

tree = ET.parse('epg.xml')
root = tree.getroot()

for channel in root.findall('channel'):
    channel_id = channel.get('id')  # e.g., "hdhomerun.3.1"
    display_name = None
    for element in channel:
        if element.tag == 'display-name':
            display_name = element.text
            break
    
    # Use channel_id and display_name to create M3U entries
    print(f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{display_name}",{display_name}')
    print(f'http://your-server/video?channel={channel_id}')
```

## UHF App Configuration

Once your M3U channels match the XMLTV:

1. In UHF app → Settings → Playlists
2. Add your M3U file URL
3. Go to Settings → EPG
4. Select your playlist
5. Set EPG URL to your XMLTV file (e.g., `http://your-server:8000/epg.xml`)
6. The channels should now display EPG data

## Additional Resources

- See `example_uhf_corrected.m3u` for a working example using actual channel numbers
- Use the `test_m3u_xmltv_matching.py` script to validate your files
- Check the generated `epg.xml` file for authoritative channel IDs
