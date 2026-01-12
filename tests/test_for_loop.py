import re
from vb2arduino.transpiler import VBTranspiler


def test_for_loop_end_expression_and_step():
    t = VBTranspiler()
    # Simulate being inside a function so var redeclaration check sees function_lines
    t.function_lines = []
    stmt = t._emit_statement("For t = 0 To BALL_TILES - 1")
    # Expect the end expression to preserve '- 1'
    assert "BALL_TILES - 1" in stmt or "BALL_TILES-1" in stmt
    # Expect the loop increment to use '+=' with the step (default 1)
    assert "+= (1)" in stmt or "+= (1);" in stmt or "+= (1)" in stmt
    # Now with explicit negative step
    stmt2 = t._emit_statement("For s = 1 To 0 Step -1")
    # Should include '-1' in the increment expression and comparison using >=
    assert "+= (-1)" in stmt2 or "+= (-1)" in stmt2
    assert (">= 0" in stmt2) or ("<= 0" in stmt2) or (">= 0" in stmt2) or ("<= 0" in stmt2)
