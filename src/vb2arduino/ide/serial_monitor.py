"""Serial monitor widget for communicating with microcontroller."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QComboBox, QLabel, QCheckBox, QFileDialog
)
from .serial_plotter import SerialPlotter
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont
from datetime import datetime
import pathlib
import serial
import serial.tools.list_ports


class SerialReader(QThread):
    """Thread for reading from serial port."""
    
    data_received = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.running = True
        self.daemon = True
        
    def run(self):
        """Read data from serial port."""
        try:
            while self.running:
                try:
                    if self.serial_port and self.serial_port.is_open:
                        if self.serial_port.in_waiting > 0:
                            raw = self.serial_port.read(self.serial_port.in_waiting)
                            if raw:
                                self.data_received.emit(raw)
                except Exception as e:
                    if self.running:
                        self.error_occurred.emit(f"Read error: {str(e)}")
                    break
                self.msleep(50)
        except Exception as e:
            self.error_occurred.emit(f"Thread error: {str(e)}")
            
    def stop(self):
        """Stop the reader thread."""
        self.running = False
        self.wait(1000)


class SerialMonitor(QWidget):
    """Serial monitor for communicating with microcontroller."""
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.reader_thread = None
        self.plotter = SerialPlotter(self)
        self.init_ui()

    def show_plotter(self):
        self.plotter.show()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Top toolbar
        toolbar = QHBoxLayout()
        
        # Baud rate selector
        toolbar.addWidget(QLabel("Baud rate:"))
        self.baud_combo = QComboBox()
        self.baud_combo.addItems([
            "300", "1200", "2400", "4800", "9600", 
            "19200", "38400", "57600", "74880", "115200", 
            "230400", "250000", "500000", "1000000", "2000000"
        ])
        self.baud_combo.setCurrentText("115200")
        # Match width to other combos and provide tooltip
        self.baud_combo.setMaximumWidth(140)
        self.baud_combo.setToolTip("Select serial baud rate for connection")
        # Accessibility
        self.baud_combo.setAccessibleName("Baud Rate Selector")
        self.baud_combo.setAccessibleDescription("Select a baud rate to use for serial connection")
        toolbar.addWidget(self.baud_combo)
        
        toolbar.addSpacing(12)
        
        # Connect/Disconnect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setMaximumWidth(100)
        self.connect_btn.clicked.connect(self.toggle_connection)
        # Accessibility
        self.connect_btn.setAccessibleName("Connect Button")
        self.connect_btn.setAccessibleDescription("Connect or disconnect the serial monitor")
        toolbar.addWidget(self.connect_btn)
        
        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setMaximumWidth(80)
        self.clear_btn.clicked.connect(self.clear_output)
        self.clear_btn.setAccessibleName("Clear Button")
        self.clear_btn.setAccessibleDescription("Clear the serial output display")
        toolbar.addWidget(self.clear_btn)

        # Autoscroll toggle
        self.autoscroll_checkbox = QCheckBox("Autoscroll")
        self.autoscroll_checkbox.setChecked(True)
        self.autoscroll_checkbox.setAccessibleName("Autoscroll Checkbox")
        self.autoscroll_checkbox.setAccessibleDescription("Automatically scroll the serial output to latest data")
        toolbar.addWidget(self.autoscroll_checkbox)

        # Timestamp toggle
        self.timestamp_checkbox = QCheckBox("Timestamp")
        self.timestamp_checkbox.setChecked(True)
        self.timestamp_checkbox.setAccessibleName("Timestamp Checkbox")
        self.timestamp_checkbox.setAccessibleDescription("Toggle timestamps for incoming serial data")
        toolbar.addWidget(self.timestamp_checkbox)

        # Hex view toggle
        self.hex_checkbox = QCheckBox("Hex")
        self.hex_checkbox.setToolTip("Show incoming data in hex format")
        self.hex_checkbox.setAccessibleName("Hex View Checkbox")
        self.hex_checkbox.setAccessibleDescription("Display incoming serial data as hexadecimal values")
        toolbar.addWidget(self.hex_checkbox)

        # Save log button
        self.save_btn = QPushButton("Save Log")
        self.save_btn.setMaximumWidth(90)
        self.save_btn.clicked.connect(self.save_log)
        self.save_btn.setAccessibleName("Save Log Button")
        self.save_btn.setAccessibleDescription("Save current serial output to a file")
        toolbar.addWidget(self.save_btn)

        # Overflow / More menu for small widths
        from PyQt6.QtWidgets import QToolButton, QMenu
        self.more_btn = QToolButton()
        self.more_btn.setText("⋯")
        self.more_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.more_menu = QMenu()
        # Actions mirror existing controls
        self.action_clear = self.more_menu.addAction("Clear")
        self.action_clear.triggered.connect(self.clear_output)
        self.action_save = self.more_menu.addAction("Save Log")
        self.action_save.triggered.connect(self.save_log)
        self.action_toggle_autoscroll = self.more_menu.addAction("Toggle Autoscroll")
        self.action_toggle_autoscroll.triggered.connect(lambda: self.autoscroll_checkbox.setChecked(not self.autoscroll_checkbox.isChecked()))
        self.action_toggle_timestamp = self.more_menu.addAction("Toggle Timestamp")
        self.action_toggle_timestamp.triggered.connect(lambda: self.timestamp_checkbox.setChecked(not self.timestamp_checkbox.isChecked()))
        self.action_toggle_hex = self.more_menu.addAction("Toggle Hex View")
        self.action_toggle_hex.triggered.connect(lambda: self.hex_checkbox.setChecked(not self.hex_checkbox.isChecked()))
        self.more_btn.setMenu(self.more_menu)
        self.more_btn.setVisible(False)
        toolbar.addWidget(self.more_btn)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 10))
        layout.addWidget(self.output_text)
        
        # Input area
        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type message and press Enter...")
        self.input_line.returnPressed.connect(self.send_data)
        input_layout.addWidget(self.input_line)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_data)
        self.send_btn.setMaximumWidth(80)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
        self.setEnabled(False)  # Disabled until port is available
        # Responsive behaviour: update visibility on resize
        self._responsive_threshold = 480  # px

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_responsive_layout()

    def _update_responsive_layout(self):
        """Show or hide less-important controls when widget is narrow."""
        w = self.width()
        # If narrow, hide Clear, Save, Autoscroll, Timestamp, Hex and show More menu
        if w < self._responsive_threshold:
            self.clear_btn.setVisible(False)
            self.save_btn.setVisible(False)
            self.autoscroll_checkbox.setVisible(False)
            self.timestamp_checkbox.setVisible(False)
            self.hex_checkbox.setVisible(False)
            self.more_btn.setVisible(True)
        else:
            self.clear_btn.setVisible(True)
            self.save_btn.setVisible(True)
            self.autoscroll_checkbox.setVisible(True)
            self.timestamp_checkbox.setVisible(True)
            self.hex_checkbox.setVisible(True)
            self.more_btn.setVisible(False)
        
    def set_port(self, port):
        """Set the serial port to use."""
        # Disconnect from previous port if connected
        if self.serial_port and self.serial_port.is_open:
            self.disconnect_serial()
        self.port_name = port
        # Only enable if port is not None/empty
        self.setEnabled(bool(port))
        if port:
            self.connect_btn.setText("Connect")
        
    def toggle_connection(self):
        """Toggle serial connection."""
        if self.serial_port and self.serial_port.is_open:
            self.disconnect_serial()
        else:
            self.connect_serial()
            
    def connect_serial(self):
        """Connect to serial port."""
        if not hasattr(self, 'port_name') or not self.port_name:
            self.output_text.append("Error: No port selected\n")
            return
        
        # Prevent multiple connections
        if self.reader_thread and self.reader_thread.isRunning():
            self.output_text.append("Already connected\n")
            return
            
        try:
            baud_rate = int(self.baud_combo.currentText())
            # Close any existing connection
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            
            # Create new serial connection
            self.serial_port = serial.Serial(
                port=self.port_name,
                baudrate=baud_rate,
                timeout=1,
                write_timeout=1
            )
            
            # Start reader thread
            self.reader_thread = SerialReader(self.serial_port)
            self.reader_thread.data_received.connect(self.append_output)
            self.reader_thread.error_occurred.connect(self.on_reader_error)
            self.reader_thread.start()
            
            self.connect_btn.setText("Disconnect")
            self.output_text.append(f"Connected to {self.port_name} at {baud_rate} baud\n")
            
        except serial.SerialException as e:
            self.output_text.append(f"Error connecting: {str(e)}\n")
            self.serial_port = None
        except Exception as e:
            self.output_text.append(f"Unexpected error: {str(e)}\n")
            self.serial_port = None
            
    def disconnect_serial(self):
        """Disconnect from serial port."""
        try:
            # Stop reader thread first
            if self.reader_thread:
                self.reader_thread.stop()
                # Wait for thread to finish (with timeout)
                if not self.reader_thread.wait(2000):
                    self.reader_thread.terminate()
                    self.reader_thread.wait()
                self.reader_thread = None
            
            # Close serial port
            if self.serial_port:
                try:
                    if self.serial_port.is_open:
                        self.serial_port.close()
                except Exception:
                    pass
                self.serial_port = None
            
            self.connect_btn.setText("Connect")
            self.output_text.append("Disconnected\n")
            
        except Exception as e:
            self.output_text.append(f"Error disconnecting: {str(e)}\n")
            
    def send_data(self):
        """Send data to serial port."""
        if not self.serial_port or not self.serial_port.is_open:
            self.output_text.append("Error: Not connected\n")
            return
            
        text = self.input_line.text()
        if text:
            try:
                self.serial_port.write((text + "\n").encode('utf-8'))
                self.append_output(f"> {text}\n")
                self.input_line.clear()
            except Exception as e:
                self.output_text.append(f"Error sending: {str(e)}\n")
                
    def append_output(self, data):
        """Append incoming data to output with formatting options."""
        try:
            # Normalize to bytes for consistent handling
            raw = data if isinstance(data, (bytes, bytearray)) else str(data).encode("utf-8", errors="ignore")

            if self.hex_checkbox.isChecked():
                rendered = " ".join(f"{b:02X}" for b in raw)
            else:
                rendered = raw.decode("utf-8", errors="replace")

            if self.timestamp_checkbox.isChecked():
                ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                rendered = f"[{ts}] {rendered}"

            # Track scroll position to support autoscroll toggle
            scrollbar = self.output_text.verticalScrollBar()
            prev_value = scrollbar.value()
            at_bottom = prev_value == scrollbar.maximum()

            cursor = self.output_text.textCursor()
            cursor.movePosition(cursor.End)
            self.output_text.setTextCursor(cursor)
            self.output_text.insertPlainText(rendered)

            # Append newline for readability when hex mode adds long lines
            if not rendered.endswith("\n"):
                self.output_text.insertPlainText("\n")

            # Try to parse and plot numeric data (simple CSV or whitespace separated)
            try:
                line = raw.decode("utf-8", errors="ignore").strip()
                if line:
                    # Accept comma or whitespace separated numbers
                    if "," in line:
                        parts = line.split(",")
                    else:
                        parts = line.split()
                    nums = [float(p) for p in parts if p.replace(".", "", 1).replace("-", "", 1).isdigit()]
                    for i, val in enumerate(nums):
                        self.plotter.add_sample(f"Y{i+1}", val)
            except Exception:
                pass
            # Restore/scroll based on autoscroll checkbox
            if self.autoscroll_checkbox.isChecked() or at_bottom:
                scrollbar.setValue(scrollbar.maximum())
            else:
                scrollbar.setValue(prev_value)
        except Exception:
            pass  # Ignore errors in GUI updates
    
    def on_reader_error(self, error_msg):
        """Handle errors from reader thread."""
        self.append_output(f"[Serial Error] {error_msg}\n")
        # Auto-disconnect on error
        self.disconnect_serial()
        
    def clear_output(self):
        """Clear output text."""
        self.output_text.clear()

    def save_log(self):
        """Save the current log to a file."""
        filename, _ = QFileDialog.getSaveFileName(self, "Save Serial Log", "serial_log.txt", "Text Files (*.txt);;All Files (*)")
        if not filename:
            return
        try:
            pathlib.Path(filename).write_text(self.output_text.toPlainText(), encoding="utf-8")
            self.append_output(f"[log saved to {filename}]\n")
        except Exception as e:
            self.append_output(f"[failed to save log: {e}]\n")
        
    def closeEvent(self, event):
        """Handle close event."""
        # Ensure serial thread is stopped and port is closed
        try:
            self.disconnect_serial()
        except Exception:
            pass
        event.accept()
