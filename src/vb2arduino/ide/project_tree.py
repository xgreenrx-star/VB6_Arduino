"""Project tree view for VB2Arduino IDE."""

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
import re


class ProjectTreeView(QTreeWidget):
    """Tree view showing project structure like VB6 Project Explorer."""
    
    item_clicked = pyqtSignal(int)  # Emits line number when item is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configure tree
        self.setHeaderLabel("Project Explorer")
        self.setMinimumWidth(200)
        self.setMaximumWidth(350)
        
        # Connect signals
        self.itemClicked.connect(self._on_item_clicked)
        
        # Store current data
        self.procedures = []
        self.variables = []
        self.constants = []
        self.includes = []
        
    def _on_item_clicked(self, item, column):
        """Handle item click."""
        line_number = item.data(0, Qt.ItemDataRole.UserRole)
        if line_number is not None:
            self.item_clicked.emit(line_number)
            
    def update_from_code(self, code_text):
        """Parse code and update tree structure."""
        self.clear()
        
        # Parse code
        self._parse_code(code_text)
        
        # Create root item for the project
        root = QTreeWidgetItem(self, ["VB2Arduino Project"])
        font = QFont()
        font.setBold(True)
        root.setFont(0, font)
        root.setExpanded(True)
        
        # Add Includes section
        if self.includes:
            includes_item = QTreeWidgetItem(root, ["Includes"])
            includes_item.setFont(0, font)
            includes_item.setExpanded(True)
            for include_name, line_num in self.includes:
                item = QTreeWidgetItem(includes_item, [include_name])
                item.setData(0, Qt.ItemDataRole.UserRole, line_num)
                
        # Add Constants section
        if self.constants:
            const_item = QTreeWidgetItem(root, ["Constants"])
            const_item.setFont(0, font)
            const_item.setExpanded(True)
            for const_name, const_type, line_num in self.constants:
                display = f"{const_name}: {const_type}" if const_type else const_name
                item = QTreeWidgetItem(const_item, [display])
                item.setData(0, Qt.ItemDataRole.UserRole, line_num)
                
        # Add Variables section
        if self.variables:
            var_item = QTreeWidgetItem(root, ["Variables"])
            var_item.setFont(0, font)
            var_item.setExpanded(True)
            for var_name, var_type, line_num in self.variables:
                display = f"{var_name}: {var_type}" if var_type else var_name
                item = QTreeWidgetItem(var_item, [display])
                item.setData(0, Qt.ItemDataRole.UserRole, line_num)
                
        # Add Procedures section
        if self.procedures:
            proc_item = QTreeWidgetItem(root, ["Procedures"])
            proc_item.setFont(0, font)
            proc_item.setExpanded(True)
            
            # Separate Subs and Functions
            subs = [(name, params, line) for ptype, name, params, ret_type, line in self.procedures if ptype == "Sub"]
            funcs = [(name, params, ret, line) for ptype, name, params, ret, line in self.procedures if ptype == "Function"]
            
            # Add Subs
            if subs:
                subs_item = QTreeWidgetItem(proc_item, ["Subs"])
                subs_item.setExpanded(True)
                for name, params, line_num in subs:
                    display = f"{name}({params})" if params else name
                    item = QTreeWidgetItem(subs_item, [display])
                    item.setData(0, Qt.ItemDataRole.UserRole, line_num)
                    
            # Add Functions
            if funcs:
                funcs_item = QTreeWidgetItem(proc_item, ["Functions"])
                funcs_item.setExpanded(True)
                for name, params, ret_type, line_num in funcs:
                    display = f"{name}({params})"
                    if ret_type:
                        display += f" As {ret_type}"
                    item = QTreeWidgetItem(funcs_item, [display])
                    item.setData(0, Qt.ItemDataRole.UserRole, line_num)
                    
    def _parse_code(self, code_text):
        """Parse code to extract structure."""
        self.procedures = []
        self.variables = []
        self.constants = []
        self.includes = []
        
        lines = code_text.split('\n')
        
        # Regex patterns
        include_pattern = re.compile(r'^\s*#Include\s+[<"](.+)[>"]', re.IGNORECASE)
        const_pattern = re.compile(r'^\s*Const\s+(\w+)(?:\s+As\s+(\w+))?', re.IGNORECASE)
        dim_pattern = re.compile(r'^\s*Dim\s+(\w+)(?:\s+As\s+(\w+))?', re.IGNORECASE)
        sub_pattern = re.compile(r'^\s*Sub\s+(\w+)\s*\((.*?)\)', re.IGNORECASE)
        func_pattern = re.compile(r'^\s*Function\s+(\w+)\s*\((.*?)\)(?:\s+As\s+(\w+))?', re.IGNORECASE)
        
        for i, line in enumerate(lines):
            line_num = i + 1  # 1-based line numbers
            
            # Skip comments
            if line.strip().startswith("'"):
                continue
                
            # Check for includes
            match = include_pattern.match(line)
            if match:
                include_name = match.group(1)
                self.includes.append((include_name, line_num))
                continue
                
            # Check for constants
            match = const_pattern.match(line)
            if match:
                const_name = match.group(1)
                const_type = match.group(2) if match.group(2) else ""
                self.constants.append((const_name, const_type, line_num))
                continue
                
            # Check for variables
            match = dim_pattern.match(line)
            if match:
                var_name = match.group(1)
                var_type = match.group(2) if match.group(2) else ""
                self.variables.append((var_name, var_type, line_num))
                continue
                
            # Check for Sub declarations
            match = sub_pattern.match(line)
            if match:
                sub_name = match.group(1)
                params = match.group(2).strip()
                self.procedures.append(("Sub", sub_name, params, None, line_num))
                continue
                
            # Check for Function declarations
            match = func_pattern.match(line)
            if match:
                func_name = match.group(1)
                params = match.group(2).strip()
                ret_type = match.group(3) if match.group(3) else ""
                self.procedures.append(("Function", func_name, params, ret_type, line_num))
                continue
