"""Serial monitor widget for communicating with microcontroller."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QLineEdit, QPushButton, QComboBox, QLabel
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont
import serial
import serial.tools.list_ports


class SerialReader(QThread):
    """Thread for reading from serial port."""
    
    data_received = pyqtSignal(str)
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
                            data = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8', errors='ignore')
                            if data:
                                self.data_received.emit(data)
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
        self.init_ui()
        
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
        self.baud_combo.setMaximumWidth(100)
        toolbar.addWidget(self.baud_combo)
        
        toolbar.addSpacing(20)
        
        # Connect/Disconnect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setMaximumWidth(100)
        self.connect_btn.clicked.connect(self.toggle_connection)
        toolbar.addWidget(self.connect_btn)
        
        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setMaximumWidth(80)
        self.clear_btn.clicked.connect(self.clear_output)
        toolbar.addWidget(self.clear_btn)
        
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
                self.output_text.append(f"> {text}\n")
                self.input_line.clear()
            except Exception as e:
                self.output_text.append(f"Error sending: {str(e)}\n")
                
    def append_output(self, text):
        """Append text to output."""
        try:
            self.output_text.moveCursor(self.output_text.textCursor().End)
            self.output_text.insertPlainText(text)
            self.output_text.moveCursor(self.output_text.textCursor().End)
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
        
    def closeEvent(self, event):
        """Handle close event."""
        # Ensure serial thread is stopped and port is closed
        try:
            self.disconnect_serial()
        except Exception:
            pass
        event.accept()
