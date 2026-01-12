# VB2Arduino

A VB6-like language transpiler and IDE that converts Visual Basic syntax to Arduino C++ code, with integrated PlatformIO build support.

## Features

- **VB6-style Syntax**: Write Arduino code using familiar Visual Basic 6 syntax
- **GUI IDE**: Arduino IDE-style desktop application with code editor and serial monitor
- **Arduino C++ Output**: Transpiles to clean, readable Arduino C++ code
- **PlatformIO Integration**: Built-in support for compiling and uploading to microcontrollers
- **ESP32 Support**: Tested with ESP32-S3-LCD-1.47 board and compatible with other Arduino boards
- **CLI and IDE**: Use command-line tools or graphical interface
- **Array Support**: Multi-dimensional arrays with UBound/LBound functions
- **Libraries Manager**: Curated catalog with board-aware recommendations; auto-download via PlatformIO
- **Pin Configuration**: Board templates with auto-load; save/load/delete custom templates per board
- **Build Flags**: Add custom compiler defines merged with board-required flags
- **Auto-Detection**: Board and port auto-detection on startup; visual indicators
- **Error Mapping**: Compilation errors map back to VB lines with clickable navigation
- **Error Copy**: Right-click errors to copy single or all to clipboard

## Supported VB Subset

### Entry Points
- `Sub Setup()` → `void setup()`
- `Sub Loop()` → `void loop()`

### Declarations
- `Const LED = 2` — Constants
- `Dim x As Integer` — Variable declarations (Integer, Long, Byte, Boolean, Single, String)
- `Dim x` — Auto-typed as Integer
- `Dim arr(9) As Integer` — Fixed-size arrays (single dimension)
- `Dim board(2, 2) As Integer` — Multi-dimensional arrays
- `UBound(arr)` / `LBound(arr)` — Array bounds functions

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

### Option 1: Download Pre-built Executable (Recommended)

**No Python installation required!**

1. Go to [GitHub Releases](https://github.com/xgreenrx-star/VB6_Arduino/releases)
2. Download for your platform:
   - **Windows**: `vb2arduino-ide-windows.zip`
   - **Linux**: `vb2arduino-ide-linux.tar.gz`
   - **macOS**: `vb2arduino-ide-macos.tar.gz`
3. Extract and run the executable

See [RELEASES.md](RELEASES.md) for detailed instructions.

### Option 2: Run from Source

```bash
# Clone the repository
git clone https://github.com/xgreenrx-star/vb2arduino.git
cd vb2arduino

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Option 3: Build Your Own Executable

See [BUILD.md](BUILD.md) for instructions on building standalone executables with PyInstaller.

## Prerequisites

- **Python 3.10+**
- **PyQt6** — For GUI IDE (automatically installed)
- **PlatformIO CLI** (`pio`) — Required for building and uploading
  ```bash
  pip install platformio
  ```

## Running Tests (headless)

The project includes headless editor tests that exercise UI features (snippets, auto-indent, completer, find/replace). These tests require a display server; the simplest way to run them locally on Linux is with Xvfb.

- Install Xvfb (Ubuntu/Debian):

```bash
sudo apt-get update
sudo apt-get install -y xvfb
```

- Run all tests (headless):

```bash
xvfb-run -s "-screen 0 1280x720x24" python -m unittest discover -v -s tests
```

- Run a single test module:

```bash
xvfb-run -s "-screen 0 1280x720x24" python -m unittest tests.test_editor_snippets -v
```

The GitHub Actions workflow `.github/workflows/editor-tests.yml` runs this suite automatically on PRs and pushes to main/master.

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
vb2arduino examples/blink/blink.vb --out generated
```

This creates `generated/main.cpp` with Arduino C++ code.

### 3. Transpile and Build

```bash
vb2arduino examples/blink/blink.vb --out generated --board esp32-s3-devkitm-1 --build
```

### 4. Transpile, Build, and Upload

```bash
vb2arduino examples/blink/blink.vb --out generated --board esp32-s3-devkitm-1 --build --upload --port /dev/ttyUSB0
```

## IDE Features

The VB2Arduino IDE provides an Arduino IDE-like experience:

### Editor
- **Syntax Highlighting**: VB keywords, functions, constants, strings, and comments
- **Line Numbers**: Easy code navigation
- **Current Line Highlight**: Visual feedback for cursor position
- **Procedure Dropdown**: Quick navigation to Sub/Function definitions
- **Project Tree**: Visual structure showing all procedures

### Toolbar
- **Verify (✓)**: Transpile and compile code without uploading
- **Upload (→)**: Compile and upload to selected board
- **Board Selection**: Choose from common Arduino/ESP32 boards with auto-detection
- **Port Selection**: Automatic detection of serial ports with refresh button and auto-detection
- **Serial Monitor**: Toggle serial monitor visibility
- **Auto-Detect Chips**: Visual indicators show when board/port were auto-detected

### Serial Monitor
- **Real-time Communication**: Send and receive data from microcontroller
- **Baud Rate Selection**: Common rates from 300 to 2000000
- **Connect/Disconnect**: Manual connection control
- **Input/Output**: Text area for received data and line input for sending

### Tools Menu
- **Manage Libraries**: Browse curated library catalog, board-aware recommendations, custom adds
- **Configure Pins**: Load board templates, edit pins by category, save/load/delete custom templates
- **Build Flags**: Add/remove compiler defines for project-specific configuration
- **Serial Monitor**: Open/close serial port monitor
- **Settings**: Customize editor colors, behavior, and pop-up notifications

### File Operations
- New, Open, Save, Save As
- Unsaved changes detection
- Default blink LED template

### Error Handling
- **Clickable Error List**: Double-click errors to jump to VB line
- **VB Line Mapping**: Compiler errors automatically mapped back to source code
- **Error Copy**: Right-click to copy single error or all errors to clipboard
- **Status Hints**: Concise error summary shown when navigating to errors

#### Diagnostics & Quick Fixes ✅
- **On-demand Linter**: Run the built-in lightweight linter (Tools → Run Linter or `Ctrl+L`) to detect issues such as debug-draw calls, wildcard imports, and suspicious baud literals.
- **Problems Panel**: Linter results appear in the Problems panel with inline gutter markers and hover tooltips.
- **Quick Fixes**: Right-click a problem or use **Tools → Apply Quick Fix** (`Ctrl+.`) to apply an available fix (for example, remove or comment out a debug draw line). The editor updates and the linter re-runs automatically.

#### Go To Definition & Find References 🔎
- **Go to Definition (F12)**: Place the cursor on a procedure/function name and press **F12** to jump to its definition in any open tab.
- **Find References (Shift+F12)**: Locate all references to the current symbol across open tabs and view the results in a quick dialog for one-click navigation.

These features improve developer productivity for refactoring and quick fixes without leaving the IDE.

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

All examples now live in per-example folders under `examples/`, using the pattern `examples/<name>/<name>.vb`.

### Blink LED
```bash
vb2arduino examples/blink/blink.vb --out generated --board esp32-s3-devkitm-1 --build --upload
```

### Button Input
```bash
vb2arduino examples/button_led/button_led.vb --out generated --board esp32-s3-devkitm-1 --build --upload
```

### Serial Echo
```bash
vb2arduino examples/serial_echo/serial_echo.vb --out generated --board esp32-s3-devkitm-1 --build --upload
```

### TicTacToe (BOOT button, LCD)
```bash
vb2arduino examples/tictactoe_boot_button/tictactoe_boot_button.vb --out generated --board esp32-s3-devkitm-1 --build --upload
```

### TicTacToe with Arrays (Advanced)
```bash
vb2arduino examples/tictactoe_array/tictactoe_array.vb --out generated --board esp32-s3-lcd-1.47 --build --upload
```

Demonstrates:
- Multi-dimensional arrays for game board
- Short press (< 500ms) to move cursor
- Long press (≥ 500ms) to place X and trigger AI
- Smart AI with win/block/center/corner strategy
- Flicker-free rendering with dirty flag

### Quick headless IDE compile check (no GUI)
From the repo root with venv active:
```bash
PYTHONPATH=$(pwd) QT_QPA_PLATFORM=offscreen .venv/bin/python scripts/verify_ide_compile.py
```
Runs `verify_code()` against the blink example and suppresses popups.

## Project Structure

```
vb2arduino/
├── src/
│   └── vb2arduino/
│       ├── __init__.py
│       ├── transpiler.py      # Core transpiler logic
│       └── cli.py             # Command-line interface
├── examples/
│   ├── blink/blink.vb
│   ├── button_led/button_led.vb
│   ├── serial_echo/serial_echo.vb
│   └── ... (per-example folders)
├── scripts/
│   └── verify_ide_compile.py  # Headless IDE compile smoke test
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
- `esp32-s3-devkitc-1` — ESP32-S3 DevKit-C
- `esp32-s3-lcd-1.47` — **ESP32-S3 with 1.47" ST7789 LCD** (pre-configured pins & build flags)
- `esp32dev` — ESP32
- `uno` — Arduino Uno
- `mega2560` — Arduino Mega
- `nano_33_iot` — Arduino Nano 33 IoT
- `pico` — Raspberry Pi Pico

See [PlatformIO Boards](https://docs.platformio.org/en/latest/boards/index.html) for full list.

### ESP32-S3 LCD 1.47" (ST7789) — Primary Testing Board

This is the primary development and testing board for VB2Arduino. The transpiler has been extensively tested on the **ESP32-S3-LCD-1.47** but should work on other Arduino-compatible boards with appropriate pin configuration.

When you select "ESP32-S3-LCD-1.47" in the IDE, default pins and build flags are automatically configured for TFT_eSPI:

**Pins (HSPI)**:
- MOSI: 45 | SCLK: 40 | CS: 42 | DC: 41 | RST: -1 | BL: 46

**Build Flags**:
```
-DST7789_DRIVER -DTFT_WIDTH=172 -DTFT_HEIGHT=320 -DTFT_ROTATION=0
-DTFT_MOSI=45 -DTFT_SCLK=40 -DTFT_CS=42 -DTFT_DC=41 -DTFT_RST=-1
-DTFT_BL=46 -DTOUCH_CS=-1 -DUSE_HSPI_PORT -DTFT_BL_ON=HIGH -DSPI_FREQUENCY=40000000
```

You can further customize these in Tools → Configure Pins.

## Limitations

This is a **minimal subset** transpiler for Arduino/embedded use:

- **No dynamic features**: No Variants, Collections, late binding
- **No GUI**: No forms, controls, or windows (MCU-only)
- **No full VB error handling**: `On Error` statements are stubbed; prefer return codes
- **String handling**: Uses Arduino `String` class (can fragment heap on small MCUs)

Implemented highlights:
- Fixed-size arrays (single/multi-dimensional) with `UBound`/`LBound`
- `Select Case` with ranges and multiple values
- Optional/ByRef parameters; `With ... End With`
- String helpers (`Split`/`Join`/`Filter`, `InStrRev`, `StrComp`, `StrReverse`), conversions (`Val`, `Hex$`, `Oct$`, `Chr$`, `Asc`)
- Math/time helpers (`Round`, `Fix`, `Sgn`, `Log`, `Exp`, `Atn`, `Timer`, `Randomize`)

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
