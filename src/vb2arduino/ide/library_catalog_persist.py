# This file stores the curated library catalog and is updated by the IDE when the user clicks 'Update Libraries'.
# It is loaded on IDE startup to persist library info across sessions.

import json
import pathlib

CATALOG_PATH = pathlib.Path.home() / ".asic_library_catalog.json"

# Default catalog (imported from the static library_catalog.py)
def get_default_catalog():
    from vb2arduino.ide.library_catalog import LIBRARY_CATALOG
    return LIBRARY_CATALOG

def load_catalog():
    if CATALOG_PATH.exists():
        try:
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return get_default_catalog()

def save_catalog(catalog):
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)
