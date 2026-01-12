from vb2arduino.transpiler import transpile_string


def test_dim_deduplication_single_function():
    src = """
    SUB Test()
        Dim t As Integer
        Dim t As Integer
        Dim s As Integer, t As Integer
    END SUB
    """
    cpp = transpile_string(src)
    # Count explicit integer declarations for 't'
    occurrences = [line for line in cpp.splitlines() if 'int t' in line]
    assert len(occurrences) == 1, f"Expected only one declaration for 't', found: {occurrences}"
