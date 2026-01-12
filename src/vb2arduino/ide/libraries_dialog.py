"""Library selection dialog similar to VB6 Components."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QTextEdit, QSplitter, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt


class LibrariesDialog(QDialog):
    """Dialog for selecting Arduino libraries similar to VB6 Components."""
    
    # Common Arduino/ESP32 libraries with descriptions
    AVAILABLE_LIBRARIES = {
        "Wire.h": {
            "name": "Wire (I2C)",
            "description": "I2C communication library for connecting sensors and displays",
            "platform": "all"
        },
        "SPI.h": {
            "name": "SPI",
            "description": "Serial Peripheral Interface for high-speed communication",
            "platform": "all"
        },
        "WiFi.h": {
            "name": "WiFi",
            "description": "WiFi connectivity for network communication",
            "platform": "esp32,esp8266"
        },
        "BLEDevice.h": {
            "name": "BLE Device",
            "description": "Bluetooth Low Energy device functionality",
            "platform": "esp32"
        },
        "BLEServer.h": {
            "name": "BLE Server",
            "description": "Create BLE server for peripheral mode",
            "platform": "esp32"
        },
        "BLEClient.h": {
            "name": "BLE Client",
            "description": "Connect to BLE peripherals as a client",
            "platform": "esp32"
        },
        "BLEUtils.h": {
            "name": "BLE Utils",
            "description": "BLE utility functions and helpers",
            "platform": "esp32"
        },
        "Preferences.h": {
            "name": "Preferences (NVS)",
            "description": "Non-volatile storage for persistent data",
            "platform": "esp32"
        },
        "SPIFFS.h": {
            "name": "SPIFFS",
            "description": "SPI Flash File System for file storage",
            "platform": "esp32,esp8266"
        },
        "SD.h": {
            "name": "SD Card",
            "description": "SD card file system access",
            "platform": "all"
        },
        "Servo.h": {
            "name": "Servo",
            "description": "Control servo motors",
            "platform": "all"
        },
        "Stepper.h": {
            "name": "Stepper",
            "description": "Control stepper motors",
            "platform": "all"
        },
        "LiquidCrystal.h": {
            "name": "LCD Display",
            "description": "Control LCD character displays",
            "platform": "all"
        },
        "Adafruit_GFX.h": {
            "name": "Adafruit GFX",
            "description": "Graphics library for displays",
            "platform": "all"
        },
        "TFT_eSPI.h": {
            "name": "TFT eSPI",
            "description": "Fast TFT display library for ESP32",
            "platform": "esp32"
        },
        "HTTPClient.h": {
            "name": "HTTP Client",
            "description": "Make HTTP requests",
            "platform": "esp32,esp8266"
        },
        "WebServer.h": {
            "name": "Web Server",
            "description": "Create HTTP web server",
            "platform": "esp32,esp8266"
        },
        "MQTT.h": {
            "name": "MQTT",
            "description": "MQTT protocol for IoT messaging",
            "platform": "all"
        },
        "ArduinoJson.h": {
            "name": "Arduino JSON",
            "description": "Parse and create JSON data",
            "platform": "all"
        },
        "OneWire.h": {
            "name": "OneWire",
            "description": "Dallas OneWire protocol (DS18B20 sensors)",
            "platform": "all"
        },
        "DHT.h": {
            "name": "DHT Sensor",
            "description": "DHT11/DHT22 temperature and humidity sensors",
            "platform": "all"
        },
        "Adafruit_Sensor.h": {
            "name": "Adafruit Unified Sensor",
            "description": "Unified sensor driver interface",
            "platform": "all"
        },
        "MPU6050.h": {
            "name": "MPU6050",
            "description": "Gyroscope and accelerometer sensor",
            "platform": "all"
        },
        "ESP32Encoder.h": {
            "name": "ESP32 Encoder",
            "description": "Rotary encoder support for ESP32",
            "platform": "esp32"
        },
        "Ticker.h": {
            "name": "Ticker",
            "description": "Timer-based callbacks",
            "platform": "esp32,esp8266"
        },
        "esp_sleep.h": {
            "name": "ESP Sleep",
            "description": "Deep sleep and power management",
            "platform": "esp32"
        },
        "driver/rtc_io.h": {
            "name": "RTC GPIO",
            "description": "RTC GPIO for deep sleep wakeup",
            "platform": "esp32"
        },
    }
    
    def __init__(self, selected_libraries=None, parent=None):
        super().__init__(parent)
        self.selected_libraries = selected_libraries or []
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle("Libraries - Asic (Arduino Basic)")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout()
        
        # Info label
        info = QLabel("Select libraries to include in your project:")
        info.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(info)
        
        # Splitter for list and description
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Library list with checkboxes
        list_widget = QGroupBox("Available Libraries")
        list_layout = QVBoxLayout()
        
        self.library_list = QListWidget()
        self.library_list.setAlternatingRowColors(True)
        self.library_list.currentItemChanged.connect(self.on_library_selected)
        
        # Populate library list
        for lib_file, lib_info in sorted(self.AVAILABLE_LIBRARIES.items(), key=lambda x: x[1]["name"]):
            item = QListWidgetItem(lib_info["name"])
            item.setData(Qt.ItemDataRole.UserRole, lib_file)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            # Check if library is in selected list
            if lib_file in self.selected_libraries:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            
            self.library_list.addItem(item)
        
        list_layout.addWidget(self.library_list)
        list_widget.setLayout(list_layout)
        splitter.addWidget(list_widget)
        
        # Right: Description area
        desc_widget = QGroupBox("Library Information")
        desc_layout = QVBoxLayout()
        
        self.desc_text = QTextEdit()
        self.desc_text.setReadOnly(True)
        self.desc_text.setMaximumHeight(150)
        desc_layout.addWidget(self.desc_text)
        
        desc_widget.setLayout(desc_layout)
        splitter.addWidget(desc_widget)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(self.select_all_btn)
        
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_all_btn)
        
        button_layout.addStretch()
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Select first item to show description
        if self.library_list.count() > 0:
            self.library_list.setCurrentRow(0)
            
    def on_library_selected(self, current, previous):
        """Update description when library is selected."""
        if not current:
            return
            
        lib_file = current.data(Qt.ItemDataRole.UserRole)
        lib_info = self.AVAILABLE_LIBRARIES.get(lib_file, {})
        
        desc = f"<b>Library:</b> {lib_info.get('name', 'Unknown')}<br>"
        desc += f"<b>Header File:</b> <code>#{lib_file}</code><br>"
        desc += f"<b>Platform:</b> {lib_info.get('platform', 'all')}<br><br>"
        desc += f"<b>Description:</b><br>{lib_info.get('description', 'No description available.')}"
        
        self.desc_text.setHtml(desc)
        
    def select_all(self):
        """Select all libraries."""
        for i in range(self.library_list.count()):
            item = self.library_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)
            
    def clear_all(self):
        """Clear all selections."""
        for i in range(self.library_list.count()):
            item = self.library_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
            
    def get_selected_libraries(self):
        """Get list of selected library #Include directives."""
        selected = []
        for i in range(self.library_list.count()):
            item = self.library_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                lib_file = item.data(Qt.ItemDataRole.UserRole)
                # Always use #Include <header_file> format
                selected.append(f'#Include <{lib_file}>')
        return selected
