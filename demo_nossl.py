#!/usr/bin/env python3
"""
Demo script with SSL workaround for macOS
This bypasses SSL verification for testing purposes only.
"""

# IMPORTANT: Disable SSL warnings and verification for demo
# This is NOT recommended for production use
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''

# Now run the normal demo
import demo
demo.main()
