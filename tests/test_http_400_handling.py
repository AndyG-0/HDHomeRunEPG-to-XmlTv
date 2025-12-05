#!/usr/bin/env python3
"""
Test script to verify HTTP 400 error handling in fetch_epg_data.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock
import urllib.error
import json
import datetime
import pytz

# Import the module we're testing
sys.path.insert(0, '/Users/andy/workspaces/forks/HDHomeRunEPG-to-XmlTv')
import HDHomeRunEPG_To_XmlTv as hdhomerun


class TestHTTP400Handling(unittest.TestCase):
    """Test HTTP 400 error handling in fetch_epg_data."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.device_auth = "test_auth_token"
        self.channels = [
            {"GuideNumber": "1", "GuideName": "Channel 1", "ImageURL": ""},
            {"GuideNumber": "501", "GuideName": "ESPN", "ImageURL": ""},
        ]
    
    @patch('HDHomeRunEPG_To_XmlTv.urllib.request.urlopen')
    def test_http_400_graceful_handling(self, mock_urlopen):
        """Test that HTTP 400 errors are caught and don't crash the script."""
        
        # Create a mock response for the first successful request
        mock_response_data = [
            {
                "GuideNumber": "1",
                "Guide": [
                    {
                        "Title": "Test Program",
                        "StartTime": 1234567890,
                        "EndTime": 1234567900,
                        "Synopsis": "Test synopsis"
                    }
                ]
            }
        ]
        
        # First call succeeds, second call raises HTTP 400
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_response_data).encode()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        
        # Make first call succeed, second call fail with 400
        mock_urlopen.side_effect = [
            mock_response,  # First successful response
            urllib.error.HTTPError(
                "https://api.hdhomerun.com/api/guide.php",
                400,
                "Bad Request",
                {},
                None
            )  # Second call raises 400
        ]
        
        # Call the function with small days/hours to trigger multiple requests
        result = hdhomerun.fetch_epg_data(
            self.device_auth,
            self.channels,
            days=7,
            hours=3
        )
        
        # Verify that the function returned data from the first successful request
        self.assertIsNotNone(result)
        self.assertEqual(len(result["channels"]), 1, "Should have one channel from successful request")
        self.assertEqual(len(result["programmes"]), 1, "Should have one programme from successful request")
        self.assertEqual(result["programmes"][0]["Title"], "Test Program")
        
        print("✓ Test passed: HTTP 400 errors are handled gracefully")
        print(f"✓ Successfully retrieved {len(result['programmes'])} programmes before API limit")
    
    @patch('HDHomeRunEPG_To_XmlTv.urllib.request.urlopen')
    def test_other_http_errors_are_raised(self, mock_urlopen):
        """Test that other HTTP errors are not suppressed."""
        
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://api.hdhomerun.com/api/guide.php",
            403,
            "Forbidden",
            {},
            None
        )
        
        # This should raise the 403 error, not catch it
        with self.assertRaises(urllib.error.HTTPError) as context:
            hdhomerun.fetch_epg_data(
                self.device_auth,
                self.channels,
                days=7,
                hours=3
            )
        
        self.assertEqual(context.exception.code, 403)
        print("✓ Test passed: Other HTTP errors (403) are properly raised")


if __name__ == "__main__":
    print("Testing HTTP 400 error handling...\n")
    unittest.main(verbosity=2)
