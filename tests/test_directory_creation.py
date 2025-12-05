#!/usr/bin/env python3
"""
Test script to verify directory creation for output files.
"""

import os
import tempfile
import unittest
import xml.etree.ElementTree as ET


class TestDirectoryCreation(unittest.TestCase):
    """Test that output directories are created if they don't exist."""

    def test_creates_nested_directories(self):
        """Test that nested directories are created for output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a nested path that doesn't exist yet
            output_file = os.path.join(tmpdir, "subdir1", "subdir2", "output.xml")

            # Verify the directory doesn't exist yet
            output_dir = os.path.dirname(output_file)
            self.assertFalse(os.path.exists(output_dir), "Directory should not exist before writing")

            # Create a minimal XMLTV structure
            xmltv_root = ET.Element("tv")
            xmltv_root.set("source-info-name", "TestSource")

            # Write the XML file (this should create directories)
            try:
                tree = ET.ElementTree(xmltv_root)
                ET.indent(tree, space="\t", level=0)

                # Create parent directories if they don't exist
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)

                tree.write(output_file, encoding="UTF-8", xml_declaration=True)

                # Verify the file was created
                self.assertTrue(os.path.exists(output_file), "Output file should exist after writing")
                self.assertTrue(os.path.exists(output_dir), "Output directory should exist after writing")

                # Verify the file is valid XML
                parsed_tree = ET.parse(output_file)
                self.assertIsNotNone(parsed_tree.getroot())

                print(f"✓ Successfully created nested directories: {output_dir}")
                print(f"✓ Successfully wrote XML file to: {output_file}")

            except OSError as e:
                self.fail(f"Failed to create directories or write file: {e}")

    def test_works_with_absolute_path(self):
        """Test with absolute paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "app", "output", "epg.xml")
            output_dir = os.path.dirname(output_file)

            # Create directories
            os.makedirs(output_dir, exist_ok=True)

            # Write file
            xmltv_root = ET.Element("tv")
            tree = ET.ElementTree(xmltv_root)
            tree.write(output_file, encoding="UTF-8", xml_declaration=True)

            # Verify
            self.assertTrue(os.path.exists(output_file))
            print(f"✓ Absolute path test passed: {output_file}")

    def test_handles_single_level_path(self):
        """Test with single-level filename (no subdirectories)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.xml")
            output_dir = os.path.dirname(output_file)

            # This should be the tmpdir and should already exist
            self.assertTrue(os.path.exists(output_dir))

            # Write file
            xmltv_root = ET.Element("tv")
            tree = ET.ElementTree(xmltv_root)
            tree.write(output_file, encoding="UTF-8", xml_declaration=True)

            # Verify
            self.assertTrue(os.path.exists(output_file))
            print(f"✓ Single-level path test passed: {output_file}")


if __name__ == "__main__":
    print("Testing directory creation for output files...\n")
    unittest.main(verbosity=2)
