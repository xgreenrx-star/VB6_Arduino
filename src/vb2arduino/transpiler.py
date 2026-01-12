import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class TranspileResult:
    cpp: str



class VBTranspiler:
    """Minimal VB6-like to Arduino C++ transpiler for a safe subset."""

    def _is_var_declared_in_scope(self, var: str) -> bool:
        # Check if a variable was declared with Dim in the current function/sub
        # This is a simple heuristic: check if the variable is in pointer_vars or array_dimensions or seen in function_lines
        # For a more robust solution, track declared variables per function
        declared = set()
        for line in self.function_lines:
            m = re.match(r"\s*(?:[a-zA-Z0-9_]+\s+)+([a-zA-Z0-9_]+)\s*[=;]", line)
            if m:
                declared.add(m.group(1))
        return var in declared or var in self.pointer_vars or var in self.array_dimensions

    def __init__(self) -> None:
        self.global_lines = []
        self.setup_lines = []
        self.loop_lines = []
        self.function_lines = []
        self.function_signatures = []  # For forward declarations
        self.block_stack = []
        # Lines to skip (used when consuming multi-line custom blocks like Every ... End Do)
        self._skip_lines = set()
        self.includes = set()
        self.current_function = None
        self.pointer_vars = set()
        self.array_dimensions = {}  # Track array dimensions for UBound/LBound
        self.option_base = 0  # Option Base 0 (default) or 1
        self.pointer_default_types = {"BLEServer", "BLEService", "BLECharacteristic", "BLEAdvertising"}
        self.value_default_types = {"Preferences"}
        # Graphics library detection
        self.graphics_lib = None  # 'tft_espi', 'adafruit_gfx', 'u8g2', 'lvgl'
        self.display_object = "tft"  # Default display object name
        self.select_expr = ""  # Track current select case expression
        self.in_case_block = False  # Track if we're inside a case block (for break statements)
        self.with_object = None  # Track object in With block
        # Every-timer tasks
        self.every_tasks = []
        self._every_counter = 0

    def transpile(self, source: str) -> TranspileResult:
        # --- Line continuation: join lines ending with _
        lines = source.splitlines()
        processed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            # Check if line ends with underscore (line continuation)
            while line.endswith('_') and i + 1 < len(lines):
                line = line[:-1].rstrip() + ' ' + lines[i + 1].lstrip()
                i += 1
            processed_lines.append(line)
            i += 1
        source = '\n'.join(processed_lines)

        self.global_lines.clear()
        self.setup_lines.clear()
        self.loop_lines.clear()
        self.function_lines.clear()
        self.function_signatures.clear()
        self.block_stack.clear()
        self.includes.clear()
        self.current_function = None
        self.pointer_vars.clear()
        self.array_dimensions.clear()
        self.option_base = 0
        self.graphics_lib = None
        self.display_object = "tft"
        self.select_expr = ""
        self.in_case_block = False
        self.with_object = None

        current = None  # None, "setup", "loop", "function"
        label_set = set()
        # Per-function and per-context variable tracking
        all_functions = []
        function_lines_buffer = []
        function_var_candidates = set()
        function_dim_vars = set()
        function_param_vars = set()
        function_header = None
        # Track DIM'd vars in other contexts to avoid duplicate declarations
        setup_dim_vars = set()
        loop_dim_vars = set()
        global_dim_vars = set()
        # Track VB source line numbers for error mapping
        for vb_line_no, raw in enumerate(source.splitlines(), start=1):
            # Skip lines consumed by multi-line block handlers
            if vb_line_no in getattr(self, '_skip_lines', set()):
                continue
            line = raw.strip()
            if not line or line.startswith("'") or line.upper().startswith("REM"):
                continue
            if "'" in line:
                comment_pos = line.find("'")
                line = line[:comment_pos].rstrip()
            if re.search(r'\bREM\b', line, re.IGNORECASE):
                rem_match = re.search(r'\bREM\b', line, re.IGNORECASE)
                if rem_match:
                    line = line[:rem_match.start()].rstrip()
            if not line:
                continue
            m_label = re.match(r"^(\w+):$", line)
            if m_label:
                label_set.add(m_label.group(1))
                target = self._target_lines(current)
                target.append(f"{m_label.group(1)}:")
                continue
            upper = line.upper()
            if upper.startswith("OPTION BASE "):
                try:
                    self.option_base = int(line.split()[-1])
                except ValueError:
                    self.option_base = 0
                continue
            if upper.startswith("#INCLUDE "):
                include = line[9:].strip()
                self.includes.add(include)
                self._detect_graphics_lib(include)
                continue
            if upper.startswith("CONST "):
                self.global_lines.append(f"// __VB_LINE__:{vb_line_no}")
                self.global_lines.append(self._emit_const(line))
                continue
            if upper.startswith("DIM "):
                target = self._target_lines(current)
                statement = self._emit_dim(line)
                # Robustly extract all variable names from a Dim line
                dim_line = line[3:].strip()
                # Split by commas at top level (not inside parentheses)
                def split_dim_vars(s):
                    vars = []
                    depth = 0
                    current = []
                    for c in s:
                        if c == '(': depth += 1
                        if c == ')': depth -= 1
                        if c == ',' and depth == 0:
                            vars.append(''.join(current).strip())
                            current = []
                        else:
                            current.append(c)
                    if current:
                        vars.append(''.join(current).strip())
                    return vars
                debug_vars = []
                # Determine variable names from the Dim line without emitting duplicates.
                new_debug_vars = []
                for var_decl in split_dim_vars(dim_line):
                    # Extract the first word (variable name) before any space, '(', or '='
                    var_name = var_decl.strip()
                    m = re.match(r"(\w+)", var_name)
                    if not m:
                        continue
                    name = m.group(1)
                    # Decide which context set to consult/modify
                    if current == "function":
                        if name in function_dim_vars:
                            continue
                        function_dim_vars.add(name)
                    elif current == "setup":
                        if name in setup_dim_vars:
                            continue
                        setup_dim_vars.add(name)
                    elif current == "loop":
                        if name in loop_dim_vars:
                            continue
                        loop_dim_vars.add(name)
                    else:
                        if name in global_dim_vars:
                            continue
                        global_dim_vars.add(name)
                    new_debug_vars.append(name)

                if new_debug_vars:
                    # Use logger.debug instead of print to avoid noisy output during normal runs
                    import logging
                    logging.getLogger(__name__).debug("Hoisted from Dim: %s", new_debug_vars)
                if statement:
                    # Emit a declaration for EACH *new* variable found in the Dim line
                    for var_decl in split_dim_vars(dim_line):
                        m2 = re.match(r"(\w+)", var_decl.strip())
                        if not m2:
                            continue
                        name = m2.group(1)
                        if name not in new_debug_vars:
                            continue
                        # Skip emitting a local declaration if a global Dim already exists
                        if current in ("setup", "loop") and name in global_dim_vars:
                            continue
                        stmt_var = self._emit_dim(f"DIM {var_decl}")
                        if not stmt_var:
                            continue
                        if current == "function":
                            function_lines_buffer.append(f"// __VB_LINE__:{vb_line_no}\n")
                            function_lines_buffer.append(stmt_var + "\n")
                        elif current == "setup":
                            target.append(f"// __VB_LINE__:{vb_line_no}")
                            target.append(stmt_var)
                        elif current == "loop":
                            target.append(f"// __VB_LINE__:{vb_line_no}")
                            target.append(stmt_var)
                        else:
                            self.global_lines.append(f"// __VB_LINE__:{vb_line_no}")
                            self.global_lines.append(stmt_var)
                continue
            if upper.startswith("SUB SETUP"):
                current = "setup"
                continue
            # --- Every timer block: Every <ms> Do ... End Do ---
            m_every = re.match(r"^EVERY\s+(.+?)\s+DO\s*$", line, re.IGNORECASE)
            if m_every:
                interval_expr = m_every.group(1)
                # Collect block lines until matching END DO
                src_lines = source.splitlines()
                j = vb_line_no
                collecting = []
                while j < len(src_lines):
                    nxt = src_lines[j].strip()
                    if re.match(r"^END\s+DO\s*$", nxt, re.IGNORECASE):
                        break
                    collecting.append(nxt)
                    j += 1
                # Mark lines as consumed (so outer loop will skip them)
                for k in range(vb_line_no + 1, j + 1):
                    getattr(self, '_skip_lines', set()).add(k)
                # Generate a helper function using a fresh transpiler instance
                self._every_counter += 1
                eid = self._every_counter
                func_name = f"_every_task_{eid}"
                tmp_src = "Sub " + func_name + "()\n" + "\n".join(collecting) + "\nEnd Sub\n"
                tmp = VBTranspiler()
                tmp_res = tmp.transpile(tmp_src)
                cpp = tmp_res.cpp
                # Extract function body if possible
                import re as _re
                m_func = _re.search(r"void\s+" + _re.escape(func_name) + r"\s*\((.*?)\)\s*\{", cpp, _re.S)
                func_text = None
                if m_func:
                    start = m_func.start()
                    brace = cpp.find('{', m_func.end()-1)
                    cnt = 1
                    i2 = brace + 1
                    while i2 < len(cpp) and cnt > 0:
                        if cpp[i2] == '{': cnt += 1
                        elif cpp[i2] == '}': cnt -= 1
                        i2 += 1
                    func_text = cpp[start:i2]
                # Add tracking variable and function (or comment)
                self.global_lines.append(f"unsigned long _every_last_{eid} = 0;")
                if func_text:
                    self.function_lines.append(func_text)
                else:
                    self.function_lines.append(f"// TODO: Failed to generate every-task {func_name} starting at line {vb_line_no}")
                # Add runtime check in the loop
                try:
                    interval_cpp = self._expr(interval_expr)
                except Exception:
                    interval_cpp = interval_expr
                self.loop_lines.append(f"if (millis() - _every_last_{eid} >= {interval_cpp}) {{")
                self.loop_lines.append(f"    _every_last_{eid} = millis();")
                self.loop_lines.append(f"    {func_name}();")
                self.loop_lines.append("}")
                continue
            if upper.startswith("SUB LOOP"):
                current = "loop"
                continue
            if upper.startswith("SUB ") or upper.startswith("FUNCTION "):
                # If we were already in a function, close and save it
                if current == "function" and function_lines_buffer:
                    # Prepend the header if it's not already present
                    if function_header and (not function_lines_buffer or not function_lines_buffer[0].strip().startswith((function_header.split()[0] + ' ', 'void '))):
                        function_lines_buffer.insert(0, function_header)
                    all_functions.append({
                        'lines_buffer': function_lines_buffer,
                        'var_candidates': function_var_candidates,
                        'dim_vars': function_dim_vars,
                        'param_vars': function_param_vars,
                        'header': function_header
                    })
                current = "function"
                function_lines_buffer = []
                function_var_candidates = set()
                function_dim_vars = set()
                function_param_vars = set()
                function_header = self._emit_function_header(line)
                # Parse parameters
                m_params = re.match(r"(?:SUB|FUNCTION)\s+\w+\s*\(([^)]*)\)", line, re.IGNORECASE)
                if m_params:
                    params = m_params.group(1)
                    for p in params.split(","):
                        pname = p.strip().split()[-1] if p.strip() else None
                        if pname:
                            function_param_vars.add(pname)
                continue
            if upper == "END SUB" or upper == "END FUNCTION":
                if current == "function":
                    # Prepend the header if it's not already present
                    if function_header and (not function_lines_buffer or not function_lines_buffer[0].strip().startswith((function_header.split()[0] + ' ', 'void '))):
                        function_lines_buffer.insert(0, function_header)
                    # Save the function before resetting
                    all_functions.append({
                        'lines_buffer': function_lines_buffer,
                        'var_candidates': function_var_candidates,
                        'dim_vars': function_dim_vars,
                        'param_vars': function_param_vars,
                        'header': function_header
                    })
                    current = None
                continue
            target = self._target_lines(current)
            statement = self._emit_statement(line)
            # Track assigned variables for hoisting
            if current == "function":
                # Find all variable assignments in the line (including multiple per line)
                assigns = re.findall(r"\b(\w+)\s*=", line)
                # Find all variable assignments in the line (including multiple per line, and in any context)
                # This regex finds all variable names on the left of an '=' that are not part of '==' or '>=' or '<=' or '!='
                assign_matches = re.finditer(r"\b(\w+)\s*=\s*[^=]", line)
                for m in assign_matches:
                    v = m.group(1)
                    function_var_candidates.add(v)
                if statement:
                    function_lines_buffer.append(f"// __VB_LINE__:{vb_line_no}\n")
                    function_lines_buffer.append(statement + "\n")
            else:
                if statement:
                    target.append(f"// __VB_LINE__:{vb_line_no}")
                    target.append(statement)

        # After all lines, emit each function only once (the last collected body for each Sub/Function)
        if all_functions:
            # Deduplicate by function header (name/signature), keep only the last occurrence
            seen_headers = set()
            unique_functions = []
            for func in reversed(all_functions):
                lines_buffer = func['lines_buffer']
                if lines_buffer:
                    header = lines_buffer[0].strip()
                    if header not in seen_headers:
                        unique_functions.append(func)
                        seen_headers.add(header)
            # Emit in original order (reverse back)
            for func in reversed(unique_functions):
                lines_buffer = func['lines_buffer']
                if not lines_buffer:
                    continue
                header = lines_buffer[0].strip()
                # Only emit valid function headers
                if not (header.startswith('void ') or header.endswith(') {')):
                    continue
                # Collect only the body lines (skip header and any duplicate headers or unrelated code)
                body_lines = []
                for line in lines_buffer[1:]:
                    # Stop if another function header is encountered (should not happen, but safety)
                    if line.strip().startswith('void '):
                        break
                    # Skip stray braces at the top level
                    if line.strip() == '{':
                        continue
                    body_lines.append(line)
                # --- Robust variable hoisting ---
                # Gather all variable names used in the function body
                var_names = set()
                var_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b')
                for line in body_lines:
                    # Exclude C++ keywords and function calls
                    tokens = var_pattern.findall(line)
                    for token in tokens:
                        # Skip known keywords and runtime/library types
                        if token in {'if','for','while','switch','case','break','continue','return','else','void','int','float','double','long','bool','char','String','const','auto','static','public','private','protected','unsigned','signed','true','false','new','delete','sizeof','class','struct','enum','union','goto','do','default','try','catch','throw','this','namespace','using','volatile','register','extern','inline','operator','template','typename','typeid','virtual','override','final','friend','explicit','constexpr','nullptr','static_cast','dynamic_cast','reinterpret_cast','const_cast','and','or','not','xor','bitand','bitor','compl','asm','export','import','module','requires','co_await','co_return','co_yield','noexcept','thread_local','alignas','alignof','concept','decltype','static_assert','char16_t','char32_t','wchar_t','short','signed','unsigned','float_t','double_t','int8_t','int16_t','int32_t','int64_t','uint8_t','uint16_t','uint32_t','uint64_t','size_t','ptrdiff_t','intptr_t','uintptr_t','FILE','fpos_t','clock_t','time_t','va_list','jmp_buf','sig_atomic_t','wint_t','wctype_t','mbstate_t','tm','div_t','ldiv_t','lldiv_t','_Bool','_Complex','_Imaginary','main','setup','loop','String','TFT_eSPI','Serial','tft'}:
                            continue
                        # Skip tokens that are used as function/method calls (e.g., cos(...), tft.drawLine(...))
                        if re.search(rf"{re.escape(token)}\s*\(", line):
                            continue
                        # Skip likely-constant tokens (all upper-case with optional underscores)
                        if token.isupper():
                            continue
                        # Skip common math and std functions that may appear as identifiers but are calls
                        builtin_skip = {'abs','cos','sin','tan','sqrt','pow','min','max','round','floor','ceil','substr','substring','indexOf','toString','println','print'}
                        if token.lower() in builtin_skip:
                            continue
                        # If token appears as an object property (preceded by '.') skip it
                        if re.search(rf"\.{re.escape(token)}\b", line):
                            continue
                        # If token appears as an object instance followed by '.' (e.g., ball.pushSprite) skip it
                        if re.search(rf"\b{re.escape(token)}\s*\.", line):
                            continue
                        var_names.add(token)
                # Remove parameters, dims and globals from hoisting set
                param_vars = func.get('param_vars', set())
                dim_vars = func.get('dim_vars', set())
                # Collect global var names declared at top-level to avoid re-declaring them inside functions
                global_var_names = set()
                gvar_pattern = re.compile(r'\b(?:float|int|double|long|bool|char|String|const auto)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b')
                for gl in self.global_lines:
                    gm = gvar_pattern.search(gl)
                    if gm:
                        global_var_names.add(gm.group(1))
                hoisted = set(param_vars) | set(dim_vars) | global_var_names
                to_hoist = sorted(var_names - hoisted)
                # Emit the function as a single unit: header, hoisted vars, body, closing brace
                self.function_lines.append(header + '\n')
                for v in to_hoist:
                    self.function_lines.append(f'    float {v} = 0;\n')
                self.function_lines.extend(body_lines)
                self.function_lines.append('}\n')
        # Ensure all open blocks are closed (especially for function/loop)
        self.current_function = None
        # Note: Do not append closing braces for setup/loop here — the renderer will wrap
        # setup/loop with their own function braces to avoid duplicate '}' emissions.
        cpp = self._render_cpp()
        cpp = cpp.rstrip() + "\n"
        return TranspileResult(cpp=cpp)

    def _target_lines(self, current: str | None) -> List[str]:
        if current == "setup":
            return self.setup_lines
        if current == "loop":
            return self.loop_lines
        if current == "function":
            return self.function_lines
        return self.global_lines

    def _split_params_balanced(self, params_str: str) -> List[str]:
        """Split parameters by top-level commas, respecting nested parentheses."""
        params = []
        current_param = []
        depth = 0
        for char in params_str:
            if char == '(':
                depth += 1
                current_param.append(char)
            elif char == ')':
                depth -= 1
                current_param.append(char)
            elif char == ',' and depth == 0:
                # Top-level comma - split here
                params.append(''.join(current_param).strip())
                current_param = []
            else:
                current_param.append(char)
        # Add the last parameter
        if current_param:
            params.append(''.join(current_param).strip())
        return params

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
        
        # Parse parameters with Optional / ByRef / default values
        param_list = []
        if params:
            param_tokens = self._split_params_balanced(params)
            for param in param_tokens:
                param = param.strip()
                pm = re.match(r"(optional\s+)?(byref|byval)?\s*(\w+)(?:\s+as\s+([\w\*]+))?(?:\s*=\s*(.+))?", param, re.IGNORECASE)
                if pm:
                    is_optional, by_mode, pname, ptype, default_val = pm.groups()
                    is_pointer = bool(ptype and ptype.endswith("*"))
                    base_type = ptype[:-1] if is_pointer else ptype
                    pc_type = self._map_type(base_type)
                    if is_pointer:
                        self.pointer_vars.add(pname)
                        pc_type = f"{pc_type}*"
                    if by_mode and by_mode.lower() == "byref":
                        pc_type = f"{pc_type}&"
                    param_decl = f"{pc_type} {pname}"
                    if is_optional or default_val:
                        if default_val:
                            def_expr = self._expr(default_val)
                        else:
                            if pc_type.lower().startswith("string"):
                                def_expr = "\"\""
                            elif "bool" in pc_type.lower():
                                def_expr = "false"
                            else:
                                def_expr = "0"
                        param_decl += f" = {def_expr}"
                    param_list.append(param_decl)
        
        params_str = ", ".join(param_list) if param_list else ""
        header = f"{ret_c_type} {name}({params_str}) {{\n"
        signature = f"{ret_c_type} {name}({params_str});"
        self.function_signatures.append(signature)
        # Return the header string; do not append it to self.function_lines here.
        # We'll prepend it to the collected function buffer when emitting functions later.
        return header

    def _emit_dim(self, line: str) -> str:
        # Dim x As Integer  | Dim x | Dim arr(10) As String | Dim arr(MAX_SIZE) As String
        # Multi-dimensional arrays: Dim arr(10, 20) As Integer | Dim arr(3, 4, 5) As Integer
        # Array syntax: Dim name(size1[, size2, ...]) As Type - sizes can be numbers or identifiers
        m_array = re.match(r"DIM\s+(\w+)\s*\(([^)]+)\)(?:\s+AS\s+([\w\*]+))?", line, re.IGNORECASE)
        if m_array:
            name, sizes_str, type_token = m_array.groups()
            base_type, is_pointer = self._type_with_pointer(type_token)
            c_type = self._map_type(base_type)
            # Track pointer arrays (rare)
            if is_pointer:
                self.pointer_vars.add(name)
                c_type = f"{c_type}*"
            # Parse multiple dimensions
            sizes = [s.strip() for s in sizes_str.split(",")]
            c_sizes = []
            dims = []
            for size in sizes:
                if size.isdigit():
                    c_sizes.append(str(int(size) + 1))  # VB arrays are 0-based but size is max index
                    dims.append(int(size))
                else:
                    # It's an identifier (constant), use it directly + 1
                    c_sizes.append(f"{size} + 1")
                    dims.append(size)  # Store as string for later reference
            # Store dimensions for UBound/LBound
            self.array_dimensions[name] = dims
            # Build array declaration with brackets for each dimension
            array_decl = "".join([f"[{size}]" for size in c_sizes])
            return f"{c_type} {name}{array_decl};"
        
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
        # --- With block method/property calls ---
        if self.with_object and line.strip().startswith('.'):
            # Method or property access within With block
            method_call = line.strip()[1:]  # Remove leading dot
            return f"{self.with_object}.{method_call};"
        upper = line.upper()

        # --- For loop (patch: avoid redeclaring already-declared variables) ---
        m_for = re.match(r"FOR\s+(\w+)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?\s*$", line, re.IGNORECASE)
        if m_for:
            var, start, end, step = m_for.groups()
            step = step or "1"
            # Check if var is already declared in function scope
            already_declared = False
            for l in self.function_lines:
                if re.match(rf"\s*(int|float|double|long|bool|char|String)\s+{var}\b", l):
                    already_declared = True
                    break
            decl = f"int {var} = {self._expr(start)};" if not already_declared else f"{var} = {self._expr(start)};"
            cond = f"(({self._expr(step)}) >= 0 ? {var} <= {self._expr(end)} : {var} >= {self._expr(end)})"
            inc = f"{var} += ({self._expr(step)})"
            return f"for ({decl} {cond}; {inc}) {{"

        # --- Single-line If ... Then ... [statement] ---
        m_single_if = re.match(r"IF\s+(.+?)\s+THEN\s+(.+)", line, re.IGNORECASE)
        if m_single_if:
            cond = self._expr(m_single_if.group(1), is_condition=True)
            stmt = self._emit_statement(m_single_if.group(2).strip())
            # Do NOT push to block_stack for single-line If
            if stmt and stmt.endswith('{'):
                return f"if ({cond}) {stmt}"
            else:
                return f"if ({cond}) {{ {stmt} }}"
        # --- DoEvents ---
        if upper == "DOEVENTS":
            return "delay(0);"
        
        # --- Randomize ---
        if upper == "RANDOMIZE":
            return "randomSeed(millis());"
        m_randomize = re.match(r"RANDOMIZE\s+(.+)", line, re.IGNORECASE)
        if m_randomize:
            seed = self._expr(m_randomize.group(1))
            return f"randomSeed({seed});"
            # --- Exit/Continue/Goto support ---
        
        if upper == "RETURN":
            return "return;"
        if upper == "EXIT SUB" or upper == "EXIT FUNCTION":
            return "return;"
        if upper == "EXIT FOR" or upper == "EXIT DO" or upper == "EXIT WHILE" or upper == "EXIT SELECT":
            return "break;"
        if upper == "CONTINUE FOR" or upper == "CONTINUE DO" or upper == "CONTINUE WHILE":
            return "continue;"
        m_goto = re.match(r"GOTO\s+(\w+)", upper)
        if m_goto:
            return f"goto {m.group(1)};"

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
            m = re.match(r"WITH\s+(.+)", line, re.IGNORECASE)
            if m:
                obj = m.group(1).strip()
                self.with_object = obj
                self.block_stack.append("with")
                return f"{{ // With {obj}"
            return "// ERROR: With needs object"
        if upper == "END WITH":
            if self.block_stack and self.block_stack[-1] == "with":
                self.block_stack.pop()
            self.with_object = None
            return "}"

        # --- Do Until / Loop Until ---
        m_do_until = re.match(r"DO\s+UNTIL\s+(.+)", line, re.IGNORECASE)
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
                self.block_stack.append("type")
                return f"struct {m.group(1)} {{"
            return "// TODO: Type not recognized"
        if upper == "END TYPE":
            if self.block_stack and self.block_stack[-1] == "type":
                self.block_stack.pop()
            return "};"

        # Inside Type block: field declarations like "x As Integer"
        if self.block_stack and self.block_stack[-1] == "type":
            m_field = re.match(r"(\w+)\s+AS\s+([\w\*]+)", line, re.IGNORECASE)
            if m_field:
                fname, ftype = m_field.groups()
                f_c_type = self._map_type(ftype)
                return f"{f_c_type} {fname};"
            return f"// TODO: Type field: {line}"
        
        # --- Enum ... End Enum ---
        if upper.startswith("ENUM "):
            m = re.match(r"ENUM\s+(\w+)", line, re.IGNORECASE)
            if m:
                self.block_stack.append("enum")
                return f"enum {m.group(1)} {{"
            return "// TODO: Enum not recognized"
        if upper == "END ENUM":
            if self.block_stack and self.block_stack[-1] == "enum":
                self.block_stack.pop()
            return "};"
        if self.block_stack and self.block_stack[-1] == "enum":
            m_enum = re.match(r"(\w+)\s*(=\s*.+)?", line, re.IGNORECASE)
            if m_enum:
                name, val = m_enum.groups()
                if val:
                    return f"{name} {val},"
                return f"{name},"
            return f"// TODO: Enum member: {line}"

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
            # Always close previous block before opening new else if
            return f"}} else if ({cond}) {{"
        if upper == "ELSE":
            # Always close previous block before opening else
            return "} else {"
        if upper in ("END IF", "ENDIF"):
            # Always close block, even if not in stack
            if self.block_stack and self.block_stack[-1] == "if":
                self.block_stack.pop()
            return "}"

        if upper.startswith("FOR "):
            m = re.match(r"FOR\s+(\w+)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$", line, re.IGNORECASE)
            if m:
                var, start, end, step = m.groups()
                self.block_stack.append("for")
                start_c = self._expr(start)
                end_c = self._expr(end)
                step_c = self._expr(step) if step else "1"
                # Use existing variable if declared, otherwise declare new
                if self._is_var_declared_in_scope(var):
                    return (
                        f"for ({var} = {start_c}; "
                        f"(({step_c}) >= 0 ? {var} <= {end_c} : {var} >= {end_c}); "
                        f"{var} += ({step_c})) {{"
                    )
                else:
                    return (
                        f"for (int {var} = {start_c}; "
                        f"(({step_c}) >= 0 ? {var} <= {end_c} : {var} >= {end_c}); "
                        f"{var} += ({step_c})) {{"
                    )
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
            self.select_expr = expr  # Store for range comparisons
            self.in_case_block = False  # Reset case block tracking
            return f"switch ({expr}) {{"
        if upper.startswith("CASE ELSE"):
            # Add break before case else if we were in a case block
            result = ""
            if self.in_case_block:
                result = "break;\n"
            self.in_case_block = True
            return result + "default:"
        if upper.startswith("CASE "):
            # Add break before new case if we were already in a case block
            result = ""
            if self.in_case_block:
                result = "break;\n"
            self.in_case_block = True
            
            # Support: CASE 1, 2, 3  |  CASE 1 TO 10  |  CASE IS >= 5
            m = re.match(r"CASE\s+(.+)", line, re.IGNORECASE)
            if m:
                case_expr = m.group(1).strip()
                
                # Handle "CASE IS >= value" (becomes if statement)
                m_is = re.match(r"IS\s+([<>=!]+)\s+(.+)", case_expr, re.IGNORECASE)
                if m_is:
                    op, val = m_is.groups()
                    # This is a conditional, not a switch case - needs different handling
                    # For now, emit as comment and use if-else pattern
                    return result + f"// CASE IS {op} {val} - use if-else instead of switch"
                
                # Handle "CASE x TO y"
                m_range = re.match(r"(\d+)\s+TO\s+(\d+)", case_expr, re.IGNORECASE)
                if m_range:
                    start, end = m_range.groups()
                    # Generate multiple case statements
                    cases = []
                    for i in range(int(start), int(end) + 1):
                        cases.append(f"case {i}:")
                    return result + "\n".join(cases)
                
                # Handle comma-separated values: CASE 1, 2, 3
                values = [v.strip() for v in case_expr.split(",")]
                cases = "\n".join([f"case {self._expr(v)}:" for v in values])
                return result + cases
        if upper == "END SELECT":
            result = ""
            if self.in_case_block:
                result = "break;\n"
            self.in_case_block = False
            if self.block_stack and self.block_stack[-1] == "select":
                self.block_stack.pop()
            return result + "}"

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
            # String functions
            (r"LEN\s*\((.+?)\)", lambda m: f"({self._expr(m.group(1))}.length())"),
            (r"SUBSTRING\s*\((.+?),\s*(.+?),\s*(.+?)\)", lambda m: f"({self._expr(m.group(1))}.substring({self._expr(m.group(2))}, {self._expr(m.group(2))} + {self._expr(m.group(3))}))"),
            (r"INSTR\s*\((.+?),\s*(.+?)\)", lambda m: f"({self._expr(m.group(1))}.indexOf({self._expr(m.group(2))}) + 1)"),
            (r"STRREPLACE\s*\((.+?),\s*(.+?),\s*(.+?)\)", lambda m: self._emit_strreplace(m)),
            (r"TRIM\s*\((.+?)\)", lambda m: self._emit_trim(m)),
            (r"LTRIM\s*\((.+?)\)", lambda m: self._emit_ltrim(m)),
            (r"RTRIM\s*\((.+?)\)", lambda m: self._emit_rtrim(m)),
            (r"UPPER\s*\((.+?)\)", lambda m: self._emit_upper(m)),
            (r"LOWER\s*\((.+?)\)", lambda m: self._emit_lower(m)),
            # Bit operations
            (r"BITREAD\s*\((.+?),\s*(.+?)\)", lambda m: f"(({self._expr(m.group(1))} >> {self._expr(m.group(2))}) & 1)"),
            (r"BITWRITE\s*\((.+?),\s*(.+?),\s*(.+?)\)", lambda m: self._emit_bitwrite(m)),
            (r"BITSET\s*\((.+?),\s*(.+?)\)", lambda m: f"({self._expr(m.group(1))} | (1 << {self._expr(m.group(2))}))"),
            (r"BITCLEAR\s*\((.+?),\s*(.+?)\)", lambda m: f"({self._expr(m.group(1))} & ~(1 << {self._expr(m.group(2))}))"),
            (r"BITSHIFTLEFT\s*\((.+?),\s*(.+?)\)", lambda m: f"({self._expr(m.group(1))} << {self._expr(m.group(2))})"),
            (r"BITSHIFTRIGHT\s*\((.+?),\s*(.+?)\)", lambda m: f"({self._expr(m.group(1))} >> {self._expr(m.group(2))})"),
            # Sleep/Power (ESP32)
            (r"DEEPSLEEP\s+(.+)", lambda m: f"esp_deep_sleep({self._expr(m.group(1))} * 1000);"),
            (r"LIGHTSLEEP\s+(.+)", lambda m: f"esp_light_sleep_start(); delay({self._expr(m.group(1))});"),
            (r"HIBERNATE\s*", lambda m: f"esp_deep_sleep(ESP_SLEEP_MAX_TIMER_WAKEUP);"),
            (r"WAKEONINTERRUPT\s+(\w+)", lambda m: f"esp_sleep_enable_ext0_wakeup({m.group(1)}, 1);"),
            # Unified Graphics Commands - work with any library!
            (r"DRAWLINE\s+(.+?),\s*(.+?),\s*(.+?),\s*(.+?),\s*(.+)", lambda m: f"{self._get_graphics_call('drawLine', self._expr(m.group(1)), self._expr(m.group(2)), self._expr(m.group(3)), self._expr(m.group(4)), self._expr(m.group(5)))};"),
            (r"DRAWRECT\s+(.+?),\s*(.+?),\s*(.+?),\s*(.+?),\s*(.+)", lambda m: f"{self._get_graphics_call('drawRect', self._expr(m.group(1)), self._expr(m.group(2)), self._expr(m.group(3)), self._expr(m.group(4)), self._expr(m.group(5)))};"),
            (r"FILLRECT\s+(.+?),\s*(.+?),\s*(.+?),\s*(.+?),\s*(.+)", lambda m: f"{self._get_graphics_call('fillRect', self._expr(m.group(1)), self._expr(m.group(2)), self._expr(m.group(3)), self._expr(m.group(4)), self._expr(m.group(5)))};"),
            (r"DRAWCIRCLE\s+(.+?),\s*(.+?),\s*(.+?),\s*(.+)", lambda m: f"{self._get_graphics_call('drawCircle', self._expr(m.group(1)), self._expr(m.group(2)), self._expr(m.group(3)), self._expr(m.group(4)))};"),
            (r"FILLCIRCLE\s+(.+?),\s*(.+?),\s*(.+?),\s*(.+)", lambda m: f"{self._get_graphics_call('fillCircle', self._expr(m.group(1)), self._expr(m.group(2)), self._expr(m.group(3)), self._expr(m.group(4)))};"),
            # Sprite commands: CREATE_SPRITE name, w, h
            (r"CREATE_SPRITE\s+(\w+),\s*(.+?),\s*(.+)", lambda m: self._emit_create_sprite(m.group(1), m.group(2), m.group(3))),
            (r"SPRITE_FILL\s+(\w+),\s*(.+)", lambda m: self._emit_sprite_method('fillSprite', m.group(1), [m.group(2)])),
            (r"SPRITE_FILL_ELLIPSE\s+(\w+),\s*(.+)", lambda m: self._handle_sprite_fill_ellipse(m)),
            (r"SPRITE_FILL_TRIANGLE\s+(\w+),\s*(.+)", lambda m: self._handle_sprite_fill_triangle(m)),
            (r"SPRITE_PUSH\s+(\w+),\s*(.+?),\s*(.+?)(?:,\s*(.+))?\s*$", lambda m: self._emit_sprite_push(m.group(1), m.group(2), m.group(3), m.group(4))),
            (r"SPRITE_DELETE\s+(\w+)", lambda m: self._emit_sprite_method('deleteSprite', m.group(1), [])),
            (r"DRAWTRIANGLE\s+(.+?),\s*(.+?),\s*(.+?),\s*(.+?),\s*(.+?),\s*(.+?),\s*(.+)", lambda m: f"{self._get_graphics_call('drawTriangle', self._expr(m.group(1)), self._expr(m.group(2)), self._expr(m.group(3)), self._expr(m.group(4)), self._expr(m.group(5)), self._expr(m.group(6)), self._expr(m.group(7)))};"),
            (r"FILLTRIANGLE\s+(.+?),\s*(.+?),\s*(.+?),\s*(.+?),\s*(.+?),\s*(.+?),\s*(.+)", lambda m: f"{self._get_graphics_call('fillTriangle', self._expr(m.group(1)), self._expr(m.group(2)), self._expr(m.group(3)), self._expr(m.group(4)), self._expr(m.group(5)), self._expr(m.group(6)), self._expr(m.group(7)))};"),
            (r"DRAWPIXEL\s+(.+?),\s*(.+?),\s*(.+)", lambda m: f"{self._get_graphics_call('drawPixel', self._expr(m.group(1)), self._expr(m.group(2)), self._expr(m.group(3)))};"),
            (r"FILLSCREEN\s+(.+)", lambda m: f"{self._get_graphics_call('fillScreen', self._expr(m.group(1)))};"),
            (r"CLEARDISPLAY\s*", lambda m: f"{self.display_object}.{'clearDisplay' if self.graphics_lib == 'adafruit_gfx' else 'clearBuffer' if self.graphics_lib == 'u8g2' else 'fillScreen'}({'0' if self.graphics_lib in ('u8g2', 'adafruit_gfx') else 'TFT_BLACK'});"),
            (r"SETTEXTSIZE\s+(.+)", lambda m: f"{self.display_object}.setTextSize({self._expr(m.group(1))});"),
            # SetTextColor with 2 parameters - use balanced split
            (r"SETTEXTCOLOR\s+(.+)", lambda m: self._emit_settextcolor(m.group(1))),
            (r"SETCURSOR\s+(.+?),\s*(.+)", lambda m: f"{self.display_object}.setCursor({self._expr(m.group(1))}, {self._expr(m.group(2))});"),
            (r"PRINTTEXT\s+(.+)", lambda m: f"{self.display_object}.print({self._expr(m.group(1))});"),
            (r"PRINTLINE\s+(.+)", lambda m: f"{self.display_object}.println({self._expr(m.group(1))});"),
            # Window Management (library-specific availability)
            (r"SETWINDOW\s+(.+?),\s*(.+?),\s*(.+?),\s*(.+)", lambda m: f"{self.display_object}.setWindow({self._expr(m.group(1))}, {self._expr(m.group(2))}, {self._expr(m.group(3))}, {self._expr(m.group(4))});"),
            (r"SETADDRWINDOW\s+(.+?),\s*(.+?),\s*(.+?),\s*(.+)", lambda m: f"{self.display_object}.setAddrWindow({self._expr(m.group(1))}, {self._expr(m.group(2))}, {self._expr(m.group(3))}, {self._expr(m.group(4))});"),
            (r"SETVIEWPORT\s+(.+?),\s*(.+?),\s*(.+?),\s*(.+)", lambda m: f"{self.display_object}.setViewport({self._expr(m.group(1))}, {self._expr(m.group(2))}, {self._expr(m.group(3))}, {self._expr(m.group(4))});"),
            (r"RESETVIEWPORT\s*", lambda m: f"{self.display_object}.resetViewport();"),
            (r"FRAMEVIEWPORT\s+(.+?),\s*(.+)", lambda m: f"{self.display_object}.frameViewport({self._expr(m.group(1))}, {self._expr(m.group(2))});"),
            (r"SETORIGIN\s+(.+?),\s*(.+)", lambda m: f"{self.display_object}.setOrigin({self._expr(m.group(1))}, {self._expr(m.group(2))});"),
            (r"PUSHPIXEL\s+(.+)", lambda m: f"{self.display_object}.pushColor({self._expr(m.group(1))});"),
            (r"PUSHBLOCK\s+(.+?),\s*(.+)", lambda m: f"{self.display_object}.pushBlock({self._expr(m.group(1))}, {self._expr(m.group(2))});"),
        ]
        for pat, fn in io_patterns:
            m = re.match(pat, line, re.IGNORECASE)
            if m:
                res = fn(m)
                # If the handler returns None, it already injected side-effects (eg. sprite creation)
                return res        
        # Handle assignments
        if "=" in line:
            m_assign = re.match(r"(\w+)\s*=\s*(.+)", line)
            if m_assign:
                var, expr = m_assign.groups()
                return f"{var} = {self._expr(expr)};"
        
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
        # Handle nested parentheses properly
        def extract_method_call(line):
            """Extract (method_name, args) from method call, handling nested parens."""
            # Match identifier.method or identifier::method or identifier->method
            m_start = re.match(r"([\w:]+(?:(?:\.|->|::)[\w:]+)*)\s*\(", line)
            if not m_start:
                return None, None
            
            method_name = m_start.group(1)
            start_paren = m_start.end() - 1  # Position of opening paren
            
            # Find matching closing paren, handling nesting
            paren_count = 0
            i = start_paren
            while i < len(line):
                if line[i] == '(':
                    paren_count += 1
                elif line[i] == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        args = line[start_paren + 1:i]
                        return method_name, args
                i += 1
            
            return None, None  # Unclosed parens
        
        method_name, args = extract_method_call(line)
        if method_name and "=" not in line and ("." in method_name or "->" in method_name or "::" in method_name):
            # This is a method call
            if args is not None:
                # Split args by comma, but respect nested parentheses
                args_list = []
                current_arg = ""
                paren_depth = 0
                for char in args:
                    if char == '(':
                        paren_depth += 1
                        current_arg += char
                    elif char == ')':
                        paren_depth -= 1
                        current_arg += char
                    elif char == ',' and paren_depth == 0:
                        if current_arg.strip():
                            args_list.append(current_arg.strip())
                        current_arg = ""
                    else:
                        current_arg += char
                if current_arg.strip():
                    args_list.append(current_arg.strip())
                
                args_expr = ", ".join([self._expr(a) for a in args_list]) if args_list else ""
                call_line = f"{method_name}({args_expr});"
                return self._apply_pointer_access(call_line)
            else:
                call_line = f"{method_name}();"
                return self._apply_pointer_access(call_line)

        # Standalone function calls: FunctionName(args) or FunctionName()
        # This handles calls without a . or -> like InitBoard(), DrawBoard(), HandleButtonPress(), etc.
        if "=" not in line:  # Not an assignment
            m_standalone_call = re.match(r"(\w+)\s*\(", line)
            if m_standalone_call:
                func_name = m_standalone_call.group(1)
                # Find the matching closing paren
                start_paren = m_standalone_call.end() - 1
                paren_count = 0
                i = start_paren
                while i < len(line):
                    if line[i] == '(':
                        paren_count += 1
                    elif line[i] == ')':
                        paren_count -= 1
                        if paren_count == 0:
                            args = line[start_paren + 1:i]
                            # Split args by comma, respecting nested parentheses
                            args_list = []
                            current_arg = ""
                            paren_depth = 0
                            for char in args:
                                if char == '(':
                                    paren_depth += 1
                                    current_arg += char
                                elif char == ')':
                                    paren_depth -= 1
                                    current_arg += char
                                elif char == ',' and paren_depth == 0:
                                    if current_arg.strip():
                                        args_list.append(current_arg.strip())
                                    current_arg = ""
                                else:
                                    current_arg += char
                            if current_arg.strip():
                                args_list.append(current_arg.strip())
                            
                            args_expr = ", ".join([self._expr(a) for a in args_list]) if args_list else ""
                            return f"{func_name}({args_expr});"
                    i += 1

        # Assignments: x = expr
        m_assign = re.match(r"(\w+(?:\s*\[.+?\]|\s*\(.+?\))?)\s*=\s*(.+)", line)
        if m_assign:
            lhs, rhs = m_assign.groups()
            # Convert VB array syntax arr(i,j) to C arr[i][j]
            def convert_lhs_array(s):
                # Split by comma inside parens to handle multi-dimensional
                return re.sub(r"(\w+)\(([^)]+)\)", lambda m: m.group(1) + "".join([f"[{idx.strip()}]" for idx in m.group(2).split(",")]), s)
            lhs = convert_lhs_array(lhs)
            return f"{lhs} = {self._expr(rhs)};"
        
        # Return statement
        if upper.startswith("RETURN "):
            expr = line[7:].strip()
            return f"return {self._expr(expr)};"

        return f"// TODO: {line}"

    def _expr(self, expr: str, is_condition: bool = False) -> str:
        # --- Mod operator (VB6) to % (C++) ---
        expr = re.sub(r"\bMod\b", "%", expr, flags=re.IGNORECASE)
        expr = expr.strip()
        # --- UBound/LBound support ---
        # UBound(arr[, dim]) returns upper bound; LBound(arr[, dim]) returns lower bound
        # Must handle BEFORE array conversion since UBound/LBound have parentheses
        def replace_ubound(match):
            arr_name = match.group(1)
            dim = match.group(2)  # May be None
            if arr_name in self.array_dimensions:
                dims = self.array_dimensions[arr_name]
                if dim:
                    try:
                        dim_idx = int(dim) - 1  # VB is 1-based for dimension numbering
                        if 0 <= dim_idx < len(dims):
                            size = dims[dim_idx]
                            if isinstance(size, int):
                                return str(size)
                            else:
                                return f"({size})"
                    except ValueError:
                        pass
                else:
                    # No dimension specified, use first (for 1D arrays)
                    size = dims[0] if dims else 0
                    if isinstance(size, int):
                        return str(size)
                    else:
                        return f"({size})"
            return match.group(0)  # Keep original if not found
        
        expr = re.sub(r"\bUBOUND\s*\(\s*(\w+)\s*(?:,\s*(\d+)\s*)?\)", replace_ubound, expr, flags=re.IGNORECASE)
        
        def replace_lbound(match):
            arr_name = match.group(1)
            # LBound always returns option_base (0 or 1)
            return str(self.option_base)
        
        expr = re.sub(r"\bLBOUND\s*\(\s*(\w+)\s*(?:,\s*(\d+)\s*)?\)", replace_lbound, expr, flags=re.IGNORECASE)
        
        # --- Hex/Oct/Bin literals ---
        expr = re.sub(r"&H([0-9A-Fa-f]+)", lambda m: f"0x{m.group(1)}", expr)
        expr = re.sub(r"&O([0-7]+)", lambda m: f"0{oct(int(m.group(1), 8))[2:]}", expr)
        expr = re.sub(r"&B([01]+)", lambda m: f"0b{m.group(1)}", expr)
        # --- String manipulation functions ---
        expr = re.sub(r"\bLEFT\s*\(([^,]+),\s*([^)]+)\)", r"\1.substring(0, \2)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bRIGHT\s*\(([^,]+),\s*([^)]+)\)", r"\1.substring(\1.length()-\2)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bMID\s*\(([^,]+),\s*([^)]+)\)", r"\1.substring(\2-1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bLEN\s*\(([^)]+)\)", r"\1.length()", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bINSTR\s*\(([^,]+),\s*([^)]+)\)", r"(\1.indexOf(\2) + 1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bSUBSTRING\s*\(([^,]+),\s*([^,]+),\s*([^)]+)\)", r"\1.substring(\2, \2 + \3)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bSTRREPLACE\s*\(([^,]+),\s*([^,]+),\s*([^)]+)\)", r"\1.replace(\2, \3)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bREPLACE\s*\(([^,]+),\s*([^,]+),\s*([^)]+)\)", r"\1.replace(\2, \3)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bTRIM\s*\(([^)]+)\)", r"\1.trim()", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bLTRIM\s*\(([^)]+)\)", r"\1.trim()", expr, flags=re.IGNORECASE)  # Arduino String doesn't have ltrim
        expr = re.sub(r"\bRTRIM\s*\(([^)]+)\)", r"\1.trim()", expr, flags=re.IGNORECASE)  # Arduino String doesn't have rtrim
        expr = re.sub(r"\bUPPER\s*\(([^)]+)\)", r"\1", expr, flags=re.IGNORECASE)  # TODO: needs custom implementation
        expr = re.sub(r"\bLOWER\s*\(([^)]+)\)", r"\1", expr, flags=re.IGNORECASE)  # TODO: needs custom implementation
        # --- Bit operations ---
        expr = re.sub(r"\bBITREAD\s*\(([^,]+),\s*([^)]+)\)", r"((\1 >> \2) & 1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bBITWRITE\s*\(([^,]+),\s*([^,]+),\s*([^)]+)\)", r"(\3 ? (\1 | (1 << \2)) : (\1 & ~(1 << \2)))", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bBITSET\s*\(([^,]+),\s*([^)]+)\)", r"(\1 | (1 << \2))", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bBITCLEAR\s*\(([^,]+),\s*([^)]+)\)", r"(\1 & ~(1 << \2))", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bBITSHIFTLEFT\s*\(([^,]+),\s*([^)]+)\)", r"(\1 << \2)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bBITSHIFTRIGHT\s*\(([^,]+),\s*([^)]+)\)", r"(\1 >> \2)", expr, flags=re.IGNORECASE)
        # --- IIf (inline if) ---
        expr = re.sub(r"\bIIF\s*\(([^,]+),\s*([^,]+),\s*([^)]+)\)", r"(\1 ? \2 : \3)", expr, flags=re.IGNORECASE)
        # --- Type conversion functions ---
        expr = re.sub(r"\bCSTR\s*\(([^)]+)\)", r"String(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bCINT\s*\(([^)]+)\)", r"atoi(String(\1).c_str())", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bCLNG\s*\(([^)]+)\)", r"atol(String(\1).c_str())", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bCDBL\s*\(([^)]+)\)", r"atof(String(\1).c_str())", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bCSNG\s*\(([^)]+)\)", r"atof(String(\1).c_str())", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bCBYTE\s*\(([^)]+)\)", r"(byte)(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bCBOOL\s*\(([^)]+)\)", r"(bool)(\1)", expr, flags=re.IGNORECASE)
        # --- String functions ---
        # String(n, char) creates n repetitions of char - MUST come before Space()
        # VB6: String(count, character) -> Arduino String(char, count)
        def string_func_replacement(match):
            count, char = match.groups()
            char = char.strip()
            # Check if it's a single-character string literal like "*" or "x"
            if char.startswith('"') and char.endswith('"'):
                char_content = char[1:-1]  # Remove quotes
                if len(char_content) == 1:  # Single character
                    # Convert "x" to 'x' for Arduino String constructor
                    return f"String('{char_content}', {count})"
                else:
                    # Multi-char string - need to repeat it manually
                    # Use a simple concatenation loop (not ideal but works)
                    return f"/* TODO: String({count}, {char}) not directly supported */ String({char})"
            elif char.startswith("'") and char.endswith("'"):  # Already a char literal like 'x'
                return f"String({char}, {count})"
            else:
                # It's a variable or expression - assume it's a char
                return f"String({char}, {count})"
        expr = re.sub(r"\bSTRING\s*\(([^,]+),\s*([^)]+)\)", string_func_replacement, expr, flags=re.IGNORECASE)
        # Space(n) creates n spaces - Arduino String constructor is String(char, count)
        # Process AFTER String() to avoid conflicts
        expr = re.sub(r"\bSPACE\s*\(([^)]+)\)", r"String(' ', \1)", expr, flags=re.IGNORECASE)
        # --- Type checking ---
        expr = re.sub(r"\bISNUMERIC\s*\(([^)]+)\)", r"(String(\1).toInt() != 0 || String(\1) == \"0\")", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bISEMPTY\s*\(([^)]+)\)", r"(String(\1).length() == 0)", expr, flags=re.IGNORECASE)
        # --- Array/string helpers (runtime helpers implemented in generated code) ---
        expr = re.sub(r"\bSPLIT\s*\(([^,]+),\s*([^)]+)\)", r"__vb_split(String(\1), String(\2))", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bJOIN\s*\(([^,]+),\s*([^)]+)\)", r"__vb_join(\1, String(\2))", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bFILTER\s*\(([^,]+),\s*([^)]+)\)", r"__vb_filter(\1, String(\2))", expr, flags=re.IGNORECASE)
        # --- Memory diagnostics ---
        expr = re.sub(r"\bFREERAM\s*\(\)", r"ESP.getFreeHeap()", expr, flags=re.IGNORECASE)
        # --- NEW: More string conversions and character functions ---
        expr = re.sub(r"\bVAL\s*\(([^)]+)\)", r"atof(String(\1).c_str())", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bHEX\$\s*\(([^)]+)\)", r"String(\1, HEX)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bOCT\$\s*\(([^)]+)\)", r"String(\1, OCT)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bCHR\$\s*\(([^)]+)\)", r"String((char)(\1))", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bCHR\s*\(([^)]+)\)", r"String((char)(\1))", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bASC\s*\(([^)]+)\)", r"(int)((\1).charAt(0))", expr, flags=re.IGNORECASE)

        # --- NEW: More string functions ---
        expr = re.sub(r"\bINSTRREV\s*\(([^,]+),\s*([^)]+)\)", r"(\1.lastIndexOf(\2) + 1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bSTRCOMP\s*\(([^,]+),\s*([^)]+)\)", r"(\1.compareTo(\2))", expr, flags=re.IGNORECASE)
        # StrReverse needs custom implementation
        def strreverse_replacement(match):
            s = match.group(1)
            return f"([&]{{String _s={s}; String _r=\"\"; for(int _i=_s.length()-1;_i>=0;_i--)_r+=_s[_i]; return _r;}}())"
        expr = re.sub(r"\bSTRREVERSE\s*\(([^)]+)\)", strreverse_replacement, expr, flags=re.IGNORECASE)

        # --- NEW: Additional type checking ---
        expr = re.sub(r"\bISNOTHING\s*\(([^)]+)\)", r"((\1) == nullptr)", expr, flags=re.IGNORECASE)
        # IsArray would need compile-time type info, so we'll skip it for now
        
        # --- RGB color helper ---
        # Library-specific RGB mapping handled after library detection
        # --- Math functions ---
        expr = re.sub(r"\bSQR\s*\(([^)]+)\)", r"sqrt(\1)", expr, flags=re.IGNORECASE)
        # --- NEW: Additional math functions ---
        expr = re.sub(r"\bROUND\s*\(([^)]+)\)", r"round(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bFIX\s*\(([^)]+)\)", r"trunc(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bSGN\s*\(([^)]+)\)", r"(((\1) > 0) ? 1 : ((\1) < 0) ? -1 : 0)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bLOG\s*\(([^)]+)\)", r"log(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bEXP\s*\(([^)]+)\)", r"exp(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bATN\s*\(([^)]+)\)", r"atan(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bSIN\s*\(([^)]+)\)", r"sin(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bCOS\s*\(([^)]+)\)", r"cos(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bTAN\s*\(([^)]+)\)", r"tan(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bABS\s*\(([^)]+)\)", r"abs(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bRND\s*\(\)", r"random(0, 32767)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bINT\s*\(([^)]+)\)", r"int(\1)", expr, flags=re.IGNORECASE)

        # --- NEW: Timer function ---
        expr = re.sub(r"\bTIMER\s*\(\)", r"millis()", expr, flags=re.IGNORECASE)

        # --- NEW: Choose function - Choose(index, val1, val2, val3, ...)
        # Complex: needs to parse variable arguments
        def choose_replacement(match):
            content = match.group(1)
            params = self._split_params_balanced(content)
            if len(params) < 2:
                return f"/* ERROR: Choose needs at least 2 parameters */"
            index = self._expr(params[0])
            values = [self._expr(p) for p in params[1:]]
            # Generate ternary chain: index==1?val1:index==2?val2:...
            result = ""
            for i, val in enumerate(values, start=1):
                if i == 1:
                    result = f"(({index})=={i}?{val}"
                elif i == len(values):
                    result += f":(({index})=={i}?{val}:String(\"\")))"
                else:
                    result += f":(({index})=={i}?{val}"
            return result
        expr = re.sub(r"\bCHOOSE\s*\(([^)]+(?:\([^)]*\))*[^)]*)\)", choose_replacement, expr, flags=re.IGNORECASE)

        # --- NEW: Switch function - Switch(cond1, val1, cond2, val2, ...)
        def switch_replacement(match):
            content = match.group(1)
            params = self._split_params_balanced(content)
            if len(params) < 2 or len(params) % 2 != 0:
                return f"/* ERROR: Switch needs even number of parameters */"
            # Generate ternary chain
            result = ""
            for i in range(0, len(params), 2):
                cond = self._expr(params[i])
                val = self._expr(params[i+1])
                if i == 0:
                    result = f"({cond}?{val}"
                elif i == len(params) - 2:
                    result += f":({cond}?{val}:String(\"\")))"
                else:
                    result += f":({cond}?{val}"
            return result
        expr = re.sub(r"\bSWITCH\s*\(([^)]+(?:\([^)]*\))*[^)]*)\)", switch_replacement, expr, flags=re.IGNORECASE)
        
        # Function mappings - do these FIRST before array conversion
        expr = re.sub(r"\bDIGITALREAD\s*\(([^)]+)\)", r"digitalRead(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bANALOGREAD\s*\(([^)]+)\)", r"analogRead(\1)", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bMILLIS\s*\(\)", "millis()", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bSERIALAVAILABLE\s*\(\)", "Serial.available()", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bSERIALREAD\s*\(\)", "Serial.read()", expr, flags=re.IGNORECASE)
        # VB string concatenation: '&' -> '+' for Arduino String
        if '&' in expr:
            expr = re.sub(r"\s*&\s*", " + ", expr)
        # RGB color helper (library-specific)
        def rgb_replacement(match):
            r, g, b = match.groups()
            if self.graphics_lib == 'tft_espi':
                return f"tft.color565({r}, {g}, {b})"
            elif self.graphics_lib == 'adafruit_gfx':
                return f"((({r} & 0xF8) << 8) | (({g} & 0xFC) << 3) | ({b} >> 3))"
            else:
                # Default to 565 format
                return f"((({r} & 0xF8) << 8) | (({g} & 0xFC) << 3) | ({b} >> 3))"
        expr = re.sub(r"\bRGB\s*\(([^,]+),\s*([^,]+),\s*([^)]+)\)", rgb_replacement, expr, flags=re.IGNORECASE)
        # Servo helpers
        # 3-arg: SERVO_DEG2PULSE(angle, minUS, maxUS)
        expr = re.sub(r"\bSERVO_DEG2PULSE\s*\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\)", r"(int)((\2) + ((\3)-(\2)) * ((\1) / 180.0))", expr, flags=re.IGNORECASE)
        # 1-arg default range 1000..2000us: SERVO_DEG2PULSE(angle)
        expr = re.sub(r"\bSERVO_DEG2PULSE\s*\(\s*([^)]+)\)", r"(int)(1000 + ((\1) * (1000.0/180.0)))", expr, flags=re.IGNORECASE)
        # 3-arg: SERVO_CLAMP_DEG2PULSE(angle, minUS, maxUS)
        expr = re.sub(r"\bSERVO_CLAMP_DEG2PULSE\s*\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\)", r"(int)((\2) + ((\3)-(\2)) * (((int)min(180, max(0, (int)(\1)))) / 180.0))", expr, flags=re.IGNORECASE)
        # 1-arg default range 1000..2000us: SERVO_CLAMP_DEG2PULSE(angle)
        expr = re.sub(r"\bSERVO_CLAMP_DEG2PULSE\s*\(\s*([^)]+)\)", r"(int)(1000 + (((int)min(180, max(0, (int)(\1)))) * (1000.0/180.0)))", expr, flags=re.IGNORECASE)
        # Clamp helper
        expr = re.sub(r"\bSERVO_CLAMP\s*\(\s*([^)]+)\)", r"(int)min(180, max(0, (int)(\1)))", expr, flags=re.IGNORECASE)
        # Explicit bitwise helpers
        expr = re.sub(r"\bBITOR\b", "|", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bBITAND\b", "&", expr, flags=re.IGNORECASE)
        # new operator
        expr = re.sub(r"\bNEW\s+(\w+)\s*\(\)", r"new \1()", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bNEW\s+(\w+)", r"new \1()", expr, flags=re.IGNORECASE)
        
        # Map VB6 built-in constants (string & boolean)
        expr = self._map_vb_constants(expr)
        
        # Unified color constants - map to library-specific format
        expr = self._map_color_constants(expr)
        
        # Convert VB array syntax arr(i) or arr(i,j) to C arr[i] or arr[i][j]
        # Handle multi-dimensional array indexing: arr(i,j,k) -> arr[i][j][k]
        # Skip if it's a known function name
        known_functions = ["digitalRead", "analogRead", "millis", "Serial", "pinMode", "digitalWrite", 
                          "analogWrite", "delay", "min", "max", "abs", "constrain", "map", "UBound", "LBound",
                          "begin", "print", "println", "read", "write", "available", "setup", "loop",
                          "checkwin", "checkwinhuman", "checkwinai",
                          "len", "substring", "instr", "strreplace", "replace", "trim", "ltrim", "rtrim", "upper", "lower",
                          "bitread", "bitwrite", "bitset", "bitclear", "bitshiftleft", "bitshiftright",
                          "left", "right", "mid", "sqr", "sin", "cos", "tan", "int", "rnd",
                          # VB6 enhancements
                          "iif", "cstr", "cint", "clng", "cdbl", "csng", "cbyte", "cbool",
                          "space", "string", "isnumeric", "isempty", "freeram", "rgb",
                          "servo_deg2pulse", "servo_clamp", "servo_clamp_deg2pulse",
                                                  # NEW: String conversions and functions
                                                  "val", "hex$", "oct$", "chr", "chr$", "asc",
                                                  "instrrev", "strcomp", "strreverse",
                                                  # NEW: Math functions
                                                  "round", "fix", "sgn", "log", "exp", "atn",
                                                  # NEW: Complex functions
                                                  "choose", "switch", "timer",
                                                  # NEW: Type checking
                                                  "isnothing",
                                                  # NEW: Array/string helpers
                                                  "split", "join", "filter",
                          # Arduino/C++ functions that should not be converted
                                                  "round", "trunc", "log", "exp", "atan", "randomSeed",
                          "atoi", "atol", "atof", "byte", "bool", "chr", "sqrt",
                          # Arduino types/classes (capital first letter)
                          "String"]  # Add user-defined functions that look like array calls
        def convert_array_access(match):
            name = match.group(1)
            indices_str = match.group(2)
            # Don't convert if it's a known function or starts with capital (likely a function)
            if name.lower() in [f.lower() for f in known_functions]:
                return match.group(0)  # Keep as-is
            # Convert to array syntax: split by comma for multi-dimensional arrays
            indices = [idx.strip() for idx in indices_str.split(",")]
            brackets = "".join([f"[{idx}]" for idx in indices])
            return f"{name}{brackets}"
        
        # Match arr(...) but NOT after a dot (to exclude method calls like Serial.println)
        expr = re.sub(r"(?<!\.)(\b[a-z_]\w*)\(([^()]+)\)(?!\s*\()", convert_array_access, expr, flags=re.IGNORECASE)
        
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

    def _emit_strreplace(self, m) -> str:
        """Helper for STRREPLACE(str, find, replace)."""
        str_expr = self._expr(m.group(1))
        find_expr = self._expr(m.group(2))
        replace_expr = self._expr(m.group(3))
        # Arduino String doesn't have built-in replace, use simple loop replacement
        return f"({str_expr}.replace({find_expr}, {replace_expr}))"
    
    def _emit_settextcolor(self, params_str: str) -> str:
        """Helper for SETTEXTCOLOR with balanced parameter parsing."""
        params = self._split_params_balanced(params_str)
        if len(params) == 2:
            return f"{self.display_object}.setTextColor({self._expr(params[0])}, {self._expr(params[1])});"
        elif len(params) == 1:
            return f"{self.display_object}.setTextColor({self._expr(params[0])});"
        else:
            return f"// ERROR: SETTEXTCOLOR expects 1 or 2 parameters, got {len(params)}"
    
    def _emit_trim(self, m) -> str:
        """Helper for TRIM(str) - remove leading/trailing whitespace."""
        str_expr = self._expr(m.group(1))
        # Simple trim implementation for Arduino String
        return f"({str_expr}.substring({str_expr}.lastIndexOf(' ') + 1))"
    
    def _emit_ltrim(self, m) -> str:
        """Helper for LTRIM(str) - remove leading whitespace."""
        str_expr = self._expr(m.group(1))
        return f"({str_expr}.substring({str_expr}.indexOf(' ') + 1))"
    
    def _emit_rtrim(self, m) -> str:
        """Helper for RTRIM(str) - remove trailing whitespace."""
        str_expr = self._expr(m.group(1))
        return f"({str_expr}.substring(0, {str_expr}.lastIndexOf(' ')))"
    
    def _emit_upper(self, m) -> str:
        """Helper for UPPER(str) - convert to uppercase."""
        str_expr = self._expr(m.group(1))
        # Need to iterate and call toUpperCase() in Arduino
        return f"({str_expr}) /* TODO: use toUpperCase() in loop */"
    
    def _emit_lower(self, m) -> str:
        """Helper for LOWER(str) - convert to lowercase."""
        str_expr = self._expr(m.group(1))
        return f"({str_expr}) /* TODO: use toLowerCase() in loop */"
    
    def _emit_bitwrite(self, m) -> str:
        """Helper for BITWRITE(value, bit, state)."""
        val_expr = self._expr(m.group(1))
        bit_expr = self._expr(m.group(2))
        state_expr = self._expr(m.group(3))
        return f"(({state_expr}) ? ({val_expr} | (1 << {bit_expr})) : ({val_expr} & ~(1 << {bit_expr})))"

    def _detect_graphics_lib(self, include: str) -> None:
        """Detect which graphics library is being used from include statement."""
        include_lower = include.lower()
        if 'tft_espi' in include_lower:
            self.graphics_lib = 'tft_espi'
            self.display_object = 'tft'
        elif 'adafruit_gfx' in include_lower or 'adafruit_ssd' in include_lower or 'adafruit_st' in include_lower or 'adafruit_ili' in include_lower:
            self.graphics_lib = 'adafruit_gfx'
            # Common object names: gfx, display, tft
            self.display_object = 'display'
        elif 'u8g2' in include_lower or 'u8x8' in include_lower:
            self.graphics_lib = 'u8g2'
            self.display_object = 'u8g2'
        elif 'lvgl' in include_lower:
            self.graphics_lib = 'lvgl'
            self.display_object = 'lv'

    def _get_graphics_call(self, method: str, *args) -> str:
        """Generate library-specific graphics call."""
        if not self.graphics_lib:
            # Default to TFT_eSPI if no library detected
            self.graphics_lib = 'tft_espi'
        
        # Format arguments
        args_str = ", ".join(str(arg) for arg in args)
        
        # Library-specific mappings
        if self.graphics_lib == 'u8g2':
            # U8g2 is monochrome, strip color parameters
            if method in ('drawLine', 'drawRect', 'fillRect', 'drawCircle', 'fillCircle', 'drawPixel'):
                # Remove last argument (color) for U8g2
                args_list = list(args)
                if len(args_list) > 0:
                    args_list = args_list[:-1]
                    args_str = ", ".join(str(arg) for arg in args_list)
        
        return f"{self.display_object}.{method}({args_str})"

    # Sprite helpers
    def _emit_create_sprite(self, name: str, w: str, h: str) -> str | None:
        w_expr = self._expr(w)
        h_expr = self._expr(h)
        decl = f"TFT_eSprite {name} = TFT_eSprite(&tft);"
        if decl not in self.global_lines:
            # place declaration after helpers to keep globals organized
            self.global_lines.append(decl)
            if self.setup_lines is not None:
                # create sprite in setup AFTER any size/initialization assignments
                self.setup_lines.append(f"{name}.createSprite({w_expr}, {h_expr});")
        return f"// CREATE_SPRITE {name} {w_expr} {h_expr}"

    # Handlers that need balanced param splitting
    def _handle_sprite_fill_ellipse(self, m) -> str:
        name = m.group(1)
        params = self._split_params_balanced(m.group(2))
        if len(params) < 5:
            # fall back to raw emission so failures are visible
            return f"// TODO: SPRITE_FILL_ELLIPSE parse error: {m.group(0)}"
        # ensure exactly 5 parameters
        args = params[:5]
        return self._emit_sprite_method('fillEllipse', name, args)

    def _handle_sprite_fill_triangle(self, m) -> str:
        name = m.group(1)
        params = self._split_params_balanced(m.group(2))
        if len(params) < 7:
            return f"// TODO: SPRITE_FILL_TRIANGLE parse error: {m.group(0)}"
        args = params[:7]
        return self._emit_sprite_method('fillTriangle', name, args)

    def _emit_sprite_method(self, method: str, name: str, args: list) -> str:
        args_str = ", ".join(self._expr(a) for a in args)
        return f"{name}.{method}({args_str});"

    def _emit_sprite_push(self, name: str, x: str, y: str, bg: str | None) -> str:
        x_expr = self._expr(x)
        y_expr = self._expr(y)
        if bg:
            bg_expr = self._expr(bg)
            return f"{name}.pushSprite({x_expr}, {y_expr}, {bg_expr});"
        return f"{name}.pushSprite({x_expr}, {y_expr});"

    def _map_vb_constants(self, expr: str) -> str:
        """Map VB6 and GDScript built-in constants to C++ equivalents."""
        vb_const_map = {
            # String constants - double-escape to preserve in output
            'vbCr': '"\\\\r"',
            'vbLf': '"\\\\n"',
            'vbCrLf': '"\\\\r\\\\n"',
            'vbTab': '"\\\\t"',
            'vbNullChar': '"\\\\0"',
            'vbNullString': '""',
            # Boolean constants
            'vbTrue': 'true',
            'vbFalse': 'false',
            # Math constants (GDScript-inspired)
            'PI': 'PI',            # Arduino core defines PI
            'TAU': '(2.0 * PI)',   # TAU = 2 * PI
            'DEG2RAD': '(PI / 180.0)',  # degrees to radians
            'RAD2DEG': '(180.0 / PI)',  # radians to degrees
            'INF': 'INFINITY',     # C99 infinity
            'NAN': 'NAN',          # Not-a-Number
            # Status constants (GDScript-inspired)
            'OK': '0',
            'FAILED': '-1',
        }

        for vb_const, cpp_value in vb_const_map.items():
            expr = re.sub(rf'\b{vb_const}\b', cpp_value, expr, flags=re.IGNORECASE)

        return expr

    def _map_color_constants(self, expr: str) -> str:
        """Map unified color constants to library-specific format."""
        # Color mappings for different libraries
        color_map = {
            # Basic colors (both COLOR_ and vb prefix)
            'COLOR_BLACK': {'tft_espi': 'TFT_BLACK', 'adafruit_gfx': 'BLACK', 'u8g2': '0'},
            'vbBlack': {'tft_espi': 'TFT_BLACK', 'adafruit_gfx': 'BLACK', 'u8g2': '0'},
            'COLOR_WHITE': {'tft_espi': 'TFT_WHITE', 'adafruit_gfx': 'WHITE', 'u8g2': '1'},
            'vbWhite': {'tft_espi': 'TFT_WHITE', 'adafruit_gfx': 'WHITE', 'u8g2': '1'},
            'COLOR_RED': {'tft_espi': 'TFT_RED', 'adafruit_gfx': 'RED', 'u8g2': '1'},
            'vbRed': {'tft_espi': 'TFT_RED', 'adafruit_gfx': 'RED', 'u8g2': '1'},
            'COLOR_GREEN': {'tft_espi': 'TFT_GREEN', 'adafruit_gfx': 'GREEN', 'u8g2': '1'},
            'vbGreen': {'tft_espi': 'TFT_GREEN', 'adafruit_gfx': 'GREEN', 'u8g2': '1'},
            'COLOR_BLUE': {'tft_espi': 'TFT_BLUE', 'adafruit_gfx': 'BLUE', 'u8g2': '1'},
            'vbBlue': {'tft_espi': 'TFT_BLUE', 'adafruit_gfx': 'BLUE', 'u8g2': '1'},
            'COLOR_YELLOW': {'tft_espi': 'TFT_YELLOW', 'adafruit_gfx': 'YELLOW', 'u8g2': '1'},
            'vbYellow': {'tft_espi': 'TFT_YELLOW', 'adafruit_gfx': 'YELLOW', 'u8g2': '1'},
            'COLOR_CYAN': {'tft_espi': 'TFT_CYAN', 'adafruit_gfx': 'CYAN', 'u8g2': '1'},
            'vbCyan': {'tft_espi': 'TFT_CYAN', 'adafruit_gfx': 'CYAN', 'u8g2': '1'},
            'COLOR_MAGENTA': {'tft_espi': 'TFT_MAGENTA', 'adafruit_gfx': 'MAGENTA', 'u8g2': '1'},
            'vbMagenta': {'tft_espi': 'TFT_MAGENTA', 'adafruit_gfx': 'MAGENTA', 'u8g2': '1'},
            # Extended colors (TFT/Adafruit only, map to white for U8g2)
            'COLOR_ORANGE': {'tft_espi': 'TFT_ORANGE', 'adafruit_gfx': 'ORANGE', 'u8g2': '1'},
            'COLOR_PURPLE': {'tft_espi': 'TFT_PURPLE', 'adafruit_gfx': 'MAGENTA', 'u8g2': '1'},
            'COLOR_PINK': {'tft_espi': 'TFT_PINK', 'adafruit_gfx': 'MAGENTA', 'u8g2': '1'},
            'COLOR_BROWN': {'tft_espi': 'TFT_BROWN', 'adafruit_gfx': 'BROWN', 'u8g2': '1'},
            'COLOR_GRAY': {'tft_espi': 'TFT_DARKGREY', 'adafruit_gfx': 'LIGHTGREY', 'u8g2': '1'},
            'COLOR_DARKGRAY': {'tft_espi': 'TFT_DARKGREY', 'adafruit_gfx': 'DARKGREY', 'u8g2': '1'},
            'COLOR_LIGHTGRAY': {'tft_espi': 'TFT_LIGHTGREY', 'adafruit_gfx': 'LIGHTGREY', 'u8g2': '1'},
        }
        
        # Determine library (default to tft_espi)
        lib = self.graphics_lib or 'tft_espi'
        
        # Replace color constants
        for color_const, lib_map in color_map.items():
            target_color = lib_map.get(lib, lib_map['tft_espi'])
            # Case-insensitive replacement with word boundaries
            expr = re.sub(rf'\b{color_const}\b', target_color, expr, flags=re.IGNORECASE)
        
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
        # Always need vector for Split/Join/Filter helpers
        helper_includes = "#include <vector>\n"
        includes_section = helper_includes
        if self.includes:
            includes_section += "\n".join(f"#include {inc}" for inc in sorted(self.includes)) + "\n\n"
        else:
            includes_section += "\n"

        # Forward declarations for all functions
        forward_declarations = ""
        if self.function_signatures:
            forward_declarations = "\n".join(self.function_signatures) + "\n\n"

        # Runtime helpers for Split/Join/Filter - include only if used
        helpers = ""
        content_to_scan = "\n".join(self.global_lines + self.function_lines + self.setup_lines + self.loop_lines)
        if '__vb_split' in content_to_scan or '__vb_join' in content_to_scan or '__vb_filter' in content_to_scan:
            helpers = """
// Runtime helpers generated by transpiler
static std::vector<String> __vb_split(const String& input, const String& delim) {
    std::vector<String> parts;
    int start = 0;
    int idx = 0;
    if (delim.length() == 0) { parts.push_back(input); return parts; }
    while ((idx = input.indexOf(delim, start)) != -1) {
        parts.push_back(input.substring(start, idx));
        start = idx + delim.length();
    }
    parts.push_back(input.substring(start));
    return parts;
}

static String __vb_join(const std::vector<String>& parts, const String& delim) {
    String out = "";
    for (size_t i = 0; i < parts.size(); ++i) {
        out += parts[i];
        if (i + 1 < parts.size()) out += delim;
    }
    return out;
}

static std::vector<String> __vb_filter(const std::vector<String>& parts, const String& match) {
    std::vector<String> out;
    for (const auto& p : parts) {
        if (p.indexOf(match) != -1) out.push_back(p);
    }
    return out;
}
"""

        # --- Inject TFT_eSPI tft; declaration and tft.begin() if using TFT_eSPI ---
        tft_declaration = ""
        tft_init = ""
        if self.graphics_lib == 'tft_espi' or (self.graphics_lib is None and any('TFT_eSPI.h' in inc for inc in self.includes)):
            tft_declaration = "TFT_eSPI tft;\n"
            tft_init = "tft.begin();\n    "

        globals_section = helpers + "\n" + tft_declaration + "\n".join(self.global_lines)
        functions_section = "".join(self.function_lines) if self.function_lines else ""

        # Add initialization delay at the start of setup for USB/serial init
        setup_lines_list = self.setup_lines if self.setup_lines else []
        if setup_lines_list:
            setup_section = f"delay(1000);\n    {tft_init}" + "\n    ".join(setup_lines_list)
        else:
            setup_section = f"delay(1000);\n    {tft_init}".rstrip()

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
