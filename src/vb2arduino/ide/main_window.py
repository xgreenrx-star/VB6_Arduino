"""Main window for VB2Arduino IDE."""

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QToolBar, QPushButton, QComboBox, QLabel, QMessageBox, QFileDialog,
    QStatusBar, QDialog, QProgressDialog, QListWidget, QListWidgetItem, QMenu
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction, QClipboard
import pathlib
import subprocess
import tempfile
import re

from vb2arduino.ide.editor import CodeEditorWidget
from vb2arduino.ide.serial_monitor import SerialMonitor
from vb2arduino.ide.project_tree import ProjectTreeView
from vb2arduino.ide.utils import (
    get_available_ports,
    get_platformio_boards,
    auto_detect_board_and_port,
)
from vb2arduino.ide.settings import Settings
from vb2arduino.ide.settings_dialog import SettingsDialog
from vb2arduino.ide.libraries_dialog import LibrariesDialog
from vb2arduino.ide.manage_libraries_dialog import LibrariesDialog as ManageLibrariesDialog
from vb2arduino.ide.pin_configuration_dialog import PinConfigurationDialog
from vb2arduino.ide.pin_templates import get_template_for_board
from vb2arduino.ide.project_config import ProjectConfig
from vb2arduino import transpile_string


class MainWindow(QMainWindow):
    """Main IDE window similar to Arduino IDE."""
    
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.project_config = ProjectConfig()  # Load project configuration
        self.current_file = None
        self.is_modified = False
        self.build_output_dir = pathlib.Path(tempfile.gettempdir()) / "vb2arduino_build"
        self.selected_libraries = []  # Track selected libraries
        
        # Board to platform mapping
        self.board_platforms = {
            # ESP32 boards
            "esp32-s3-devkitm-1": "espressif32",
            "esp32-s3-devkitc-1": "espressif32",
            "esp32dev": "espressif32",
            "esp32-c3-devkitm-1": "espressif32",
            "esp32-s2-saola-1": "espressif32",
            "lolin_d32": "espressif32",
            # Arduino AVR boards
            "uno": "atmelavr",
            "mega2560": "atmelavr",
            "megaatmega2560": "atmelavr",
            "nano": "atmelavr",
            "nanoatmega328": "atmelavr",
            "leonardo": "atmelavr",
            "micro": "atmelavr",
            "pro16MHzatmega328": "atmelavr",
            # Arduino ARM boards
            "nano_33_iot": "atmelsam",
            "mkr1000": "atmelsam",
            "mkrwifi1010": "atmelsam",
            "zero": "atmelsam",
            "due": "atmelsam",
            # RP2040 boards
            "pico": "raspberrypi",
            "nanorp2040connect": "raspberrypi",
        }
        
        self.init_ui()
        self.update_title()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("VB2Arduino IDE")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create central widget with splitter
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Vertical splitter for editor area and serial monitor
        v_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Horizontal splitter for editor and tree view
        h_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Code editor with procedure dropdown
        self.editor_widget = CodeEditorWidget(self.settings)
        self.editor = self.editor_widget.editor  # Keep reference for backward compatibility
        self.editor.textChanged.connect(self.on_text_changed)
        
        # Timer for updating tree view (debounced)
        self.tree_update_timer = QTimer()
        self.tree_update_timer.setSingleShot(True)
        self.tree_update_timer.timeout.connect(self.update_tree_view)
        self.editor.textChanged.connect(lambda: self.tree_update_timer.start(500))
        
        h_splitter.addWidget(self.editor_widget)
        
        # Project tree view
        self.tree_view = ProjectTreeView()
        self.tree_view.item_clicked.connect(self.goto_line)
        h_splitter.addWidget(self.tree_view)
        
        # Set initial sizes (editor larger than tree)
        h_splitter.setSizes([700, 250])
        
        v_splitter.addWidget(h_splitter)
        
        # Serial monitor
        self.serial_monitor = SerialMonitor()
        v_splitter.addWidget(self.serial_monitor)
        
        # Set initial sizes (editor area larger)
        v_splitter.setSizes([600, 200])
        
        layout.addWidget(v_splitter)
        
        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")
        
        # Create menu bar
        self.create_menus()
        
        # Load default template
        self.load_template()
        
    def create_toolbar(self):
        """Create toolbar with buttons."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Track auto-detected marks to revert labels on manual change
        self._auto_board_mark_idx = None
        self._auto_port_mark_idx = None
        self._board_original_text = {}
        self._port_original_text = {}
        
        # Compile button (was Verify)
        verify_btn = QPushButton("✓ Compile")
        verify_btn.setToolTip("Compile (Ctrl+R)")
        verify_btn.clicked.connect(self.verify_code)
        toolbar.addWidget(verify_btn)
        
        # Upload button  
        upload_btn = QPushButton("→ Upload")
        upload_btn.setToolTip("Compile and Upload (Ctrl+U)")
        upload_btn.clicked.connect(self.upload_code)
        toolbar.addWidget(upload_btn)
        
        toolbar.addSeparator()
        
        # Board selection
        toolbar.addWidget(QLabel("Board: "))
        self.board_combo = QComboBox()
        
        # Organize boards by category
        boards = [
            ("ESP32", [
                ("ESP32-S3 DevKitM-1", "esp32-s3-devkitm-1"),
                ("ESP32-S3 DevKitC-1", "esp32-s3-devkitc-1"),
                ("ESP32-S3-LCD-1.47", "esp32-s3-devkitm-1"),
                ("ESP32 Dev Module", "esp32dev"),
                ("ESP32-C3 DevKitM-1", "esp32-c3-devkitm-1"),
                ("ESP32-S2 Saola-1", "esp32-s2-saola-1"),
                ("WEMOS LOLIN D32", "lolin_d32"),
            ]),
            ("Arduino AVR", [
                ("Arduino Uno", "uno"),
                ("Arduino Mega 2560", "megaatmega2560"),
                ("Arduino Nano", "nanoatmega328"),
                ("Arduino Leonardo", "leonardo"),
                ("Arduino Micro", "micro"),
                ("Arduino Pro Mini 5V 16MHz", "pro16MHzatmega328"),
            ]),
            ("Arduino ARM", [
                ("Arduino Nano 33 IoT", "nano_33_iot"),
                ("Arduino MKR1000", "mkr1000"),
                ("Arduino MKR WiFi 1010", "mkrwifi1010"),
                ("Arduino Zero", "zero"),
                ("Arduino Due", "due"),
            ]),
            ("Raspberry Pi", [
                ("Raspberry Pi Pico", "pico"),
                ("Arduino Nano RP2040 Connect", "nanorp2040connect"),
            ]),
        ]
        
        for category, board_list in boards:
            self.board_combo.addItem(f"--- {category} ---", None)
            for display_name, board_id in board_list:
                self.board_combo.addItem(display_name, board_id)
        
        self.board_combo.setMinimumWidth(250)
        toolbar.addWidget(self.board_combo)
        # Clear [Auto] badge when user changes selection
        self.board_combo.currentIndexChanged.connect(self._clear_board_auto_mark)
        # Load pin template when board changes
        self.board_combo.currentIndexChanged.connect(self._on_board_changed)
        # Persistent chip indicating auto-detection
        self.board_auto_chip = QLabel("Auto")
        self.board_auto_chip.setVisible(False)
        self.board_auto_chip.setStyleSheet(
            "QLabel{background:#E6F4EA;color:#137333;border-radius:4px;"
            "padding:1px 4px;font-size:10px;border:1px solid #CDE9D6;}"
        )
        toolbar.addWidget(self.board_auto_chip)
        
        toolbar.addSeparator()
        
        # Port selection
        toolbar.addWidget(QLabel("Port: "))
        self.port_combo = QComboBox()
        self.refresh_ports()
        self.port_combo.setMinimumWidth(150)
        toolbar.addWidget(self.port_combo)
        # Clear [Auto] badge when user changes selection and update serial monitor
        self.port_combo.currentIndexChanged.connect(self._clear_port_auto_mark)
        self.port_combo.currentIndexChanged.connect(self._on_port_changed)
        # Persistent chip indicating auto-detection
        self.port_auto_chip = QLabel("Auto")
        self.port_auto_chip.setVisible(False)
        self.port_auto_chip.setStyleSheet(
            "QLabel{background:#E6F4EA;color:#137333;border-radius:4px;"
            "padding:1px 4px;font-size:10px;border:1px solid #CDE9D6;}"
        )
        toolbar.addWidget(self.port_auto_chip)
        
        # Refresh ports button
        refresh_btn = QPushButton("↻")
        refresh_btn.setToolTip("Refresh ports")
        refresh_btn.clicked.connect(self.refresh_ports)
        toolbar.addWidget(refresh_btn)
        
        toolbar.addSeparator()
        
        # Serial Monitor toggle
        serial_btn = QPushButton("Serial Monitor")
        serial_btn.setCheckable(True)
        serial_btn.setChecked(True)
        serial_btn.toggled.connect(self.toggle_serial_monitor)
        toolbar.addWidget(serial_btn)

        # After toolbar setup, try auto-selecting detected board/port
        self.auto_select_defaults()
        
    def create_menus(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)
        
        # Sketch menu
        sketch_menu = menubar.addMenu("&Sketch")
        
        verify_action = QAction("&Compile", self)
        verify_action.setShortcut("Ctrl+R")
        verify_action.triggered.connect(self.verify_code)
        sketch_menu.addAction(verify_action)
        
        upload_action = QAction("&Upload", self)
        upload_action.setShortcut("Ctrl+U")
        upload_action.triggered.connect(self.upload_code)
        sketch_menu.addAction(upload_action)
        
        sketch_menu.addSeparator()
        
        libraries_action = QAction("Include &Library...", self)
        libraries_action.triggered.connect(self.show_libraries)
        sketch_menu.addAction(libraries_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        serial_action = QAction("Serial &Monitor", self)
        serial_action.setShortcut("Ctrl+Shift+M")
        serial_action.triggered.connect(lambda: self.serial_monitor.setVisible(not self.serial_monitor.isVisible()))
        tools_menu.addAction(serial_action)
        
        libraries_action = QAction("Manage &Libraries...", self)
        libraries_action.setShortcut("Ctrl+Shift+L")
        libraries_action.triggered.connect(self.show_libraries_manager)
        tools_menu.addAction(libraries_action)
        
        pins_action = QAction("Configure &Pins...", self)
        pins_action.setShortcut("Ctrl+Shift+P")
        pins_action.triggered.connect(self.show_pin_configuration)
        tools_menu.addAction(pins_action)
        
        tools_menu.addSeparator()
        
        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About VB2Arduino", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def load_template(self):
        """Load default VB template."""
        template = """' VB2Arduino Sketch
Const LED = 2

Sub Setup()
    PinMode LED, OUTPUT
End Sub

Sub Loop()
    DigitalWrite LED, HIGH
    Delay 1000
    DigitalWrite LED, LOW
    Delay 1000
End Sub
"""
        self.editor_widget.setPlainText(template)
        self.is_modified = False
        self.update_title()
        self.update_tree_view()
        
    def new_file(self):
        """Create new file."""
        if self.check_save_changes():
            self.current_file = None
            self.load_template()
            
    def open_file(self):
        """Open existing file."""
        if not self.check_save_changes():
            return
            
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open VB File",
            "",
            "VB Files (*.vb);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.editor_widget.setPlainText(f.read())
                self.current_file = pathlib.Path(filename)
                self.is_modified = False
                self.update_title()
                self.update_tree_view()
                self.status.showMessage(f"Opened: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{e}")
                
    def save_file(self):
        """Save current file."""
        if self.current_file is None:
            return self.save_file_as()
        return self._save_to_file(self.current_file)
        
    def save_file_as(self):
        """Save file with new name."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save VB File",
            "",
            "VB Files (*.vb);;All Files (*)"
        )
        
        if filename:
            path = pathlib.Path(filename)
            if path.suffix == "":
                path = path.with_suffix(".vb")
            return self._save_to_file(path)
        return False
        
    def _save_to_file(self, path: pathlib.Path):
        """Internal save helper."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.current_file = path
            self.is_modified = False
            self.update_title()
            self.status.showMessage(f"Saved: {path}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")
            return False
            
    def check_platformio(self):
        """Check if PlatformIO is installed."""
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
            
    def verify_code(self):
        """Compile/verify code."""
        # Check if PlatformIO is installed
        if not self.check_platformio():
            QMessageBox.critical(
                self,
                "PlatformIO Not Found",
                "PlatformIO CLI is not installed or not in PATH.\n\n"
                "Please install it using:\n"
                "  pip install platformio\n\n"
                "Or visit: https://platformio.org/install/cli"
            )
            self.status.showMessage("✗ PlatformIO not found")
            return
            
        self.status.showMessage("Compiling...")
        progress = QProgressDialog("Compiling...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setCancelButton(None)
        progress.setWindowTitle("Compile")
        progress.show()
        QApplication.processEvents()
        
        try:
            # Transpile VB to C++
            vb_code = self.editor.toPlainText()
            cpp_code = transpile_string(vb_code)
            
            # Create PlatformIO project structure
            self.build_output_dir.mkdir(parents=True, exist_ok=True)
            src_dir = self.build_output_dir / "src"
            src_dir.mkdir(exist_ok=True)
            
            # Write main.cpp to src directory
            cpp_file = src_dir / "main.cpp"
            cpp_file.write_text(cpp_code, encoding='utf-8')
            
            # Get board ID and platform (try auto-detect if none selected)
            board = self.board_combo.currentData()
            if not board:
                self.auto_select_defaults()
                board = self.board_combo.currentData()
            if not board:  # Still not selected (likely category header)
                QMessageBox.warning(self, "No Board", "Please select a board, not a category header.")
                self.status.showMessage("✗ No board selected")
                return
            
            platform = self.board_platforms.get(board, "atmelavr")
            
            # Create platformio.ini
            ini_file = self.build_output_dir / "platformio.ini"
            ini_file.write_text(self._platformio_ini_content(board, platform), encoding='utf-8')
            
            # Run PlatformIO compile
            result = subprocess.run(
                ["pio", "run", "--project-dir", str(self.build_output_dir), "--environment", board],
                capture_output=True,
                text=True
            )

            # Persist logs for troubleshooting
            try:
                (self.build_output_dir / "compile_stdout.txt").write_text(result.stdout or "", encoding='utf-8')
                (self.build_output_dir / "compile_stderr.txt").write_text(result.stderr or "", encoding='utf-8')
            except Exception:
                pass
            
            if result.returncode == 0:
                self.status.showMessage("✓ Compilation successful")
                if self.settings.get("editor", "show_compile_success_popup", True):
                    QMessageBox.information(self, "Success", "Code compiled successfully!")
            else:
                self.status.showMessage("✗ Compilation failed")
                # Parse errors, map to VB lines, and show clickable list
                vb_map = self._build_vb_line_map(cpp_file)
                errors = self._parse_compile_errors(result.stderr, cpp_file.name)
                if errors:
                    if self.settings.get("editor", "show_compile_failure_popup", True):
                        self._show_compile_errors(errors, vb_map)
                    else:
                        # Show concise status only; no popup
                        self.status.showMessage("✗ Compilation failed - see status output", 5000)
                else:
                    if self.settings.get("editor", "show_compile_failure_popup", True):
                        QMessageBox.warning(self, "Compilation Error", 
                            f"Compilation failed:\n\n{result.stderr[:500]}")
                    else:
                        self.status.showMessage("✗ Compilation failed", 5000)
                    
        except Exception as e:
            self.status.showMessage("✗ Error")
            QMessageBox.critical(self, "Error", f"Compilation error:\n{e}")
        finally:
            progress.close()
            
    def upload_code(self):
        """Compile and upload code."""
        # Check if PlatformIO is installed
        if not self.check_platformio():
            QMessageBox.critical(
                self,
                "PlatformIO Not Found",
                "PlatformIO CLI is not installed or not in PATH.\n\n"
                "Please install it using:\n"
                "  pip install platformio\n\n"
                "Or visit: https://platformio.org/install/cli"
            )
            self.status.showMessage("✗ PlatformIO not found")
            return
            
        port = self.port_combo.currentText()
        if not port:
            # Try to auto-detect
            self.refresh_ports()
            self.auto_select_defaults()
            port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, "No Port", "Please select a serial port first.")
            return
            
        self.status.showMessage("Uploading...")
        progress = QProgressDialog("Compiling & Uploading...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setCancelButton(None)
        progress.setWindowTitle("Upload")
        progress.show()
        QApplication.processEvents()
        
        try:
            # Transpile VB to C++
            vb_code = self.editor.toPlainText()
            cpp_code = transpile_string(vb_code)
            
            # Create PlatformIO project structure
            self.build_output_dir.mkdir(parents=True, exist_ok=True)
            src_dir = self.build_output_dir / "src"
            src_dir.mkdir(exist_ok=True)
            
            # Write main.cpp to src directory
            cpp_file = src_dir / "main.cpp"
            cpp_file.write_text(cpp_code, encoding='utf-8')
            
            # Get board ID and platform (try auto-detect if none selected)
            board = self.board_combo.currentData()
            if not board:
                self.auto_select_defaults()
                board = self.board_combo.currentData()
            if not board:  # Still not selected (likely category header)
                QMessageBox.warning(self, "No Board", "Please select a board, not a category header.")
                self.status.showMessage("✗ No board selected")
                return
            
            platform = self.board_platforms.get(board, "atmelavr")
            
            # Create platformio.ini
            ini_file = self.build_output_dir / "platformio.ini"
            ini_file.write_text(self._platformio_ini_content(board, platform), encoding='utf-8')
            
            # Run PlatformIO upload
            result = subprocess.run(
                ["pio", "run", "--project-dir", str(self.build_output_dir), 
                 "--environment", board, "--target", "upload", "--upload-port", port],
                capture_output=True,
                text=True
            )

            # Persist logs for troubleshooting
            try:
                (self.build_output_dir / "upload_stdout.txt").write_text(result.stdout or "", encoding='utf-8')
                (self.build_output_dir / "upload_stderr.txt").write_text(result.stderr or "", encoding='utf-8')
            except Exception:
                pass
            
            if result.returncode == 0:
                self.status.showMessage("✓ Upload successful")
                if self.settings.get("editor", "show_upload_success_popup", True):
                    QMessageBox.information(self, "Success", "Code uploaded successfully!")
            else:
                self.status.showMessage("✗ Upload failed")
                # On compile/upload error, parse and present clickable errors
                vb_map = self._build_vb_line_map(cpp_file)
                errors = self._parse_compile_errors(result.stderr, cpp_file.name)
                if errors:
                    if self.settings.get("editor", "show_upload_failure_popup", True):
                        self._show_compile_errors(errors, vb_map)
                    else:
                        self.status.showMessage("✗ Upload failed - see status output", 5000)
                else:
                    if self.settings.get("editor", "show_upload_failure_popup", True):
                        QMessageBox.warning(self, "Upload Error",
                            f"Upload failed:\n\n{result.stderr[:500]}")
                    else:
                        self.status.showMessage("✗ Upload failed", 5000)
                    
        except Exception as e:
            self.status.showMessage("✗ Error")
            QMessageBox.critical(self, "Error", f"Upload error:\n{e}")
        finally:
            progress.close()
            
    def refresh_ports(self):
        """Refresh available serial ports."""
        ports = get_available_ports()
        self.port_combo.clear()
        self.port_combo.addItems(ports)
        # Auto-select port if nothing chosen yet
        if not self.port_combo.currentText():
            self.auto_select_defaults()
        
    def _on_port_changed(self):
        """Handle port selection change - update serial monitor."""
        port = self.port_combo.currentText()
        if port:
            self.serial_monitor.set_port(port)
        else:
            self.serial_monitor.set_port(None)
        
    def toggle_serial_monitor(self, checked):
        """Toggle serial monitor visibility."""
        self.serial_monitor.setVisible(checked)
        
    def on_text_changed(self):
        """Handle text change in editor."""
        self.is_modified = True
        self.update_title()
        
    def update_tree_view(self):
        """Update the project tree view with current code structure."""
        code = self.editor.toPlainText()
        self.tree_view.update_from_code(code)
        
    def goto_line(self, line_number):
        """Navigate to a specific line in the editor."""
        if line_number > 0:
            cursor = self.editor.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.MoveAnchor, line_number - 1)
            self.editor.setTextCursor(cursor)
            self.editor.centerCursor()
            self.editor.setFocus()
            # Temporary highlight to make the target line obvious
            try:
                duration = int(self.settings.get("editor", "jump_highlight_duration_ms", 3000))
                self.editor.highlight_line(line_number, duration)
            except Exception:
                pass
        
    def update_title(self):
        """Update window title."""
        title = "VB2Arduino IDE"
        if self.current_file:
            title += f" - {self.current_file.name}"
        else:
            title += " - Untitled"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)

    def auto_select_defaults(self):
        """Auto-detect board and port via PlatformIO and set defaults."""
        try:
            board, port = auto_detect_board_and_port()
        except Exception:
            board, port = (None, None)

        # Set port if detected and available
        if port:
            idx = self.port_combo.findText(port)
            if idx != -1 and not self.port_combo.currentText():
                self.port_combo.setCurrentIndex(idx)
                # Set a helpful tooltip and extend message duration
                self.port_combo.setToolTip(f"Auto-detected: {port}")
                self.status.showMessage(f"Detected port: {port}", 8000)
                # Add [Auto] badge to the selected item
                try:
                    original = self.port_combo.itemText(idx)
                    self._port_original_text[idx] = original
                    if "[Auto]" not in original:
                        self.port_combo.setItemText(idx, f"{original} [Auto]")
                    self._auto_port_mark_idx = idx
                except Exception:
                    pass
                # Show persistent auto chip
                self.port_auto_chip.setVisible(True)

        # Set board if detected and no valid board selected yet
        current_board = self.board_combo.currentData()
        if board and (current_board is None):
            for i in range(self.board_combo.count()):
                if self.board_combo.itemData(i) == board:
                    self.board_combo.setCurrentIndex(i)
                    # Tooltip + longer message for clarity
                    name = self.board_combo.itemText(i)
                    self.board_combo.setToolTip(f"Auto-detected: {name} ({board})")
                    self.status.showMessage(f"Detected board: {board}", 8000)
                    # Add [Auto] badge to the selected item
                    try:
                        original = self.board_combo.itemText(i)
                        self._board_original_text[i] = original
                        if "[Auto]" not in original:
                            self.board_combo.setItemText(i, f"{original} [Auto]")
                        self._auto_board_mark_idx = i
                    except Exception:
                        pass
                    # Show persistent auto chip
                    self.board_auto_chip.setVisible(True)
                    break

    def _clear_board_auto_mark(self, idx: int):
        """Remove [Auto] badge from board item when user manually changes selection."""
        try:
            if self._auto_board_mark_idx is not None:
                original = self._board_original_text.get(self._auto_board_mark_idx)
                if original is not None and self._auto_board_mark_idx < self.board_combo.count():
                    self.board_combo.setItemText(self._auto_board_mark_idx, original)
            self._auto_board_mark_idx = None
            self.board_auto_chip.setVisible(False)
        except Exception:
            pass

    def _clear_port_auto_mark(self, idx: int):
        """Remove [Auto] badge from port item when user manually changes selection."""
        try:
            if self._auto_port_mark_idx is not None:
                original = self._port_original_text.get(self._auto_port_mark_idx)
                if original is not None and self._auto_port_mark_idx < self.port_combo.count():
                    self.port_combo.setItemText(self._auto_port_mark_idx, original)
            self._auto_port_mark_idx = None
            self.port_auto_chip.setVisible(False)
        except Exception:
            pass

    def _platformio_ini_content(self, board: str, platform: str) -> str:
        """Generate platformio.ini content with libraries and build flags from project config."""
        lines = [
            f"[env:{board}]",
            f"platform = {platform}",
            f"board = {board}",
            "framework = arduino",
            "monitor_speed = 115200",
        ]
        
        # Add libraries from project config
        libraries = self.project_config.get_libraries()
        if libraries:
            lib_deps = ", ".join(libraries)
            lines.append(f"lib_deps = {lib_deps}")
        
        # Build flags: merge board-required flags with user-defined flags
        board_flags: list[str] = []
        user_flags = self.project_config.get_build_flags() or []
        
        # ESP32-S3 special handling
        if "s3" in board:
            # Enable USB CDC mode for serial communication on ESP32-S3
            # CDC (Communications Device Class) allows native USB serial without UART-to-USB converter
            board_flags.extend([
                "-DARDUINO_USB_MODE=1",           # Enable native USB
                "-DARDUINO_USB_CDC_ON_BOOT=1"     # Use CDC for Serial (Serial goes to USB, not UART)
            ])
            lines.append("upload_speed = 921600")  # High speed USB upload
        
        merged_flags = board_flags + user_flags
        if merged_flags:
            lines.append("build_flags = " + " ".join(merged_flags))
        
        return "\n".join(lines) + "\n"

    def _build_vb_line_map(self, cpp_path: pathlib.Path) -> dict[int, int]:
        """Build a map of C++ line -> VB line by scanning marker comments.

        We emit lines like: // __VB_LINE__:N before each generated statement.
        We map each subsequent C++ line to the most recent VB marker.
        """
        try:
            lines = cpp_path.read_text(encoding='utf-8').splitlines()
        except Exception:
            return {}
        vb_map: dict[int, int] = {}
        current_vb = None
        for idx, l in enumerate(lines, start=1):
            if l.strip().startswith("// __VB_LINE__:"):
                try:
                    current_vb = int(l.strip().split(":", 1)[1])
                except Exception:
                    current_vb = current_vb
            vb_map[idx] = current_vb if current_vb is not None else 1
        return vb_map

    def _parse_compile_errors(self, stderr: str, cpp_name: str) -> list[tuple[int, str, str]]:
        """Parse compiler stderr to extract (cpp_line, level, message) for main file.

        Matches lines like: src/main.cpp:123:45: error: message
        Returns a list of tuples.
        """
        errors: list[tuple[int, str, str]] = []
        for line in stderr.splitlines():
            # General gcc/clang style: <file>:<line>:<col>: <level>: <message>
            m = re.match(r"(.+?):(\d+):\d+:\s+(fatal error|error|warning):\s+(.*)", line)
            if m:
                file_path, line_no, level, msg = m.groups()
                if file_path.endswith(cpp_name):
                    try:
                        errors.append((int(line_no), level, msg))
                    except ValueError:
                        pass
        return errors

    def _show_compile_errors(self, errors: list[tuple[int, str, str]], vb_map: dict[int, int]):
        """Show a clickable list of compile errors mapped to VB lines."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Compilation Errors")
        layout = QVBoxLayout(dlg)
        lst = QListWidget(dlg)
        layout.addWidget(lst)
        # Populate list with VB line numbers and messages
        for cpp_line, level, msg in errors:
            vb_line = vb_map.get(cpp_line, 1)
            item = QListWidgetItem(f"VB line {vb_line}: {level} - {msg}")
            # store VB line and message in item data
            item.setData(Qt.ItemDataRole.UserRole, (vb_line, level, msg))
            lst.addItem(item)

        def on_item_activated(item: QListWidgetItem):
            data = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(data, tuple) and len(data) == 3:
                vb_line, level, msg = data
                if isinstance(vb_line, int):
                    self.goto_line(vb_line)
                    # Update status bar with concise hint
                    self.status.showMessage(f"{level.capitalize()} at VB line {vb_line}: {msg}", 5000)
        
        # Context menu for copying error text
        def on_context_menu(pos):
            item = lst.itemAt(pos)
            if item:
                menu = QMenu(lst)
                copy_action = menu.addAction("Copy Error")
                copy_all_action = menu.addAction("Copy All Errors")
                
                def copy_error():
                    clipboard = QApplication.clipboard()
                    clipboard.setText(item.text())
                    self.status.showMessage("Error copied to clipboard", 3000)
                
                def copy_all_errors():
                    all_text = "\n".join([lst.item(i).text() for i in range(lst.count())])
                    clipboard = QApplication.clipboard()
                    clipboard.setText(all_text)
                    self.status.showMessage(f"{lst.count()} errors copied to clipboard", 3000)
                
                copy_action.triggered.connect(copy_error)
                copy_all_action.triggered.connect(copy_all_errors)
                menu.exec(lst.mapToGlobal(pos))
        
        lst.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        lst.customContextMenuRequested.connect(on_context_menu)
        lst.itemActivated.connect(on_item_activated)
        lst.itemDoubleClicked.connect(on_item_activated)
        dlg.resize(800, 400)
        dlg.show()
        
    def check_save_changes(self):
        """Check if unsaved changes exist and prompt user."""
        if not self.is_modified:
            return True
            
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            "Do you want to save your changes?",
            QMessageBox.StandardButton.Save | 
            QMessageBox.StandardButton.Discard | 
            QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False
            
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About VB2Arduino IDE",
            "<h2>VB2Arduino IDE</h2>"
            "<p>Version 0.1.0</p>"
            "<p>A Visual Basic 6-style IDE for Arduino development.</p>"
            "<p>Write VB6-like code that transpiles to Arduino C++.</p>"
            "<p>Licensed under GPL-3.0-or-later</p>"
        )
        
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Apply new settings to editor
            self.editor.apply_settings(self.settings)
            self.status.showMessage("Settings applied", 2000)
    
    def show_libraries_manager(self):
        """Show libraries manager dialog."""
        # Get currently selected board
        board = self.board_combo.currentData()
        dialog = ManageLibrariesDialog(self.project_config, selected_board=board, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.status.showMessage("Libraries updated", 2000)
    
    def show_pin_configuration(self):
        """Show pin configuration dialog."""
        board = self.board_combo.currentData()
        dialog = PinConfigurationDialog(self.project_config, board_id=board, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.status.showMessage("Pin configuration updated", 2000)
    
    def _on_board_changed(self):
        """Handle board selection change - auto-load pin template."""
        board = self.board_combo.currentData()
        if board:
            # If UI selection indicates LCD 1.47 variant, load its template
            display_name = self.board_combo.currentText() or ""
            if ("LCD-1.47" in display_name) or ("LCS-1.47" in display_name):
                alias_tpl = get_template_for_board("esp32-s3-lcd-1.47")
                if alias_tpl:
                    self.project_config.load_template(alias_tpl)
                    return
            # Otherwise load the standard template for the board id
            template = get_template_for_board(board)
            if template:
                self.project_config.load_template(template)
                # Silently load template without showing dialog
                # User can still customize via Configure Pins menu
    
    def show_libraries(self):
        """Show library selection dialog."""
        dialog = LibrariesDialog(self.selected_libraries, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_libraries = dialog.get_selected_libraries()
            self.inject_library_includes()
            self.status.showMessage(f"Selected {len(self.selected_libraries)} libraries", 2000)
    
    def inject_library_includes(self):
        """Inject #Include statements for selected libraries at the top of the code."""
        if not self.selected_libraries:
            return
        
        current_code = self.editor.toPlainText()
        lines = current_code.split('\n')
        
        # Find existing #Include lines
        include_lines = []
        code_start = 0
        for i, line in enumerate(lines):
            if line.strip().upper().startswith('#INCLUDE'):
                include_lines.append(i)
            elif line.strip() and not line.strip().startswith("'"):
                code_start = i
                break
        
        # Remove old includes
        for i in reversed(include_lines):
            lines.pop(i)
        
        # Add new includes at the top
        new_includes = [f"#Include <{lib}>" for lib in self.selected_libraries]
        
        # Insert after any initial comments
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("'") or not line.strip():
                insert_pos = i + 1
            else:
                break
        
        # Insert includes
        for include in reversed(new_includes):
            lines.insert(insert_pos, include)
        
        # Add blank line after includes if needed
        if new_includes and lines[insert_pos + len(new_includes)].strip():
            lines.insert(insert_pos + len(new_includes), "")
        
        # Update editor
        self.editor_widget.setPlainText('\n'.join(lines))
        self.is_modified = True
        self.update_title()
        
    def closeEvent(self, event):
        """Handle window close event."""
        if self.check_save_changes():
            event.accept()
        else:
            event.ignore()
