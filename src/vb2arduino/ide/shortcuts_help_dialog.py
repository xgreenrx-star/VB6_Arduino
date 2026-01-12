"""Dialog showing keyboard shortcuts and feature help for the VB2Arduino IDE."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton
from PyQt6.QtCore import Qt

SHORTCUTS = [
    ("Ctrl+S", "Save file"),
    ("Ctrl+O", "Open file"),
    ("Ctrl+N", "New file"),
    ("Ctrl+R", "Compile/Verify"),
    ("Ctrl+U", "Compile and Upload"),
    ("Ctrl+F", "Find"),
    ("Ctrl+H", "Replace"),
    ("Ctrl+/", "Toggle comment"),
    ("Ctrl+Space", "Show completions"),
    ("Tab", "Expand snippet (if available)"),
    ("Ctrl+Shift+[", "Fold block at cursor"),
    ("Ctrl+Shift+]", "Unfold block at cursor"),
    ("Ctrl++ / Ctrl+- / Ctrl+0", "Change/reset font size"),
    ("F2", "Rename variable (planned)"),
    ("F12", "Go to definition"),
    ("Ctrl+G", "Go to line (planned)"),
    ("Right-click", "Context menu: comment, go to def, fold"),
    ("Ctrl+Q", "Show this shortcuts help"),
    ("Serial Monitor: Clear, Save Log, Autoscroll, Timestamp, Hex", "Toolbar buttons/toggles")
]

class ShortcutsHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts & Feature Help")
        self.setMinimumWidth(520)
        layout = QVBoxLayout(self)
        label = QLabel("<b>Keyboard Shortcuts and Features</b>")
        layout.addWidget(label)
        table = QTableWidget(len(SHORTCUTS), 2)
        table.setHorizontalHeaderLabels(["Shortcut", "Action"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        for row, (shortcut, action) in enumerate(SHORTCUTS):
            table.setItem(row, 0, QTableWidgetItem(shortcut))
            table.setItem(row, 1, QTableWidgetItem(action))
        table.resizeColumnsToContents()
        layout.addWidget(table)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
