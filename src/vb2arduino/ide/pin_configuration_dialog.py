"""Pin configuration dialog for managing GPIO/interface pins and build flags."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QGroupBox,
    QPushButton, QMessageBox, QScrollArea, QWidget, QTabWidget, QListWidget,
    QListWidgetItem, QLineEdit, QInputDialog
)
from PyQt6.QtCore import Qt
from vb2arduino.ide.project_config import ProjectConfig
from vb2arduino.ide.pin_templates import (
    get_pin_category, get_pin_description, PIN_CATEGORIES,
    get_template_for_board
)


class PinConfigurationDialog(QDialog):
    """Dialog for configuring GPIO/interface pins and custom build flags."""
    
    def __init__(self, project_config: ProjectConfig, board_id: str = None, parent=None):
        super().__init__(parent)
        self.project_config = project_config
        self.board_id = board_id
        self.pin_inputs = {}  # Map pin_name -> QSpinBox
        
        self.setWindowTitle("Board Configuration")
        self.setGeometry(200, 200, 700, 600)
        self.init_ui()
        self.load_pins()
        self.load_build_flags()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Header
        if self.board_id:
            header = QLabel(f"<b>Pin Configuration for {self.board_id}</b>")
            layout.addWidget(header)
        else:
            header = QLabel("<b>Pin Configuration</b>")
            layout.addWidget(header)
        
        # Tabs: Pins | Build Flags | Templates
        tabs = QTabWidget()
        
        # Pins tab
        pins_tab = QWidget()
        pins_layout = QVBoxLayout(pins_tab)
        if self.board_id:
            template_btn = QPushButton("Load Board Pin Template")
            template_btn.clicked.connect(self.load_board_template)
            pins_layout.addWidget(template_btn)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        for category in PIN_CATEGORIES.keys():
            group_layout = self._create_category_group(category)
            scroll_layout.addLayout(group_layout)
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        pins_layout.addWidget(scroll)
        tabs.addTab(pins_tab, "Pins")
        
        # Build Flags tab
        flags_tab = QWidget()
        flags_layout = QVBoxLayout(flags_tab)
        flags_layout.addWidget(QLabel("Custom Build Flags (space-separated or one per line):"))
        self.flags_list = QListWidget()
        flags_layout.addWidget(self.flags_list)
        add_row = QHBoxLayout()
        self.flag_input = QLineEdit()
        self.flag_input.setPlaceholderText("e.g., -DUSER_DEFINE=1, -O2, -DUSE_TFT")
        add_btn = QPushButton("Add Flag")
        add_btn.clicked.connect(self.add_flag)
        add_row.addWidget(self.flag_input)
        add_row.addWidget(add_btn)
        flags_layout.addLayout(add_row)
        remove_btn = QPushButton("Remove Selected Flag")
        remove_btn.clicked.connect(self.remove_selected_flag)
        flags_layout.addWidget(remove_btn)
        tabs.addTab(flags_tab, "Build Flags")

        # Templates tab
        templates_tab = QWidget()
        templates_layout = QVBoxLayout(templates_tab)
        templates_layout.addWidget(QLabel("Saved Templates"))
        self.templates_list = QListWidget()
        templates_layout.addWidget(self.templates_list)
        tpl_btns = QHBoxLayout()
        self.load_template_btn = QPushButton("Load")
        self.save_template_btn = QPushButton("Save Current…")
        self.delete_template_btn = QPushButton("Delete")
        tpl_btns.addWidget(self.load_template_btn)
        tpl_btns.addWidget(self.save_template_btn)
        tpl_btns.addWidget(self.delete_template_btn)
        templates_layout.addLayout(tpl_btns)
        self.load_template_btn.clicked.connect(self._on_load_template)
        self.save_template_btn.clicked.connect(self._on_save_template)
        self.delete_template_btn.clicked.connect(self._on_delete_template)
        tabs.addTab(templates_tab, "Templates")
        
        layout.addWidget(tabs)
        # Populate templates list initially
        self._refresh_templates_list()
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_defaults)
        btn_layout.addWidget(reset_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_category_group(self, category: str) -> QVBoxLayout:
        """Create a group for a pin category."""
        group_box = QGroupBox(category)
        group_layout = QVBoxLayout(group_box)
        
        pin_names = PIN_CATEGORIES.get(category, [])
        for pin_name in pin_names:
            row_layout = self._create_pin_row(pin_name)
            group_layout.addLayout(row_layout)
        
        group_layout.addStretch()
        
        parent_layout = QVBoxLayout()
        parent_layout.addWidget(group_box)
        return parent_layout
    
    def _create_pin_row(self, pin_name: str) -> QHBoxLayout:
        """Create a row for a single pin."""
        layout = QHBoxLayout()
        
        # Label with description
        description = get_pin_description(pin_name)
        label = QLabel(f"{pin_name}:")
        label.setToolTip(description)
        layout.addWidget(label)
        
        # Spinbox for pin number
        spinbox = QSpinBox()
        spinbox.setMinimum(-1)
        spinbox.setMaximum(99)
        spinbox.setValue(0)
        spinbox.setToolTip(f"GPIO pin number for {pin_name}")
        self.pin_inputs[pin_name] = spinbox
        layout.addWidget(spinbox)
        
        layout.addStretch()
        return layout
    
    def load_pins(self):
        """Load pins from project config."""
        pins = self.project_config.get_pins()
        for pin_name, spinbox in self.pin_inputs.items():
            pin_value = pins.get(pin_name, 0)
            spinbox.setValue(pin_value)

    def load_build_flags(self):
        """Load build flags into list widget."""
        self.flags_list.clear()
        for flag in self.project_config.get_build_flags():
            self.flags_list.addItem(flag)

    def _reload_flags_ui(self):
        """Reload flags from project config into UI."""
        self.load_build_flags()
    
    def load_board_template(self):
        """Load the template for the selected board."""
        if not self.board_id:
            QMessageBox.warning(self, "No Board", "Please select a board first.")
            return
        
        template = get_template_for_board(self.board_id)
        if template:
            # Update spinboxes with template values
            for pin_name, pin_value in template.get("pins", {}).items():
                if pin_name in self.pin_inputs:
                    self.pin_inputs[pin_name].setValue(pin_value)
            QMessageBox.information(self, "Template Loaded", 
                                  f"Loaded template for {template.get('name', self.board_id)}")
            # Update project config pins to reflect loaded template
            pins = {}
            for pin_name, spin in self.pin_inputs.items():
                pins[pin_name] = spin.value()
            self.project_config.set_pins(pins)
            # Also apply any build flags that come with the template so TFT_eSPI picks up pin/driver config
            if "build_flags" in template:
                self.project_config.set_build_flags(template.get("build_flags", []))
            self._reload_pins_ui()
            self._reload_flags_ui()
        else:
            QMessageBox.warning(self, "No Template", 
                              f"No template available for {self.board_id}")
    
    def reset_defaults(self):
        """Reset pins to default values."""
        if QMessageBox.question(
            self, "Reset Pins",
            "Reset all pins to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            # Reset to 0
            for spinbox in self.pin_inputs.values():
                spinbox.setValue(0)
    
    def accept(self):
        """Save pins and flags on OK."""
        pins = {}
        for pin_name, spinbox in self.pin_inputs.items():
            pins[pin_name] = spinbox.value()
        
        self.project_config.set_pins(pins)
        flags = [self.flags_list.item(i).text() for i in range(self.flags_list.count())]
        self.project_config.set_build_flags(flags)
        super().accept()

    def _refresh_templates_list(self):
        """Refresh templates list filtered by board."""
        if not hasattr(self, 'templates_list'):
            return
        self.templates_list.clear()
        templates = self.project_config.get_templates_for_board(self.board_id)
        for name in sorted(templates.keys()):
            self.templates_list.addItem(name)

    def _on_save_template(self):
        """Save current pins and flags as named template."""
        name, ok = QInputDialog.getText(self, "Save Template", "Template name:")
        if not ok or not name:
            return
        pins = {}
        for pin_name, spin in self.pin_inputs.items():
            pins[pin_name] = spin.value()
        flags = [self.flags_list.item(i).text() for i in range(self.flags_list.count())]
        self.project_config.save_template(name, pins, self.board_id, flags)
        self._refresh_templates_list()

    def _on_load_template(self):
        """Load selected template into project config and UI."""
        item = getattr(self, 'templates_list', None).currentItem() if hasattr(self, 'templates_list') else None
        if not item:
            QMessageBox.warning(self, "Load Template", "Select a template to load.")
            return
        name = item.text()
        if self.project_config.load_template_by_name(name):
            QMessageBox.information(self, "Template Loaded", f"Applied template: {name}")
            self._reload_pins_ui()
            self._reload_flags_ui()
        else:
            QMessageBox.warning(self, "Load Template", "Failed to load template.")

    def _on_delete_template(self):
        """Delete selected template."""
        item = getattr(self, 'templates_list', None).currentItem() if hasattr(self, 'templates_list') else None
        if not item:
            QMessageBox.warning(self, "Delete Template", "Select a template to delete.")
            return
        name = item.text()
        confirm = QMessageBox.question(self, "Delete Template", f"Delete '{name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.project_config.delete_template(name)
            self._refresh_templates_list()

    def _reload_pins_ui(self):
        """Reload pin spinboxes from project config pins."""
        pins = self.project_config.get_pins()
        for pin_name, spin in self.pin_inputs.items():
            spin.setValue(pins.get(pin_name, spin.value()))

    # Build flags handlers
    def add_flag(self):
        text = self.flag_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Empty", "Please enter a flag.")
            return
        # Split by whitespace to allow multiple flags
        parts = [p for p in text.replace("\n", " ").split(" ") if p]
        for p in parts:
            # avoid duplicates in UI
            existing = [self.flags_list.item(i).text() for i in range(self.flags_list.count())]
            if p not in existing:
                self.flags_list.addItem(p)
        self.flag_input.clear()

    def remove_selected_flag(self):
        item = self.flags_list.currentItem()
        if item:
            self.flags_list.takeItem(self.flags_list.row(item))
