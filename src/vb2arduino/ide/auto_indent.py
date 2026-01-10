"""Auto-indentation support for VB-like syntax."""

import re


class AutoIndenter:
    """Handles automatic indentation for VB-like code."""
    
    # Keywords that increase indentation
    INDENT_INCREASE = [
        r'^\s*(Sub|Function)\b',
        r'^\s*If\b.*Then\s*$',
        r'^\s*ElseIf\b.*Then\s*$',
        r'^\s*Else\s*$',
        r'^\s*Select\s+Case\b',
        r'^\s*Case\b',
        r'^\s*For\b',
        r'^\s*While\b',
        r'^\s*Do\b',
        r'^\s*With\b',
        r'^\s*Type\b',
    ]
    
    # Keywords that decrease indentation
    INDENT_DECREASE = [
        r'^\s*End\s+(Sub|Function|If|Select|With|Type)\b',
        r'^\s*(Next|Wend|Loop)\b',
        r'^\s*ElseIf\b',
        r'^\s*Else\s*$',
        r'^\s*Case\b',
    ]
    
    # Keywords that decrease current line but increase next
    INDENT_BOTH = [
        r'^\s*ElseIf\b',
        r'^\s*Else\s*$',
        r'^\s*Case\b',
    ]
    
    def __init__(self, tab_width=4):
        self.tab_width = tab_width
        self.indent_increase_patterns = [re.compile(p, re.IGNORECASE) for p in self.INDENT_INCREASE]
        self.indent_decrease_patterns = [re.compile(p, re.IGNORECASE) for p in self.INDENT_DECREASE]
        self.indent_both_patterns = [re.compile(p, re.IGNORECASE) for p in self.INDENT_BOTH]
    
    def get_indent_level(self, line):
        """Get the indentation level of a line (number of leading spaces)."""
        stripped = line.lstrip()
        return len(line) - len(stripped)
    
    def should_increase_indent(self, line):
        """Check if line should increase next line's indentation."""
        stripped = line.strip()
        for pattern in self.indent_increase_patterns:
            if pattern.match(line):
                return True
        return False
    
    def should_decrease_indent(self, line):
        """Check if line should decrease its own indentation."""
        for pattern in self.indent_decrease_patterns:
            if pattern.match(line):
                return True
        return False
    
    def should_both(self, line):
        """Check if line should decrease its own and increase next."""
        for pattern in self.indent_both_patterns:
            if pattern.match(line):
                return True
        return False
    
    def calculate_indent(self, previous_line, current_line=""):
        """Calculate the indent for the current line based on the previous line."""
        if not previous_line:
            return 0
        
        prev_indent = self.get_indent_level(previous_line)
        
        # Check if current line should be dedented
        if current_line and self.should_decrease_indent(current_line):
            return max(0, prev_indent - self.tab_width)
        
        # Check if current line is one of the "both" keywords
        if current_line and self.should_both(current_line):
            return max(0, prev_indent - self.tab_width)
        
        # Check if previous line increases indent
        if self.should_increase_indent(previous_line):
            return prev_indent + self.tab_width
        
        return prev_indent
    
    def auto_indent_line(self, cursor, previous_line):
        """Auto-indent the current line based on previous line."""
        indent = self.calculate_indent(previous_line)
        cursor.insertText(' ' * indent)
    
    def handle_return_key(self, editor):
        """Handle Enter key press with auto-indentation."""
        cursor = editor.textCursor()
        
        # Get current line text before Enter
        cursor.select(cursor.SelectionType.LineUnderCursor)
        current_line = cursor.selectedText()
        
        # Move cursor to end of selection and insert newline
        cursor.clearSelection()
        cursor.movePosition(cursor.MoveOperation.EndOfLine)
        cursor.insertText('\n')
        
        # Calculate and apply indent
        indent = self.calculate_indent(current_line)
        cursor.insertText(' ' * indent)
        
        editor.setTextCursor(cursor)
        return True  # Event handled
