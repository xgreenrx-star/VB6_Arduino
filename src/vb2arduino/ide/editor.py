"""Code editor with VB syntax highlighting."""

from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit, QComboBox, QVBoxLayout, QCompleter, QTreeView, QHeaderView
from PyQt6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont, 
    QPainter, QTextFormat, QTextCursor, QPalette
)
from PyQt6.QtCore import Qt, QRect, QRegularExpression, QTimer, QStringListModel, QVariant
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from .completion_catalog import get_all_completions
from .completion_docs import DESCRIPTIONS
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
            # Blocks & declarations
            "\\bSub\\b", "\\bEnd\\b", "\\bFunction\\b", "\\bDim\\b", "\\bConst\\b", "\\bStatic\\b",
            "\\bAs\\b", "\\bOptional\\b", "\\bByRef\\b", "\\bByVal\\b",
            "\\bType\\b", "\\bEnd\\s+Type\\b",
            # Control flow
            "\\bIf\\b", "\\bThen\\b", "\\bElse\\b", "\\bElseIf\\b", "\\bEnd\\s+If\\b",
            "\\bSelect\\s+Case\\b", "\\bCase\\b", "\\bCase\\s+Else\\b", "\\bEnd\\s+Select\\b",
            "\\bFor\\b", "\\bTo\\b", "\\bStep\\b", "\\bNext\\b",
            "\\bWhile\\b", "\\bWend\\b",
            "\\bDo\\b", "\\bLoop\\b", "\\bLoop\\s+While\\b", "\\bLoop\\s+Until\\b",
            # Misc
            "\\bWith\\b", "\\bEnd\\s+With\\b",
            "\\bAnd\\b", "\\bOr\\b", "\\bNot\\b", "\\bMod\\b",
            "\\bReturn\\b", "\\bExit\\s+Sub\\b", "\\bExit\\s+Function\\b", "\\bExit\\s+For\\b",
            "\\bGoto\\b", "^\\s*\\w+:$",
            "\\bOption\\s+Base\\b",
            # Types
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
            # Entry points
            "\\bSetup\\b", "\\bLoop\\b",
            # Arduino helpers
            "\\bPinMode\\b", "\\bDigitalWrite\\b", "\\bDigitalRead\\b",
            "\\bAnalogRead\\b", "\\bAnalogWrite\\b", "\\bDelay\\b", "\\bMillis\\b", "\\bMicros\\b",
            "\\bSerialBegin\\b", "\\bSerialPrint\\b", "\\bSerialPrintLine\\b", "\\bSerialAvailable\\b", "\\bSerialRead\\b",
            # String functions
            "\\bSplit\\b", "\\bJoin\\b", "\\bFilter\\b", "\\bInStrRev\\b", "\\bStrComp\\b", "\\bStrReverse\\b",
            "\\bVal\\b", "\\bHex\\$\\b", "\\bOct\\$\\b", "\\bChr\\$\\b", "\\bAsc\\b", "\\bSpace\\b", "\\bString\\b",
            # Math/time
            "\\bSqr\\b", "\\bRound\\b", "\\bFix\\b", "\\bSgn\\b", "\\bLog\\b", "\\bExp\\b", "\\bAtn\\b",
            "\\bSin\\b", "\\bCos\\b", "\\bTan\\b", "\\bAbs\\b", "\\bInt\\b", "\\bRnd\\b",
            "\\bTimer\\b", "\\bRandomize\\b",
            # Choice helpers
            "\\bChoose\\b", "\\bSwitch\\b",
            # Convenience
            "\\bRGB\\b", "\\bSERVO_DEG2PULSE\\b", "\\bSERVO_CLAMP\\b", "\\bSERVO_CLAMP_DEG2PULSE\\b",
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
            # Arduino
            "\\bOUTPUT\\b", "\\bINPUT\\b", "\\bINPUT_PULLUP\\b",
            "\\bHIGH\\b", "\\bLOW\\b",
            # VB-like
            "\\bvbCr\\b", "\\bvbLf\\b", "\\bvbCrLf\\b", "\\bvbTab\\b", "\\bvbNullString\\b", "\\bvbNullChar\\b",
            "\\bvbTrue\\b", "\\bvbFalse\\b",
            # Math/status
            "\\bPI\\b", "\\bTAU\\b", "\\bDEG2RAD\\b", "\\bRAD2DEG\\b", "\\bINF\\b", "\\bNAN\\b", "\\bOK\\b", "\\bFAILED\\b",
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
        """Setup auto-completion with comprehensive catalog."""
        # Load comprehensive catalog from completion_catalog
        self.base_completions = get_all_completions()

        # Create completer with two-column model (command, description)
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        # Allow matching anywhere to keep suggestions useful while typing
        try:
            self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        except Exception:
            pass
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.activated.connect(self.insert_completion)
        # Build initial model
        self._build_completion_model(self.base_completions)
        # Use first column (command) for completion text
        self.completer.setCompletionColumn(0)
        # Use a tree view popup to display two columns
        popup = QTreeView()
        popup.setRootIsDecorated(False)
        popup.setItemsExpandable(False)
        popup.setUniformRowHeights(True)
        popup.header().setStretchLastSection(True)
        popup.header().setDefaultSectionSize(220)
        # Widen columns for readability: names and descriptions
        # Prefer explicit column widths to avoid platform-specific header issues
        popup.setColumnWidth(0, 260)
        popup.setColumnWidth(1, 520)
        popup.setMinimumWidth(820)
        self.completer.setPopup(popup)

    def _build_completion_model(self, items_list):
        """Build a two-column (command, description) model for the completer."""
        model = QStandardItemModel(0, 2, self)
        model.setHeaderData(0, Qt.Orientation.Horizontal, "Command")
        model.setHeaderData(1, Qt.Orientation.Horizontal, "Description")
        for cmd in items_list:
            desc = DESCRIPTIONS.get(cmd, "")
            name_item = QStandardItem(cmd)
            desc_item = QStandardItem(desc)
            name_item.setToolTip(desc)
            desc_item.setToolTip(desc)
            model.appendRow([name_item, desc_item])
        self.completion_model = model
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
        # Navigation keys should close the popup and move the cursor, not navigate the popup
        if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Page_Up, Qt.Key.Key_Page_Down, 
                          Qt.Key.Key_Home, Qt.Key.Key_End):
            self.completer.popup().hide()
            super().keyPressEvent(event)
            return
        
        # Ctrl+Space: force popup with entire catalog
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Space:
            self.completer.setCompletionPrefix("")
            # Position popup at cursor
            cursor_rect = self.cursorRect()
            cursor_rect.setWidth(
                self.completer.popup().sizeHintForColumn(0) +
                self.completer.popup().verticalScrollBar().sizeHint().width()
            )
            self.completer.complete(cursor_rect)
            return
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
                self.completer.popup().hide()
                event.accept()
                return
                
        # Normal key processing
        super().keyPressEvent(event)
        
        # Trigger completion
        completion_prefix = self.text_under_cursor()
        
        # Don't show completer for empty text or pure numbers
        if len(completion_prefix) < 1 or completion_prefix.isdigit():
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
                
        # Update model (preserve popup state and prefix to avoid flicker)
        was_visible = self.completer.popup().isVisible() if hasattr(self, 'completer') else False
        current_prefix = self.completer.completionPrefix() if hasattr(self, 'completer') else ""
        all_completions.sort(key=str.lower)
        self._build_completion_model(all_completions)
        if was_visible:
            # Restore prefix and popup position after model reset
            if current_prefix:
                self.completer.setCompletionPrefix(current_prefix)
            cursor_rect = self.cursorRect()
            cursor_rect.setWidth(
                self.completer.popup().sizeHintForColumn(0) +
                self.completer.popup().verticalScrollBar().sizeHint().width()
            )
            if self.completer.completionCount() > 0:
                self.completer.complete(cursor_rect)
        
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
    
    def __init__(self, settings=None, includes=None, include_callback=None):
        super().__init__()
        self.settings = settings if settings else Settings()
        self.includes = includes or []
        self.include_callback = include_callback
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        # Source/Includes dropdown
        self.view_combo = QComboBox()
        self.view_combo.addItem("Source")
        self.view_combo.addItem("Includes")
        self.view_combo.setMinimumWidth(120)
        layout.addWidget(self.view_combo)
        # Widget stack: code editor and includes list
        from PyQt6.QtWidgets import QStackedWidget, QListWidget
        self.stack = QStackedWidget()
        # Code editor
        self.editor = CodeEditor(self.settings)
        # Includes list
        self.includes_list = QListWidget()
        self.refresh_includes()
        self.stack.addWidget(self.editor)
        self.stack.addWidget(self.includes_list)
        layout.addWidget(self.stack)
        # Procedure dropdown (for code editor)
        self.procedure_combo = QComboBox()
        self.procedure_combo.addItem("(General)", 0)
        self.procedure_combo.setMinimumWidth(200)
        layout.addWidget(self.procedure_combo)
        self.editor.procedure_combo = self.procedure_combo
        self.procedure_combo.currentIndexChanged.connect(self.editor.goto_procedure)
        # Connect signals
        self.editor.textChanged.connect(self.on_text_changed)
        self.view_combo.currentIndexChanged.connect(self._on_view_changed)
        self.includes_list.itemDoubleClicked.connect(self._on_include_clicked)

    def refresh_includes(self):
        self.includes_list.clear()
        for inc in self.includes:
            self.includes_list.addItem(inc)

    def _on_view_changed(self, idx):
        self.stack.setCurrentIndex(idx)

    def _on_include_clicked(self, item):
        if self.include_callback:
            self.include_callback(item.text())
        
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
