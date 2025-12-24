"""Library catalog with curated libraries organized by category."""

# Curated libraries organized by category
LIBRARY_CATALOG = {
    "Display": [
        {"name": "TFT_eSPI", "description": "Fast TFT LCD display driver", "boards": ["esp32*", "esp8266"]},
        {"name": "Adafruit SSD1306", "description": "OLED display driver", "boards": ["*"]},
        {"name": "LiquidCrystal I2C", "description": "16x2/20x4 LCD with I2C", "boards": ["*"]},
        {"name": "Adafruit GFX", "description": "Graphics library for displays", "boards": ["*"]},
        {"name": "U8g2", "description": "Monochrome LCD/OLED library", "boards": ["*"]},
    ],
    "Networking": [
        {"name": "WiFi", "description": "WiFi connectivity (built-in)", "boards": ["esp32*", "esp8266"]},
        {"name": "WebServer", "description": "Simple HTTP server", "boards": ["esp32*", "esp8266"]},
        {"name": "PubSubClient", "description": "MQTT client library", "boards": ["*"]},
        {"name": "ArduinoHttpClient", "description": "HTTP client for Arduino", "boards": ["*"]},
        {"name": "WiFiManager", "description": "WiFi configuration manager", "boards": ["esp32*", "esp8266"]},
    ],
    "Sensors": [
        {"name": "DHT sensor library", "description": "DHT temperature/humidity sensor", "boards": ["*"]},
        {"name": "Adafruit BME680", "description": "Environmental sensor (temp, humidity, pressure, gas)", "boards": ["*"]},
        {"name": "Adafruit BMP280", "description": "Barometric pressure sensor", "boards": ["*"]},
        {"name": "VL53L0X", "description": "Time-of-flight distance sensor", "boards": ["*"]},
        {"name": "MPU6050", "description": "6-axis accelerometer/gyroscope", "boards": ["*"]},
    ],
    "Data Storage": [
        {"name": "ArduinoJson", "description": "JSON parsing and generation", "boards": ["*"]},
        {"name": "SPIFFS", "description": "File system for flash storage", "boards": ["esp32*", "esp8266"]},
        {"name": "LittleFS", "description": "Lightweight file system", "boards": ["esp32*", "esp8266", "rp2040"]},
        {"name": "SD", "description": "SD card library", "boards": ["*"]},
        {"name": "EEPROMex", "description": "Extended EEPROM library", "boards": ["*"]},
    ],
    "Communication": [
        {"name": "BluetoothSerial", "description": "Bluetooth serial (ESP32)", "boards": ["esp32*"]},
        {"name": "NRFLite", "description": "nRF24L01 wireless module", "boards": ["*"]},
        {"name": "OneWire", "description": "1-Wire protocol library", "boards": ["*"]},
        {"name": "Wire", "description": "I2C communication (built-in)", "boards": ["*"]},
        {"name": "SPI", "description": "SPI communication (built-in)", "boards": ["*"]},
    ],
    "Motion Control": [
        {"name": "Servo", "description": "Servo motor control", "boards": ["*"]},
        {"name": "AccelStepper", "description": "Stepper motor library", "boards": ["*"]},
        {"name": "Motor2", "description": "Motor driver control", "boards": ["*"]},
    ],
    "Utilities": [
        {"name": "TimeLib", "description": "Time and date library", "boards": ["*"]},
        {"name": "FastLED", "description": "LED strip control (WS2812, etc)", "boards": ["*"]},
        {"name": "Button2", "description": "Advanced button library", "boards": ["*"]},
        {"name": "Ticker", "description": "Timer library for async tasks", "boards": ["esp32*", "esp8266"]},
    ],
}

def get_libraries_by_category(category: str) -> list[dict]:
    """Get libraries in a specific category."""
    return LIBRARY_CATALOG.get(category, [])

def get_all_categories() -> list[str]:
    """Get all available categories."""
    return list(LIBRARY_CATALOG.keys())

def get_compatible_libraries(board: str) -> list[dict]:
    """Get libraries compatible with a given board."""
    compatible = []
    for category, libs in LIBRARY_CATALOG.items():
        for lib in libs:
            for board_pattern in lib.get("boards", []):
                if _board_matches_pattern(board, board_pattern):
                    compatible.append(lib)
                    break
    return compatible

def _board_matches_pattern(board: str, pattern: str) -> bool:
    """Check if board matches pattern (e.g., 'esp32*' matches 'esp32-s3-devkitc-1')."""
    if pattern == "*":
        return True
    if pattern.endswith("*"):
        return board.startswith(pattern[:-1])
    return board == pattern

def get_library_description(lib_name: str) -> str:
    """Get description for a library."""
    for category, libs in LIBRARY_CATALOG.items():
        for lib in libs:
            if lib["name"] == lib_name:
                return lib.get("description", "")
    return ""
