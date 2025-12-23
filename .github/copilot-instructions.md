# VB2Arduino Project Instructions

## Project Overview
VB2Arduino is a VB6-like language transpiler that converts VB syntax to Arduino C++ code. It integrates with PlatformIO for building and uploading to microcontrollers like ESP32.

## Checklist

- [x] Verify that the copilot-instructions.md file in the .github directory is created.
- [x] Clarify Project Requirements
- [x] Scaffold the Project
- [x] Customize the Project
- [x] Install Required Extensions
- [x] Compile the Project
- [x] Create and Run Task
- [x] Launch the Project
- [x] Ensure Documentation is Complete
- [x] Create IDE with code editor
- [x] Add syntax highlighting
- [x] Add serial monitor
- [x] Integrate with PlatformIO
- [x] Test IDE functionality

## Progress Notes
- Created .github/copilot-instructions.md
- Scaffolded Python project with pyproject.toml, src/vb2arduino package
- Added transpiler core (transpiler.py), CLI (cli.py), and __init__.py
- Created examples: blink.vb, button_led.vb, serial_echo.vb
- Added comprehensive README.md and LICENSE (GPL-3.0-or-later)
- Created virtual environment and installed package in editable mode
- Tested transpiler successfully: blink.vb → generated/main.cpp works correctly
- Added .gitignore for Python and generated files
- Created PyQt6-based IDE with Arduino IDE-style interface
- Added code editor with VB syntax highlighting and line numbers
- Implemented serial monitor with baud rate selection and real-time communication
- Integrated PlatformIO build/upload functionality
- Added toolbar with Verify/Upload buttons, board/port selection
- File operations: New, Open, Save with unsaved changes detection
- Successfully launched and tested IDE

## Project Structure
```
VB6_Arduino/
├── .github/
│   └── copilot-instructions.md
├── src/
│   └── vb2arduino/
│       ├── __init__.py
│       ├── transpiler.py
│       └── cli.py
├── examples/
│   ├── blink.vb
│   ├── button_led.vb
│   └── serial_echo.vb
├── venv/                     (virtual environment)
├── generated/                (transpiler output)
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## Usage
```bash
# Activate virtual environment
source venv/bin/activate

# Launch IDE (recommended)
vb2arduino-ide

# Or use CLI for transpiling only
vb2arduino examples/blink.vb --out generated

# Transpile and build for ESP32
vb2arduino examples/blink.vb --out generated --board esp32-s3-devkitm-1 --build

# Transpile, build, and upload
vb2arduino examples/blink.vb --out generated --board esp32-s3-devkitm-1 --build --upload --port /dev/ttyUSB0
```
