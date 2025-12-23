"""Utility functions for the IDE."""

import serial.tools.list_ports
import subprocess


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
