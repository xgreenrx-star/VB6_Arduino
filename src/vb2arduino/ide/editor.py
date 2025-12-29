"""Code editor with VB syntax highlighting."""

from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit, QComboBox, QVBoxLayout, QCompleter
from PyQt6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont, 
    QPainter, QTextFormat, QTextCursor, QPalette
)
from PyQt6.QtCore import Qt, QRect, QRegularExpression, QTimer, QStringListModel
from .settings import Settings
import re


class VBSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for VB6-like code."""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.highlighting_rules = []
        self.update_highlighting_rules()
        
    def update_highlighting_rules(self):
        """Update highlighting rules from settings."""
        self.highlighting_rules = []
        
        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(self.settings.get("syntax", "keyword_color", "#0000FF")))
        if self.settings.get("syntax", "keyword_bold", True):
            keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = [
            "\\bSub\\b", "\\bEnd\\b", "\\bFunction\\b", "\\bDim\\b", "\\bConst\\b",
            "\\bAs\\b", "\\bIf\\b", "\\bThen\\b", "\\bElse\\b", "\\bElseIf\\b",
            "\\bFor\\b", "\\bTo\\b", "\\bNext\\b", "\\bWhile\\b", "\\bWend\\b",
            "\\bDo\\b", "\\bLoop\\b", "\\bAnd\\b", "\\bOr\\b", "\\bNot\\b",
            "\\bInteger\\b", "\\bLong\\b", "\\bByte\\b", "\\bBoolean\\b",
            "\\bSingle\\b", "\\bDouble\\b", "\\bString\\b"
        ]
        
        for keyword in keywords:
            pattern = QRegularExpression(keyword, QRegularExpression.PatternOption.CaseInsensitiveOption)
            self.highlighting_rules.append((pattern, keyword_format))
            
        # Function names format
        func_format = QTextCharFormat()
        func_format.setForeground(QColor(self.settings.get("syntax", "function_color", "#FF00FF")))
        if self.settings.get("syntax", "function_bold", True):
            func_format.setFontWeight(QFont.Weight.Bold)
        
        functions = [
            "\\bSetup\\b", "\\bLoop\\b",
            "\\bPinMode\\b", "\\bDigitalWrite\\b", "\\bDigitalRead\\b",
            "\\bAnalogRead\\b", "\\bAnalogWrite\\b", "\\bDelay\\b",
            "\\bSerialBegin\\b", "\\bSerialPrint\\b", "\\bSerialPrintLine\\b",
            "\\bSerialAvailable\\b", "\\bSerialRead\\b"
        ]
        
        for func in functions:
            pattern = QRegularExpression(func, QRegularExpression.PatternOption.CaseInsensitiveOption)
            self.highlighting_rules.append((pattern, func_format))
            
        # Constants format
        const_format = QTextCharFormat()
        const_format.setForeground(QColor(self.settings.get("syntax", "constant_color", "#0000FF")))
        if self.settings.get("syntax", "constant_bold", False):
            const_format.setFontWeight(QFont.Weight.Bold)
        
        constants = [
            "\\bOUTPUT\\b", "\\bINPUT\\b", "\\bINPUT_PULLUP\\b",
            "\\bHIGH\\b", "\\bLOW\\b"
        ]
        
        for const in constants:
            pattern = QRegularExpression(const, QRegularExpression.PatternOption.CaseInsensitiveOption)
            self.highlighting_rules.append((pattern, const_format))
            
        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(self.settings.get("syntax", "number_color", "#FF0000")))
        if self.settings.get("syntax", "number_bold", False):
            number_format.setFontWeight(QFont.Weight.Bold)
        pattern = QRegularExpression("\\b[0-9]+\\b")
        self.highlighting_rules.append((pattern, number_format))
        
        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(self.settings.get("syntax", "string_color", "#FF0000")))
        if self.settings.get("syntax", "string_bold", False):
            string_format.setFontWeight(QFont.Weight.Bold)
        pattern = QRegularExpression('"[^"]*"')
        self.highlighting_rules.append((pattern, string_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.settings.get("syntax", "comment_color", "#008000")))
        if self.settings.get("syntax", "comment_italic", True):
            comment_format.setFontItalic(True)
        pattern = QRegularExpression("'[^\n]*")
        self.highlighting_rules.append((pattern, comment_format))
        
    def highlightBlock(self, text):
        """Apply syntax highlighting to block."""
        for pattern, format_style in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format_style)



from PyQt6.QtWidgets import QWidget

class LineNumberArea(QWidget):
    """Line number area for code editor."""
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return self.code_editor.line_number_area_width()

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Code editor with line numbers and syntax highlighting."""
    
    def __init__(self, settings=None):
        super().__init__()
        
        self.settings = settings if settings else Settings()
        self.procedures = []  # List of (name, line_number) tuples
        self.variables = []  # List of variable names
        
        # Set font from settings
        font_family = self.settings.get("editor", "font_family", "Courier New")
        font_size = self.settings.get("editor", "font_size", 11)
        font = QFont(font_family, font_size)
        self.setFont(font)
        
        # Set tab width (4 spaces)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))
        
        # Syntax highlighter
        self.highlighter = VBSyntaxHighlighter(self.settings, self.document())
        
        # Setup auto-completion
        self.setup_completer()
        
        # Line numbers
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        # Timer for updating procedure list (debounced)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.parse_code)
        self.textChanged.connect(lambda: self.update_timer.start(500))  # 500ms delay
        
        # Apply colors after line_number_area is created
        self.apply_colors()

        # Temporary jump highlight support (init before any highlighting)
        self._temp_highlight = None
        self._temp_highlight_timer = QTimer(self)
        self._temp_highlight_timer.setSingleShot(True)
        self._temp_highlight_timer.timeout.connect(self._clear_temp_highlight)

        self.update_line_number_area_width(0)
        self.highlight_current_line()
        
    def setup_completer(self):
        """Setup auto-completion."""
        # Base completion list with VB keywords, Arduino functions, and constants
        self.base_completions = [
            # VB Keywords
            "Sub", "End Sub", "Function", "End Function", "Dim", "Const", "As",
            "If", "Then", "Else", "ElseIf", "End If",
            "For", "To", "Step", "Next",
            "While", "Wend", "Do", "Loop", "Until",
            "And", "Or", "Not", "Mod",
            "Return", "Exit Sub", "Exit Function",
            # Data Types
            "Integer", "Long", "Byte", "Boolean", "Single", "Double", "String",
            # Arduino Functions
            "Setup", "Loop",
            "PinMode", "DigitalWrite", "DigitalRead",
            "AnalogRead", "AnalogWrite", "AnalogReference",
            "Delay", "DelayMicroseconds", "Millis", "Micros",
            "SerialBegin", "SerialEnd", "SerialAvailable", "SerialRead", 
            "SerialPrint", "SerialPrintLine", "SerialWrite",
            "AttachInterrupt", "DetachInterrupt",
            "Tone", "NoTone", "ShiftOut", "ShiftIn", "PulseIn",
            "Map", "Constrain", "Min", "Max", "Abs", "Pow", "Sqrt",
            "Sin", "Cos", "Tan", "Random", "RandomSeed",
            # Arduino Constants
            "HIGH", "LOW", "INPUT", "OUTPUT", "INPUT_PULLUP",
            "LED_BUILTIN", "true", "false",
            "A0", "A1", "A2", "A3", "A4", "A5",
        ]
        
        # Create completer
        self.completer = QCompleter(self.base_completions, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.activated.connect(self.insert_completion)
        
        # Model for dynamic updates
        self.completion_model = QStringListModel(self.base_completions, self.completer)
        self.completer.setModel(self.completion_model)
        
    def insert_completion(self, completion):
        """Insert selected completion."""
        cursor = self.textCursor()
        # Find the start of the current word
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfWord)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfWord, QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(completion)
        self.setTextCursor(cursor)
        
    def text_under_cursor(self):
        """Get the word under cursor."""
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        return cursor.selectedText()
        
    def keyPressEvent(self, event):
        """Handle key press events for auto-completion."""
        # If completer is visible and has special keys
        if self.completer.popup().isVisible():
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Tab):
                # Use the completer's current completion (first match)
                completion = self.completer.currentCompletion()
                if completion:
                    self.insert_completion(completion)
                self.completer.popup().hide()
                event.accept()
                return
            elif event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Backtab):
                event.ignore()
                return
            elif event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                # Let the completer handle navigation
                event.ignore()
                return
                
        # Normal key processing
        super().keyPressEvent(event)
        
        # Trigger completion
        completion_prefix = self.text_under_cursor()
        
        # Don't show completer for very short text or numbers
        if len(completion_prefix) < 2 or completion_prefix.isdigit():
            self.completer.popup().hide()
            return
            
        # Update completer
        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            
        # Show completer popup
        if self.completer.completionCount() > 0:
            cursor_rect = self.cursorRect()
            cursor_rect.setWidth(
                self.completer.popup().sizeHintForColumn(0) +
                self.completer.popup().verticalScrollBar().sizeHint().width()
            )
            self.completer.complete(cursor_rect)
        else:
            self.completer.popup().hide()
        
    def parse_code(self):
        """Parse the code to find procedures and variables."""
        self.parse_procedures()
        self.parse_variables()
        self.update_completions()
        
    def parse_variables(self):
        """Parse the code to find all variable declarations."""
        self.variables = []
        text = self.toPlainText()
        lines = text.split('\n')
        
        # Regex patterns for variable declarations
        dim_pattern = re.compile(r'^\s*Dim\s+(\w+)', re.IGNORECASE)
        const_pattern = re.compile(r'^\s*Const\s+(\w+)', re.IGNORECASE)
        
        for line in lines:
            # Skip comments
            if line.strip().startswith("'"):
                continue
                
            # Check for Dim declaration
            match = dim_pattern.match(line)
            if match:
                var_name = match.group(1)
                if var_name not in self.variables:
                    self.variables.append(var_name)
                continue
                
            # Check for Const declaration
            match = const_pattern.match(line)
            if match:
                var_name = match.group(1)
                if var_name not in self.variables:
                    self.variables.append(var_name)
                    
    def update_completions(self):
        """Update completion list with procedures and variables."""
        # Combine base completions with user-defined items
        all_completions = list(self.base_completions)
        
        # Add procedure names (without Sub/Function prefix for completion)
        for proc_name, _ in self.procedures:
            # Extract just the name part
            name = proc_name.split()[-1] if ' ' in proc_name else proc_name
            if name not in all_completions:
                all_completions.append(name)
                
        # Add variables
        for var_name in self.variables:
            if var_name not in all_completions:
                all_completions.append(var_name)
                
        # Update model
        all_completions.sort(key=str.lower)
        self.completion_model.setStringList(all_completions)
        
    def parse_procedures(self):
        """Parse the code to find all Sub and Function declarations."""
        self.procedures = []
        text = self.toPlainText()
        lines = text.split('\n')
        
        # Regex patterns for Sub and Function declarations
        sub_pattern = re.compile(r'^\s*Sub\s+(\w+)', re.IGNORECASE)
        func_pattern = re.compile(r'^\s*Function\s+(\w+)', re.IGNORECASE)
        
        for i, line in enumerate(lines):
            # Skip comments
            if line.strip().startswith("'"):
                continue
                
            # Check for Sub declaration
            match = sub_pattern.match(line)
            if match:
                proc_name = match.group(1)
                self.procedures.append((f"Sub {proc_name}", i + 1))  # +1 for 1-based line numbers
                continue
                
            # Check for Function declaration
            match = func_pattern.match(line)
            if match:
                proc_name = match.group(1)
                self.procedures.append((f"Function {proc_name}", i + 1))
                
        # Notify any connected procedure combo that the list has changed
        if hasattr(self, 'procedure_combo'):
            self.update_procedure_combo()
            
    def update_procedure_combo(self):
        """Update the procedure combo box with current procedures."""
        if not hasattr(self, 'procedure_combo'):
            return
            
        # Block signals to prevent jumping while updating
        self.procedure_combo.blockSignals(True)
        
        # Save current text to restore selection if possible
        current_text = self.procedure_combo.currentText()
        
        # Clear and repopulate
        self.procedure_combo.clear()
        self.procedure_combo.addItem("(General)", 0)
        
        for proc_name, line_num in self.procedures:
            self.procedure_combo.addItem(proc_name, line_num)
            
        # Try to restore previous selection
        index = self.procedure_combo.findText(current_text)
        if index >= 0:
            self.procedure_combo.setCurrentIndex(index)
        else:
            self.procedure_combo.setCurrentIndex(0)
            
        self.procedure_combo.blockSignals(False)
        
    def goto_procedure(self, index):
        """Navigate to the selected procedure."""
        line_number = self.procedure_combo.itemData(index)
        if line_number and line_number > 0:
            # Move cursor to the specified line
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.MoveAnchor, line_number - 1)
            self.setTextCursor(cursor)
            
            # Ensure the line is visible and centered if possible
            self.centerCursor()
            self.setFocus()

        
    def apply_colors(self):
        """Apply color scheme from settings."""
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(self.settings.get("editor", "background_color", "#FFFFFF")))
        palette.setColor(QPalette.ColorRole.Text, QColor(self.settings.get("editor", "text_color", "#000000")))
        self.setPalette(palette)
        self.line_number_area.update()
        
    def apply_settings(self, settings):
        """Apply new settings to editor."""
        self.settings = settings
        
        # Update font
        font_family = self.settings.get("editor", "font_family", "Courier New")
        font_size = self.settings.get("editor", "font_size", 11)
        font = QFont(font_family, font_size)
        self.setFont(font)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))
        
        # Update colors
        self.apply_colors()
        
        # Update syntax highlighting
        self.highlighter.settings = settings
        self.highlighter.update_highlighting_rules()
        self.highlighter.rehighlight()
        
        # Update line number area
        self.update_line_number_area_width(0)
        self.highlight_current_line()
        
    def line_number_area_width(self):
        """Calculate width needed for line numbers."""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
        
    def update_line_number_area_width(self, _):
        """Update line number area width."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        
    def update_line_number_area(self, rect, dy):
        """Update line number area on scroll."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                         self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
            
    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
        
    def line_number_area_paint_event(self, event):
        """Paint line numbers."""
        painter = QPainter(self.line_number_area)
        bg_color = self.settings.get("editor", "line_number_bg", "#F0F0F0")
        painter.fillRect(event.rect(), QColor(bg_color))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                fg_color = self.settings.get("editor", "line_number_fg", "#808080")
                painter.setPen(QColor(fg_color))
                painter.drawText(
                    0, int(top), self.line_number_area.width() - 2,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number
                )
                
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
            
    def highlight_current_line(self):
        """Highlight the current line."""
        extra_selections = []
        
        if not self.isReadOnly():
            # Create selection for current line
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(self.settings.get("editor", "current_line_color", "#FFFFCC"))
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
            # Include temporary jump highlight if present
            if self._temp_highlight is not None:
                extra_selections.append(self._temp_highlight)
            
        self.setExtraSelections(extra_selections)

    def highlight_line(self, line_number: int, duration_ms: int = 3000):
        """Temporarily highlight a specific line for visual guidance."""
        if line_number <= 0:
            return
        # Create a cursor positioned at the start of the target line
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.MoveAnchor, line_number - 1)

        sel = QTextEdit.ExtraSelection()
        jump_color = QColor(self.settings.get("editor", "jump_highlight_color", "#FFD7A1"))
        sel.format.setBackground(jump_color)
        sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        sel.cursor = cursor
        sel.cursor.clearSelection()
        self._temp_highlight = sel
        # Refresh selections to include temp highlight
        self.highlight_current_line()
        # Auto-clear after duration
        self._temp_highlight_timer.start(max(1, duration_ms))

    def _clear_temp_highlight(self):
        self._temp_highlight = None
        self.highlight_current_line()


class CodeEditorWidget(QWidget):
    """Widget combining procedure dropdown and code editor."""
    
    def __init__(self, settings=None):
        super().__init__()
        
        self.settings = settings if settings else Settings()
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Create procedure dropdown
        self.procedure_combo = QComboBox()
        self.procedure_combo.addItem("(General)", 0)
        self.procedure_combo.setMinimumWidth(200)
        layout.addWidget(self.procedure_combo)
        
        # Create code editor
        self.editor = CodeEditor(settings)
        layout.addWidget(self.editor)
        
        # Connect editor to combo box
        self.editor.procedure_combo = self.procedure_combo
        self.procedure_combo.currentIndexChanged.connect(self.editor.goto_procedure)
        
        # Parse procedures when editor content changes
        self.editor.textChanged.connect(self.on_text_changed)
        
    def on_text_changed(self):
        """Handle text changes in the editor."""
        # The timer in the editor will trigger parse_procedures automatically
        pass
        
    def toPlainText(self):
        """Get plain text from editor."""
        return self.editor.toPlainText()
        
    def setPlainText(self, text):
        """Set plain text in editor."""
        self.editor.setPlainText(text)
        # Trigger immediate parse of procedures and variables
        self.editor.parse_code()
        
    def document(self):
        """Get the editor's document."""
        return self.editor.document()
        
    def apply_settings(self, settings):
        """Apply settings to editor."""
        self.settings = settings
        self.editor.apply_settings(settings)
