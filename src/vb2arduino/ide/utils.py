"""Utility functions for the IDE."""

import serial.tools.list_ports
import subprocess
import json
import threading
from typing import Optional, Callable


def get_available_ports():
    """Get list of available serial ports.
    
    Returns:
        list: List of port names (e.g., ['/dev/ttyUSB0', 'COM3'])
    """
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


def get_platformio_boards():
    """Get list of common PlatformIO boards.
    
    Returns:
        list: List of (display_name, board_id) tuples
    """
    # Common boards - could be expanded by parsing `pio boards` output
    boards = [
        ("ESP32-S3 DevKitM-1", "esp32-s3-devkitm-1"),
        ("ESP32 DevKit", "esp32dev"),
        ("Arduino Uno", "uno"),
        ("Arduino Mega 2560", "megaatmega2560"),
        ("Arduino Nano 33 IoT", "nano_33_iot"),
    ]
    return boards


def check_platformio_installed():
    """Check if PlatformIO CLI is installed.
    
    Returns:
        bool: True if installed, False otherwise
    """
    try:
        result = subprocess.run(
            ["pio", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def get_pio_devices():
    """Return PlatformIO devices via `pio device list --json-output`.

    Returns:
        list[dict]: Device entries with fields like 'port', 'hwid', 'protocol', 'properties'.
    """
    try:
        result = subprocess.run(
            ["pio", "device", "list", "--json-output"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return []
        return json.loads(result.stdout or "[]")
    except Exception:
        return []


def auto_detect_board_and_port():
    """Heuristically detect board and port from PlatformIO devices.

    Returns:
        tuple[str|None, str|None]: (board_id, port) best guesses, or (None, None).
    """
    devices = get_pio_devices()
    if not devices:
        # Fallback to pyserial ports if pio output not available
        ports = get_available_ports()
        return (None, ports[0] if ports else None)

    # Known vendor VID mappings (hex strings without 0x)
    VIDS = {
        "303a": "espressif",  # Espressif Systems
        "2341": "arduino",    # Arduino LLC
        "2e8a": "raspberrypi",  # Raspberry Pi (RP2040)
        "10c4": "silabs",     # CP210x (used by many boards)
        "1a86": "wch",        # CH340 (used by many boards)
    }

    # Default guesses per vendor
    DEFAULT_BOARD_BY_VENDOR = {
        "espressif": "esp32-s3-devkitc-1",
        "arduino": "uno",
        "raspberrypi": "pico",
    }

    def parse_vid(hwid: str | None) -> str | None:
        if not hwid:
            return None
        # hwid may contain 'USB VID:PID=303A:1001'
        try:
            if "VID:PID=" in hwid:
                vid_pid = hwid.split("VID:PID=", 1)[1].split()[0]
                vid = vid_pid.split(":")[0].lower()
                return vid
        except Exception:
            return None
        return None

    # Prefer USB serial devices
    for dev in devices:
        port = dev.get("port")
        hwid = dev.get("hwid") or dev.get("hardware_id")
        vid = parse_vid(hwid)
        vendor_key = VIDS.get(vid) if vid else None
        # Choose board based on vendor
        board = DEFAULT_BOARD_BY_VENDOR.get(vendor_key) if vendor_key else None
        # If unknown vendor, pick ESP32 DevKit as safe default when ttyUSB/ACM present
        if not board and port:
            if str(port).lower().find("ttyusb") >= 0 or str(port).lower().find("ttyacm") >= 0:
                board = "esp32dev"
        if port:
            return (board, port)

    # Fallback: first available port only
    ports = get_available_ports()
    return (None, ports[0] if ports else None)


def search_platformio_libraries(query: str, callback: Optional[Callable] = None) -> list[dict]:
    """Search PlatformIO library registry.
    
    Args:
        query: Search term (e.g., 'WiFi', 'display', 'sensor')
        callback: Optional callback(results) called when search completes
        
    Returns:
        list[dict]: List of library info dicts with 'name', 'description', 'url', etc.
    """
    def run_search():
        try:
            result = subprocess.run(
                ["pio", "lib", "search", query],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                # Parse output - pio lib search returns text table format
                # For now, return empty list as parsing is complex
                # In production, could implement text parsing or use JSON if available
                libraries = []
                if callback:
                    callback(libraries)
                return libraries
            return []
        except Exception:
            return []
    
    # Run in thread to avoid blocking UI
    if callback:
        thread = threading.Thread(target=run_search, daemon=True)
        thread.start()
        return []
    else:
        return run_search()

