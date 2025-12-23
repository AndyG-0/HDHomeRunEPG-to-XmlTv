
import argparse
import datetime
import io
import json
import logging
import os
import ssl
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

import pytz  # noqa: F401, E402
from dotenv import load_dotenv  # noqa: F401, E402
from tzlocal import get_localzone  # noqa: F401, E402

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

__author__ = "Incubus Victim"
__credits__ = ["Incubus Victim"]
__license__ = "GPL"
__version__ = "2.0.0"
__maintainer__ = "Incubus Victim"

def setup_logging(debug_mode: str) -> logging.Logger:
    """Configure logging based on debug mode."""
    log_level = logging.INFO
    if debug_mode.lower() == "full":
        log_level = logging.DEBUG
    elif debug_mode.lower() == "off":
        log_level = logging.WARNING

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger_instance = logging.getLogger(__name__)
    return logger_instance

def discover_device_auth(host: str) -> str:
    """Discover HDHomeRun device auth."""
    try:
        logger.info("Fetching HDHomeRun Web API Device Auth")
        with urllib.request.urlopen(f"http://{host}/discover.json") as response:
            data = json.loads(response.read().decode())
            for key in data:
                if "DeviceAuth" in key:
                    device_auth = data["DeviceAuth"]
                    logger.info("Discovered device auth: %s", device_auth)
                    return device_auth
        logger.error("No devices found")
        sys.exit(1)
    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Error discovering device: %s", e)
        sys.exit(1)

def fetch_channels(host: str, device_auth: str) -> list:
    """Fetch EPG channels from HDHomeRun device."""
    channel_data = []
    logger.info("Fetching HDHomeRun Web API Lineup for auth %s", device_auth)
    url = f"http://{host}/lineup.json"
    with urllib.request.urlopen(url) as response:
        channel_data = json.loads(response.read().decode())

    return channel_data

def fetch_epg_data(device_auth: str, channels: list, days: int, hours: int) -> dict:
    """Fetch EPG data for a specific channel via POST to HDHomeRun API."""
    epg_data = {}
    epg_data["channels"] = []
    epg_data["programmes"] = []
    url = f"https://api.hdhomerun.com/api/guide.php?DeviceAuth={device_auth}"
    # Start with the now
    next_start_date = datetime.datetime.now(pytz.UTC)
    # End with the desired number of days
    end_time = next_start_date + datetime.timedelta(days=days)

    try:
        while next_start_date < end_time:
            url_start_date = int(next_start_date.timestamp())
            context = ssl._create_unverified_context()
            req = urllib.request.Request(f"{url}&Start={url_start_date}")
            logger.debug("Fetching EPG for all channels starting %s from %s", next_start_date, url)
            try:
                with urllib.request.urlopen(req, context=context) as response:
                    epg_segment = json.loads(response.read().decode())
                    logger.info("Processing from %s", next_start_date.strftime("%Y-%m-%d %H:%M:%S"))
                    for channel_epg_segment in epg_segment:
                        programmes = channel_epg_segment["Guide"]
                        for programme in programmes:
                            channel = next((ch for ch in channels if ch.get("GuideNumber") == channel_epg_segment["GuideNumber"]), None)
                            # Check if the epg program channel is within our tuned channel list
                            if channel is None:
                                logger.debug("Skipping program for untuned channel %s", channel_epg_segment['GuideNumber'])
                                continue
                            # Check if the epg program has already been retrieved due to overlapping requests
                            if any(epg["StartTime"] == programme["StartTime"] and epg["Title"] == programme["Title"] and epg["GuideNumber"] == channel_epg_segment["GuideNumber"] for epg in epg_data["programmes"]):
                                logger.debug("Skipping duplicate program %s starting at %s", programme["Title"], programme["StartTime"])
                                continue
                            epg_channel = next((ch for ch in epg_data["channels"] if ch.get("GuideNumber") == channel_epg_segment["GuideNumber"]), None)
                            if epg_channel is None:
                                channel["ImageURL"] = channel_epg_segment.get("ImageURL", "")
                                epg_data["channels"].append(channel)
                            programme["GuideNumber"] = channel_epg_segment["GuideNumber"]
                            logger.debug("Appending: %s from %s to %s", programme["Title"], programme["StartTime"], programme["EndTime"])
                            epg_data["programmes"].append(programme)
            except urllib.error.HTTPError as e:
                if e.code == 400:
                    logger.warning("HTTP 400 error at %s - API limit reached, stopping EPG fetch with available data", next_start_date.strftime("%Y-%m-%d %H:%M:%S"))
                    break
                else:
                    logger.error("HTTP Error %d at %s: %s", e.code, next_start_date.strftime("%Y-%m-%d %H:%M:%S"), e)
                    raise
            next_start_date += datetime.timedelta(hours=hours)
        return epg_data
    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Error fetching EPG for all channels for start time %s: %s", next_start_date, e)
        return epg_data

def add_doctype_declaration(xml_content: str) -> str:
    """Add DOCTYPE declaration to XMLTV content for DTD compliance.
    
    Args:
        xml_content: XML string with or without XML declaration
        
    Returns:
        XML string with DOCTYPE declaration inserted after XML declaration
    """
    xml_lines = xml_content.split('\n', 1)
    
    # Check if first line contains XML declaration
    if len(xml_lines) >= 1 and xml_lines[0].strip().startswith('<?xml'):
        # Insert DOCTYPE after XML declaration
        if len(xml_lines) == 2:
            return xml_lines[0] + '\n<!DOCTYPE tv SYSTEM "xmltv.dtd">\n' + xml_lines[1]
        else:
            # Only XML declaration, no content after it
            return xml_lines[0] + '\n<!DOCTYPE tv SYSTEM "xmltv.dtd">\n'
    else:
        # No XML declaration found, add both
        return '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE tv SYSTEM "xmltv.dtd">\n' + xml_content

def create_xmltv_channel(channel_data: dict, xmltv_root: ET.Element) -> None:
    """Create XMLTV channel element according to DTD."""
    # Create a stable channel ID based on guide number for M3U tvg-id matching
    guide_number = channel_data.get("GuideNumber", "")
    channel_id = f"hdhomerun.{guide_number}"

    channel = ET.SubElement(xmltv_root, "channel", id=channel_id)
    ET.SubElement(channel, "display-name").text = channel_data.get("GuideName", "Unknown")
    ET.SubElement(channel, "icon", src=channel_data["ImageURL"])
    logger.debug("Created channel: %s (ID: %s)", channel_data.get('GuideName', 'Unknown'), channel_id)

def create_xmltv_programme(programme_data: dict, channel_number: str, xmltv_root: ET.Element) -> None:
    """Create XMLTV programme element according to DTD."""
    try:
        # Create stable channel ID matching the format used in create_xmltv_channel
        channel_id = f"hdhomerun.{channel_number}"

        start_time = datetime.datetime.fromtimestamp(programme_data["StartTime"], tz=pytz.UTC).astimezone(LOCAL_TZ)
        duration = programme_data.get("EndTime", programme_data["StartTime"]) - programme_data["StartTime"]
        end_time = start_time + datetime.timedelta(seconds=duration)

        programme = ET.SubElement(
            xmltv_root,
            "programme",
            start=start_time.strftime("%Y%m%d%H%M%S %z"),
            stop=end_time.strftime("%Y%m%d%H%M%S %z"),
            channel=channel_id
        )

        # NOTE: All key XMLTV elements are added below in DTD order, not all are used due to HDHomeRun data limitations.
        # <title>
        ET.SubElement(programme, "title", lang="en").text = programme_data.get("Title")
        # <sub-title>
        if "EpisodeTitle" in programme_data:
            ET.SubElement(programme, "sub-title", lang="en").text = programme_data["EpisodeTitle"]
        # <desc>
        if "Synopsis" in programme_data:
            ET.SubElement(programme, "desc", lang="en").text = programme_data["Synopsis"]
        # <desc> - Could add another for a short description
        # <credits>
        # <date>
        if "Filter" in programme_data:
            for filter_item in programme_data["Filter"]:
                ET.SubElement(programme, "category", lang="en").text = filter_item
        # <keyword>
        # <language>
        # <orig-language>
        # <length units="minutes">60</keyword>
        # <icon>
        if "ImageURL" in programme_data:
            ET.SubElement(programme, "icon", src=programme_data["ImageURL"])
        # <url>
        # <country>
        # <episode-num system="xmltv_ns">1.0.0/0</episode-num>
        if "EpisodeNumber" in programme_data:
            try:
                episode_number = programme_data["EpisodeNumber"]
                series = 0
                episode = 0
                if "S" in episode_number and "E" in episode_number:
                    series = int(episode_number[episode_number.index("S") + 1:episode_number.index("E")]) - 1
                    episode = int(episode_number[episode_number.index("E") + 1:]) - 1
                ET.SubElement(programme, "episode-num", system="onscreen").text = episode_number
                ET.SubElement(programme, "episode-num", system="xmltv_ns").text = f"{series}.{episode}.0/0"
            except (ValueError, TypeError):
                logger.warning("Invalid Series/Episode data for %s", programme_data.get('Title'))
        # <video>
        # <audio>
        # <previously-shown>
        if "OriginalAirdate" in programme_data:
            air_date = datetime.datetime.fromtimestamp(programme_data["OriginalAirdate"], tz=pytz.UTC).astimezone(LOCAL_TZ)
            start_date = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            if air_date != start_date:
                ET.SubElement(programme, "previously-shown").set("start", air_date.strftime("%Y%m%d%H%M%S"))
            elif "First" in programme_data and not programme_data["First"]:
                ET.SubElement(programme, "previously-shown")
        # <new>
        if "First" in programme_data and programme_data["First"]:
            ET.SubElement(programme, "new")
        # <subtitles>
        logger.debug("Created programme: %s", programme_data.get('Title'))
    except (KeyError, ValueError, TypeError) as e:
        logger.error("Error creating programme for %s: %s", programme_data.get('Title', 'unknown'), e)

def generate_xmltv(host: str, days: int, hours: int, filename: str) -> None:
    """Generate XMLTV file from HDHomeRun EPG data."""
    # Initialize XMLTV root
    xmltv_root = ET.Element("tv")
    xmltv_root.set("source-info-name", "HDHomeRun")
    xmltv_root.set("generator-info-name", "HDHomeRunEPG_to_XmlTv")

    # Discover device authentication
    device_auth = discover_device_auth(host)

    # Fetch channel list
    channels = fetch_channels(host, device_auth)
    if not channels:
        logger.error("No channels retrieved. Exiting.")
        sys.exit(1)

    # Fetch EPG data for all channels
    logger.info("HDHomeRun RPG Extraction Started")
    epg_data = fetch_epg_data(device_auth, channels, days, hours)
    logger.info("HDHomeRun RPG Extraction Completed")

    # Create the xmltv list of channels and programmes
    logger.info("HDHomeRun XMLTV Transformation Started")
    for guide_channel in epg_data.get("channels", []):
        create_xmltv_channel(guide_channel, xmltv_root)
    for guide_channel in epg_data.get("channels", []):
        guide_number = guide_channel.get("GuideNumber", "")
        for guide_programme in epg_data.get("programmes", []):
            if guide_programme.get("GuideNumber") == guide_number:
                create_xmltv_programme(guide_programme, guide_number, xmltv_root)
    logger.info("HDHomeRun XMLTV Transformation Completed")

    # Write to XML file
    try:
        logger.info("Writing XMLTV to file %s Started", filename)
        # Create parent directories if they don't exist
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            logger.debug("Creating output directory: %s", output_dir)
            os.makedirs(output_dir, exist_ok=True)
        tree = ET.ElementTree(xmltv_root)
        ET.indent(tree, space="\t", level=0)
        
        # Write to a temporary buffer first to add DOCTYPE declaration
        buffer = io.BytesIO()
        tree.write(buffer, encoding="UTF-8", xml_declaration=True)
        xml_content = buffer.getvalue().decode("UTF-8")
        
        # Add DOCTYPE declaration for XMLTV DTD compliance
        xml_with_doctype = add_doctype_declaration(xml_content)
        
        # Write the final XML with DOCTYPE
        with open(filename, 'w', encoding='UTF-8') as f:
            f.write(xml_with_doctype)
        
        logger.info("Writing XMLTV to file %s Completed", filename)
    except OSError as e:
        logger.error("Error writing XML file: %s", e)
        sys.exit(1)

def main():
    """Main function to parse arguments and generate XMLTV file."""
    # Get defaults from environment variables
    env_host = os.getenv("HDHOMERUN_HOST", "hdhomerun.local")
    env_filename = os.getenv("EPG_OUTPUT_FILE", "output/epg.xml")
    env_days = int(os.getenv("EPG_DAYS", "7"))
    env_hours = int(os.getenv("EPG_HOURS", "3"))
    env_debug = os.getenv("DEBUG", "on")

    parser = argparse.ArgumentParser(
        add_help=False,
        description="Program to download the HDHomeRun device EPG and convert it to an XMLTV format suitable for Jellyfin."
    )
    parser.add_argument("--help", action="store_true", help="Show the command parameters available.")
    parser.add_argument("--host", default=env_host, help="The host name or IP address of the HDHomeRun server if different from \"hdhomerun.local\".")
    parser.add_argument("--filename", default=env_filename, help="The file path and name of the EPG to be generated. Defaults to output/epg.xml in the current directory.")
    parser.add_argument("--days", type=int, default=env_days, help="The number of days in the future from now to obtain an EPG for. Defaults to 7 but will be restricted to a max of about 14 by the HDHomeRun device.")
    parser.add_argument("--hours", type=int, default=env_hours, help="The number of hours of guide interation to obtain. Defaults to 3 hours.")
    parser.add_argument("--debug", default=env_debug, help="Switch debug log message on, options are \"on\", \"full\" or \"off\". Defaults to \"on\"")

    args = parser.parse_args()

    if args.help:
        parser.print_help()
        sys.exit(0)

    global logger
    logger = setup_logging(args.debug)

    generate_xmltv(args.host, args.days, args.hours, args.filename)

# Initialize local timezone with fallback to UTC
LOCAL_TZ = None
try:
    LOCAL_TZ = get_localzone()
except (OSError, AttributeError) as e:
    logger.warning("Could not detect local timezone: %s. Falling back to UTC.", e)
    LOCAL_TZ = pytz.UTC

if __name__ == "__main__":
    main()
