"""Settings dialog for customizing IDE appearance."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QSpinBox, QPushButton, QColorDialog,
    QFormLayout, QCheckBox, QFontComboBox, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont


class SettingsDialog(QDialog):
    """Dialog for editing IDE settings."""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.color_buttons = {}
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Tab widget
        tabs = QTabWidget()
        tabs.addTab(self.create_editor_tab(), "Editor")
        tabs.addTab(self.create_syntax_tab(), "Syntax Colors")
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def create_editor_tab(self):
        """Create editor settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Font settings
        font_group = QGroupBox("Font")
        font_layout = QFormLayout()
        
        self.font_family = QFontComboBox()
        font_layout.addRow("Font Family:", self.font_family)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 32)
        font_layout.addRow("Font Size:", self.font_size)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # Color settings
        color_group = QGroupBox("Colors")
        color_layout = QFormLayout()
        
        self.add_color_picker(color_layout, "editor", "background_color", "Background:")
        self.add_color_picker(color_layout, "editor", "text_color", "Text:")
        self.add_color_picker(color_layout, "editor", "current_line_color", "Current Line:")
        self.add_color_picker(color_layout, "editor", "line_number_bg", "Line Number Background:")
        self.add_color_picker(color_layout, "editor", "line_number_fg", "Line Number Foreground:")
        self.add_color_picker(color_layout, "editor", "jump_highlight_color", "Jump Highlight:")
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)

        # Behavior settings
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout()
        self.jump_highlight_duration = QSpinBox()
        self.jump_highlight_duration.setRange(250, 10000)
        self.jump_highlight_duration.setSingleStep(250)
        behavior_layout.addRow("Jump Highlight Duration (ms):", self.jump_highlight_duration)
        # Success pop-up toggles
        self.compile_success_popup_cb = QCheckBox("Show Compile Success Pop-up")
        self.upload_success_popup_cb = QCheckBox("Show Upload Success Pop-up")
        # Align as form rows for consistency
        behavior_layout.addRow("Compile Success Pop-up:", self.compile_success_popup_cb)
        behavior_layout.addRow("Upload Success Pop-up:", self.upload_success_popup_cb)
        # Failure pop-up toggles
        self.compile_failure_popup_cb = QCheckBox("Show Compile Failure Pop-up")
        self.upload_failure_popup_cb = QCheckBox("Show Upload Failure Pop-up")
        behavior_layout.addRow("Compile Failure Pop-up:", self.compile_failure_popup_cb)
        behavior_layout.addRow("Upload Failure Pop-up:", self.upload_failure_popup_cb)
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_syntax_tab(self):
        """Create syntax highlighting settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Keywords
        kw_group = QGroupBox("Keywords (Sub, If, For, Dim, etc.)")
        kw_layout = QHBoxLayout()
        self.add_color_picker(kw_layout, "syntax", "keyword_color", "Color:")
        self.keyword_bold = QCheckBox("Bold")
        kw_layout.addWidget(self.keyword_bold)
        kw_layout.addStretch()
        kw_group.setLayout(kw_layout)
        layout.addWidget(kw_group)
        
        # Functions
        func_group = QGroupBox("Functions (PinMode, DigitalWrite, etc.)")
        func_layout = QHBoxLayout()
        self.add_color_picker(func_layout, "syntax", "function_color", "Color:")
        self.function_bold = QCheckBox("Bold")
        func_layout.addWidget(self.function_bold)
        func_layout.addStretch()
        func_group.setLayout(func_layout)
        layout.addWidget(func_group)
        
        # Constants
        const_group = QGroupBox("Constants (OUTPUT, HIGH, LOW, etc.)")
        const_layout = QHBoxLayout()
        self.add_color_picker(const_layout, "syntax", "constant_color", "Color:")
        self.constant_bold = QCheckBox("Bold")
        const_layout.addWidget(self.constant_bold)
        const_layout.addStretch()
        const_group.setLayout(const_layout)
        layout.addWidget(const_group)
        
        # Numbers
        num_group = QGroupBox("Numbers")
        num_layout = QHBoxLayout()
        self.add_color_picker(num_layout, "syntax", "number_color", "Color:")
        self.number_bold = QCheckBox("Bold")
        num_layout.addWidget(self.number_bold)
        num_layout.addStretch()
        num_group.setLayout(num_layout)
        layout.addWidget(num_group)
        
        # Strings
        str_group = QGroupBox("Strings")
        str_layout = QHBoxLayout()
        self.add_color_picker(str_layout, "syntax", "string_color", "Color:")
        self.string_bold = QCheckBox("Bold")
        str_layout.addWidget(self.string_bold)
        str_layout.addStretch()
        str_group.setLayout(str_layout)
        layout.addWidget(str_group)
        
        # Comments
        comment_group = QGroupBox("Comments")
        comment_layout = QHBoxLayout()
        self.add_color_picker(comment_layout, "syntax", "comment_color", "Color:")
        self.comment_italic = QCheckBox("Italic")
        comment_layout.addWidget(self.comment_italic)
        comment_layout.addStretch()
        comment_group.setLayout(comment_layout)
        layout.addWidget(comment_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def add_color_picker(self, layout, category, key, label):
        """Add a color picker button to layout."""
        if isinstance(layout, QFormLayout):
            btn = QPushButton()
            btn.setFixedSize(60, 25)
            btn.clicked.connect(lambda: self.pick_color(category, key))
            self.color_buttons[f"{category}.{key}"] = btn
            layout.addRow(label, btn)
        else:
            layout.addWidget(QLabel(label))
            btn = QPushButton()
            btn.setFixedSize(60, 25)
            btn.clicked.connect(lambda: self.pick_color(category, key))
            self.color_buttons[f"{category}.{key}"] = btn
            layout.addWidget(btn)
            
    def pick_color(self, category, key):
        """Open color picker dialog."""
        current_color = self.settings.get(category, key, "#000000")
        color = QColorDialog.getColor(QColor(current_color), self)
        if color.isValid():
            self.color_buttons[f"{category}.{key}"].setStyleSheet(
                f"background-color: {color.name()};"
            )
            
    def load_settings(self):
        """Load current settings into UI."""
        # Editor settings
        font_family = self.settings.get("editor", "font_family", "Courier New")
        self.font_family.setCurrentFont(QFont(font_family))
        self.font_size.setValue(
            self.settings.get("editor", "font_size", 11)
        )
        
        # Load colors into buttons
        for key, btn in self.color_buttons.items():
            category, setting = key.split(".")
            color = self.settings.get(category, setting, "#000000")
            btn.setStyleSheet(f"background-color: {color};")
        # Behavior
        self.jump_highlight_duration.setValue(
            self.settings.get("editor", "jump_highlight_duration_ms", 3000)
        )
        self.compile_success_popup_cb.setChecked(
            self.settings.get("editor", "show_compile_success_popup", True)
        )
        self.upload_success_popup_cb.setChecked(
            self.settings.get("editor", "show_upload_success_popup", True)
        )
        self.compile_failure_popup_cb.setChecked(
            self.settings.get("editor", "show_compile_failure_popup", True)
        )
        self.upload_failure_popup_cb.setChecked(
            self.settings.get("editor", "show_upload_failure_popup", True)
        )
            
        # Syntax style checkboxes
        self.keyword_bold.setChecked(
            self.settings.get("syntax", "keyword_bold", True)
        )
        self.function_bold.setChecked(
            self.settings.get("syntax", "function_bold", True)
        )
        self.constant_bold.setChecked(
            self.settings.get("syntax", "constant_bold", False)
        )
        self.number_bold.setChecked(
            self.settings.get("syntax", "number_bold", False)
        )
        self.string_bold.setChecked(
            self.settings.get("syntax", "string_bold", False)
        )
        self.comment_italic.setChecked(
            self.settings.get("syntax", "comment_italic", True)
        )
        
    def save_settings(self):
        """Save UI values to settings."""
        # Editor settings
        self.settings.set("editor", "font_family", self.font_family.currentFont().family())
        self.settings.set("editor", "font_size", self.font_size.value())
        
        # Colors from buttons
        for key, btn in self.color_buttons.items():
            category, setting = key.split(".")
            color = btn.palette().button().color().name()
            self.settings.set(category, setting, color)
        # Behavior
        self.settings.set("editor", "jump_highlight_duration_ms", self.jump_highlight_duration.value())
        self.settings.set("editor", "show_compile_success_popup", self.compile_success_popup_cb.isChecked())
        self.settings.set("editor", "show_upload_success_popup", self.upload_success_popup_cb.isChecked())
        self.settings.set("editor", "show_compile_failure_popup", self.compile_failure_popup_cb.isChecked())
        self.settings.set("editor", "show_upload_failure_popup", self.upload_failure_popup_cb.isChecked())
            
        # Syntax style checkboxes
        self.settings.set("syntax", "keyword_bold", self.keyword_bold.isChecked())
        self.settings.set("syntax", "function_bold", self.function_bold.isChecked())
        self.settings.set("syntax", "constant_bold", self.constant_bold.isChecked())
        self.settings.set("syntax", "number_bold", self.number_bold.isChecked())
        self.settings.set("syntax", "string_bold", self.string_bold.isChecked())
        self.settings.set("syntax", "comment_italic", self.comment_italic.isChecked())
        
        self.settings.save()
        
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.data = self.settings.DEFAULT_SETTINGS.copy()
            self.load_settings()
            
    def accept(self):
        """Save and close."""
        self.save_settings()
        super().accept()
