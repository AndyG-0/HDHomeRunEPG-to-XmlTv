# HDHomeRun EPG to XMLTV - UHF App Integration Guide

## Issue Resolved

The UHF app on Apple TV/iOS was unable to automatically match M3U playlist channels with XMLTV EPG data. This was because the XMLTV channel IDs were using a generic numeric format that couldn't be reliably referenced in M3U playlists.

**This has been fixed!** Channel IDs are now in the format `hdhomerun.{GuideNumber}` which provides a stable, predictable ID that M3U playlists can reference.

## What Changed

### Before
```xml
<!-- Old format - just a number -->
<channel id="1">
  <display-name>Channel 1</display-name>
</channel>
<programme channel="1" ... />
```

### After
```xml
<!-- New format - prefixed with hdhomerun. for clarity and stability -->
<channel id="hdhomerun.1">
  <display-name>Channel 1</display-name>
</channel>
<programme channel="hdhomerun.1" ... />
```

## Setup Instructions

### Step 1: Generate XMLTV File

```bash
# Basic usage with default settings
python HDHomeRunEPG_To_XmlTv.py --host your-hdhomerun-ip

# Example with custom settings
python HDHomeRunEPG_To_XmlTv.py --host 192.168.1.100 --filename /var/www/html/epg.xml --days 7
```

### Step 2: Host the XMLTV File

The generated XMLTV file needs to be accessible via HTTP.

**Option A: Use the included HTTP server**
```bash
python http_server.py /path/to/epg.xml
# Then access at: http://localhost:8000/epg.xml
```

**Option B: Use your own web server**
- Copy the `epg.xml` file to your web server's document root
- Example: `/var/www/html/epg.xml`
- Access at: `http://your-server-ip/epg.xml`

**Option C: Use Docker**
```bash
docker compose up -d
# The XMLTV file will be served at: http://localhost:8000/epg.xml
```

### Step 3: Create M3U Playlist

**IMPORTANT:** Your M3U `tvg-id` values **MUST EXACTLY MATCH** the channel IDs in your generated XMLTV file.

#### Option A: Auto-Generate M3U (Recommended)

Use the included tool to automatically generate a correct M3U file:

```bash
python generate_m3u_from_xmltv.py epg.xml playlist.m3u --server-url http://192.168.1.100:8000
```

This guarantees all channels will match correctly.

#### Option B: Manual M3U Creation

1. Open your generated `epg.xml` file
2. Look at the channel IDs (format: `hdhomerun.X.Y`, e.g., `hdhomerun.3.1`)
3. Create M3U entries using those exact channel IDs:

```m3u
#EXTM3U

#EXTINF:-1 tvg-id="hdhomerun.3.1" tvg-name="KTVK-HD" group-title="Broadcast",KTVK-HD
http://192.168.1.100:8000/video?channel=3.1

#EXTINF:-1 tvg-id="hdhomerun.5.1" tvg-name="KPHO-HD" group-title="Broadcast",KPHO-HD
http://192.168.1.100:8000/video?channel=5.1

#EXTINF:-1 tvg-id="hdhomerun.10.1" tvg-name="KSAZ-TV" group-title="Broadcast",KSAZ-TV
http://192.168.1.100:8000/video?channel=10.1
```

**Key points:**
- `tvg-id` MUST exactly match the channel ID from your XMLTV (including dots)
- Copy channel IDs from your `epg.xml`, not from documentation examples
- `tvg-name` is the channel name (displayed in guides)
- `group-title` groups channels (optional but recommended)
- URLs should use your actual server IP and channel numbers

#### Verify Channel Matching

After creating your M3U, test it to ensure all channels match:

```bash
python test_m3u_xmltv_matching.py playlist.m3u epg.xml
```

You should see: `✓ SUCCESS: All M3U channels match XMLTV!`

### Step 4: Configure UHF App (Apple TV)

1. **Add Playlist:**
   - Open UHF app → Settings → Playlists
   - Add new playlist URL (HTTP or local path to your .m3u file)

2. **Set EPG Source:**
   - Settings → EPG
   - Select your playlist
   - Set EPG URL to your XMLTV file
   - Example: `http://your-server-ip:8000/epg.xml`

3. **Verify Connection:**
   - Go back to Live TV view
   - Channels should now display EPG information
   - Press select/OK on a channel to see program details

### Step 5: Configure Other Apps (Jellyfin, Plex, etc.)

**Jellyfin:**
1. Settings → Live TV
2. Add tuner device (HDHomeRun)
3. Settings → Guide Data Providers
4. Add custom XMLTV guide source
5. Import/add M3U playlist with matching tvg-id values

**Plex:**
1. Settings → Live TV & DVR
2. Add tuner device (HDHomeRun)
3. Settings → EPG
4. Add custom EPG source
5. Set M3U guide with matching tvg-id values

## Verification

Use the provided test script to verify your XMLTV file:

```bash
python test_xmltv_format.py epg.xml
```

This will:
- ✓ Validate the XML format
- ✓ Display all channel IDs in the correct format
- ✓ Verify programme references are valid
- ✓ Generate an M3U example for your channels

## Troubleshooting

### "No EPG showing"
- Verify the tvg-id values in your M3U exactly match the XMLTV channel IDs
- Check that the XMLTV file is accessible via HTTP
- Restart the UHF app
- Force refresh EPG in settings

### "Wrong channels matching"
- The tvg-id format must be exactly `hdhomerun.{GuideNumber}`
- Check your M3U file for typos
- Run the test script to see actual channel IDs

### "EPG not updating"
- Set up a cron job or scheduler to regenerate the XMLTV file regularly
- Use the included Docker setup for automatic updates
- Example cron: `0 1 * * * python /path/to/HDHomeRunEPG_To_XmlTv.py --host 192.168.1.100`

## Example Setup

Here's a complete example setup:

```bash
# 1. Generate XMLTV
python HDHomeRunEPG_To_XmlTv.py --host 192.168.1.100 --filename /tmp/epg.xml

# 2. Start HTTP server
python http_server.py /tmp/epg.xml &

# 3. Create M3U with matching tvg-id values
cat > channels.m3u << 'EOF'
#EXTM3U
#EXTINF:-1 tvg-id="hdhomerun.1" tvg-name="Channel 1",Channel 1
http://192.168.1.100:5004/tuner0
EOF

# 4. In UHF app:
#    - Add channels.m3u as playlist
#    - Set EPG to http://localhost:8000/epg.xml
```

## Advanced: Automatic Updates

Create a cron job for automatic daily updates:

```bash
# Edit crontab
crontab -e

# Add this line (runs at 1 AM daily)
0 1 * * * cd /path/to/HDHomeRunEPG-to-XmlTv && python HDHomeRunEPG_To_XmlTv.py --host 192.168.1.100 --filename /var/www/html/epg.xml
```

Or use the Docker setup which includes automatic scheduling.

## Questions or Issues?

For issues with the HDHomeRun EPG converter:
- Check the XMLTV_FIX_NOTES.md for technical details
- Run the test script to verify format
- Check application logs for error messages
- Visit the project repository for known issues

## Format Reference

### XMLTV Channel ID Format
- **Format:** `hdhomerun.{GuideNumber}`
- **Examples:** `hdhomerun.1`, `hdhomerun.501`, `hdhomerun.10`

### M3U tvg-id Matching
```m3u
#EXTINF:-1 tvg-id="hdhomerun.1",Channel Name
```

This `tvg-id="hdhomerun.1"` must match the XMLTV `<channel id="hdhomerun.1">` exactly for EPG linking to work.
