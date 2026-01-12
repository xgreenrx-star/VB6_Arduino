
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QToolBar, QPushButton, QComboBox, QLabel, QMessageBox, QFileDialog,
    QStatusBar, QDialog, QProgressDialog, QListWidget, QListWidgetItem, QMenu, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QAction, QClipboard
import sys
import pathlib
import subprocess
import tempfile
import re

from vb2arduino.ide.pin_diagram_overlay import PinDiagramOverlay


class ClickableLabel(QLabel):
    """A QLabel that emits a clicked() signal on mouse release and can flash."""
    clicked = pyqtSignal()

    def mouseReleaseEvent(self, event):
        try:
            self.clicked.emit()
        except Exception:
            pass
        super().mouseReleaseEvent(event)

    def flash(self, color: str = "#FFD54F", duration_ms: int = 200):
        """Animate opacity briefly for a click effect using QGraphicsOpacityEffect.

        Animates opacity from 1.0 -> 0.4 -> 1.0 over the duration and restores the previous
        graphics effect (if any).
        """
        try:
            from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
            from PyQt6.QtWidgets import QGraphicsOpacityEffect
            # Save existing effect
            prev_effect = self.graphicsEffect()
            # Apply opacity effect
            effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(effect)
            # Animation: fade to 0.4 then back to 1.0
            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(max(40, int(duration_ms)))
            # Use smoother cubic easing for a nicer feel
            anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            # Key values: 0.0 -> middle -> end
            anim.setKeyValueAt(0.0, 1.0)
            anim.setKeyValueAt(0.5, 0.4)
            anim.setKeyValueAt(1.0, 1.0)
            # Start animation
            anim.start()
            # Restore previous effect after animation completes
            def _restore():
                try:
                    # stop and delete animation
                    try:
                        anim.stop()
                    except Exception:
                        pass
                    self.setGraphicsEffect(prev_effect)
                except Exception:
                    self.setGraphicsEffect(None)
            # Schedule restore after duration + small buffer
            QTimer.singleShot(max(40, int(duration_ms)) + 20, _restore)
        except Exception:
            # fallback: revert to style flash if animation not available
            try:
                prev = self.styleSheet() or ""
                self.setStyleSheet(f"background-color: {color}; padding: 2px;")
                from PyQt6.QtCore import QTimer
                def _restore2():
                    try:
                        self.setStyleSheet(prev)
                    except Exception:
                        self.setStyleSheet("")
                QTimer.singleShot(max(10, int(duration_ms)), _restore2)
            except Exception:
                pass

from vb2arduino.ide.editor import CodeEditorWidget
from vb2arduino.ide.serial_monitor import SerialMonitor
from vb2arduino.ide.serial_plotter import SerialPlotter
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
from vb2arduino.ide.programmers_reference_dialog import ProgrammersReferenceDialog
from vb2arduino.ide.shortcuts_help_dialog import ShortcutsHelpDialog
from vb2arduino.ide.find_replace_dialog import FindReplaceDialog
from vb2arduino import transpile_string

"""Main window for Asic (Arduino Basic) IDE.

This IDE supports Asic (Arduino Basic) language, macro commands (e.g., {{KEY:...}}, {{DELAY:...}}), and full PlatformIO integration for Arduino/ESP32 development.
"""


class MainWindow(QMainWindow):
    def show_shortcuts_help(self):
        dlg = ShortcutsHelpDialog(self)
        dlg.exec()

    def show_pin_diagram_overlay(self):
        """Show or raise the pin diagram overlay window."""
        board = self.board_combo.currentData()
        if not self.pin_diagram_overlay:
            self.pin_diagram_overlay = PinDiagramOverlay(self, board=board)
        else:
            self.pin_diagram_overlay.set_board(board)
        self.pin_diagram_overlay.show()
        self.pin_diagram_overlay.raise_()

    def _connect_editor_signals(self):
        editor = self.get_current_editor()
        if editor:
            try:
                editor.cursorPositionChanged.disconnect(self.update_status_bar)
            except Exception:
                pass
            editor.cursorPositionChanged.connect(self.update_status_bar)
            self.update_status_bar()

    def update_status_bar(self):
        # Update line/col
        editor = self.get_current_editor()
        if editor:
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.positionInBlock() + 1
            self.status_linecol.setText(f"Ln {line}, Col {col}")
        else:
            self.status_linecol.setText("")
        # Encoding (fixed for now)
        self.status_encoding.setText("UTF-8")
        # Board/port
        board = self.board_combo.currentText() if hasattr(self, 'board_combo') else ""
        port = self.port_combo.currentText() if hasattr(self, 'port_combo') else ""
        self.status_board.setText(f"Board: {board}" if board else "")
        self.status_port.setText(f"Port: {port}" if port else "")

    def show_serial_plotter(self):
        if hasattr(self, 'serial_monitor') and self.serial_monitor:
            self.serial_monitor.show_plotter()
        else:
            # fallback: create a standalone plotter
            if not hasattr(self, '_standalone_plotter'):
                self._standalone_plotter = SerialPlotter(self)
            self._standalone_plotter.show()

    def apply_settings(self):
        """Apply settings after dialog is accepted (auto-save, font, etc)."""
        self.auto_save_enabled = self.settings.get("editor", "auto_save_enabled", False)
        self.auto_save_interval = self.settings.get("editor", "auto_save_interval", 30)
        if self.auto_save_enabled:
            self.auto_save_timer.start(self.auto_save_interval * 1000)
        else:
            self.auto_save_timer.stop()

    def _auto_save_tick(self):
        editor = self.get_current_editor()
        if not editor or not editor.is_modified():
            return
        # Only save if file path is known
        if self.current_file:
            self._save_to_file(self.current_file)
            self.status.showMessage(f"[Auto-saved] {self.current_file}", 2000)
    def get_current_editor(self):
        """Return the current CodeEditorWidget in the active tab, or None."""
        if hasattr(self, 'tab_widget') and self.tab_widget.count() > 0:
            widget = self.tab_widget.currentWidget()
            # Check if widget is a CodeEditorWidget
            if isinstance(widget, CodeEditorWidget):
                return widget.editor
        return None
    def __init__(self):
        self.pin_diagram_overlay = None
        super().__init__()
        self.settings = Settings()
        self.project_config = ProjectConfig()  # Load project configuration
        self.current_file = None
        self.is_modified = False
        self.build_output_dir = pathlib.Path(tempfile.gettempdir()) / "asic_build"
        self.selected_libraries = []  # Track selected libraries
        self.recent_files = self.settings.get("editor", "recent_files", [])
        self.max_recent_files = 10
        self.find_dialog = None
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
        # Auto-save
        self.auto_save_enabled = self.settings.get("editor", "auto_save_enabled", False)
        self.auto_save_interval = self.settings.get("editor", "auto_save_interval", 30)  # seconds
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self._auto_save_tick)
        if self.auto_save_enabled:
            self.auto_save_timer.start(self.auto_save_interval * 1000)
        self.init_ui()

    def init_ui(self):
        # Initialize UI elements
        # Status bar (initialize first)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")
        # Add status widgets
        self.status_linecol = QLabel("Ln 1, Col 1")
        self.status_encoding = QLabel("UTF-8")
        self.status_board = QLabel("")
        self.status_port = QLabel("")
        # Problems status indicator (shows "Problem X/Y")
        self.status_problems = ClickableLabel("")
        self.status_problems.setToolTip("Click to open Problems")
        # Accessibility metadata
        self.status_problems.setAccessibleName("Problems Status")
        self.status_problems.setAccessibleDescription("Shows the current problem index and count; click to open Problems panel")
        # Connection to toggle will be bound after menus are created (toggle_problems_action exists then)
        self.status.addPermanentWidget(self.status_linecol)
        self.status.addPermanentWidget(self.status_encoding)
        self.status.addPermanentWidget(self.status_board)
        self.status.addPermanentWidget(self.status_port)
        self.status.addPermanentWidget(self.status_problems)

        # Create toolbar FIRST so board_combo is available
        self.create_toolbar()
        # Create Problems panel (hidden by default)
        self.create_problems_panel()

        # Set up central widget and layout
        central = QWidget(self)
        layout = QVBoxLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)

        # Create main splitters
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Project explorer (tree view)
        self.tree_view = ProjectTreeView()
        self.tree_view.item_clicked.connect(self.goto_line)
        self.tree_view.file_clicked.connect(self.on_project_file_clicked)
        self.h_splitter.addWidget(self.tree_view)

        # Editor tabs
        from PyQt6.QtWidgets import QTabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.h_splitter.addWidget(self.tab_widget)

        # Connect editor cursor movement to status bar update
        self.tab_widget.currentChanged.connect(lambda idx: self._connect_editor_signals())

        # Add horizontal splitter (explorer/editor) to vertical splitter
        self.v_splitter.addWidget(self.h_splitter)

        # Serial monitor at the bottom
        self.serial_monitor = SerialMonitor()
        self.v_splitter.addWidget(self.serial_monitor)

        # Add main splitter to layout
        layout.addWidget(self.v_splitter)

        # Set initial sizes for splitters
        self.setMinimumSize(1000, 700)
        self.v_splitter.setSizes([600, 200])
        self.h_splitter.setSizes([220, 780])

        # Show all widgets
        self.v_splitter.show()
        self.h_splitter.show()
        self.tab_widget.show()
        self.tree_view.show()
        self.serial_monitor.show()

        # Open initial editor tab
        self.open_file_in_tab(None, title="Untitled")

        # Populate project explorer
        self.project_root = None
        self.populate_explorer()

        # Create menu bar (must be after central widget is set)
        self.create_menus()

        # Apply high-contrast theme if configured
        try:
            self.apply_high_contrast(self.settings.get("editor", "high_contrast", False))
        except Exception:
            pass
    def on_project_file_clicked(self, file_path):
        import os
        from pathlib import Path
        ext = Path(file_path).suffix.lower()
        image_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        sound_exts = {'.wav', '.mp3', '.ogg', '.flac', '.aac'}
        if ext in image_exts:
            self.open_external_editor(file_path, kind='image')
        elif ext in sound_exts:
            self.open_external_editor(file_path, kind='sound')
        else:
            self.open_file_in_tab(file_path)

    def open_external_editor(self, file_path, kind='image'):
        import subprocess, platform
        editor = None
        if kind == 'image':
            editor = getattr(self.settings, 'image_editor', None)
        elif kind == 'sound':
            editor = getattr(self.settings, 'sound_editor', None)
        if not editor:
            # Fallback: try xdg-open (Linux), start (Windows), open (macOS)
            if platform.system() == 'Windows':
                subprocess.Popen(['start', '', file_path], shell=True)
            elif platform.system() == 'Darwin':
                subprocess.Popen(['open', file_path])
            else:
                subprocess.Popen(['xdg-open', file_path])
        else:
            try:
                subprocess.Popen([editor, file_path])
            except Exception as e:
                QMessageBox.warning(self, f"Open {kind.title()} Editor", f"Failed to open {kind} editor: {e}")





    def load_file_on_startup(self, file_path):
        """Load a file when the application starts (called from command line)."""
        try:
            path = pathlib.Path(file_path).resolve()
            if path.exists() and path.is_file():
                self.open_file_in_tab(str(path), title=path.name)
                
                # Restore board and port selection for this file
                saved_board = self.project_config.get_board()
                saved_port = self.project_config.get_port()
                
                # Restore board selection
                if saved_board:
                    for i in range(self.board_combo.count()):
                        if self.board_combo.itemData(i) == saved_board:
                            self.board_combo.setCurrentIndex(i)
                            break
                
                # Restore port selection
                if saved_port:
                    for i in range(self.port_combo.count()):
                        if self.port_combo.itemText(i) == saved_port:
                            self.port_combo.setCurrentIndex(i)
                            break
            else:
                print(f"Warning: File not found: {file_path}")
        except Exception as e:
            print(f"Error loading file: {e}")

    def populate_explorer(self, root_path=None, parent_item=None, includes=None):
        """Populate the explorer tree with categorized files and folders, passing includes to highlight."""
        if root_path is None:
            if self.project_root:
                root_path = str(self.project_root)
            else:
                root_path = str(pathlib.Path.cwd())
        self.tree_view.show_project_files(root_path, includes=includes)

    # open_explorer_file removed (no longer needed)

    def open_file_in_tab(self, path, title=None):
        """Open a file in a new tab, or switch to it if already open."""
        for i in range(self.tab_widget.count()):
            tab_path = self.tab_widget.widget(i).property("file_path")
            if tab_path and path and pathlib.Path(tab_path) == pathlib.Path(path):
                self.tab_widget.setCurrentIndex(i)
                self._update_selected_libraries_from_editor(self.tab_widget.widget(i))
                return
        includes = []
        code_for_includes = None
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    code_for_includes = f.read()
            except Exception:
                code_for_includes = None
        if code_for_includes:
            include_pattern = re.compile(r'^\s*#Include\s+[<"](.+)[>"]', re.IGNORECASE | re.MULTILINE)
            includes = [m.group(1) for m in include_pattern.finditer(code_for_includes)]
        editor_widget = CodeEditorWidget(self.settings, includes=includes, include_callback=self._on_include_selected)
        editor = editor_widget.editor
        if path and code_for_includes:
            editor.setPlainText(code_for_includes)
            editor_widget.setProperty("file_path", str(path))
            tab_title = title or pathlib.Path(path).name
        else:
            tab_title = title or "Untitled"
        self.tab_widget.addTab(editor_widget, tab_title)
        self.tab_widget.setCurrentWidget(editor_widget)
        editor.textChanged.connect(self.on_text_changed)
        # Connect dirty file indicator
        editor.modified_changed.connect(lambda modified: self.on_editor_modified_changed(editor_widget, modified))
        # Connect status bar updates
        editor.cursorPositionChanged.connect(self.update_status_bar)
        self.update_status_bar()
        self._update_selected_libraries_from_editor(editor_widget)
        if path and str(path).endswith((".vb", ".bas")):
            self.current_file = pathlib.Path(path)
            self.is_modified = False
            self.update_title()
            self.update_tree_view()
            self.status.showMessage(f"Opened: {path}")
            self.set_project_root(pathlib.Path(path).parent)

    def on_tab_changed(self, index):
        widget = self.tab_widget.widget(index)
        if widget:
            self._update_selected_libraries_from_editor(widget)
            file_path = widget.property("file_path")
            if file_path:
                self.current_file = pathlib.Path(file_path)
            else:
                self.current_file = None
        self.update_title()

    def _update_selected_libraries_from_editor(self, editor_widget):
        """Update self.selected_libraries from #Include lines in the given editor widget."""
        if hasattr(editor_widget, 'editor'):
            code = editor_widget.editor.toPlainText()
            include_pattern = re.compile(r'^\s*#Include\s+[<"](.+)[>"]', re.IGNORECASE | re.MULTILINE)
            self.selected_libraries = [m.group(1) for m in include_pattern.finditer(code)]

    def _on_include_selected(self, include_name):
        # Try to resolve include path and open in new tab
        if self.project_root:
            candidate_paths = [
                self.project_root / "headers" / include_name,
                self.project_root / include_name
            ]
        else:
            candidate_paths = [
                pathlib.Path("headers") / include_name,
                pathlib.Path(include_name)
            ]
        for candidate in candidate_paths:
            if candidate.exists() and candidate.is_file():
                self.open_file_in_tab(str(candidate))
                return

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        widget.deleteLater()
        # Optionally update current_file
        if self.tab_widget.count() > 0:
            current_widget = self.tab_widget.currentWidget()
            file_path = current_widget.property("file_path")
            if file_path:
                self.current_file = pathlib.Path(file_path)
            else:
                self.current_file = None
        else:
            self.current_file = None
        self.update_title()

    def on_tab_changed(self, index):
        widget = self.tab_widget.widget(index)
        if widget:
            file_path = widget.property("file_path")
            if file_path:
                self.current_file = pathlib.Path(file_path)
                
                # Restore board and port selection for this file
                saved_board = self.project_config.get_board()
                saved_port = self.project_config.get_port()
                
                # Restore board selection
                if saved_board:
                    for i in range(self.board_combo.count()):
                        if self.board_combo.itemData(i) == saved_board:
                            self.board_combo.setCurrentIndex(i)
                            break
                
                # Restore port selection
                if saved_port:
                    for i in range(self.port_combo.count()):
                        if self.port_combo.itemText(i) == saved_port:
                            self.port_combo.setCurrentIndex(i)
                            break
            else:
                self.current_file = None
        self.update_title()

    def set_project_root(self, root_path):
        """Set the project root for the explorer and refresh it."""
        self.project_root = pathlib.Path(root_path)
        # Parse includes from the main file if possible
        includes = []
        if self.current_file and self.current_file.exists():
            try:
                with open(self.current_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                import re
                include_pattern = re.compile(r'^\s*#Include\s+[<"](.+)[>"]', re.IGNORECASE | re.MULTILINE)
                includes = [m.group(1) for m in include_pattern.finditer(code)]
            except Exception:
                pass
        self.populate_explorer(str(self.project_root), includes=includes)
        
    def create_toolbar(self):
        """Create toolbar with buttons."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        self.main_toolbar = toolbar

        # Track auto-detected marks to revert labels on manual change
        self._auto_board_mark_idx = None
        self._auto_port_mark_idx = None
        self._board_original_text = {}
        self._port_original_text = {}
        
        # Compile button (was Verify)
        self.verify_btn = QPushButton("✓ Compile")
        self.verify_btn.setToolTip("Compile (Ctrl+R)")
        self.verify_btn.setMaximumWidth(110)
        self.verify_btn.clicked.connect(self.verify_code)
        # Accessibility
        self.verify_btn.setAccessibleName("Compile Button")
        self.verify_btn.setAccessibleDescription("Compiles the current sketch (Ctrl+R)")
        toolbar.addWidget(self.verify_btn)
        
        # Upload button  
        self.upload_btn = QPushButton("→ Upload")
        self.upload_btn.setToolTip("Compile and Upload (Ctrl+U)")
        self.upload_btn.setMaximumWidth(110)
        self.upload_btn.clicked.connect(self.upload_code)
        # Accessibility
        self.upload_btn.setAccessibleName("Upload Button")
        self.upload_btn.setAccessibleDescription("Uploads the compiled sketch to the selected board (Ctrl+U)")
        toolbar.addWidget(self.upload_btn)
        
        toolbar.addSeparator()
        
        # Board selection
        toolbar.addWidget(QLabel("Board: "))
        self.board_combo = QComboBox()
        # Accessibility
        self.board_combo.setAccessibleName("Board Selector")
        self.board_combo.setAccessibleDescription("Select the target board for building and uploading")
        
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
        self.board_combo.setMinimumWidth(160)
        self.board_combo.setMaximumWidth(220)
        toolbar.addWidget(self.board_combo)
        # Clear [Auto] badge when user changes selection
        self.board_combo.currentIndexChanged.connect(self._clear_board_auto_mark)
        # Load pin template when board changes
        self.board_combo.currentIndexChanged.connect(self._on_board_changed)
        self.board_combo.currentIndexChanged.connect(self._on_board_combo_pin_diagram_update)

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
        self.port_combo.setMinimumWidth(100)
        self.port_combo.setMaximumWidth(160)
        # Accessibility
        self.port_combo.setAccessibleName("Port Selector")
        self.port_combo.setAccessibleDescription("Select the serial port for upload and monitoring")
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
        refresh_btn.setMaximumWidth(40)
        refresh_btn.clicked.connect(self.refresh_ports)
        toolbar.addWidget(refresh_btn)

        toolbar.addSeparator()

        # Serial Monitor toggle
        serial_btn = QPushButton("Serial")
        serial_btn.setCheckable(True)
        serial_btn.setChecked(True)
        serial_btn.setMaximumWidth(80)
        serial_btn.toggled.connect(self.toggle_serial_monitor)
        toolbar.addWidget(serial_btn)

        # Overflow 'More' button (hidden by default)
        from PyQt6.QtWidgets import QToolButton, QMenu
        self._toolbar_more = QToolButton()
        self._toolbar_more.setText("⋯")
        self._toolbar_more.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._toolbar_more_menu = QMenu()
        # Add actions to mirror key toolbar controls
        self._toolbar_more_menu.addAction("Toggle Serial Monitor", lambda: serial_btn.toggle())
        self._toolbar_more_menu.addAction("Refresh Ports", refresh_btn.click)
        self._toolbar_more_menu.addAction("Upload", self.upload_code)
        self._toolbar_more_menu.addAction("Compile", self.verify_code)
        self._toolbar_more.setMenu(self._toolbar_more_menu)
        self._toolbar_more.setVisible(False)
        toolbar.addWidget(self._toolbar_more)

        # Track toolbar controls for responsive layout (now that all are created)
        self._toolbar_controls = [self.verify_btn, self.upload_btn, self.board_combo, self.board_auto_chip, self.port_combo, self.port_auto_chip, refresh_btn, serial_btn]

        # After toolbar setup, try auto-selecting detected board/port
        self.auto_select_defaults()
        # Responsive toolbar threshold
        self._toolbar_responsive_threshold = 700


    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update responsive toolbar behavior
        try:
            w = self.width()
            if w < self._toolbar_responsive_threshold:
                # hide less important widgets and show overflow
                for wgt in (self.board_auto_chip, self.port_auto_chip):
                    wgt.setVisible(False)
                if hasattr(self, '_toolbar_more'):
                    self._toolbar_more.setVisible(True)
                # reduce combo widths slightly for narrow layouts
                self.board_combo.setMaximumWidth(200)
                self.port_combo.setMaximumWidth(150)
            else:
                for wgt in (self.board_auto_chip, self.port_auto_chip):
                    wgt.setVisible(True)
                if hasattr(self, '_toolbar_more'):
                    self._toolbar_more.setVisible(False)
                self.board_combo.setMaximumWidth(260)
                self.port_combo.setMaximumWidth(180)
        except Exception:
            pass

    def _on_board_combo_pin_diagram_update(self):
        if self.pin_diagram_overlay and self.pin_diagram_overlay.isVisible():
            board = self.board_combo.currentData()
            if not board:
                board = self.board_combo.currentText().lower().replace(' ', '-')
            self.pin_diagram_overlay.set_board(board)

        # After toolbar setup, try auto-selecting detected board/port
        self.auto_select_defaults()
        
    def create_menus(self):
        """Create menu bar with all options, including View."""
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
        
        # Recent Files submenu
        self.recent_files_menu = file_menu.addMenu("Recent &Files")
        self.update_recent_files_menu()
        
        file_menu.addSeparator()
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu (insert after File)
        view_menu = menubar.addMenu("&View")
        self.toggle_explorer_action = QAction("Project Explorer", self, checkable=True)
        self.toggle_explorer_action.setChecked(True)
        self.toggle_explorer_action.triggered.connect(self.toggle_explorer)
        view_menu.addAction(self.toggle_explorer_action)
        # Problems panel toggle
        self.toggle_problems_action = QAction("Problems", self, checkable=True)
        self.toggle_problems_action.setShortcut("Ctrl+Shift+I")
        self.toggle_problems_action.setChecked(False)
        self.toggle_problems_action.triggered.connect(self.toggle_problems)
        view_menu.addAction(self.toggle_problems_action)
        # Bind clickable status label to toggle via the action (ensures checked state is updated)
        try:
            self.status_problems.clicked.connect(lambda: self.toggle_problems_action.trigger())
            # Also flash the label when clicked for a visual cue
            self.status_problems.clicked.connect(lambda: self.status_problems.flash())
        except Exception:
            pass

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        # Go menu for navigation commands
        go_menu = menubar.addMenu("&Go")
        goto_def_action = QAction("Go to Definition", self)
        goto_def_action.setShortcut("F12")
        goto_def_action.triggered.connect(self.go_to_definition)
        go_menu.addAction(goto_def_action)
        find_refs_action = QAction("Find References", self)
        find_refs_action.setShortcut("Shift+F12")
        find_refs_action.triggered.connect(self.find_references)
        go_menu.addAction(find_refs_action)
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().undo())
        edit_menu.addAction(undo_action)
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().redo())
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().cut())
        edit_menu.addAction(cut_action)
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().copy())
        edit_menu.addAction(copy_action)
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().paste())
        edit_menu.addAction(paste_action)
        edit_menu.addSeparator()
        
        find_action = QAction("&Find...", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        
        replace_action = QAction("&Replace...", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.show_replace_dialog)
        edit_menu.addAction(replace_action)
        # Format document
        format_action = QAction("Format Document", self)
        format_action.setShortcut("Ctrl+Alt+F")
        format_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().format_document())
        edit_menu.addAction(format_action)
        # Rename symbol (refactor)
        rename_action = QAction("Rename Symbol...", self)
        rename_action.setShortcut("F2")
        rename_action.triggered.connect(self.rename_symbol_action)
        edit_menu.addAction(rename_action)
        
        edit_menu.addSeparator()
        comment_action = QAction("Toggle &Comment", self)
        comment_action.setShortcut("Ctrl+/")
        comment_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().toggle_comment())
        edit_menu.addAction(comment_action)

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
        run_linter_action = QAction("Run Linter", self)
        run_linter_action.setShortcut("Ctrl+L")
        run_linter_action.triggered.connect(self.run_linter)
        tools_menu.addAction(run_linter_action)
        # Quick Fix: apply to the currently selected problem (if available)
        self.apply_quick_fix_action = QAction("Apply Quick Fix", self)
        self.apply_quick_fix_action.setShortcut("Ctrl+.")
        self.apply_quick_fix_action.triggered.connect(self.apply_quick_fix_for_current_problem)
        tools_menu.addAction(self.apply_quick_fix_action)
        # Pin Diagram Overlay
        pin_diagram_action = QAction("Show Pin Diagram", self)
        pin_diagram_action.setShortcut("Ctrl+Alt+P")
        pin_diagram_action.triggered.connect(self.show_pin_diagram_overlay)
        tools_menu.addAction(pin_diagram_action)
        # Serial monitor/plotter actions
        serial_action = QAction("Serial &Monitor", self)
        serial_action.setShortcut("Ctrl+Shift+M")
        serial_action.triggered.connect(lambda: self.serial_monitor.setVisible(not self.serial_monitor.isVisible()))
        tools_menu.addAction(serial_action)
        plotter_action = QAction("Serial &Plotter", self)
        plotter_action.setShortcut("Ctrl+Shift+P")
        plotter_action.triggered.connect(self.show_serial_plotter)
        tools_menu.addAction(plotter_action)
        # Navigation: Next/Previous problem
        next_problem_action = QAction("Next Problem", self)
        next_problem_action.setShortcut("F8")
        next_problem_action.triggered.connect(self.next_problem)
        tools_menu.addAction(next_problem_action)
        prev_problem_action = QAction("Previous Problem", self)
        prev_problem_action.setShortcut("Shift+F8")
        prev_problem_action.triggered.connect(self.prev_problem)
        tools_menu.addAction(prev_problem_action)
        # Help menu
        help_menu = menubar.addMenu("&Help")
        reference_action = QAction("Programmer's &Reference", self)
        reference_action.triggered.connect(self.show_programmers_reference)
        help_menu.addAction(reference_action)
        about_action = QAction("&About Asic (Arduino Basic)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def apply_high_contrast(self, enable: bool):
        """Apply or remove a simple high-contrast stylesheet and persist setting."""
        try:
            if enable:
                # Very simple high-contrast dark stylesheet
                ss = """
                QWidget { background-color: #000000; color: #FFFFFF; }
                QMenuBar, QMenu, QStatusBar { background-color: #111111; color: #FFFFFF; }
                QToolButton, QPushButton { background-color: #222222; color: #FFFFFF; border: 1px solid #444444; }
                QComboBox { background-color: #111111; color: #FFFFFF; }
                QTextEdit, QPlainTextEdit { background-color: #000000; color: #FFFFFF; }
                """
                self.setStyleSheet(ss)
            else:
                self.setStyleSheet("")
            # persist
            try:
                self.settings.set("editor", "high_contrast", bool(enable))
                self.settings.save()
            except Exception:
                pass
            # sync action state
            try:
                if hasattr(self, 'high_contrast_action'):
                    self.high_contrast_action.setChecked(bool(enable))
            except Exception:
                pass
        except Exception:
            pass

    def toggle_high_contrast(self, checked=None):
        """Toggle high contrast; accepts optional checked from QAction.triggered."""
        try:
            if checked is None:
                # flip
                desired = not (self.settings.get("editor", "high_contrast", False))
            else:
                desired = bool(checked)
            self.apply_high_contrast(desired)
        except Exception:
            pass
    def create_problems_panel(self):
        """Create dockable Problems panel to show linter diagnostics."""
        from PyQt6.QtWidgets import QDockWidget, QTreeWidget, QTreeWidgetItem
        self.problems_dock = QDockWidget("Problems", self)
        self.problems_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.problems_widget = QTreeWidget()
        self.problems_widget.setColumnCount(5)
        self.problems_widget.setHeaderLabels(["Severity", "Message", "File", "Line", "Col"])
        self.problems_widget.itemDoubleClicked.connect(self._on_problem_double_clicked)
        # Also react to selection changes (single-click) to jump cursor
        self.problems_widget.currentItemChanged.connect(self._on_problem_selected)
        # Context menu for Quick Fixes
        try:
            self.problems_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.problems_widget.customContextMenuRequested.connect(self._on_problems_context_menu)
        except Exception:
            pass
        self.problems_dock.setWidget(self.problems_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.problems_dock)
        self.problems_dock.setVisible(False)

    def toggle_problems(self, checked=None):
        """Toggle Problems panel visibility. Accepts optional checked flag from QAction.triggered."""
        try:
            if checked is None:
                # infer desired state from current visibility
                desired = not self.problems_dock.isVisible()
            else:
                desired = bool(checked)
            self.problems_dock.setVisible(desired)
            # Ensure the action's checked state matches desired
            self.toggle_problems_action.setChecked(desired)
            # Update status indicator accordingly
            self._update_problems_status()
        except Exception:
            pass

    def run_linter(self):
        """Run the lightweight linter on the current editor and populate Problems."""
        try:
            editor = self.get_current_editor()
            if not editor:
                return
            text = editor.toPlainText()
            from vb2arduino.linter import run_linter_on_text
            path = str(self.current_file) if self.current_file else "<unsaved>"
            diags = run_linter_on_text(text, path=path)
            self._show_problems_from_diags(diags)
            self.status.showMessage(f"Linter: {len(diags)} issues found", 3000)
            # Show the panel if any diagnostics found
            if diags:
                self.problems_dock.setVisible(True)
                self.toggle_problems_action.setChecked(True)
        except Exception as e:
            QMessageBox.critical(self, "Linter Error", f"Failed to run linter:\n{e}")

    def _show_problems_from_diags(self, diags):
        """Populate the problems widget from diagnostic list."""
        from PyQt6.QtWidgets import QTreeWidgetItem
        self.problems_widget.clear()
        for d in diags:
            item = QTreeWidgetItem([
                d.get('severity', ''),
                d.get('message', ''),
                str(d.get('file', '')),
                str(d.get('line', '')),
                str(d.get('col', '')),
            ])
            # attach metadata
            item.setData(0, Qt.ItemDataRole.UserRole, d)
            self.problems_widget.addTopLevelItem(item)
        # Also show inline gutter markers for the current editor when appropriate
        try:
            editor = self.get_current_editor()
            if editor:
                # Filter diagnostics to those matching the current file (or unsaved)
                current_path = str(self.current_file) if self.current_file else '<unsaved>'
                editor_diags = [d for d in diags if not d.get('file') or d.get('file') in (current_path, '<unsaved>', None)]
                editor.set_diagnostics(editor_diags)
        except Exception:
            pass
        # Update problems status indicator
        self._update_problems_status()

    def focus_problem(self, diag: dict):
        """Show the Problems panel and focus/select the item matching diag."""
        try:
            self.problems_dock.setVisible(True)
            self.toggle_problems_action.setChecked(True)
            # Try to match by file and line
            for i in range(self.problems_widget.topLevelItemCount()):
                item = self.problems_widget.topLevelItem(i)
                d = item.data(0, Qt.ItemDataRole.UserRole)
                if not d:
                    continue
                try:
                    file_ok = (not d.get('file')) or (not diag.get('file')) or str(d.get('file')) == str(diag.get('file'))
                    line_ok = int(d.get('line', -1)) == int(diag.get('line', -1))
                    if file_ok and line_ok:
                        self.problems_widget.setCurrentItem(item)
                        self.problems_widget.scrollToItem(item)
                        self.problems_widget.setFocus()
                        # Update status indicator
                        self._update_problems_status()
                        return
                except Exception:
                    continue
        except Exception:
            pass

    def _on_problem_double_clicked(self, item, col):
        """Jump to file/line when user double-clicks a problem."""
        d = item.data(0, Qt.ItemDataRole.UserRole)
        if not d:
            return
        self._jump_to_diag(d)
        # Update status after double click as well
        self._update_problems_status()

    def _update_problems_status(self):
        """Update the problems status label (e.g., 'Problem 2/5')."""
        try:
            total = self.problems_widget.topLevelItemCount()
            if total == 0:
                self.status_problems.setText("")
                return
            cur = self.problems_widget.currentItem()
            if not cur:
                # no selection — show total
                self.status_problems.setText(f"Problems: {total}")
                return
            idx = self.problems_widget.indexOfTopLevelItem(cur)
            if idx < 0:
                self.status_problems.setText(f"Problems: {total}")
                return
            # 1-based index for display
            self.status_problems.setText(f"Problem {idx+1}/{total}")
        except Exception:
            try:
                self.status_problems.setText("")
            except Exception:
                pass
    def _on_problem_selected(self, current, previous):
        """Handle single-click selection in Problems panel by jumping cursor and update status."""
        # Update status indicator when selection changes
        self._update_problems_status()
        if not current:
            return
        d = current.data(0, Qt.ItemDataRole.UserRole)
        if not d:
            return
        self._jump_to_diag(d)

    def _on_problems_context_menu(self, pos):
        """Show a context menu with quick-fix actions for the selected problem (if available)."""
        try:
            item = self.problems_widget.itemAt(pos)
            if not item:
                return
            d = item.data(0, Qt.ItemDataRole.UserRole)
            if not d:
                return
            from vb2arduino.linter import available_fixes_for_diag
            fixes = available_fixes_for_diag(d)
            menu = QMenu(self)
            if fixes:
                for f in fixes:
                    a = menu.addAction(f.get('label', 'Apply'))
                    # capture fix id and diag in closure
                    a.triggered.connect(lambda checked=False, diag=d, fid=f.get('id'): self.apply_quick_fix_for_diag(diag, fid))
            else:
                a = menu.addAction("No quick fixes")
                a.setEnabled(False)
            menu.exec(self.problems_widget.viewport().mapToGlobal(pos))
        except Exception:
            pass

    def apply_quick_fix_for_current_problem(self):
        """Apply the first available quick fix for the currently selected problem in the Problems panel."""
        try:
            cur = self.problems_widget.currentItem()
            if not cur:
                self.status.showMessage("No problem selected for Quick Fix", 2000)
                return
            d = cur.data(0, Qt.ItemDataRole.UserRole)
            if not d:
                self.status.showMessage("Selected problem has no data", 2000)
                return
            from vb2arduino.linter import available_fixes_for_diag
            fixes = available_fixes_for_diag(d)
            if not fixes:
                self.status.showMessage("No quick fixes available for the selected problem", 2000)
                return
            # Apply the first fix by default
            fix_id = fixes[0].get('id')
            self.apply_quick_fix_for_diag(d, fix_id)
        except Exception as e:
            QMessageBox.warning(self, "Quick Fix Failed", f"Failed to apply quick fix: {e}")

    def apply_quick_fix_for_diag(self, diag: dict, fix_id: str):
        """Apply the specified quick fix for the given diagnostic. Operates on the indicated file if present."""
        try:
            file_path = diag.get('file')
            # If the diagnostic refers to another file, open it
            if file_path and file_path not in ('', '<unsaved>'):
                try:
                    self.open_file_in_tab(file_path)
                except Exception:
                    pass
            editor = self.get_current_editor()
            if not editor:
                self.status.showMessage("No active editor to apply quick fix", 2000)
                return
            original = editor.toPlainText()
            from vb2arduino.linter import apply_fix_on_text
            new_text = apply_fix_on_text(original, diag, fix_id)
            if new_text == original:
                self.status.showMessage("Quick fix made no changes", 2000)
                return
            # Apply changes and re-run linter
            editor.setPlainText(new_text)
            # Move caret to the location where the change occurred (try to put at diag line)
            try:
                line_no = int(diag.get('line', 1))
                cursor = editor.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)
                for _ in range(max(0, line_no - 1)):
                    cursor.movePosition(cursor.MoveOperation.Down)
                editor.setTextCursor(cursor)
                editor.setFocus()
            except Exception:
                pass
            # Re-run linter to refresh problems
            self.run_linter()
            self.status.showMessage("Quick fix applied", 3000)
        except Exception as e:
            QMessageBox.warning(self, "Quick Fix Error", f"Failed to apply quick fix: {e}")

    def _jump_to_diag(self, d: dict):
        """Jump to diagnostic location in the editor. Opens file if needed."""
        try:
            file_path = d.get('file')
            line_no = int(d.get('line')) if d.get('line') else 1
            # Treat '<unsaved>' or empty file markers as referring to the current editor
            if not file_path or file_path in ('<unsaved>', ''):
                file_path = None
            # If no file specified, jump in current editor
            if file_path is None:
                editor = self.get_current_editor()
                if editor:
                    cursor = editor.textCursor()
                    cursor.movePosition(cursor.MoveOperation.Start)
                    for _ in range(line_no - 1):
                        cursor.movePosition(cursor.MoveOperation.Down)
                    editor.setTextCursor(cursor)
                    # visually highlight the target line
                    try:
                        editor.highlight_line(line_no)
                    except Exception:
                        pass
                    editor.setFocus()
            # If the file matches current_file, jump there
            elif self.current_file and str(self.current_file) == str(file_path):
                editor = self.get_current_editor()
                if editor:
                    cursor = editor.textCursor()
                    cursor.movePosition(cursor.MoveOperation.Start)
                    for _ in range(line_no - 1):
                        cursor.movePosition(cursor.MoveOperation.Down)
                    editor.setTextCursor(cursor)
                    try:
                        editor.highlight_line(line_no)
                    except Exception:
                        pass
                    editor.setFocus()
            else:
                # try to open the file path
                try:
                    self.open_file_in_tab(file_path)
                    # then move cursor
                    ed = self.get_current_editor()
                    if ed:
                        cursor = ed.textCursor()
                        cursor.movePosition(cursor.MoveOperation.Start)
                        for _ in range(line_no - 1):
                            cursor.movePosition(cursor.MoveOperation.Down)
                        ed.setTextCursor(cursor)
                        try:
                            ed.highlight_line(line_no)
                        except Exception:
                            pass
                        ed.setFocus()
                except Exception:
                    pass
        except Exception:
            pass

    def next_problem(self):
        """Select the next problem in the Problems panel and jump to it (wraps)."""
        try:
            count = self.problems_widget.topLevelItemCount()
            if count == 0:
                self._update_problems_status()
                return
            cur = self.problems_widget.currentItem()
            start = 0
            if cur:
                start = self.problems_widget.indexOfTopLevelItem(cur) + 1
            for i in range(count):
                idx = (start + i) % count
                item = self.problems_widget.topLevelItem(idx)
                if item:
                    self.problems_widget.setCurrentItem(item)
                    self._update_problems_status()
                    d = item.data(0, Qt.ItemDataRole.UserRole)
                    if d:
                        self._jump_to_diag(d)
                    return
        except Exception:
            pass

    def prev_problem(self):
        """Select the previous problem in the Problems panel and jump to it (wraps)."""
        try:
            count = self.problems_widget.topLevelItemCount()
            if count == 0:
                self._update_problems_status()
                return
            cur = self.problems_widget.currentItem()
            if cur:
                start = self.problems_widget.indexOfTopLevelItem(cur) - 1
            else:
                start = count - 1
            for i in range(count):
                idx = (start - i) % count
                item = self.problems_widget.topLevelItem(idx)
                if item:
                    self.problems_widget.setCurrentItem(item)
                    self._update_problems_status()
                    d = item.data(0, Qt.ItemDataRole.UserRole)
                    if d:
                        self._jump_to_diag(d)
                    return
        except Exception:
            pass

    def go_to_definition(self):
        """Jump to the procedure/function definition for the symbol under the cursor (F12)."""
        try:
            editor = self.get_current_editor()
            if not editor:
                self.status.showMessage("No active editor", 2000)
                return
            symbol = editor.text_under_cursor().strip()
            if not symbol:
                self.status.showMessage("No symbol under cursor", 2000)
                return
            # Search open tabs for a procedure/function with this name
            for i in range(self.tab_widget.count()):
                tab = self.tab_widget.widget(i)
                if not hasattr(tab, 'editor'):
                    continue
                ed = tab.editor
                # Ensure procedures are up to date
                ed.parse_code()
                for proc_name, line_no in ed.procedures:
                    # proc_name looks like 'Sub Foo' or 'Function Bar'; we extract the last token
                    try:
                        name = proc_name.split()[-1]
                    except Exception:
                        name = proc_name
                    if name.lower() == symbol.lower():
                        # switch to tab and jump
                        self.tab_widget.setCurrentIndex(i)
                        cursor = ed.textCursor()
                        cursor.movePosition(cursor.MoveOperation.Start)
                        for _ in range(max(0, line_no - 1)):
                            cursor.movePosition(cursor.MoveOperation.Down)
                        ed.setTextCursor(cursor)
                        ed.setFocus()
                        ed.highlight_line(line_no)
                        self.status.showMessage(f"Jumped to definition of '{symbol}'", 2000)
                        return
            self.status.showMessage(f"Definition for '{symbol}' not found", 3000)
        except Exception as e:
            QMessageBox.warning(self, "Go to Definition", f"Failed to go to definition: {e}")

    def find_references(self, show_dialog: bool = True):
        """Find all references to the symbol under the cursor across open tabs (Shift+F12).

        When `show_dialog` is False (used by tests), the function returns the results list
        instead of showing a modal dialog.
        """
        try:
            editor = self.get_current_editor()
            if not editor:
                self.status.showMessage("No active editor", 2000)
                return [] if not show_dialog else None
            symbol = editor.text_under_cursor().strip()
            if not symbol:
                self.status.showMessage("No symbol under cursor", 2000)
                return [] if not show_dialog else None
            import re
            pat = re.compile(r"\b" + re.escape(symbol) + r"\b", re.IGNORECASE)
            results = []
            for i in range(self.tab_widget.count()):
                tab = self.tab_widget.widget(i)
                if not hasattr(tab, 'editor'):
                    continue
                ed = tab.editor
                text = ed.toPlainText()
                for m in pat.finditer(text):
                    # compute line number
                    start = m.start()
                    line_no = text.count('\n', 0, start) + 1
                    # snippet for context
                    line = text.splitlines()[line_no - 1].strip() if line_no - 1 < len(text.splitlines()) else ''
                    file_path = tab.property('file_path') or '<unsaved>'
                    results.append({'file': file_path, 'line': line_no, 'col': m.start() - text.rfind('\n', 0, start), 'snippet': line, 'tab_index': i})
            # Show results dialog
            dlg = QDialog(self)
            dlg.setWindowTitle(f"References for '{symbol}' ({len(results)})")
            dlg.setModal(True)
            dlg_layout = QVBoxLayout()
            listw = QListWidget()
            if not show_dialog:
                return results
            for r in results:
                item = QListWidgetItem(f"{r['file']}:{r['line']} - {r['snippet']}")
                item.setData(Qt.ItemDataRole.UserRole, r)
                listw.addItem(item)
            listw.itemDoubleClicked.connect(lambda it: self._on_reference_activated(it, dlg))
            dlg_layout.addWidget(listw)
            dlg.setLayout(dlg_layout)
            dlg.resize(800, 400)
            dlg.exec()
        except Exception as e:
            QMessageBox.warning(self, "Find References", f"Failed to find references: {e}")

    def _on_reference_activated(self, item, dialog=None):
        try:
            data = item.data(Qt.ItemDataRole.UserRole)
            if not data:
                return
            idx = data.get('tab_index')
            if idx is None:
                return
            self.tab_widget.setCurrentIndex(idx)
            ed = self.get_current_editor()
            if ed:
                line_no = data.get('line', 1)
                cursor = ed.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)
                for _ in range(max(0, line_no - 1)):
                    cursor.movePosition(cursor.MoveOperation.Down)
                ed.setTextCursor(cursor)
                ed.setFocus()
            if dialog:
                try:
                    dialog.accept()
                except Exception:
                    pass
        except Exception:
            pass


    def rename_symbol_action(self):
        """Prompt for a new symbol name and apply rename across open tabs."""
        try:
            editor = self.get_current_editor()
            if not editor:
                self.status.showMessage("No active editor", 2000)
                return
            symbol = editor.text_under_cursor().strip()
            if not symbol:
                self.status.showMessage("No symbol under cursor", 2000)
                return
            from PyQt6.QtWidgets import QInputDialog
            new, ok = QInputDialog.getText(self, "Rename Symbol", f"Rename '{symbol}' to:")
            if not ok or not new:
                return
            # Apply rename across all open tabs (simple textual replace with word boundaries)
            import re
            pattern = re.compile(rf"\b{re.escape(symbol)}\b")
            for i in range(self.tab_widget.count()):
                tab = self.tab_widget.widget(i)
                if not hasattr(tab, 'editor'):
                    continue
                ed = tab.editor
                txt = ed.toPlainText()
                new_txt = pattern.sub(new, txt)
                if new_txt != txt:
                    ed.setPlainText(new_txt)
            # Re-run linter and update UI
            try:
                self.run_linter()
            except Exception:
                pass
            self.status.showMessage(f"Renamed '{symbol}' to '{new}'", 3000)
        except Exception as e:
            QMessageBox.warning(self, "Rename Symbol", f"Failed to rename symbol: {e}")

    def toggle_explorer(self, checked):
        """Show or hide the project explorer (tree view) window."""
        self.tree_view.setVisible(checked)
        # Optionally, adjust splitter sizes for better UX
        if checked:
            self.h_splitter.setSizes([220, 700, 250])
        else:
            self.h_splitter.setSizes([0, 900, 250])

    def show_programmers_reference(self):
        dialog = ProgrammersReferenceDialog(self)
        dialog.exec()
        
    def load_template(self):
        """Load default VB template into the current editor tab."""
        template = """' Asic (Arduino Basic) Sketch
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
        editor = self.get_current_editor()
        if editor:
            editor.setPlainText(template)
        self.is_modified = False
        self.update_title()
        self.update_tree_view()
        
    def new_file(self):
        """Create new file."""
        if self.check_save_changes():
            self.current_file = None
            self.load_template()
            
    def open_file(self):
        """Open existing file and update project explorer root."""
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
                self.open_file_in_tab(filename)
                # Set project explorer root to the directory of the opened file
                self.set_project_root(pathlib.Path(filename).parent)
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
            # Accept str paths too
            path = pathlib.Path(path)
            editor = self.get_current_editor()
            if not editor:
                return False
            with open(path, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())
            self.current_file = path
            self.is_modified = False
            self.update_title()
            
            # Add to recent files
            self.add_to_recent_files(str(path))
            
            # Save board and port selection for this file
            self.project_config.set_board_and_port(
                self.board_combo.currentData(),
                self.port_combo.currentText() if self.port_combo.count() > 0 else None
            )
            
            self.status.showMessage(f"Saved: {path}")
            # Run linter on save to populate Problems panel
            try:
                self.run_linter()
            except Exception:
                pass
            return True
        except Exception as e:
            import traceback, sys
            traceback.print_exc()
            print('Save failed:', e, file=sys.stderr)
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")
            return False
            
    def check_platformio(self):
        """Check if PlatformIO is installed."""
        try:
            # Try using Python module first (works in venv)
            result = subprocess.run(
                [sys.executable, "-m", "platformio", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True
            
            # Fallback to 'pio' command in PATH
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
            editor = self.get_current_editor()
            if not editor:
                QMessageBox.warning(self, "No Editor", "No active editor found.")
                progress.close()
                return
            vb_code = editor.toPlainText()
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
                [sys.executable, "-m", "platformio", "run", "--project-dir", str(self.build_output_dir), "--environment", board],
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
                errors = self._parse_compile_errors(result.stderr, cpp_file)
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
            editor = self.get_current_editor()
            if not editor:
                QMessageBox.warning(self, "No Editor", "No active editor found.")
                progress.close()
                return
            vb_code = editor.toPlainText()
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
                [sys.executable, "-m", "platformio", "run", "--project-dir", str(self.build_output_dir), 
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
                errors = self._parse_compile_errors(result.stderr, cpp_file)
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
        editor = self.get_current_editor()
        if editor:
            code = editor.toPlainText()
            self.tree_view.update_from_code(code)
        
    def goto_line(self, line_number):
        """Navigate to a specific line in the current editor."""
        editor = self.get_current_editor()
        if editor and line_number > 0:
            cursor = editor.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.MoveAnchor, line_number - 1)
            editor.setTextCursor(cursor)
            editor.centerCursor()
            editor.setFocus()
            # Temporary highlight to make the target line obvious
            try:
                duration = int(self.settings.get("editor", "jump_highlight_duration_ms", 3000))
                editor.highlight_line(line_number, duration)
            except Exception:
                pass
        
    def update_title(self):
        """Update window title."""
        title = "Asic (Arduino Basic) IDE"
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

    def _parse_compile_errors(self, stderr: str, cpp_path: "pathlib.Path|str") -> list[tuple[int, str, str]]:
        """Parse compiler stderr to extract (cpp_line, level, message) for main file.

        Handles common GCC/Clang formats including:
          - <file>:<line>:<col>: <level>: <message>
          - <file>:<line>: <level>: <message>
        Also handles multi-line messages where the error line may be on the following
        line (e.g., "error: redeclaration of 't'") by using the most recent file/line
        context or by searching the generated C++ for a matching symbol when possible.
        """
        errors: list[tuple[int, str, str]] = []
        # Normalize cpp_path to a pathlib.Path when possible so we can inspect the file.
        try:
            import pathlib as _pathlib
            if isinstance(cpp_path, _pathlib.Path):
                cpp_path_obj = cpp_path
                cpp_name = cpp_path.name
            else:
                cpp_path_obj = None
                cpp_name = str(cpp_path)
        except Exception:
            cpp_path_obj = None
            cpp_name = str(cpp_path)

        last_file = None
        last_line = None
        for line in stderr.splitlines():
            # 1) Try file:line:col: format
            m = re.match(r"(.+?):(\d+):(\d+):\s+(fatal error|error|warning):\s+(.*)", line)
            if not m:
                # 2) Try file:line: (no column)
                m = re.match(r"(.+?):(\d+):\s+(fatal error|error|warning):\s+(.*)", line)
            if m:
                file_path, line_no, *_rest = m.groups()
                # Last two groups are level and message in either case
                if len(_rest) == 2:
                    level, msg = _rest
                else:
                    level = _rest[0]
                    msg = _rest[1] if len(_rest) > 1 else ""
                last_file = file_path
                try:
                    last_line = int(line_no)
                except Exception:
                    last_line = None

                # Only return errors that originate in the generated C++ main file
                if file_path.endswith(cpp_name):
                    try:
                        errors.append((int(line_no), level, msg, f"{file_path}:{line_no}", False))
                    except Exception:
                        pass
                else:
                    # If the error points into another file, attempt to map it by
                    # searching for the same symbol in our generated C++ file (best-effort).
                    # This covers cases like "redeclaration of 't'" where the message doesn't
                    # include a direct file:line reference into main.cpp.
                    if cpp_path_obj and cpp_path_obj.exists():
                        # Look for a token in the error message
                        token_match = re.search(r"redeclaration of ['\"]?([A-Za-z0-9_]+)['\"]?", msg)
                        if token_match:
                            token = token_match.group(1)
                            try:
                                found = False
                                for idx, l in enumerate(cpp_path_obj.read_text(encoding='utf-8').splitlines(), start=1):
                                    if re.search(rf"\b(?:int|float|double|long|char|uint8_t|uint16_t|uint32_t)\s+{re.escape(token)}\b", l):
                                        errors.append((idx, level, msg, f"{file_path}:{line_no}" if file_path and line_no else None, True))
                                        found = True
                                        break
                                if not found:
                                    # No declaration found, fall back to the last line reference
                                    if last_line is not None:
                                        errors.append((last_line, level, msg, f"{file_path}:{line_no}" if file_path and line_no else None, True))
                            except Exception:
                                pass
                        else:
                            # As a fallback, map to the last recognized line if any
                            if last_line is not None:
                                errors.append((last_line, level, msg, f"{file_path}:{line_no}" if file_path and line_no else None, True))
            else:
                # Handle continuation lines like: "error: redeclaration of 't'"
                m2 = re.match(r"^\s*(fatal error|error|warning):\s+(.*)", line)
                if m2 and last_file is not None:
                    level, msg = m2.groups()
                    if last_file.endswith(cpp_name) and last_line is not None:
                        errors.append((last_line, level, msg, f"{last_file}:{last_line}", False))
                    else:
                        # Try to find token in generated C++ and map to its declaration
                        token_match = re.search(r"redeclaration of ['\"]?([A-Za-z0-9_]+)['\"]?", msg)
                        if token_match and cpp_path_obj and cpp_path_obj.exists():
                            token = token_match.group(1)
                            try:
                                found = False
                                for idx, l in enumerate(cpp_path_obj.read_text(encoding='utf-8').splitlines(), start=1):
                                    if re.search(rf"\b(?:int|float|double|long|char|uint8_t|uint16_t|uint32_t)\s+{re.escape(token)}\b", l):
                                        errors.append((idx, level, msg, f"{last_file}:{last_line}" if last_file and last_line else None, True))
                                        found = True
                                        break
                                if not found and last_line is not None:
                                    errors.append((last_line, level, msg, f"{last_file}:{last_line}" if last_file and last_line else None, True))
                            except Exception:
                                pass
                        elif last_line is not None:
                            errors.append((last_line, level, msg, f"{last_file}:{last_line}" if last_file and last_line else None, True))
        return errors

    def _show_compile_errors(self, errors: list[tuple[int, str, str]], vb_map: dict[int, int]):
        """Show a clickable list of compile errors mapped to VB lines."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Compilation Errors")
        layout = QVBoxLayout(dlg)
        lst = QListWidget(dlg)
        layout.addWidget(lst)
        # Populate list with VB line numbers and messages
        for e in errors:
            # Accept either old-style (cpp_line, level, msg) or new-style (cpp_line, level, msg, orig_ref, ambiguous)
            if isinstance(e, tuple) and len(e) >= 5:
                cpp_line, level, msg, orig_ref, ambiguous = e[:5]
            elif isinstance(e, tuple) and len(e) == 3:
                cpp_line, level, msg = e
                orig_ref = None
                ambiguous = False
            else:
                # Unexpected format: skip
                continue

            # Map cpp line to the closest VB marker: prefer exact match, otherwise
            # use the nearest preceding marker so we don't default everything to line 1.
            if cpp_line in vb_map:
                vb_line = vb_map[cpp_line]
            else:
                keys = [k for k in vb_map.keys() if k <= cpp_line]
                if keys:
                    vb_line = vb_map[max(keys)]
                    ambiguous = True
                else:
                    vb_line = vb_map.get(1, 1)
                    ambiguous = True

            label = f"VB line {vb_line}: {level} - {msg}"
            if ambiguous:
                if orig_ref:
                    label += f" (approx, from {orig_ref})"
                else:
                    label += " (approx)"
            item = QListWidgetItem(label)
            # store VB line and message in item data (include orig_ref and ambiguous for richer details)
            item.setData(Qt.ItemDataRole.UserRole, (vb_line, level, msg, orig_ref, ambiguous))
            lst.addItem(item)

        def on_item_activated(item: QListWidgetItem):
            data = item.data(Qt.ItemDataRole.UserRole)
            # Expect (vb_line, level, msg, orig_ref, ambiguous) or legacy (vb_line, level, msg)
            if isinstance(data, tuple) and len(data) >= 3:
                vb_line = data[0]
                level = data[1]
                msg = data[2]
                orig_ref = data[3] if len(data) >= 4 else None
                ambiguous = data[4] if len(data) >= 5 else False
                if isinstance(vb_line, int):
                    self.goto_line(vb_line)
                    # Update status bar with concise hint, include orig_ref when ambiguous
                    if ambiguous and orig_ref:
                        self.status.showMessage(f"{level.capitalize()} at VB line {vb_line} (from {orig_ref}): {msg}", 5000)
                    else:
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
            "About Asic (Arduino Basic) IDE",
            "<h2>Asic (Arduino Basic) IDE</h2>"
            "<p>Version 0.1.0</p>"
            "<p>An Arduino Basic IDE inspired by Visual Basic 6.</p>"
            "<p>Write VB6-like code that transpiles to Arduino C++.</p>"
            "<p>Licensed under GPL-3.0-or-later</p>"
        )
        
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Apply new settings to editor
            editor = self.get_current_editor()
            if editor:
                editor.apply_settings(self.settings)
            self.apply_settings()
            self.status.showMessage("Settings applied", 2000)
    
    def show_libraries_manager(self):
        """Show libraries manager dialog."""
        board = self.board_combo.currentData()
        # Parse #Include statements from the current editor and normalize names
        used_libraries = []
        editor = self.get_current_editor()
        if editor:
            code = editor.toPlainText()
            import re
            include_pattern = re.compile(r'^\s*#Include\s+[<"](.+)[>"]', re.IGNORECASE | re.MULTILINE)
            raw_includes = [m.group(1) for m in include_pattern.finditer(code)]
            # Strip .h/.hpp extensions for matching with catalog
            def normalize_include(name):
                if name.lower().endswith('.h'):
                    return name[:-2]
                if name.lower().endswith('.hpp'):
                    return name[:-4]
                return name
            used_libraries = [normalize_include(n) for n in raw_includes]
        dialog = ManageLibrariesDialog(
            self.project_config,
            selected_board=board,
            parent=self,
            on_libraries_changed=self._on_libraries_changed,
            used_libraries=used_libraries
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.status.showMessage("Libraries updated", 2000)

    def _on_libraries_changed(self, libraries):
        """Update #Include statements in the code when libraries are changed from the dialog."""
        # Update selected_libraries for consistency
        self.selected_libraries = list(libraries)
        # Update #Include statements in the current editor
        editor = self.get_current_editor()
        if editor:
            current_code = editor.toPlainText()
            lines = current_code.split('\n')
            # Remove old includes
            include_lines = [i for i, line in enumerate(lines) if line.strip().upper().startswith('#INCLUDE')]
            for i in reversed(include_lines):
                lines.pop(i)
            # Add new includes at the top
            new_includes = [f"#Include <{lib}>" for lib in libraries]
            # Insert after any initial comments
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip().startswith("'") or not line.strip():
                    insert_pos = i + 1
                else:
                    break
            for include in reversed(new_includes):
                lines.insert(insert_pos, include)
            # Add blank line after includes if needed
            if new_includes and lines[insert_pos + len(new_includes)].strip():
                lines.insert(insert_pos + len(new_includes), "")
            new_code = '\n'.join(lines)
            editor.setPlainText(new_code)
            # Update Project Explorer tree view
            self.tree_view.update_from_code(new_code)
    
    def show_pin_configuration(self):
        """Show pin configuration dialog."""
        board = self.board_combo.currentData()
        dialog = PinConfigurationDialog(self.project_config, board_id=board, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.status.showMessage("Pin configuration updated", 2000)
    
    def show_build_flags(self):
        """Show build flags editor dialog."""
        # Get current flags from project config
        current_flags = self.project_config.get_build_flags()
        current_text = '\n'.join(current_flags)
        
        # Create a simple dialog for editing build flags
        dialog = QDialog(self)
        dialog.setWindowTitle("Build Flags (Compiler Defines)")
        dialog.setGeometry(100, 100, 500, 300)
        
        layout = QVBoxLayout()
        
        label = QLabel("Enter compiler defines (one per line, e.g., -DDEBUG -DVERSION=1):")
        layout.addWidget(label)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(current_text)
        layout.addWidget(text_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        reset_btn = QPushButton("Reset to Empty")
        
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        def save_flags():
            try:
                flag_text = text_edit.toPlainText()
                # Split by newlines and filter empty lines
                new_flags = [f.strip() for f in flag_text.split('\n') if f.strip()]
                self.project_config.set_build_flags(new_flags)
                self.status.showMessage(f"Build flags updated ({len(new_flags)} flags)", 2000)
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save build flags:\n{e}")
        
        def reset_flags():
            text_edit.setPlainText("")
            self.status.showMessage("Build flags cleared", 2000)
        
        ok_btn.clicked.connect(save_flags)
        cancel_btn.clicked.connect(dialog.reject)
        reset_btn.clicked.connect(reset_flags)
        
        dialog.exec()
    
    def clean_build(self):
        """Clean build artifacts using PlatformIO."""
        try:
            # Save current file first
            if self.is_modified:
                self.save_file()
            
            board = self.board_combo.currentData()
            if not board:
                QMessageBox.warning(self, "Warning", "Please select a board first")
                return
            
            self.status.showMessage("Cleaning build artifacts...")
            
            # Run clean in generated directory
            gen_dir = pathlib.Path.cwd() / "generated"
            cmd = [
                sys.executable, "-m", "platformio",
                "run", "--target", "clean",
                "--environment", board
            ]
            
            result = subprocess.run(
                cmd,
                cwd=str(gen_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.status.showMessage("✓ Build cleaned successfully", 3000)
                QMessageBox.information(self, "Success", "Build artifacts cleaned successfully")
            else:
                self.status.showMessage("✗ Clean failed", 3000)
                QMessageBox.warning(self, "Error", f"Clean failed:\n{result.stderr}")
        except Exception as e:
            self.status.showMessage("✗ Clean error", 3000)
            QMessageBox.critical(self, "Error", f"Failed to clean build:\n{e}")
    
    def open_device_monitor(self):
        """Open PlatformIO device monitor."""
        try:
            port = self.port_combo.currentText()
            if not port or port == "No port detected":
                QMessageBox.warning(self, "Warning", "Please select a serial port first")
                return
            
            board = self.board_combo.currentData()
            if not board:
                QMessageBox.warning(self, "Warning", "Please select a board first")
                return
            
            self.status.showMessage("Opening device monitor...")
            
            # Open device monitor in a terminal
            gen_dir = pathlib.Path.cwd() / "generated"
            cmd = [
                sys.executable, "-m", "platformio",
                "device", "monitor",
                "--port", port,
                "--baud", "115200"
            ]
            
            # Open in new terminal (works on Linux/Mac/Windows)
            if sys.platform == "linux":
                subprocess.Popen(["gnome-terminal", "--", "bash", "-c", " ".join(cmd)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-a", "Terminal", " ".join(cmd)])
            elif sys.platform == "win32":
                subprocess.Popen(cmd, cwd=str(gen_dir), creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            self.status.showMessage("Device monitor opened in terminal", 3000)
        except Exception as e:
            self.status.showMessage("✗ Monitor error", 3000)
            QMessageBox.critical(self, "Error", f"Failed to open device monitor:\n{e}")
    
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
        
        editor = self.get_current_editor()
        if not editor:
            return
            
        current_code = editor.toPlainText()
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
        editor.setPlainText('\n'.join(lines))
        self.is_modified = True
        self.update_title()
        
    def closeEvent(self, event):
        """Handle window close event and ensure all resources are cleaned up."""
        if self.check_save_changes():
            # Ensure serial monitor is closed and cleaned up
            try:
                if hasattr(self, 'serial_monitor') and self.serial_monitor is not None:
                    self.serial_monitor.close()
            except Exception:
                pass
            event.accept()
        else:
            event.ignore()    
    def show_find_dialog(self):
        """Show find dialog."""
        editor = self.get_current_editor()
        if not editor:
            return
        if not self.find_dialog:
            self.find_dialog = FindReplaceDialog(editor, self)
        else:
            self.find_dialog.editor = editor
        self.find_dialog.show()
        self.find_dialog.find_edit.setFocus()
    
    def show_replace_dialog(self):
        """Show find/replace dialog."""
        self.show_find_dialog()  # Same dialog handles both
    
    def add_to_recent_files(self, filepath):
        """Add file to recent files list."""
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        self.recent_files.insert(0, filepath)
        self.recent_files = self.recent_files[:self.max_recent_files]
        self.settings.set("editor", "recent_files", self.recent_files)
        self.update_recent_files_menu()
    
    def update_recent_files_menu(self):
        """Update the recent files menu."""
        if not hasattr(self, 'recent_files_menu'):
            return
        self.recent_files_menu.clear()
        if not self.recent_files:
            action = self.recent_files_menu.addAction("(No recent files)")
            action.setEnabled(False)
            return
        for filepath in self.recent_files:
            if pathlib.Path(filepath).exists():
                action = self.recent_files_menu.addAction(pathlib.Path(filepath).name)
                action.setData(filepath)
                action.triggered.connect(lambda checked, f=filepath: self.open_recent_file(f))
    
    def open_recent_file(self, filepath):
        """Open a file from recent files."""
        if pathlib.Path(filepath).exists():
            self.load_file(pathlib.Path(filepath))
        else:
            QMessageBox.warning(self, "File Not Found", f"File not found: {filepath}")
            self.recent_files.remove(filepath)
            self.settings.set("editor", "recent_files", self.recent_files)
            self.update_recent_files_menu()
    
    def on_editor_modified_changed(self, editor_widget, modified):
        """Handle editor modified state change to update tab title."""
        index = self.tab_widget.indexOf(editor_widget)
        if index >= 0:
            current_title = self.tab_widget.tabText(index)
            # Remove existing * if present
            if current_title.startswith("*"):
                current_title = current_title[1:]
            # Add * if modified
            if modified:
                self.tab_widget.setTabText(index, f"*{current_title}")
            else:
                self.tab_widget.setTabText(index, current_title)