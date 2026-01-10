"""Hover tooltip support for showing function descriptions."""

import re
from PyQt6.QtWidgets import QToolTip
from PyQt6.QtCore import QPoint
from .completion_docs import DESCRIPTIONS


def get_word_at_position(text, position):
    """Extract the word at the given position in text."""
    if position < 0 or position >= len(text):
        return ""
    
    # Find word boundaries
    start = position
    while start > 0 and (text[start - 1].isalnum() or text[start - 1] in ('_', '$', '.')):
        start -= 1
    
    end = position
    while end < len(text) and (text[end].isalnum() or text[end] in ('_', '$', '.')):
        end += 1
    
    return text[start:end]


def show_hover_tooltip(editor, event):
    """Show tooltip with function description when hovering over code."""
    # Get cursor position from mouse event
    cursor = editor.cursorForPosition(event.pos())
    cursor.select(cursor.SelectionType.WordUnderCursor)
    word = cursor.selectedText()
    
    if not word:
        return
    
    # Check if word has a description
    description = DESCRIPTIONS.get(word, None)
    
    if description:
        # Show tooltip at mouse position
        global_pos = editor.mapToGlobal(event.pos())
        QToolTip.showText(global_pos, description, editor)
