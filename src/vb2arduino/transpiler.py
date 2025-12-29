import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class TranspileResult:
    cpp: str


class VBTranspiler:
    """Minimal VB6-like to Arduino C++ transpiler for a safe subset."""

    def __init__(self) -> None:
        self.global_lines: List[str] = []
        self.setup_lines: List[str] = []
        self.loop_lines: List[str] = []
        self.function_lines: List[str] = []
        self.function_signatures: List[str] = []  # For forward declarations
        self.block_stack: List[str] = []
        self.includes: set = set()
        self.current_function: str | None = None
        self.pointer_vars: set[str] = set()
        self.pointer_default_types = {"BLEServer", "BLEService", "BLECharacteristic", "BLEAdvertising"}
        self.value_default_types = {"Preferences"}

    def transpile(self, source: str) -> TranspileResult:
        self.global_lines.clear()
        self.setup_lines.clear()
        self.loop_lines.clear()
        self.function_lines.clear()
        self.function_signatures.clear()
        self.block_stack.clear()
        self.includes.clear()
        self.current_function = None
        self.pointer_vars.clear()

        current = None  # None, "setup", "loop", "function"
        label_set = set()
        # Track VB source line numbers for error mapping
        for vb_line_no, raw in enumerate(source.splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith("'") or line.upper().startswith("REM"):
                # Support Rem as comment
                continue

            # Label: support (must be at start of line, not indented)
            m_label = re.match(r"^(\w+):$", line)
            if m_label:
                label_set.add(m_label.group(1))
                target = self._target_lines(current)
                target.append(f"{m_label.group(1)}:")
                continue

            upper = line.upper()
            
            # Include/Import statements
            if upper.startswith("#INCLUDE "):
                include = line[9:].strip()
                self.includes.add(include)
                continue
            
            if upper.startswith("CONST "):
                # Emit a mapping marker to correlate C++ lines back to VB
                self.global_lines.append(f"// __VB_LINE__:{vb_line_no}")
                self.global_lines.append(self._emit_const(line))
                continue
            if upper.startswith("DIM "):
                target = self._target_lines(current)
                statement = self._emit_dim(line)
                # Add newlines to function statements for proper formatting
                if statement:
                    if current == "function":
                        target.append(f"// __VB_LINE__:{vb_line_no}\n")
                        target.append(statement + "\n")
                    else:
                        target.append(f"// __VB_LINE__:{vb_line_no}")
                        target.append(statement)
                continue
            if upper.startswith("SUB SETUP"):
                current = "setup"
                continue
            if upper.startswith("SUB LOOP"):
                current = "loop"
                continue
            if upper.startswith("SUB ") or upper.startswith("FUNCTION "):
                current = "function"
                self.current_function = self._emit_function_header(line)
                continue
            if upper == "END SUB" or upper == "END FUNCTION":
                if current == "function":
                    self.function_lines.append("}\n")
                    self.current_function = None
                current = None
                continue

            target = self._target_lines(current)
            statement = self._emit_statement(line)
            # Add mapping marker and newlines to function statements for proper formatting
            if statement:
                if current == "function":
                    target.append(f"// __VB_LINE__:{vb_line_no}\n")
                    target.append(statement + "\n")
                else:
                    target.append(f"// __VB_LINE__:{vb_line_no}")
                    target.append(statement)

        cpp = self._render_cpp()
        return TranspileResult(cpp=cpp)

    def _target_lines(self, current: str | None) -> List[str]:
        if current == "setup":
            return self.setup_lines
        if current == "loop":
            return self.loop_lines
        if current == "function":
            return self.function_lines
        return self.global_lines

    def _emit_const(self, line: str) -> str:
        # Const LED = 2  or  Const LED As Integer = 2
        # Try with type annotation first
        m = re.match(r"CONST\s+(\w+)(?:\s+AS\s+\w+)?\s*=\s*(.+)", line, re.IGNORECASE)
        if not m:
            return f"// TODO const: {line}"
        name, value = m.groups()
        value_expr = self._expr(value)
        if re.match(r'^".*"$', value_expr):
            return f"const char* {name} = {value_expr};"
        return f"const auto {name} = {value_expr};"
    
    def _emit_function_header(self, line: str) -> str:
        # Sub MyFunc(param1 As Integer) or Function MyFunc() As Integer
        is_function = line.upper().startswith("FUNCTION")
        
        if is_function:
            m = re.match(r"FUNCTION\s+(\w+)\s*\(([^)]*)\)(?:\s+AS\s+(\w+))?", line, re.IGNORECASE)
            if not m:
                return line
            name, params, ret_type = m.groups()
            ret_c_type = self._map_type(ret_type) if ret_type else "void"
        else:
            # Sub with optional parentheses
            m = re.match(r"SUB\s+(\w+)(?:\s*\(([^)]*)\))?", line, re.IGNORECASE)
            if not m:
                return line
            name, params = m.groups()
            params = params or ""  # Handle None when no parentheses
            ret_c_type = "void"
        
        # Parse parameters
        param_list = []
        if params:
            for param in params.split(","):
                param = param.strip()
                pm = re.match(r"(\w+)(?:\s+AS\s+([\w\*]+))?", param, re.IGNORECASE)
                if pm:
                    pname, ptype = pm.groups()
                    is_pointer = bool(ptype and ptype.endswith("*"))
                    base_type = ptype[:-1] if is_pointer else ptype
                    pc_type = self._map_type(base_type)
                    if is_pointer:
                        self.pointer_vars.add(pname)
                        pc_type = f"{pc_type}*"
                    param_list.append(f"{pc_type} {pname}")
        
        params_str = ", ".join(param_list) if param_list else ""
        header = f"{ret_c_type} {name}({params_str}) {{\n"
        signature = f"{ret_c_type} {name}({params_str});"
        self.function_signatures.append(signature)
        self.function_lines.append(header)
        return name

    def _emit_dim(self, line: str) -> str:
        # Dim x As Integer  | Dim x | Dim arr(10) As String | Dim arr(MAX_SIZE) As String | Dim pServer As BLEServer*
        # Array syntax: Dim name(size) As Type - size can be number or identifier
        m_array = re.match(r"DIM\s+(\w+)\s*\((\w+)\)(?:\s+AS\s+([\w\*]+))?", line, re.IGNORECASE)
        if m_array:
            name, size, type_token = m_array.groups()
            base_type, is_pointer = self._type_with_pointer(type_token)
            c_type = self._map_type(base_type)
            # Track pointer arrays (rare)
            if is_pointer:
                self.pointer_vars.add(name)
                c_type = f"{c_type}*"
            # Check if size is a number or identifier
            if size.isdigit():
                array_size = int(size) + 1  # VB arrays are 0-based but size is max index
            else:
                # It's an identifier (constant), use it directly + 1
                array_size = f"{size} + 1"
            return f"{c_type} {name}[{array_size}];"
        
        m = re.match(r"DIM\s+(\w+)(?:\s+AS\s+([\w\*]+))?", line, re.IGNORECASE)
        if not m:
            return f"// TODO dim: {line}"
        name, type_token = m.groups()
        base_type, is_pointer = self._type_with_pointer(type_token)
        c_type = self._map_type(base_type)
        basic_types = {"integer", "long", "byte", "boolean", "single", "double", "string"}
        is_object = base_type and base_type[0].isupper() and base_type.lower() not in basic_types

        if is_pointer:
            self.pointer_vars.add(name)
            return f"{c_type}* {name} = nullptr;"

        if is_object:
            if base_type not in self.value_default_types and (base_type in self.pointer_default_types):
                self.pointer_vars.add(name)
                return f"{base_type}* {name} = nullptr;"
            return f"{base_type} {name};"  # Object declaration by value
        
        init_value = self._default_init(c_type)
        return f"{c_type} {name} = {init_value};"

    def _emit_statement(self, line: str) -> str:
        upper = line.upper()

        # --- Exit/Continue/Goto support ---
        if upper == "EXIT SUB" or upper == "EXIT FUNCTION":
            return "return;"
        if upper == "EXIT FOR" or upper == "EXIT DO" or upper == "EXIT WHILE" or upper == "EXIT SELECT":
            return "break;"
        if upper == "CONTINUE FOR" or upper == "CONTINUE DO" or upper == "CONTINUE WHILE":
            return "continue;"
        m_goto = re.match(r"GOTO\s+(\w+)", upper)
        if m_goto:
            return f"goto {m_goto.group(1)};"

        # --- InputBox/MsgBox ---
        m_inputbox = re.match(r"INPUTBOX\s*\((.+)\)", line, re.IGNORECASE)
        if m_inputbox:
            # Stub: InputBox returns empty string
            return "// TODO: InputBox not implemented (returns \"\")"
        m_msgbox = re.match(r"MSGBOX\s*\((.+)\)", line, re.IGNORECASE)
        if m_msgbox:
            # Stub: MsgBox prints to Serial
            return f"Serial.println({self._expr(m_msgbox.group(1))});"

        # --- On Error ---
        if upper.startswith("ON ERROR RESUME NEXT"):
            return "// TODO: On Error Resume Next not implemented"
        m_onerr = re.match(r"ON ERROR GOTO\s+(\w+)", upper)
        if m_onerr:
            return f"// TODO: On Error GoTo {m_onerr.group(1)} not implemented"

        # --- With ... End With ---
        if upper.startswith("WITH "):
            return "// TODO: With block not implemented"
        if upper == "END WITH":
            return "// TODO: End With"

        # --- Do Until / Loop Until ---
        m_do_until = re.match(r"DO\s+UNTIL\s+(.+)", line, re.IGNORECASE)
        if m_do_until:
            cond = self._expr(m_do_until.group(1), is_condition=True)
            self.block_stack.append("do")
            return f"do {{ // until {cond}"
        m_loop_until = re.match(r"LOOP\s+UNTIL\s+(.+)", line, re.IGNORECASE)
        if m_loop_until:
            if self.block_stack and self.block_stack[-1] == "do":
                self.block_stack.pop()
            cond = self._expr(m_loop_until.group(1), is_condition=True)
            return f"}} while (!({cond}));"

        # --- Static variable declaration ---
        m_static = re.match(r"STATIC\s+(\w+)(?:\s+AS\s+([\w\*]+))?", line, re.IGNORECASE)
        if m_static:
            name, type_token = m_static.groups()
            base_type, is_pointer = self._type_with_pointer(type_token)
            c_type = self._map_type(base_type)
            init_value = self._default_init(c_type)
            if is_pointer:
                return f"static {c_type}* {name} = nullptr;"
            return f"static {c_type} {name} = {init_value};"

        # --- Timer/Now/Date/Time ---
        if upper == "TIMER":
            return "millis()"
        if upper == "NOW":
            return "// TODO: Now not implemented"
        if upper == "DATE":
            return "// TODO: Date not implemented"
        if upper == "TIME":
            return "// TODO: Time not implemented"

        # --- Const arrays ---
        m_constarr = re.match(r"CONST\s+(\w+)\(\)\s+AS\s+(\w+)\s*=\s*\{(.+)\}", line, re.IGNORECASE)
        if m_constarr:
            name, typ, values = m_constarr.groups()
            c_type = self._map_type(typ)
            vals = ",".join([self._expr(v.strip()) for v in values.split(",")])
            return f"const {c_type} {name}[] = {{{vals}}};"

        # --- Array assignment/initialization ---
        m_dimarr = re.match(r"DIM\s+(\w+)\(\)\s+AS\s+(\w+)\s*=\s*\{(.+)\}", line, re.IGNORECASE)
        if m_dimarr:
            name, typ, values = m_dimarr.groups()
            c_type = self._map_type(typ)
            vals = ",".join([self._expr(v.strip()) for v in values.split(",")])
            return f"{c_type} {name}[] = {{{vals}}};"

        # --- Property Get/Let/Set ---
        if upper.startswith("PROPERTY "):
            return "// TODO: Property Get/Let/Set not implemented"
        if upper == "END PROPERTY":
            return "// TODO: End Property"

        # --- Type ... End Type ---
        if upper.startswith("TYPE "):
            m = re.match(r"TYPE\s+(\w+)", line, re.IGNORECASE)
            if m:
                return f"struct {m.group(1)} {{"
            return "// TODO: Type not recognized"
        if upper == "END TYPE":
            return "};"

        # --- For Each ... In ... ---
        m_foreach = re.match(r"FOR EACH\s+(\w+)\s+IN\s+(\w+)", line, re.IGNORECASE)
        if m_foreach:
            var, arr = m_foreach.groups()
            return f"for (auto& {var} : {arr}) {{"
        
        # Control flow
        if upper.startswith("IF "):
            m = re.match(r"IF\s+(.+?)\s+THEN", line, re.IGNORECASE)
            cond = self._expr(m.group(1), is_condition=True) if m else "/*cond*/"
            self.block_stack.append("if")
            return f"if ({cond}) {{"
        if upper.startswith("ELSEIF "):
            m = re.match(r"ELSEIF\s+(.+?)\s+THEN", line, re.IGNORECASE)
            cond = self._expr(m.group(1), is_condition=True) if m else "/*cond*/"
            return f"}} else if ({cond}) {{"
        if upper == "ELSE":
            return "} else {"
        if upper in ("END IF", "ENDIF"):
            if self.block_stack and self.block_stack[-1] == "if":
                self.block_stack.pop()
            return "}"

        if upper.startswith("FOR "):
            m = re.match(r"FOR\s+(\w+)\s*=\s*(.+)\s+TO\s+(.+)", line, re.IGNORECASE)
            if m:
                var, start, end = m.groups()
                self.block_stack.append("for")
                return f"for (int {var} = {self._expr(start)}; {var} <= {self._expr(end)}; ++{var}) {{"
        if upper.startswith("NEXT"):
            if self.block_stack and self.block_stack[-1] == "for":
                self.block_stack.pop()
            return "}"

        if upper.startswith("WHILE "):
            m = re.match(r"WHILE\s+(.+)", line, re.IGNORECASE)
            cond = self._expr(m.group(1), is_condition=True) if m else "/*cond*/"
            self.block_stack.append("while")
            return f"while ({cond}) {{"
        if upper == "WEND":
            if self.block_stack and self.block_stack[-1] == "while":
                self.block_stack.pop()
            return "}"

        if upper == "DO":
            self.block_stack.append("do")
            return "do {"
        if upper.startswith("LOOP"):
            if self.block_stack and self.block_stack[-1] == "do":
                self.block_stack.pop()
            # Check for LOOP WHILE/UNTIL
            m = re.match(r"LOOP\s+WHILE\s+(.+)", line, re.IGNORECASE)
            if m:
                return f"}} while ({self._expr(m.group(1), is_condition=True)});"
            return "} while (true);"

        # --- Select Case support ---
        if upper.startswith("SELECT CASE "):
            m = re.match(r"SELECT\s+CASE\s+(.+)", line, re.IGNORECASE)
            expr = self._expr(m.group(1)) if m else "/*expr*/"
            self.block_stack.append("select")
            return f"switch ({expr}) {{"
        if upper.startswith("CASE ELSE"):
            return "default:"
        if upper.startswith("CASE "):
            # Support multiple values: CASE 1, 2, 3
            m = re.match(r"CASE\s+(.+)", line, re.IGNORECASE)
            if m:
                values = [v.strip() for v in m.group(1).split(",")]
                cases = "\n".join([f"case {self._expr(v)}:" for v in values])
                return cases
        if upper == "END SELECT":
            if self.block_stack and self.block_stack[-1] == "select":
                self.block_stack.pop()
            return "}"

        # I/O helpers
        io_patterns = [
            (r"PINMODE\s+(\w+),\s*(\w+)", lambda m: f"pinMode({m.group(1)}, {m.group(2)});"),
            (r"DIGITALWRITE\s+(\w+),\s*(\w+)", lambda m: f"digitalWrite({m.group(1)}, {m.group(2)});"),
            (r"DIGITALREAD\s+(\w+)", lambda m: f"digitalRead({m.group(1)})"),
            (r"ANALOGREAD\s+(\w+)", lambda m: f"analogRead({m.group(1)})"),
            (r"DELAY\s+(.+)", lambda m: f"delay({self._expr(m.group(1))});"),
            (r"ANALOGWRITE\s+(\w+),\s*(.+)", lambda m: f"analogWrite({m.group(1)}, {self._expr(m.group(2))});"),
                (r"SERIALBEGIN\s+(.+)", lambda m: "Serial.begin(" + self._expr(m.group(1)) + ");\n    Serial.setRxBufferSize(1024);\n    Serial.setTxBufferSize(1024);"),
            (r"SERIALPRINTLINE\s+(.+)", lambda m: f"Serial.println({self._expr(m.group(1))});"),
            (r"SERIALPRINT\s+(.+)", lambda m: f"Serial.print({self._expr(m.group(1))});"),
        ]
        for pat, fn in io_patterns:
            m = re.match(pat, line, re.IGNORECASE)
            if m:
                return fn(m)
        
        # Method/function calls without parentheses but with arguments (VB allows Foo arg)
        m_call_no_paren = re.match(r"([\w:]+(?:(?:\.|->)[\w:]+)*)\s+(.+)", line)
        if m_call_no_paren and "=" not in line:
            name, args = m_call_no_paren.groups()
            # Avoid catching control keywords
            if name.upper() not in ("IF", "ELSEIF", "FOR", "WHILE", "DO", "LOOP", "RETURN", "SUB", "FUNCTION"):
                # Support comma-separated arguments
                arg_list = [self._expr(a.strip()) for a in args.split(",")]
                args_joined = ", ".join(arg_list)
                call_line = f"{name}({args_joined});"
                return self._apply_pointer_access(call_line)

        # Method calls: object.method(args) or function calls
        m_method = re.match(r"([\w:]+(?:(?:\.|->)[\w:]+)*|\w+\([^)]*\))\s*(?:\(([^)]*)\))?", line)
        # Treat as direct method call only when there's a dot/arrow scope or when the line starts with name(
        if m_method and "=" not in line and ("." in m_method.group(1) or "->" in m_method.group(1) or "::" in m_method.group(1) or line.startswith(m_method.group(1) + "(")):
            # Convert method call
            if m_method.group(2) is not None:
                args = m_method.group(2).strip()
                args_expr = ", ".join([self._expr(a.strip()) for a in args.split(",")]) if args else ""
                call_line = f"{m_method.group(1)}({args_expr});"
                return self._apply_pointer_access(call_line)
            call = self._expr(line)
            if not call.endswith(";"):
                call = f"{call};"
            return self._apply_pointer_access(call)

        # Assignments: x = expr
        m_assign = re.match(r"(\w+(?:\s*\[.+?\]|\s*\(.+?\))?)\s*=\s*(.+)", line)
        if m_assign:
            lhs, rhs = m_assign.groups()
            # Convert VB array syntax arr(i) to C arr[i]
            lhs = re.sub(r"(\w+)\(([^)]+)\)", r"\1[\2]", lhs)
            return f"{lhs} = {self._expr(rhs)};"
        
        # Return statement
        if upper.startswith("RETURN "):
            expr = line[7:].strip()
            return f"return {self._expr(expr)};"

        return f"// TODO: {line}"

    def _expr(self, expr: str, is_condition: bool = False) -> str:
        expr = expr.strip()
        # --- Hex/Oct/Bin literals ---
        expr = re.sub(r"&H([0-9A-Fa-f]+)", lambda m: f"0x{m.group(1)}", expr)
        expr = re.sub(r"&O([0-7]+)", lambda m: f"0{oct(int(m.group(1), 8))[2:]}", expr)
        expr = re.sub(r"&B([01]+)", lambda m: f"0b{m.group(1)}", expr)
        # --- String manipulation functions ---
        expr = re.sub(r"\bLEFT\s*\(([^,]+),\s*([^)]+)\)", r"\1.substring(0, \2)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bRIGHT\s*\(([^,]+),\s*([^)]+)\)", r"\1.substring(\1.length()-\2)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bMID\s*\(([^,]+),\s*([^)]+)\)", r"\1.substring(\2-1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bLEN\s*\(([^)]+)\)", r"\1.length()", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bINSTR\s*\(([^,]+),\s*([^)]+)\)", r"\1.indexOf(\2)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bREPLACE\s*\(([^,]+),\s*([^,]+),\s*([^)]+)\)", r"\1.replace(\2, \3)", expr, flags=re.IGNORECASE)
        # --- Math functions ---
        expr = re.sub(r"\bSQR\s*\(([^)]+)\)", r"sqrt(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bSIN\s*\(([^)]+)\)", r"sin(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bCOS\s*\(([^)]+)\)", r"cos(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bTAN\s*\(([^)]+)\)", r"tan(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bABS\s*\(([^)]+)\)", r"abs(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bRND\s*\(\)", r"random(0, 32767)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bINT\s*\(([^)]+)\)", r"int(\1)", expr, flags=re.IGNORECASE)
        # Function mappings - do these FIRST before array conversion
        expr = re.sub(r"\bDIGITALREAD\s*\(([^)]+)\)", r"digitalRead(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bANALOGREAD\s*\(([^)]+)\)", r"analogRead(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bMILLIS\s*\(\)", "millis()", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bSERIALAVAILABLE\s*\(\)", "Serial.available()", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bSERIALREAD\s*\(\)", "Serial.read()", expr, flags=re.IGNORECASE)
        # Explicit bitwise helpers
        expr = re.sub(r"\bBITOR\b", "|", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bBITAND\b", "&", expr, flags=re.IGNORECASE)
        # new operator
        expr = re.sub(r"\bNEW\s+(\w+)\s*\(\)", r"new \1()", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bNEW\s+(\w+)", r"new \1()", expr, flags=re.IGNORECASE)
        
        # Convert VB array syntax arr(i) to C arr[i] - but not for function calls
        # Only convert if it's clearly an array access (variable followed by parens with simple content)
        # Skip if it's a known function name
        known_functions = ["digitalRead", "analogRead", "millis", "Serial", "pinMode", "digitalWrite", 
                          "analogWrite", "delay", "min", "max", "abs", "constrain", "map"]
        def convert_array_access(match):
            name = match.group(1)
            # Don't convert if it's a known function or starts with capital (likely a function)
            if name.lower() in [f.lower() for f in known_functions]:
                return match.group(0)  # Keep as-is
            # Convert to array syntax
            return f"{name}[{match.group(2)}]"
        
        expr = re.sub(r"(?<!\.)(?<!>)(?<!:)(\b\w+)\(([\w\s+\-*/]+)\)(?!\s*\.)", convert_array_access, expr)
        
        # Logical replacements
        expr = re.sub(r"\bAND\b", "&&", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bOR\b", "||", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bNOT\b", "!", expr, flags=re.IGNORECASE)
        # Boolean values
        expr = re.sub(r"\bTRUE\b", "true", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bFALSE\b", "false", expr, flags=re.IGNORECASE)
        # Comparisons
        expr = expr.replace("<>", "!=")
        # Convert = to == for comparisons in conditional expressions
        if is_condition:
            # Replace = with == only when it's a comparison operator, not assignment
            expr = re.sub(r"([^<>!=])=([^=])", r"\1==\2", expr)
        expr = self._apply_pointer_access(expr)
        # Strings already VB-style quotes, leave as-is
        return expr

    def _map_type(self, token: str | None) -> str:
        if not token:
            return "int"
        t = token.lower()
        if t in ("integer",):
            return "int"
        if t in ("long",):
            return "long"
        if t in ("byte",):
            return "uint8_t"
        if t in ("boolean",):
            return "bool"
        if t in ("single", "double"):
            return "float"
        if t in ("string",):
            return "String"
        return token

    def _type_with_pointer(self, type_token: str | None) -> tuple[str | None, bool]:
        if not type_token:
            return None, False
        is_pointer = type_token.endswith("*")
        base = type_token[:-1] if is_pointer else type_token
        return base, is_pointer

    def _default_init(self, c_type: str) -> str:
        if c_type == "bool":
            return "false"
        if c_type == "String":
            return '""'
        return "0"

    def _apply_pointer_access(self, text: str) -> str:
        for pvar in sorted(self.pointer_vars, key=len, reverse=True):
            text = re.sub(rf"\b{pvar}\.([\w:]+)", rf"{pvar}->\1", text)
        return text

    def _render_cpp(self) -> str:
        includes_section = ""
        if self.includes:
            includes_section = "\n".join(f"#include {inc}" for inc in sorted(self.includes)) + "\n\n"
        
        # Forward declarations for all functions
        forward_declarations = ""
        if self.function_signatures:
            forward_declarations = "\n".join(self.function_signatures) + "\n\n"
        
        globals_section = "\n".join(self.global_lines)
        functions_section = "".join(self.function_lines) if self.function_lines else ""
        
        # Add initialization delay at the start of setup for USB/serial init
        setup_lines_list = self.setup_lines if self.setup_lines else []
        if setup_lines_list:
            setup_section = "delay(1000);\n    " + "\n    ".join(setup_lines_list)
        else:
            setup_section = "delay(1000);"
        
        loop_section = "\n    ".join(self.loop_lines) if self.loop_lines else ""

        cpp_body = f"""#include <Arduino.h>
{includes_section}{forward_declarations}{globals_section}

{functions_section}void setup() {{
    {setup_section}
}}

void loop() {{
    {loop_section}
}}
"""

        return self._with_line_numbers(cpp_body)

    def _with_line_numbers(self, text: str) -> str:
        """Attach line-number suffix comments for reference only."""
        numbered: list[str] = []
        for idx, line in enumerate(text.splitlines(), start=1):
            stripped = line.rstrip("\n")
            if stripped:
                numbered.append(f"{stripped} // L{idx:04d}")
            else:
                numbered.append(f"// L{idx:04d}")
        return "\n".join(numbered) + "\n"


def transpile_string(source: str) -> str:
    """Convenience function to transpile VB source to Arduino C++."""
    return VBTranspiler().transpile(source).cpp
