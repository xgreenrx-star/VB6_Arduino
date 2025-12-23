"""VB2Arduino - VB6-like language transpiler for Arduino C++."""

__version__ = "0.1.0"

from vb2arduino.transpiler import VBTranspiler, transpile_string

__all__ = ["VBTranspiler", "transpile_string", "__version__"]
