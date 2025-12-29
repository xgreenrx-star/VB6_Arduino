"""Libraries manager dialog for Asic (Arduino Basic) IDE."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QLabel, QMessageBox, QTabWidget, QWidget,
    QCheckBox
)
from PyQt6.QtCore import Qt
from vb2arduino.ide.project_config import ProjectConfig
from vb2arduino.ide.library_catalog import (
    get_all_categories, get_libraries_by_category, get_compatible_libraries,
    get_library_description
)


class LibrariesDialog(QDialog):
    """Dialog for managing project library dependencies with board-aware suggestions."""
    
    def __init__(self, project_config: ProjectConfig, selected_board: str = None, parent=None):
        super().__init__(parent)
        self.project_config = project_config
        self.selected_board = selected_board
        self.selected_libraries = set(project_config.get_libraries())
        
        self.setWindowTitle("Manage Libraries")
        self.setGeometry(200, 200, 700, 600)
        self.init_ui()
        self.load_libraries()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Board info and description
        if self.selected_board:
            board_label = QLabel(f"<b>Selected Board:</b> {self.selected_board}")
            layout.addWidget(board_label)
            desc_label = QLabel(
                "Compatible libraries are suggested at the top. "
                "You can add any library from the categories below, "
                "even if not officially compatible."
            )
        else:
            desc_label = QLabel(
                "Browse libraries by category or search. "
                "Check boxes to select libraries for your project."
            )
        layout.addWidget(desc_label)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Recommended tab (if board selected)
        if self.selected_board:
            recommended_widget = self._create_recommended_tab()
            tabs.addTab(recommended_widget, "Recommended")
        
        # Category tabs
        for category in get_all_categories():
            category_widget = self._create_category_tab(category)
            tabs.addTab(category_widget, category)
        
        # Search tab
        search_widget = self._create_search_tab()
        tabs.addTab(search_widget, "Search")
        
        layout.addWidget(tabs)
        
        # Selected libraries display
        layout.addWidget(QLabel("Selected Libraries:"))
        self.selected_list = QListWidget()
        self.selected_list.setMaximumHeight(100)
        layout.addWidget(self.selected_list)
        
        # Clear selection button
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_selection)
        layout.addWidget(clear_btn)
        
        # Buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def _create_recommended_tab(self) -> QWidget:
        """Create recommended libraries tab for selected board."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        compatible = get_compatible_libraries(self.selected_board)
        if compatible:
            layout.addWidget(QLabel(f"Libraries compatible with {self.selected_board}:"))
        else:
            layout.addWidget(QLabel("No specific library recommendations for this board."))
        
        lib_list = QListWidget()
        for lib in compatible:
            item = self._create_lib_item(lib)
            lib_list.addItem(item)
        
        lib_list.itemClicked.connect(lambda item: self._toggle_lib_item(item, lib_list))
        layout.addWidget(lib_list)
        layout.addStretch()
        
        return widget
    
    def _create_category_tab(self, category: str) -> QWidget:
        """Create a category tab with libraries."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        libs = get_libraries_by_category(category)
        if not libs:
            layout.addWidget(QLabel(f"No libraries in {category}"))
            layout.addStretch()
            return widget
        
        lib_list = QListWidget()
        for lib in libs:
            item = self._create_lib_item(lib)
            lib_list.addItem(item)
        
        lib_list.itemClicked.connect(lambda item: self._toggle_lib_item(item, lib_list))
        layout.addWidget(lib_list)
        layout.addStretch()
        
        return widget
    
    def _create_search_tab(self) -> QWidget:
        """Create search tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Search for libraries (type keywords):"))
        search_input = QLineEdit()
        search_input.setPlaceholderText("e.g., 'WiFi', 'display', 'sensor'...")
        layout.addWidget(search_input)
        
        # Custom library input
        layout.addWidget(QLabel("Or add a custom library name:"))
        custom_input = QLineEdit()
        custom_input.setPlaceholderText("Enter exact library name from PlatformIO registry")
        layout.addWidget(custom_input)
        
        add_btn = QPushButton("Add Custom Library")
        def add_custom():
            lib_name = custom_input.text().strip()
            if lib_name:
                self.selected_libraries.add(lib_name)
                self.update_selected_display()
                custom_input.clear()
            else:
                QMessageBox.warning(self, "Empty", "Please enter a library name.")
        
        add_btn.clicked.connect(add_custom)
        layout.addWidget(add_btn)
        layout.addStretch()
        
        return widget
    
    def _create_lib_item(self, lib: dict) -> QListWidgetItem:
        """Create a library list item."""
        name = lib.get("name", "Unknown")
        desc = lib.get("description", "")
        
        is_selected = name in self.selected_libraries
        item = QListWidgetItem(f"{'✓ ' if is_selected else '  '}{name}")
        item.setData(Qt.ItemDataRole.UserRole, name)
        
        # Show description as tooltip
        if desc:
            item.setToolTip(desc)
        
        return item
    
    def _toggle_lib_item(self, item: QListWidgetItem, lib_list: QListWidget):
        """Toggle library selection."""
        lib_name = item.data(Qt.ItemDataRole.UserRole)
        
        if lib_name in self.selected_libraries:
            self.selected_libraries.remove(lib_name)
            item.setText(f"  {lib_name}")
        else:
            self.selected_libraries.add(lib_name)
            item.setText(f"✓ {lib_name}")
        
        self.update_selected_display()
    
    def update_selected_display(self):
        """Update the selected libraries list."""
        self.selected_list.clear()
        for lib in sorted(self.selected_libraries):
            desc = get_library_description(lib)
            text = f"{lib}"
            if desc:
                text += f" - {desc}"
            item = QListWidgetItem(text)
            # Add remove button functionality
            self.selected_list.addItem(item)
    
    def clear_selection(self):
        """Clear all selected libraries."""
        if QMessageBox.question(
            self, "Clear All",
            "Remove all selected libraries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self.selected_libraries.clear()
            self.update_selected_display()
    
    def load_libraries(self):
        """Load and display selected libraries."""
        self.update_selected_display()
    
    def accept(self):
        """Save libraries on OK."""
        if not self.selected_libraries:
            QMessageBox.warning(self, "No Libraries", "Please select at least one library.")
            return
        
        self.project_config.set_libraries(list(self.selected_libraries))
        super().accept()

