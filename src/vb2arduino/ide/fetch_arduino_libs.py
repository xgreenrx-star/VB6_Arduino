"""Fetch Arduino library list from Arduino Library Manager JSON API."""
import urllib.request
import json

def fetch_arduino_libraries():
    url = "https://downloads.arduino.cc/libraries/library_index.json"
    with urllib.request.urlopen(url, timeout=20) as response:
        data = json.load(response)
    # data['libraries'] is a list of dicts
    libraries = data.get('libraries', [])
    # Return a list of dicts with at least name and sentence (description)
    return [
        {
            'name': lib.get('name', ''),
            'description': lib.get('sentence', ''),
            'author': lib.get('author', ''),
            'version': lib.get('version', ''),
            'maintainer': lib.get('maintainer', ''),
            'website': lib.get('website', ''),
            'architectures': lib.get('architectures', []),
        }
        for lib in libraries
    ]
