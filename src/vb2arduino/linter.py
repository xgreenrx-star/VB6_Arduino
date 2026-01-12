"""Lightweight static linter for VB2Arduino VB-like sources.

Provides a simple ruleset and a runner that returns diagnostics usable by
an IDE Problems panel.
"""
import re
from typing import List, Dict

Rule = Dict[str, object]

# Simple rules
RULES = [
    {
        "id": "debug-draw",
        "severity": "warning",
        "pattern": re.compile(r"\b(tft\.fillTriangle|SPRITE_FILL_ELLIPSE)\b", re.IGNORECASE),
        "message": "Debug drawing call detected; this may overlay graphics in final output",
        "fix": "remove_line",
    },
    {
        "id": "wildcard-import",
        "severity": "warning",
        "pattern": re.compile(r"from\s+\w+(?:\.\w+)*\s+import\s+\*"),
        "message": "Wildcard import detected; prefer explicit imports for clarity",
    },
    {
        "id": "suspicious-baud",
        "severity": "info",
        "pattern": re.compile(r"\b(300|1200|2400|4800|9600|19200|38400|57600|74880|115200|230400|250000|500000|1000000|2000000)\b"),
        "message": "Serial baud literal found; consider making this configurable",
    },
    {
        "id": "unused-variable",
        "severity": "warning",
        "pattern": re.compile(r"^\s*Dim\s+(\w+)", re.IGNORECASE),
        "message": "Variable appears to be declared but not used",
    },

    {
        "id": "blocking-delay",
        "severity": "warning",
        "pattern": re.compile(r"\bDelay\s+(\d+)", re.IGNORECASE),
        "message": "Blocking Delay detected; consider using a non-blocking timer (Every) or shorter delays",

    },
]


def run_linter_on_text(text: str, path: str = "<string>") -> List[Dict]:
    """Run the linter over the provided source text.

    Returns a list of diagnostics with fields: file, line, col, severity, message, rule
    """
    diagnostics: List[Dict] = []
    lines = text.splitlines()
    # First pass: basic rule matches and gather suppression directives
    file_suppressed = set()
    suppressed_by_line = {}
    for lineno, line in enumerate(lines, start=1):
        # Detect suppression directives
        m_file_sup = re.search(r"LINTER:DISABLE-FILE\s+([a-zA-Z0-9_\-]+)", line, re.IGNORECASE)
        if m_file_sup:
            file_suppressed.add(m_file_sup.group(1))
        m_line_sup = re.search(r"LINTER:DISABLE\s+([a-zA-Z0-9_\-]+)", line, re.IGNORECASE)
        if m_line_sup:
            # Apply suppression to the following line (common pattern: comment above the statement)
            suppressed_by_line.setdefault(lineno + 1, set()).add(m_line_sup.group(1))
        for rule in RULES:
            m = rule["pattern"].search(line)
            if m:
                diagnostics.append(
                    {
                        "file": path,
                        "line": lineno,
                        "col": m.start() + 1,
                        "severity": rule["severity"],
                        "message": rule["message"],
                        "rule": rule["id"],
                        "snippet": line.strip(),
                    }
                )

    # Post analysis: detect unused variables, missing sprite deletes, and blocking Delay values
    # Unused variables: find DIM declarations and check if used elsewhere
    dim_pattern = re.compile(r"^\s*Dim\s+(\w+)", re.IGNORECASE)
    declared = []  # tuples (name, lineno)
    for lineno, line in enumerate(lines, start=1):
        m = dim_pattern.match(line)
        if m:
            declared.append((m.group(1), lineno))
    for name, ln in declared:
        # count usages excluding the declaration line
        usage_count = 0
        for lno, l in enumerate(lines, start=1):
            if lno == ln:
                continue
            if re.search(rf"\b{re.escape(name)}\b", l):
                usage_count += 1
        if usage_count == 0:
            diagnostics.append({
                "file": path,
                "line": ln,
                "col": 1,
                "severity": "warning",
                "message": "Variable declared but never used",
                "rule": "unused-variable",
                "snippet": lines[ln - 1].strip(),
            })

    # Sprite create without delete
    create_pattern = re.compile(r"\bCREATE_SPRITE\s+(\w+)", re.IGNORECASE)
    delete_pattern = re.compile(r"\bSPRITE_DELETE\s+(\w+)", re.IGNORECASE)
    creates = {}
    deletes = set()
    for lineno, line in enumerate(lines, start=1):
        m = create_pattern.search(line)
        if m:
            creates[m.group(1)] = lineno
        m2 = delete_pattern.search(line)
        if m2:
            deletes.add(m2.group(1))
    for name, ln in creates.items():
        if name not in deletes:
            diagnostics.append({
                "file": path,
                "line": ln,
                "col": 1,
                "severity": "warning",
                "message": "Sprite created but no delete found",
                "rule": "missing-delete-sprite",
                "snippet": lines[ln - 1].strip(),
            })

    # Blocking Delay detection: numeric delays >= 200 ms
    delay_pattern = re.compile(r"\bDelay\s+(\d+)\b", re.IGNORECASE)
    for lineno, line in enumerate(lines, start=1):
        m = delay_pattern.search(line)
        if m:
            try:
                val = int(m.group(1))
                if val >= 200:
                    diagnostics.append({
                        "file": path,
                        "line": lineno,
                        "col": m.start() + 1,
                        "severity": "warning",
                        "message": f"Blocking Delay ({val} ms) detected; consider using a non-blocking timer",
                        "rule": "blocking-delay",
                        "snippet": line.strip(),
                    })
            except Exception:
                pass

    # Filter suppressed diagnostics
    filtered = []
    for d in diagnostics:
        r = d.get('rule')
        ln = d.get('line')
        if r in file_suppressed:
            continue
        if ln in suppressed_by_line and r in suppressed_by_line[ln]:
            continue
        filtered.append(d)

    return filtered


# Simple quick-fix support
# Rules may specify a 'fix' key describing the available fix for that rule.
# Supported fix types: 'remove_line', 'comment_line'

def available_fixes_for_diag(diag: Dict) -> List[Dict]:
    """Return a list of available fix descriptors for a diagnostic.

    Each descriptor is a dict: {'id': '<fix-id>', 'label': '<Human label>'}
    """
    rule_id = diag.get("rule")
    # First, check explicit rule definitions
    for r in RULES:
        if r["id"] == rule_id and r.get("fix"):
            fix = r["fix"]
            if fix == "remove_line":
                return [{"id": "remove_line", "label": "Remove line"}]
            if fix == "comment_line":
                return [{"id": "comment_line", "label": "Comment out line"}]
            if fix == "insert_delete":
                return [{"id": "insert_delete", "label": "Insert sprite delete"}]
    # Some diagnostics are generated by post-analysis; add fix info here
    if rule_id == "missing-delete-sprite":
        return [{"id": "insert_delete", "label": "Insert sprite delete"}]
    if rule_id == "blocking-delay":
        # Offer two quick-fixes: comment the Delay, or replace with an Every skeleton
        return [
            {"id": "comment_line", "label": "Comment out line"},
            {"id": "replace_with_every", "label": "Replace with Every skeleton"},
        ]
    return []


def apply_fix_on_text(text: str, diag: Dict, fix_id: str) -> str:
    """Apply the named fix to the provided source text for the given diagnostic.

    Returns the updated text. The function is intentionally simple and operates on line numbers.
    """
    lines = text.splitlines()
    lineno = diag.get("line", 0) - 1
    if lineno < 0 or lineno >= len(lines):
        return text

    if fix_id == "remove_line":
        # Remove the line entirely
        del lines[lineno]
    elif fix_id == "comment_line":
        # Prefix with an apostrophe to make it a VB comment (VB6 style)
        lines[lineno] = "' " + lines[lineno]
    elif fix_id == "insert_delete":
        # Insert a sprite delete call after the diagnostic line like: SPRITE_DELETE name
        # Expect diag['snippet'] or diag['message'] to include the sprite name; attempt to extract
        name_match = re.search(r"CREATE_SPRITE\s+(\w+)", diag.get('snippet', '') , re.IGNORECASE)
        if not name_match:
            name_match = re.search(r"CREATE_SPRITE\s+(\w+)", lines[lineno], re.IGNORECASE)
        if name_match:
            sprite_name = name_match.group(1)
            lines.insert(lineno + 1, f"SPRITE_DELETE {sprite_name}")
    elif fix_id == "replace_with_every":
        # Replace a blocking Delay line with a commented Delay and a skeleton Every block
        # Expect pattern: Delay <ms>
        m = re.search(r"Delay\s+(\d+)", lines[lineno], re.IGNORECASE)
        if m:
            val = m.group(1)
            # Comment original delay
            lines[lineno] = "' " + lines[lineno]
            # Insert a skeleton Every block after it
            skeleton = [f"Every {val} Do", "    ' TODO: move blocking code here", "End Do"]
            for idx, sline in enumerate(skeleton, start=1):
                lines.insert(lineno + idx, sline)
    else:
        # Unknown fix: return text unchanged
        return text
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: linter.py <file>")
        sys.exit(1)
    p = sys.argv[1]
    with open(p, "r") as fh:
        txt = fh.read()
    for d in run_linter_on_text(txt, path=p):
        print(f"{d['file']}:{d['line']}:{d['col']} {d['severity'].upper()} {d['rule']} - {d['message']}")
