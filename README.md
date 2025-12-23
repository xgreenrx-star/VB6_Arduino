# VB2Arduino

A VB6-like language transpiler and IDE that converts Visual Basic syntax to Arduino C++ code, with integrated PlatformIO build support.

## Features

- **VB6-style Syntax**: Write Arduino code using familiar Visual Basic 6 syntax
- **GUI IDE**: Arduino IDE-style desktop application with code editor and serial monitor
- **Arduino C++ Output**: Transpiles to clean, readable Arduino C++ code
- **PlatformIO Integration**: Built-in support for compiling and uploading to microcontrollers
- **ESP32 Support**: Tested with ESP32-S3 and other Arduino-compatible boards
- **CLI and IDE**: Use command-line tools or graphical interface

## Supported VB Subset

### Entry Points
- `Sub Setup()` → `void setup()`
- `Sub Loop()` → `void loop()`

### Declarations
- `Const LED = 2` — Constants
- `Dim x As Integer` — Variable declarations (Integer, Long, Byte, Boolean, Single, String)
- `Dim x` — Auto-typed as Integer

### Control Flow
- `If...ElseIf...Else...End If`
- `For i = start To end...Next`
- `While...Wend`
- `Do...Loop`

### Arduino I/O
- `PinMode pin, mode` → `pinMode(pin, mode)`
- `DigitalWrite pin, value` → `digitalWrite(pin, value)`
- `DigitalRead(pin)` → `digitalRead(pin)`
- `AnalogRead(pin)` → `analogRead(pin)`
- `AnalogWrite pin, value` → `analogWrite(pin, value)`
- `Delay milliseconds` → `delay(milliseconds)`

### Serial Communication
- `SerialBegin baud` → `Serial.begin(baud)`
- `SerialPrint value` → `Serial.print(value)`
- `SerialPrintLine value` → `Serial.println(value)`
- `SerialAvailable()` → `Serial.available()`
- `SerialRead()` → `Serial.read()`

### Operators
- Logical: `And` → `&&`, `Or` → `||`, `Not` → `!`
- Comparison: `=`, `<>` → `!=`, `<`, `>`, `<=`, `>=`

## Installation

```bash
# Clone the repository
git clone https://github.com/xgreenrx-star/vb2arduino.git
cd vb2arduino

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Or install from PyPI (when available)
pip install vb2arduino
```

## Prerequisites

- **Python 3.10+**
- **PyQt6** — For GUI IDE (automatically installed)
- **PlatformIO CLI** (`pio`) — Required for building and uploading
  ```bash
  pip install platformio
  ```

## Quick Start

### Using the IDE (Recommended)

Launch the graphical IDE:
```bash
vb2arduino-ide
```

The IDE provides:
- Code editor with VB syntax highlighting and line numbers
- Toolbar with Verify and Upload buttons
- Board and port selection dropdowns
- Integrated serial monitor
- File operations (New, Open, Save)

### Using the Command Line

#### 1. Write VB Code

Create `blink.vb`:
```vb
' Blink LED on pin 2
Const LED = 2

Sub Setup()
    PinMode LED, OUTPUT
End Sub

Sub Loop()
    DigitalWrite LED, HIGH
    Delay 1000
    DigitalWrite LED, LOW
    Delay 1000
End Sub
```

### 2. Transpile Only

```bash
vb2arduino blink.vb --out generated
```

This creates `generated/main.cpp` with Arduino C++ code.

### 3. Transpile and Build

```bash
vb2arduino blink.vb --out generated --board esp32-s3-devkitm-1 --build
```

### 4. Transpile, Build, and Upload

```bash
vb2arduino blink.vb --out generated --board esp32-s3-devkitm-1 --build --upload --port /dev/ttyUSB0
```

## IDE Features

The VB2Arduino IDE provides an Arduino IDE-like experience:

### Editor
- **Syntax Highlighting**: VB keywords, functions, constants, strings, and comments
- **Line Numbers**: Easy code navigation
- **Current Line Highlight**: Visual feedback for cursor position

### Toolbar
- **Verify (✓)**: Transpile and compile code without uploading
- **Upload (→)**: Compile and upload to selected board
- **Board Selection**: Choose from common Arduino/ESP32 boards
- **Port Selection**: Automatic detection of serial ports with refresh button
- **Serial Monitor**: Toggle serial monitor visibility

### Serial Monitor
- **Real-time Communication**: Send and receive data from microcontroller
- **Baud Rate Selection**: Common rates from 300 to 2000000
- **Connect/Disconnect**: Manual connection control
- **Input/Output**: Text area for received data and line input for sending

### File Operations
- New, Open, Save, Save As
- Unsaved changes detection
- Default blink LED template

## Command-Line Options

```
vb2arduino [OPTIONS] INPUT

Positional Arguments:
  INPUT              VB source file (.vb)

Options:
  --out DIR          Output directory (default: generated)
  --board BOARD      PlatformIO board ID (e.g., esp32-s3-devkitm-1, uno, mega2560)
  --build            Compile with PlatformIO after transpiling
  --upload           Upload to board after building (requires --build)
  --port PORT        Serial port for upload (e.g., /dev/ttyUSB0, COM3)
  -h, --help         Show help message
```

## Examples

The `examples/` directory contains sample VB programs:

### Blink LED
```bash
vb2arduino examples/blink.vb --out generated --board esp32-s3-devkitm-1 --build --upload
```

### Button Input
```bash
vb2arduino examples/button_led.vb --out generated --board esp32-s3-devkitm-1 --build --upload
```

### Serial Echo
```bash
vb2arduino examples/serial_echo.vb --out generated --board esp32-s3-devkitm-1 --build --upload
```

## Project Structure

```
vb2arduino/
├── src/
│   └── vb2arduino/
│       ├── __init__.py
│       ├── transpiler.py      # Core transpiler logic
│       └── cli.py             # Command-line interface
├── examples/
│   ├── blink.vb               # LED blink example
│   ├── button_led.vb          # Button input example
│   └── serial_echo.vb         # Serial communication example
├── tests/
│   └── test_transpiler.py     # Unit tests
├── pyproject.toml             # Project metadata and dependencies
├── README.md                  # This file
└── LICENSE                    # GPL-3.0-or-later
```

## How It Works

1. **Parse**: The transpiler reads your VB source file and parses it into an internal representation
2. **Transform**: VB constructs are mapped to Arduino C++ equivalents
3. **Emit**: Clean Arduino C++ code is generated in `generated/main.cpp`
4. **Build** (optional): PlatformIO compiles the C++ code for your target board
5. **Upload** (optional): Firmware is uploaded to your microcontroller

## Supported Boards

Any board supported by PlatformIO works. Common examples:

- `esp32-s3-devkitm-1` — ESP32-S3
- `esp32dev` — ESP32
- `uno` — Arduino Uno
- `mega2560` — Arduino Mega
- `nano_33_iot` — Arduino Nano 33 IoT
- `teensy40` — Teensy 4.0

See [PlatformIO Boards](https://docs.platformio.org/en/latest/boards/index.html) for full list.

## Limitations

This is a **minimal subset** transpiler for Arduino/embedded use:

- **No dynamic features**: No Variants, Collections, late binding
- **No GUI**: No forms, controls, or windows (MCU-only)
- **No error handling**: No `On Error` statements (use return codes)
- **Fixed arrays only**: Dynamic arrays not yet supported
- **String handling**: Uses Arduino `String` class (can fragment heap on small MCUs)
- **Basic type system**: Integer, Long, Byte, Boolean, Single, String

Future enhancements may add:
- Fixed-size arrays (`Dim arr(10) As Integer`)
- User-defined functions with parameters
- `Select Case` statements
- Modules and code organization
- More sophisticated error reporting

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

### Building from Source

```bash
# Install build tools
pip install build

# Build distribution packages
python -m build
```

## License

GNU General Public License v3.0 or later (GPL-3.0-or-later)

See [LICENSE](LICENSE) for the full text.

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Roadmap

- [ ] Add array support (fixed-size)
- [ ] Add `Select Case` statement
- [ ] User-defined functions with parameters and return values
- [ ] Module system for code organization
- [ ] Better error diagnostics with line numbers
- [ ] VS Code extension with syntax highlighting
- [ ] Debugger integration
- [ ] Standard library of Arduino-specific functions

## Related Projects

- [Arduino](https://www.arduino.cc/) — Arduino platform
- [PlatformIO](https://platformio.org/) — Build system and IDE
- [Visual Basic 6](https://en.wikipedia.org/wiki/Visual_Basic_(classic)) — Original VB6 language

## Credits

Created by the VB2Arduino contributors.

Inspired by the simplicity of Visual Basic 6 and the versatility of Arduino.
