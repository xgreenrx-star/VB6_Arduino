"""Settings management for VB2Arduino IDE."""

import json
import pathlib
from typing import Dict, Any


class Settings:
    """Manages IDE settings."""
    
    DEFAULT_SETTINGS = {
        "editor": {
            "font_family": "Courier New",
            "font_size": 11,
            "background_color": "#FFFFFF",
            "text_color": "#000000",
            "current_line_color": "#FFFFCC",
            "line_number_bg": "#F0F0F0",
            "line_number_fg": "#808080",
            "jump_highlight_color": "#FFD7A1",
            "jump_highlight_duration_ms": 3000,
            "show_compile_success_popup": True,
            "show_upload_success_popup": True,
            "show_compile_failure_popup": True,
            "show_upload_failure_popup": True,
        },
        "syntax": {
            "keyword_color": "#0000FF",
            "keyword_bold": True,
            "function_color": "#FF00FF",
            "function_bold": True,
            "constant_color": "#0000FF",
            "constant_bold": False,
            "number_color": "#FF0000",
            "number_bold": False,
            "string_color": "#FF0000",
            "string_bold": False,
            "comment_color": "#008000",
            "comment_italic": True,
        }
    }
    
    def __init__(self):
        self.config_dir = pathlib.Path.home() / ".vb2arduino"
        self.config_file = self.config_dir / "settings.json"
        self.data = self.load()
        
    def load(self) -> Dict[str, Any]:
        """Load settings from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._merge_settings(self.DEFAULT_SETTINGS.copy(), loaded)
            except Exception:
                pass
        return self.DEFAULT_SETTINGS.copy()
        
    def save(self):
        """Save settings to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")
            
    def get(self, category: str, key: str, default=None):
        """Get a setting value."""
        return self.data.get(category, {}).get(key, default)
        
    def set(self, category: str, key: str, value):
        """Set a setting value."""
        if category not in self.data:
            self.data[category] = {}
        self.data[category][key] = value
        
    def _merge_settings(self, defaults: dict, loaded: dict) -> dict:
        """Recursively merge loaded settings with defaults."""
        result = defaults.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result
