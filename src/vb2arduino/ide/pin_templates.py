"""Board-specific pin configuration templates."""

# Pin templates for common boards
PIN_TEMPLATES = {
    "esp32-s3-devkitc-1": {
        "name": "ESP32-S3 DevKit-C",
        "pins": {
            "led": 8,
            "button": 0,
            "tft_clk": 12,
            "tft_mosi": 11,
            "tft_miso": 13,
            "tft_cs": 10,
            "tft_dc": 9,
            "tft_rst": 14,
            "tft_bl": 46,
            "i2c_sda": 8,
            "i2c_scl": 9,
            "spi_clk": 12,
            "spi_mosi": 11,
            "spi_miso": 13,
        }
    },
    "esp32-s3-devkitm-1": {
        "name": "ESP32-S3 DevKit-M",
        "pins": {
            "led": 2,
            "button": 0,
            "tft_clk": 12,
            "tft_mosi": 11,
            "tft_miso": 13,
            "tft_cs": 10,
            "tft_dc": 9,
            "tft_rst": 8,
            "tft_bl": 46,
            "i2c_sda": 17,
            "i2c_scl": 18,
            "spi_clk": 12,
            "spi_mosi": 11,
            "spi_miso": 13,
        }
    },
    "esp32dev": {
        "name": "ESP32 DevKit V1",
        "pins": {
            "led": 2,
            "button": 0,
            "tft_clk": 14,
            "tft_mosi": 13,
            "tft_miso": 12,
            "tft_cs": 15,
            "tft_dc": 4,
            "tft_rst": 5,
            "tft_bl": 32,
            "i2c_sda": 21,
            "i2c_scl": 22,
            "spi_clk": 14,
            "spi_mosi": 13,
            "spi_miso": 12,
        }
    },
    "esp32-c3-devkitm-1": {
        "name": "ESP32-C3 DevKit",
        "pins": {
            "led": 3,
            "button": 9,
            "tft_clk": 6,
            "tft_mosi": 7,
            "tft_miso": 5,
            "tft_cs": 4,
            "tft_dc": 8,
            "tft_rst": 2,
            "tft_bl": 1,
            "i2c_sda": 5,
            "i2c_scl": 6,
            "spi_clk": 6,
            "spi_mosi": 7,
            "spi_miso": 5,
        }
    },
    "esp32-s3-lcd-1.47": {
        "name": "ESP32-S3 LCD 1.47",
        "pins": {
            "led": 2,
            "button": 0,
            "tft_clk": 40,
            "tft_mosi": 45,
            "tft_miso": -1,
            "tft_cs": 42,
            "tft_dc": 41,
            "tft_rst": -1,
            "tft_bl": 46,
            "i2c_sda": 17,
            "i2c_scl": 18,
            "spi_clk": 40,
            "spi_mosi": 45,
            "spi_miso": -1,
        },
        "build_flags": [
            "-DST7789_DRIVER",
            "-DTFT_WIDTH=172",
            "-DTFT_HEIGHT=320",
            "-DTFT_ROTATION=0",
            "-DTFT_MOSI=45",
            "-DTFT_SCLK=40",
            "-DTFT_CS=42",
            "-DTFT_DC=41",
            "-DTFT_RST=-1",
            "-DTFT_BL=46",
            "-DTOUCH_CS=-1",
            "-DUSE_HSPI_PORT",
            "-DTFT_BL_ON=HIGH",
            "-DSPI_FREQUENCY=40000000",
        ],
    },
    "uno": {
        "name": "Arduino Uno",
        "pins": {
            "led": 13,
            "button": 2,
            "tft_clk": 13,
            "tft_mosi": 11,
            "tft_miso": 12,
            "tft_cs": 10,
            "tft_dc": 9,
            "tft_rst": 8,
            "tft_bl": 3,
            "i2c_sda": 18,
            "i2c_scl": 19,
            "spi_clk": 13,
            "spi_mosi": 11,
            "spi_miso": 12,
        }
    },
    "megaatmega2560": {
        "name": "Arduino Mega 2560",
        "pins": {
            "led": 13,
            "button": 2,
            "tft_clk": 52,
            "tft_mosi": 51,
            "tft_miso": 50,
            "tft_cs": 49,
            "tft_dc": 48,
            "tft_rst": 47,
            "tft_bl": 46,
            "i2c_sda": 20,
            "i2c_scl": 21,
            "spi_clk": 52,
            "spi_mosi": 51,
            "spi_miso": 50,
        }
    },
    "nano": {
        "name": "Arduino Nano",
        "pins": {
            "led": 13,
            "button": 2,
            "tft_clk": 13,
            "tft_mosi": 11,
            "tft_miso": 12,
            "tft_cs": 10,
            "tft_dc": 9,
            "tft_rst": 8,
            "tft_bl": 3,
            "i2c_sda": 4,
            "i2c_scl": 5,
            "spi_clk": 13,
            "spi_mosi": 11,
            "spi_miso": 12,
        }
    },
    "pico": {
        "name": "Raspberry Pi Pico",
        "pins": {
            "led": 25,
            "button": 14,
            "tft_clk": 2,
            "tft_mosi": 3,
            "tft_miso": 4,
            "tft_cs": 5,
            "tft_dc": 6,
            "tft_rst": 7,
            "tft_bl": 8,
            "i2c_sda": 4,
            "i2c_scl": 5,
            "spi_clk": 2,
            "spi_mosi": 3,
            "spi_miso": 4,
        }
    },
}

# Pin descriptions for UI
PIN_DESCRIPTIONS = {
    "led": "LED indicator (GPIO)",
    "button": "Push button input (GPIO)",
    "tft_clk": "TFT Clock (SPI CLK)",
    "tft_mosi": "TFT MOSI (SPI MOSI)",
    "tft_miso": "TFT MISO (SPI MISO)",
    "tft_cs": "TFT Chip Select",
    "tft_dc": "TFT Data/Command",
    "tft_rst": "TFT Reset",
    "tft_bl": "TFT Backlight",
    "i2c_sda": "I2C SDA",
    "i2c_scl": "I2C SCL",
    "spi_clk": "SPI Clock",
    "spi_mosi": "SPI MOSI",
    "spi_miso": "SPI MISO",
}

PIN_CATEGORIES = {
    "Basic": ["led", "button"],
    "TFT Display": ["tft_clk", "tft_mosi", "tft_miso", "tft_cs", "tft_dc", "tft_rst", "tft_bl"],
    "I2C": ["i2c_sda", "i2c_scl"],
    "SPI": ["spi_clk", "spi_mosi", "spi_miso"],
}

def get_template_for_board(board_id: str) -> dict:
    """Get pin template for a board."""
    return PIN_TEMPLATES.get(board_id, None)

def get_default_pins() -> dict:
    """Get default pins (from ESP32 DevKit)."""
    return PIN_TEMPLATES["esp32dev"]["pins"].copy()

def get_all_pin_names() -> list[str]:
    """Get all available pin names."""
    return list(PIN_DESCRIPTIONS.keys())

def get_pin_description(pin_name: str) -> str:
    """Get description for a pin."""
    return PIN_DESCRIPTIONS.get(pin_name, "")

def get_pin_category(pin_name: str) -> str:
    """Get category for a pin."""
    for category, pins in PIN_CATEGORIES.items():
        if pin_name in pins:
            return category
    return "Other"
