"""Code snippets support for quick template insertion."""

from PyQt6.QtCore import Qt


class SnippetManager:
    """Manages code snippets for quick insertion."""
    
    SNIPPETS = {
        'sub': {
            'template': '''Sub ${1:ProcedureName}()
    ${2:' Your code here}
End Sub''',
            'description': 'Sub procedure'
        },
        'func': {
            'template': '''Function ${1:FunctionName}(${2:params}) As ${3:Integer}
    ${4:' Your code here}
    Return ${5:0}
End Function''',
            'description': 'Function with return'
        },
        'if': {
            'template': '''If ${1:condition} Then
    ${2:' Your code}
End If''',
            'description': 'If-Then block'
        },
        'ifelse': {
            'template': '''If ${1:condition} Then
    ${2:' True branch}
Else
    ${3:' False branch}
End If''',
            'description': 'If-Then-Else block'
        },
        'for': {
            'template': '''For ${1:i} = ${2:0} To ${3:10}
    ${4:' Your code}
Next''',
            'description': 'For loop'
        },
        'forstep': {
            'template': '''For ${1:i} = ${2:0} To ${3:10} Step ${4:1}
    ${5:' Your code}
Next''',
            'description': 'For loop with step'
        },
        'while': {
            'template': '''While ${1:condition}
    ${2:' Your code}
Wend''',
            'description': 'While loop'
        },
        'do': {
            'template': '''Do While ${1:condition}
    ${2:' Your code}
Loop''',
            'description': 'Do-While loop'
        },
        'select': {
            'template': '''Select Case ${1:expression}
    Case ${2:0}
        ${3:' Case 0}
    Case ${4:1}
        ${5:' Case 1}
    Case Else
        ${6:' Default}
End Select''',
            'description': 'Select Case block'
        },
        'with': {
            'template': '''With ${1:object}
    ${2:' Your code}
End With''',
            'description': 'With block'
        },
        'dim': {
            'template': 'Dim ${1:variable} As ${2:Integer}',
            'description': 'Variable declaration'
        },
        'setup': {
            'template': '''Sub Setup()
    ${1:' Initialization code}
End Sub''',
            'description': 'Arduino Setup'
        },
        'loop': {
            'template': '''Sub Loop()
    ${1:' Main loop code}
End Sub''',
            'description': 'Arduino Loop'
        },
    }
    
    def __init__(self):
        self.current_snippet = None
        self.current_field = 0
        self.field_positions = []
    
    def get_snippet(self, trigger):
        """Get snippet by trigger word."""
        return self.SNIPPETS.get(trigger.lower())
    
    def expand_snippet(self, editor, trigger):
        """Expand snippet at cursor position."""
        snippet = self.get_snippet(trigger)
        if not snippet:
            return False
        
        cursor = editor.textCursor()
        
        # Remove the trigger word
        cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.KeepAnchor, len(trigger))
        
        # Parse template and extract placeholders
        template = snippet['template']
        self.field_positions = []
        self.current_field = 0
        
        # Simple placeholder expansion (replace ${n:text} with text and track positions)
        import re
        pattern = r'\$\{(\d+):([^}]*)\}'
        
        # Store original position
        start_pos = cursor.position()
        
        # Replace placeholders with their default text
        expanded_text = template
        offset = 0
        
        for match in re.finditer(pattern, template):
            field_num = int(match.group(1))
            default_text = match.group(2)
            
            # Calculate position in expanded text
            pos_in_template = match.start() + offset
            placeholder_len = len(match.group(0))
            
            # Store field position
            self.field_positions.append({
                'num': field_num,
                'start': start_pos + pos_in_template,
                'length': len(default_text)
            })
            
            # Replace in text
            expanded_text = expanded_text.replace(match.group(0), default_text, 1)
            offset += len(default_text) - placeholder_len
        
        # Insert the expanded text
        cursor.insertText(expanded_text)
        
        # Select first placeholder
        if self.field_positions:
            self.field_positions.sort(key=lambda x: x['num'])
            first_field = self.field_positions[0]
            cursor.setPosition(first_field['start'])
            cursor.setPosition(first_field['start'] + first_field['length'], cursor.MoveMode.KeepAnchor)
            editor.setTextCursor(cursor)
        
        return True
    
    def try_expand_snippet(self, editor):
        """Try to expand snippet if trigger word is followed by Tab."""
        cursor = editor.textCursor()
        cursor.select(cursor.SelectionType.WordUnderCursor)
        trigger = cursor.selectedText()
        
        if trigger and self.get_snippet(trigger):
            return self.expand_snippet(editor, trigger)
        
        return False
