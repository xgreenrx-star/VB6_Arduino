"""Project configuration management for Asic (Arduino Basic) IDE."""

import json
import pathlib
from typing import Optional


class ProjectConfig:
    """Manages project-specific settings like library dependencies."""
    
    CONFIG_FILENAME = ".asic.json"
    
    def __init__(self, project_dir: Optional[pathlib.Path] = None):
        self.project_dir = project_dir or pathlib.Path.home() / ".asic"
        self.config_path = self.project_dir / self.CONFIG_FILENAME
        self.data = self._load_config()
    
    def _load_config(self) -> dict:
        """Load project configuration from disk."""
        if self.config_path.exists():
            try:
                return json.loads(self.config_path.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, IOError):
                pass
        return self._default_config()
    
    def _default_config(self) -> dict:
        """Return default project configuration."""
        from vb2arduino.ide.pin_templates import get_default_pins
        return {
            "version": 1,
            "libraries": ["TFT_eSPI"],  # Default libraries
            "pins": get_default_pins(),  # Default pin configuration
            "build_flags": [],  # Custom build flags/defines
            "templates": {},  # Saved custom templates
            "board": None,  # Selected board ID
            "port": None,   # Selected serial port
        }
    
    def save(self):
        """Save configuration to disk."""
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(
            json.dumps(self.data, indent=2),
            encoding='utf-8'
        )
    
    def get_libraries(self) -> list[str]:
        """Get list of project libraries."""
        return self.data.get("libraries", [])
    
    def set_libraries(self, libraries: list[str]):
        """Set project libraries."""
        self.data["libraries"] = libraries
        self.save()
    
    def add_library(self, library: str):
        """Add a library to the project."""
        libs = self.get_libraries()
        if library not in libs:
            libs.append(library)
            self.set_libraries(libs)
    
    def remove_library(self, library: str):
        """Remove a library from the project."""
        libs = self.get_libraries()
        if library in libs:
            libs.remove(library)
            self.set_libraries(libs)
    
    def get_pins(self) -> dict[str, int]:
        """Get pin configuration."""
        return self.data.get("pins", {})
    
    def set_pins(self, pins: dict[str, int]):
        """Set pin configuration."""
        self.data["pins"] = pins
        self.save()
    
    def get_pin(self, pin_name: str) -> int:
        """Get a specific pin number."""
        pins = self.get_pins()
        return pins.get(pin_name, -1)
    
    def set_pin(self, pin_name: str, pin_number: int):
        """Set a specific pin."""
        pins = self.get_pins()
        pins[pin_name] = pin_number
        self.set_pins(pins)
    
    def load_template(self, template: dict):
        """Load a pin template."""
        if "pins" in template:
            self.set_pins(template["pins"])
        # Optionally load build flags
        if "build_flags" in template:
            self.set_build_flags(template.get("build_flags", []))

    # Build flags management
    def get_build_flags(self) -> list[str]:
        """Get custom build flags."""
        return self.data.get("build_flags", [])

    def set_build_flags(self, flags: list[str]):
        """Set custom build flags."""
        self.data["build_flags"] = flags
        self.save()

    def add_build_flag(self, flag: str):
        """Add a build flag if not present."""
        flags = self.get_build_flags()
        if flag and flag not in flags:
            flags.append(flag)
            self.set_build_flags(flags)

    def remove_build_flag(self, flag: str):
        """Remove a build flag if present."""
        flags = self.get_build_flags()
        if flag in flags:
            flags.remove(flag)
            self.set_build_flags(flags)

    # Custom templates management
    def get_templates(self) -> dict:
        """Return dict of saved templates {name: {board_id,pins,build_flags}}."""
        return self.data.get("templates", {})

    def list_template_names(self) -> list[str]:
        return sorted(self.get_templates().keys())

    def save_template(self, name: str, pins: dict[str, int], board_id: str | None = None, build_flags: list[str] | None = None):
        """Save a custom template with name."""
        if not name:
            return
        templates = self.get_templates()
        templates[name] = {
            "board_id": board_id,
            "pins": pins,
            "build_flags": build_flags or [],
        }
        self.data["templates"] = templates
        self.save()

    def delete_template(self, name: str):
        """Delete a saved template by name."""
        templates = self.get_templates()
        if name in templates:
            del templates[name]
            self.data["templates"] = templates
            self.save()

    def get_template(self, name: str) -> dict | None:
        return self.get_templates().get(name)

    def get_templates_for_board(self, board_id: str | None) -> dict:
        """Return templates matching board_id; if None, return all."""
        all_t = self.get_templates()
        if not board_id:
            return all_t
        return {k: v for k, v in all_t.items() if v.get("board_id") == board_id}

    def load_template_by_name(self, name: str) -> bool:
        """Load template pins/flags by name into project config."""
        t = self.get_template(name)
        if not t:
            return False
        self.set_pins(t.get("pins", {}))
        self.set_build_flags(t.get("build_flags", []))
        return True
    # Board and port management
    def get_board(self) -> Optional[str]:
        """Get the selected board ID."""
        return self.data.get("board")
    
    def set_board(self, board_id: Optional[str]):
        """Set the selected board ID."""
        self.data["board"] = board_id
        self.save()
    
    def get_port(self) -> Optional[str]:
        """Get the selected serial port."""
        return self.data.get("port")
    
    def set_port(self, port: Optional[str]):
        """Set the selected serial port."""
        self.data["port"] = port
        self.save()
    
    def set_board_and_port(self, board_id: Optional[str], port: Optional[str]):
        """Set both board and port at once."""
        self.data["board"] = board_id
        self.data["port"] = port
        self.save()