"""Find and Replace dialog for code editor."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QTextDocument
import re


class FindReplaceDialog(QDialog):
    """Dialog for finding and replacing text in the editor."""
    
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.last_match_pos = -1
        self.setWindowTitle("Find and Replace")
        self.setModal(False)
        self.setMinimumWidth(400)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Find group
        find_group = QGroupBox("Find")
        find_layout = QVBoxLayout()
        
        find_input_layout = QHBoxLayout()
        find_input_layout.addWidget(QLabel("Find:"))
        self.find_edit = QLineEdit()
        self.find_edit.textChanged.connect(self.on_find_text_changed)
        self.find_edit.returnPressed.connect(self.find_next)
        find_input_layout.addWidget(self.find_edit)
        find_layout.addLayout(find_input_layout)
        
        # Find buttons
        find_buttons_layout = QHBoxLayout()
        self.find_next_btn = QPushButton("Find Next")
        self.find_next_btn.clicked.connect(self.find_next)
        self.find_prev_btn = QPushButton("Find Previous")
        self.find_prev_btn.clicked.connect(self.find_previous)
        self.find_all_btn = QPushButton("Find All")
        self.find_all_btn.clicked.connect(self.find_all)
        find_buttons_layout.addWidget(self.find_next_btn)
        find_buttons_layout.addWidget(self.find_prev_btn)
        find_buttons_layout.addWidget(self.find_all_btn)
        find_layout.addLayout(find_buttons_layout)
        
        find_group.setLayout(find_layout)
        layout.addWidget(find_group)
        
        # Replace group
        replace_group = QGroupBox("Replace")
        replace_layout = QVBoxLayout()
        
        replace_input_layout = QHBoxLayout()
        replace_input_layout.addWidget(QLabel("Replace:"))
        self.replace_edit = QLineEdit()
        self.replace_edit.returnPressed.connect(self.replace_current)
        replace_input_layout.addWidget(self.replace_edit)
        replace_layout.addLayout(replace_input_layout)
        
        # Replace buttons
        replace_buttons_layout = QHBoxLayout()
        self.replace_btn = QPushButton("Replace")
        self.replace_btn.clicked.connect(self.replace_current)
        self.replace_all_btn = QPushButton("Replace All")
        self.replace_all_btn.clicked.connect(self.replace_all)
        replace_buttons_layout.addWidget(self.replace_btn)
        replace_buttons_layout.addWidget(self.replace_all_btn)
        replace_layout.addLayout(replace_buttons_layout)
        
        replace_group.setLayout(replace_layout)
        layout.addWidget(replace_group)
        
        # Options
        options_layout = QHBoxLayout()
        self.case_sensitive_cb = QCheckBox("Case Sensitive")
        self.whole_word_cb = QCheckBox("Whole Word")
        self.regex_cb = QCheckBox("Regular Expression")
        options_layout.addWidget(self.case_sensitive_cb)
        options_layout.addWidget(self.whole_word_cb)
        options_layout.addWidget(self.regex_cb)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def on_find_text_changed(self):
        """Reset search position when find text changes."""
        self.last_match_pos = -1
    
    def get_find_flags(self):
        """Get QTextDocument find flags based on options."""
        flags = QTextDocument.FindFlag(0)
        if self.case_sensitive_cb.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_word_cb.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        return flags
    
    def find_next(self):
        """Find next occurrence."""
        search_text = self.find_edit.text()
        if not search_text:
            return
        
        cursor = self.editor.textCursor()
        
        if self.regex_cb.isChecked():
            # Use regex search
            pattern = search_text
            flags = re.IGNORECASE if not self.case_sensitive_cb.isChecked() else 0
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:
                QMessageBox.warning(self, "Invalid Regex", f"Invalid regular expression: {e}")
                return
            
            text = self.editor.toPlainText()
            start_pos = cursor.selectionEnd() if cursor.hasSelection() else cursor.position()
            match = regex.search(text, start_pos)
            
            if match:
                cursor.setPosition(match.start())
                cursor.setPosition(match.end(), QTextCursor.MoveMode.KeepAnchor)
                self.editor.setTextCursor(cursor)
                self.editor.centerCursor()
                self.last_match_pos = match.start()
            else:
                # Wrap around
                match = regex.search(text, 0)
                if match:
                    cursor.setPosition(match.start())
                    cursor.setPosition(match.end(), QTextCursor.MoveMode.KeepAnchor)
                    self.editor.setTextCursor(cursor)
                    self.editor.centerCursor()
                    self.last_match_pos = match.start()
                else:
                    QMessageBox.information(self, "Not Found", f"'{search_text}' not found.")
        else:
            # Use simple text search
            found = self.editor.find(search_text, self.get_find_flags())
            if not found:
                # Wrap around
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                self.editor.setTextCursor(cursor)
                found = self.editor.find(search_text, self.get_find_flags())
                if not found:
                    QMessageBox.information(self, "Not Found", f"'{search_text}' not found.")
    
    def find_previous(self):
        """Find previous occurrence."""
        search_text = self.find_edit.text()
        if not search_text:
            return
        
        flags = self.get_find_flags() | QTextDocument.FindFlag.FindBackward
        found = self.editor.find(search_text, flags)
        if not found:
            # Wrap around
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.editor.setTextCursor(cursor)
            found = self.editor.find(search_text, flags)
            if not found:
                QMessageBox.information(self, "Not Found", f"'{search_text}' not found.")
    
    def find_all(self):
        """Find and highlight all occurrences."""
        search_text = self.find_edit.text()
        if not search_text:
            return
        
        # Clear previous selections
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.editor.setTextCursor(cursor)
        
        count = 0
        while self.editor.find(search_text, self.get_find_flags()):
            count += 1
        
        if count > 0:
            QMessageBox.information(self, "Find All", f"Found {count} occurrence(s) of '{search_text}'.")
        else:
            QMessageBox.information(self, "Not Found", f"'{search_text}' not found.")
    
    def replace_current(self):
        """Replace current selection."""
        search_text = self.find_edit.text()
        replace_text = self.replace_edit.text()
        
        if not search_text:
            return
        
        cursor = self.editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == search_text:
            cursor.insertText(replace_text)
        
        # Find next after replace
        self.find_next()
    
    def replace_all(self):
        """Replace all occurrences."""
        search_text = self.find_edit.text()
        replace_text = self.replace_edit.text()
        
        if not search_text:
            return
        
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        # Move to start
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.editor.setTextCursor(cursor)
        
        count = 0
        if self.regex_cb.isChecked():
            # Regex replace
            pattern = search_text
            flags = re.IGNORECASE if not self.case_sensitive_cb.isChecked() else 0
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:
                QMessageBox.warning(self, "Invalid Regex", f"Invalid regular expression: {e}")
                cursor.endEditBlock()
                return
            
            text = self.editor.toPlainText()
            new_text, count = regex.subn(replace_text, text)
            
            if count > 0:
                cursor.select(QTextCursor.SelectionType.Document)
                cursor.insertText(new_text)
        else:
            # Simple replace
            while self.editor.find(search_text, self.get_find_flags()):
                cursor = self.editor.textCursor()
                cursor.insertText(replace_text)
                count += 1
        
        cursor.endEditBlock()
        
        if count > 0:
            QMessageBox.information(self, "Replace All", f"Replaced {count} occurrence(s) of '{search_text}'.")
        else:
            QMessageBox.information(self, "Not Found", f"'{search_text}' not found.")
    
    def showEvent(self, event):
        """When dialog is shown, populate with selected text if any."""
        super().showEvent(event)
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            self.find_edit.setText(cursor.selectedText())
        self.find_edit.setFocus()
        self.find_edit.selectAll()
