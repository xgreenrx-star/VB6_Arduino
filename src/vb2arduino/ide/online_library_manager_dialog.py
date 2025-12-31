"""Advanced dialog for online Arduino library management with version comparison and selection."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QCheckBox, QMessageBox, QHeaderView, QTabWidget, QStatusBar
)
from PyQt6.QtCore import Qt
from vb2arduino.ide.fetch_arduino_libs import fetch_arduino_libraries

class OnlineLibraryManagerDialog(QDialog):
    def __init__(self, installed_libraries: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Online Library Manager")
        self.setGeometry(300, 200, 1000, 700)
        self.installed_libraries = installed_libraries  # {name: version}
        self.selected = set()
        self.libraries = []
        self.category_tabs = None
        self.status_bar = None
        self.category_tables = {}
        self.init_ui()
        self.load_libraries()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select libraries to install or update. Compare installed and online versions."))
        from vb2arduino.ide.library_catalog import get_all_categories
        self.category_tabs = QTabWidget()
        layout.addWidget(self.category_tabs)
        btn_layout = QHBoxLayout()
        self.install_btn = QPushButton("Install/Update Selected")
        self.install_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.install_btn)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        # Status bar
        from PyQt6.QtWidgets import QStatusBar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

    def load_libraries(self):
        from vb2arduino.ide.library_catalog import get_all_categories
        from PyQt6.QtWidgets import QProgressDialog, QApplication
        self.status_bar.showMessage("Fetching online library list... Please wait.")
        progress = QProgressDialog("Fetching online library list...", None, 0, 0, self)
        progress.setWindowTitle("Please Wait")
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()
        QApplication.processEvents()  # Force dialog to show before blocking call
        try:
            self.libraries = fetch_arduino_libraries()
            self.status_bar.showMessage(f"Loaded {len(self.libraries)} libraries from Arduino Library Manager.", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch libraries:\n{e}")
            self.libraries = []
            self.status_bar.showMessage("Failed to load libraries.", 5000)
        progress.close()
        # Organize libraries by category (using curated categories, but show all online libs)
        self.category_tables.clear()
        self.category_tabs.clear()
        # Build a mapping: category -> [libs]
        category_map = {cat: [] for cat in get_all_categories()}
        uncategorized = []
        for lib in self.libraries:
            found = False
            for cat in category_map:
                if lib["name"] in [l["name"] for l in category_map[cat]]:
                    found = True
                    break
            # Try to match by name to curated categories
            for cat in category_map:
                from vb2arduino.ide.library_catalog import get_libraries_by_category
                curated_names = [l["name"] for l in get_libraries_by_category(cat)]
                if lib["name"] in curated_names:
                    category_map[cat].append(lib)
                    found = True
                    break
            if not found:
                uncategorized.append(lib)
        # Add tabs for each category
        for cat in get_all_categories():
            table = self._create_table_for_category(cat, category_map[cat])
            self.category_tabs.addTab(table, cat)
            self.category_tables[cat] = table
        # Add "Other" tab for uncategorized
        if uncategorized:
            table = self._create_table_for_category("Other", uncategorized)
            self.category_tabs.addTab(table, "Other")
            self.category_tables["Other"] = table
    def _create_table_for_category(self, category, libs):
        table = QTableWidget(len(libs), 6)
        table.setHorizontalHeaderLabels([
            "Select", "Library Name", "Installed Version", "Online Version", "Description", "Author"
        ])
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        for row, lib in enumerate(libs):
            name = lib.get("name", "")
            online_version = lib.get("version", "")
            desc = lib.get("description", "")
            author = lib.get("author", "")
            installed_version = self.installed_libraries.get(name, "-")
            cb = QCheckBox()
            if installed_version != "-":
                cb.setChecked(True)
                self.selected.add(name)
            cb.stateChanged.connect(lambda state, n=name: self._on_checkbox(n, state))
            table.setCellWidget(row, 0, cb)
            # Name
            item_name = QTableWidgetItem(name)
            if installed_version != "-" and installed_version != online_version:
                item_name.setBackground(Qt.GlobalColor.yellow)
            table.setItem(row, 1, item_name)
            # Installed Version
            item_installed = QTableWidgetItem(installed_version)
            if installed_version != "-" and installed_version == online_version:
                font = item_installed.font()
                font.setBold(True)
                item_installed.setFont(font)
            table.setItem(row, 2, item_installed)
            # Online Version
            table.setItem(row, 3, QTableWidgetItem(online_version))
            # Description
            table.setItem(row, 4, QTableWidgetItem(desc))
            # Author
            table.setItem(row, 5, QTableWidgetItem(author))
        return table

    def _on_checkbox(self, name, state):
        if state == Qt.CheckState.Checked.value:
            self.selected.add(name)
        else:
            self.selected.discard(name)
        self.status_bar.showMessage(f"Selected {len(self.selected)} libraries.", 3000)

    def get_selected_libraries(self):
        return list(self.selected)
