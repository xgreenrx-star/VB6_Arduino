"""Libraries manager dialog for Asic (Arduino Basic) IDE."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QLabel, QMessageBox, QTabWidget, QWidget,
    QCheckBox, QStatusBar
)

from PyQt6.QtCore import Qt
from vb2arduino.ide.project_config import ProjectConfig
from vb2arduino.ide.library_catalog_persist import load_catalog, save_catalog
from vb2arduino.ide.library_catalog import get_compatible_libraries, get_library_description
from vb2arduino.ide.online_library_manager_dialog import OnlineLibraryManagerDialog


class LibrariesDialog(QDialog):
    def set_used_libraries(self, used_libraries):
        """Set the libraries actually used in the current program (from #Include). Normalize for matching."""
        def normalize(name):
            n = name.lower()
            if n.endswith('.h'):
                n = n[:-2]
            elif n.endswith('.hpp'):
                n = n[:-4]
            return n
        self.used_libraries = set(normalize(n) for n in used_libraries)
        # Debug output removed

    def _show_library_info(self, item):
        """Show library info in the label below the tabs when a library is highlighted."""
        if item is None:
            self.library_info_label.setText("")
            return
        lib_name = item.data(Qt.ItemDataRole.UserRole)
        # Find the library dict in the curated catalog
        lib_info = None
        for libs in self.curated_catalog.values():
            for lib in libs:
                if lib.get("name") == lib_name:
                    lib_info = lib
                    break
            if lib_info:
                break
        if lib_info:
            desc = lib_info.get("description", "")
            version = lib_info.get("version", None)
            author = lib_info.get("author", None)
            info = f"<b>{lib_name}</b>"
            if version:
                info += f"  <i>(v{version})</i>"
            if author:
                info += f"<br><b>Author:</b> {author}"
            if desc:
                info += f"<br><b>Description:</b> {desc}"
            self.library_info_label.setText(info)
        else:
            self.library_info_label.setText(f"<b>{lib_name}</b>")
    
    def __init__(self, project_config: ProjectConfig, selected_board: str = None, parent=None, on_libraries_changed=None, used_libraries=None):
        super().__init__(parent)
        self.project_config = project_config
        self.selected_board = selected_board
        self.selected_libraries = set()
        self.used_libraries = set()
        self.on_libraries_changed = on_libraries_changed
        if used_libraries is not None:
            self.set_used_libraries(used_libraries)
        self.setWindowTitle("Manage Libraries")
        self.setGeometry(200, 200, 700, 600)
        self.init_ui()
    
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

        # Update Libraries button
        update_btn = QPushButton("Update Libraries")
        update_btn.setToolTip("Refresh the library catalog to get the latest libraries.")
        update_btn.clicked.connect(self._update_libraries_online)
        layout.addWidget(update_btn)

        # Advanced Online Library Manager button
        adv_btn = QPushButton("Advanced Online Library Manager")
        adv_btn.setToolTip("Open advanced online library manager with version comparison and selection.")
        adv_btn.clicked.connect(self._open_online_manager)
        layout.addWidget(adv_btn)

        # Create tab widget for project library management
        self.tabs = QTabWidget()
        # Load curated catalog (persistent)
        self.curated_catalog = load_catalog()
        # Add a label for library details below the tabs
        self.library_info_label = QLabel()
        self.library_info_label.setWordWrap(True)

        # Add selected libraries list below info label
        self.selected_list = QListWidget()
        self.selected_list.setToolTip("Selected libraries for your project")
        # Recommended tab (if board selected)
        if self.selected_board:
            recommended_widget = self._create_recommended_tab()
            self.tabs.addTab(recommended_widget, "Recommended")
        # Category tabs
        for category in self.curated_catalog.keys():
            category_widget = self._create_category_tab(category)
            self.tabs.addTab(category_widget, category)
        # Search tab
        search_widget = self._create_search_tab()
        self.tabs.addTab(search_widget, "Search")
        # Add the tab widget, then the info label below it
        layout.addWidget(self.tabs)
        layout.addWidget(self.library_info_label)

        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
    def _open_online_manager(self):
        """Open the advanced online library manager dialog for updating/installing libraries only."""
        # Build installed_libraries dict: {name: version}
        # Build installed_libraries dict: {name: version}
        installed = {}
        # Try to get installed versions from project config or PlatformIO lib list (future: parse platformio.ini)
        # For now, use project_config.get_libraries() and set version to curated version if available
        from vb2arduino.ide.library_catalog import LIBRARY_CATALOG
        for category, libs in LIBRARY_CATALOG.items():
            for lib in libs:
                name = lib.get("name")
                if name in self.selected_libraries:
                    version = lib.get("version", "-")
                    installed[name] = version
        dlg = None
        self.status_bar.showMessage("Opening Online Library Manager...", 3000)
        try:
            dlg = OnlineLibraryManagerDialog(installed, parent=self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                selected = dlg.get_selected_libraries()
                if selected:
                    QMessageBox.information(self, "Libraries Updated", "The selected libraries are now available for use.\nYou can now select which ones to use in your project from the main list.")
                self.load_libraries()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open online manager:\n{e}")
        self.status_bar.showMessage("Ready", 2000)

    def _update_libraries_online(self):
        self.status_bar.showMessage("Updating curated library info from Arduino Library Manager...", 3000)
        """Update only the curated/installed libraries (not the full online catalog)."""
        from vb2arduino.ide.fetch_arduino_libs import fetch_arduino_libraries
        import traceback
        try:
            self.setEnabled(False)
            self.setWindowTitle("Manage Libraries (Updating...)")
            # Only update versions/descriptions for curated libraries
            curated = load_catalog()
            online_libs = {lib['name']: lib for lib in fetch_arduino_libraries()}
            updated = 0
            for category, libs in curated.items():
                for lib in libs:
                    name = lib.get('name')
                    if name in online_libs:
                        online = online_libs[name]
                        # Update version/description if changed
                        if lib.get('version') != online.get('version') or lib.get('description') != online.get('description'):
                            lib['version'] = online.get('version')
                            lib['description'] = online.get('description')
                            updated += 1
            save_catalog(curated)
            self.curated_catalog = curated
            # Refresh tabs
            while self.tabs.count():
                self.tabs.removeTab(0)
            if self.selected_board:
                recommended_widget = self._create_recommended_tab()
                self.tabs.addTab(recommended_widget, "Recommended")
            for category in self.curated_catalog.keys():
                category_widget = self._create_category_tab(category)
                self.tabs.addTab(category_widget, category)
            search_widget = self._create_search_tab()
            self.tabs.addTab(search_widget, "Search")
            self.setWindowTitle("Manage Libraries (Updated)")
            QMessageBox.information(self, "Library Update Complete", f"Updated {updated} curated libraries with latest info from Arduino Library Manager.")
            self.status_bar.showMessage(f"Updated {updated} curated libraries.", 4000)
        except Exception as e:
            QMessageBox.critical(self, "Update Failed", f"Failed to update curated libraries:\n{e}\n{traceback.format_exc()}")
            self.status_bar.showMessage("Update failed.", 4000)
        finally:
            self.setEnabled(True)
            self.setWindowTitle("Manage Libraries")
            self.status_bar.showMessage("Ready", 2000)
        # (Dialog buttons are handled elsewhere; no need to add here)
    
    def _create_recommended_tab(self) -> QWidget:
        """Create recommended libraries tab for selected board with checkboxes."""
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
        lib_list.itemChanged.connect(self._on_lib_item_changed)
        lib_list.currentItemChanged.connect(lambda curr, prev: self._show_library_info(curr))
        layout.addWidget(lib_list)
        layout.addStretch()
        return widget
    
    def _create_category_tab(self, category: str) -> QWidget:
        """Create a category tab with libraries and checkboxes."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        libs = self.curated_catalog.get(category, [])
        if not libs:
            layout.addWidget(QLabel(f"No libraries in {category}"))
            layout.addStretch()
            return widget
        lib_list = QListWidget()
        for lib in libs:
            item = self._create_lib_item(lib)
            lib_list.addItem(item)
        lib_list.itemChanged.connect(self._on_lib_item_changed)
        lib_list.currentItemChanged.connect(lambda curr, prev: self._show_library_info(curr))
        layout.addWidget(lib_list)
        layout.addStretch()
        return widget
        def _show_library_info(self, item):
            """Show library info in the label below the tabs when a library is highlighted."""
            if item is None:
                self.library_info_label.setText("")
                return
            lib_name = item.data(Qt.ItemDataRole.UserRole)
            # Find the library dict in the curated catalog
            lib_info = None
            for libs in self.curated_catalog.values():
                for lib in libs:
                    if lib.get("name") == lib_name:
                        lib_info = lib
                        break
                if lib_info:
                    break
            if lib_info:
                desc = lib_info.get("description", "")
                version = lib_info.get("version", None)
                author = lib_info.get("author", None)
                info = f"<b>{lib_name}</b>"
                if version:
                    info += f"  <i>(v{version})</i>"
                if author:
                    info += f"<br><b>Author:</b> {author}"
                if desc:
                    info += f"<br><b>Description:</b> {desc}"
                self.library_info_label.setText(info)
            else:
                self.library_info_label.setText(f"<b>{lib_name}</b>")
    
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
        """Create a library list item with a real checkbox and version number."""
        name = lib.get("name", "Unknown")
        desc = lib.get("description", "")
        version = lib.get("version", None)
        label = name
        if version:
            label += f"  (v{version})"
        item = QListWidgetItem(label)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        # Normalize name for matching
        def normalize(n):
            n = n.lower()
            if n.endswith('.h'):
                n = n[:-2]
            elif n.endswith('.hpp'):
                n = n[:-4]
            return n
        norm_name = normalize(name)
        # Debug output removed
        if hasattr(self, 'used_libraries') and norm_name in self.used_libraries:
            item.setCheckState(Qt.CheckState.Checked)
        else:
            item.setCheckState(Qt.CheckState.Unchecked)
        item.setData(Qt.ItemDataRole.UserRole, name)
        if desc:
            item.setToolTip(desc)
        return item

    def _on_lib_item_changed(self, item: QListWidgetItem):
        """Handle checkbox state change for library selection."""
        lib_name = item.data(Qt.ItemDataRole.UserRole)
        if item.checkState() == Qt.CheckState.Checked:
            self.selected_libraries.add(lib_name)
        else:
            self.selected_libraries.discard(lib_name)
        self.update_selected_display()
        if self.on_libraries_changed:
            self.on_libraries_changed(sorted(self.selected_libraries))
    
    def _toggle_lib_item(self, item: QListWidgetItem, lib_list: QListWidget):
        """Toggle library selection."""
        lib_name = item.data(Qt.ItemDataRole.UserRole)
        changed = False
        if lib_name in self.selected_libraries:
            self.selected_libraries.remove(lib_name)
            item.setText(f"  {lib_name}")
            changed = True
        else:
            self.selected_libraries.add(lib_name)
            item.setText(f"✓ {lib_name}")
            changed = True
        self.update_selected_display()
        if changed and self.on_libraries_changed:
            self.on_libraries_changed(sorted(self.selected_libraries))
    
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
        """Save libraries on OK, with safety check for excessive selection."""
        MAX_LIBS = 50
        if not self.selected_libraries:
            QMessageBox.warning(self, "No Libraries", "Please select at least one library.")
            return
        if len(self.selected_libraries) > MAX_LIBS:
            QMessageBox.critical(self, "Too Many Libraries", f"You have selected {len(self.selected_libraries)} libraries. Please select fewer than {MAX_LIBS} libraries at once.")
            return
        self.project_config.set_libraries(list(self.selected_libraries))
        super().accept()

