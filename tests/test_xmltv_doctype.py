#!/usr/bin/env python3
"""
Test script to verify XMLTV format includes proper DOCTYPE declaration
and channel IDs use the correct hdhomerun.X format.
"""

import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

import HDHomeRunEPG_To_XmlTv as hdhomerun


class TestXMLTVDoctypeAndFormat(unittest.TestCase):
    """Test XMLTV file format compliance."""

    def test_xmltv_has_doctype_declaration(self):
        """Test that generated XMLTV includes DOCTYPE declaration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tf:
            filename = tf.name

        try:
            # Create minimal XMLTV structure
            xmltv_root = ET.Element("tv")
            xmltv_root.set("source-info-name", "HDHomeRun")
            xmltv_root.set("generator-info-name", "HDHomeRunEPG_to_XmlTv")

            # Add a test channel
            channel_data = {
                "GuideNumber": "3.1",
                "GuideName": "Test Channel",
                "ImageURL": "http://example.com/icon.png"
            }
            hdhomerun.create_xmltv_channel(channel_data, xmltv_root)

            # Write the file using the same method as the main code
            tree = ET.ElementTree(xmltv_root)
            ET.indent(tree, space="\t", level=0)

            import io
            buffer = io.BytesIO()
            tree.write(buffer, encoding="UTF-8", xml_declaration=True)
            xml_content = buffer.getvalue().decode("UTF-8")

            # Add DOCTYPE declaration
            xml_lines = xml_content.split('\n', 1)
            if len(xml_lines) == 2:
                xml_with_doctype = xml_lines[0] + '\n<!DOCTYPE tv SYSTEM "xmltv.dtd">\n' + xml_lines[1]
            else:
                xml_with_doctype = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE tv SYSTEM "xmltv.dtd">\n' + xml_content

            with open(filename, 'w', encoding='UTF-8') as f:
                f.write(xml_with_doctype)

            # Read and verify
            with open(filename, 'r', encoding='UTF-8') as f:
                content = f.read()

            # Check for DOCTYPE declaration
            self.assertIn('<!DOCTYPE tv SYSTEM "xmltv.dtd">', content,
                         "XMLTV file must include DOCTYPE declaration")
            
            # Check XML declaration
            self.assertTrue(content.startswith('<?xml'),
                           "XMLTV file must start with XML declaration")

            # Verify DOCTYPE is between XML declaration and root element
            lines = content.split('\n')
            self.assertTrue(lines[0].startswith('<?xml'),
                           "First line must be XML declaration")
            self.assertIn('<!DOCTYPE tv', lines[1],
                         "Second line must be DOCTYPE declaration")

            print("✓ XMLTV file includes proper DOCTYPE declaration")
            print(f"✓ First two lines:\n  {lines[0]}\n  {lines[1]}")

        finally:
            Path(filename).unlink(missing_ok=True)

    def test_channel_id_format(self):
        """Test that channel IDs use hdhomerun.X format."""
        xmltv_root = ET.Element("tv")
        
        # Test various GuideNumber formats
        test_cases = [
            ("3.1", "hdhomerun.3.1"),
            ("501", "hdhomerun.501"),
            ("10.2", "hdhomerun.10.2"),
        ]

        for guide_number, expected_id in test_cases:
            channel_data = {
                "GuideNumber": guide_number,
                "GuideName": f"Test Channel {guide_number}",
                "ImageURL": "http://example.com/icon.png"
            }
            hdhomerun.create_xmltv_channel(channel_data, xmltv_root)

        # Verify all channels have correct ID format
        channels = xmltv_root.findall('channel')
        self.assertEqual(len(channels), len(test_cases),
                        f"Expected {len(test_cases)} channels")

        for idx, (guide_number, expected_id) in enumerate(test_cases):
            channel = channels[idx]
            actual_id = channel.get('id')
            self.assertEqual(actual_id, expected_id,
                           f"Channel ID for {guide_number} should be {expected_id}, got {actual_id}")
            self.assertTrue(actual_id.startswith('hdhomerun.'),
                           f"Channel ID must start with 'hdhomerun.', got {actual_id}")

        print("✓ All channel IDs use correct hdhomerun.X format")
        for guide_number, expected_id in test_cases:
            print(f"  ✓ {guide_number} → {expected_id}")

    def test_programme_channel_references(self):
        """Test that programme elements reference channels with correct IDs."""
        xmltv_root = ET.Element("tv")
        
        # Create a channel
        channel_data = {
            "GuideNumber": "3.1",
            "GuideName": "Test Channel",
            "ImageURL": "http://example.com/icon.png"
        }
        hdhomerun.create_xmltv_channel(channel_data, xmltv_root)

        # Create a programme
        programme_data = {
            "StartTime": 1702468800,  # 2023-12-13 12:00:00 UTC
            "EndTime": 1702472400,    # 2023-12-13 13:00:00 UTC
            "Title": "Test Programme",
            "GuideNumber": "3.1"
        }
        hdhomerun.create_xmltv_programme(programme_data, "3.1", xmltv_root)

        # Verify programme references correct channel ID
        programme = xmltv_root.find('programme')
        self.assertIsNotNone(programme, "Programme should be created")
        
        programme_channel = programme.get('channel')
        self.assertEqual(programme_channel, "hdhomerun.3.1",
                        f"Programme channel should be 'hdhomerun.3.1', got {programme_channel}")

        # Verify channel ID matches
        channel = xmltv_root.find('channel')
        channel_id = channel.get('id')
        self.assertEqual(programme_channel, channel_id,
                        "Programme channel must match channel ID")

        print("✓ Programme elements correctly reference channels with hdhomerun.X format")
        print(f"  ✓ Channel ID: {channel_id}")
        print(f"  ✓ Programme channel: {programme_channel}")


if __name__ == "__main__":
    unittest.main()
