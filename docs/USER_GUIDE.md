# VB2Arduino User Guide

## 1. Installation

### Prerequisites
- Python 3.10+
- PlatformIO CLI (`pio`) for build/upload
- Git (optional)

### Windows
```powershell
py -m venv venv
venv\Scripts\activate
py -m pip install -e .
py -m pip install platformio
```
Launch IDE:
```powershell
venv\Scripts\activate
vb2arduino-ide
```

### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install platformio
```
Launch IDE:
```bash
source venv/bin/activate
vb2arduino-ide
```

If `pio` is not on PATH, run as `python -m platformio ...`.

## 2. IDE Features
- **Editor**: VB syntax highlighting, line numbers, current-line highlight, procedure dropdown.
- **Toolbar**:
  - `✓ Compile`: Transpile + PlatformIO compile.
  - `→ Upload`: Compile + upload (uses selected board/port).
  - Board dropdown with common ESP32/Arduino/RP2040 IDs.
  - Port dropdown + refresh.
  - Serial Monitor toggle.
- **Menus**:
  - File: New/Open/Save/Save As/Quit (unsaved-changes prompt).
  - Edit: Undo/Redo/Cut/Copy/Paste.
  - Sketch: Compile, Upload, Include Library...
  - Tools: Serial Monitor toggle, Settings.
  - Help: About.
- **Project Tree**: Procedures list for quick navigation.
- **Serial Monitor**: Connect/disconnect, baud selection, send/receive.
- **Library Include Helper**: Inserts `#Include <...>` lines at top of the sketch.
- **Progress Dialogs**: Indeterminate progress shown during compile/upload.
- **Clickable Errors**: On compile/upload failure, a list of errors maps directly to VB lines; double-click to jump.
- **VB-only Focus**: The generated C++ is hidden; errors are mapped back to VB automatically.
- **Configurable Pop-ups**: Success/failure pop-ups can be enabled/disabled in Settings.
- **Jump Highlight**: When navigating to an error, the target VB line is briefly highlighted; color/duration configurable.

## 3. Workflow
1) Select board in toolbar.
2) Optionally select serial port (needed for upload).
3) Write or open `.vb` sketch.
4) Click `✓ Compile` to transpile+build with PlatformIO.
5) Click `→ Upload` to flash (requires port).
6) Use Serial Monitor to observe output.

Build output is written to the temp build dir (platformio.ini + src/main.cpp).

## 4. CLI Usage
```bash
vb2arduino input.vb --out generated               # transpile only
vb2arduino input.vb --out generated --board esp32-s3-devkitm-1 --build
vb2arduino input.vb --out generated --board esp32-s3-devkitm-1 --build --upload --port /dev/ttyUSB0
```

## 5. VB Language Reference (subset used here)

### Entry Points
- `Sub Setup()` → `void setup()`
- `Sub Loop()` → `void loop()`

### Declarations
- `Const NAME = value` or `Const NAME As Type = value` (string consts emitted as `const char*`).
- `Dim x As Integer` | `Dim x` (defaults to Integer)
- Arrays: `Dim arr(10) As Type` (size is max index; emitted as size+1). Constant sizes also supported (`Dim arr(MAX) As Type`).
- Object/pointer examples: `Dim bleServer As BLEServer*` (emitted as pointer).

### Types
- Integer → `int`
- Long → `long`
- Byte → `uint8_t`
- Boolean → `bool`
- Single/Double → `float`
- String → `String`
- Other tokens pass through (e.g., `BLEServer`).

### Control Flow
- `If ... Then / ElseIf ... Then / Else / End If`
- `For i = a To b ... Next i`
- `While ... Wend`
- `Do ... Loop` (with optional `Loop While condition`)

### Operators
- `And` → `&&`, `Or` → `||`, `Not` → `!`
- `<>` → `!=`
- In conditions, `=` is treated as `==`.
- Bitwise helpers: `BITOR`, `BITAND` map to `|`, `&`.

### Functions/Calls
- Calls with or without parentheses: `Foo 1, 2` → `Foo(1, 2);`
- Member access converts to `->` for known pointer vars when needed.
- `Return expr` inside Function.

### Arrays & Indexing
- VB-style `arr(i)` becomes `arr[i]` in output.

### Arduino Mappings
- `PinMode pin, mode` → `pinMode(pin, mode);`
- `DigitalWrite pin, val` → `digitalWrite(pin, val);`
- `DigitalRead(pin)` → `digitalRead(pin)`
- `AnalogRead(pin)` → `analogRead(pin)`
- `AnalogWrite pin, val` → `analogWrite(pin, val);`
- `Delay ms` → `delay(ms);`
- Serial: `SerialBegin baud`, `SerialPrint val`, `SerialPrintLine val`, `SerialAvailable()`, `SerialRead()`
- Time: `Millis()` → `millis()`

### BLE/Preferences (project-specific usage)
- BLE pointers: declare with `*`; calls convert `.` to `->` for those vars.
- Preferences: `prefs.begin`, `putInt`, `putString`, `getInt`, `getString` (no `flush` on ESP32 Preferences).

## 6. Troubleshooting
- **PlatformIO not found**: ensure `pio` on PATH or use `python -m platformio`.
- **Board not selected**: pick a concrete board (not category header) in toolbar/menu.
- **Upload needs port**: select correct `COMx` (Windows) or `/dev/ttyUSB*` `/dev/ttyACM*` (Linux/macOS).
- **BLE setValue(String) error**: use `command.c_str()` (already applied in examples).
- **Preferences flush error**: removed; ESP32 Preferences does not expose `flush`.
- **Qt accessibility warning**: benign message on Linux; does not affect functionality.

## 7. Examples
See `examples/` for ready-made sketches: `blink.vb`, `button_led.vb`, `serial_echo.vb`, `pwdongle_port.vb`, and demos.

## 8. Compile Errors & VB Line Mapping
- When compilation/upload fails, the IDE parses compiler output and shows a clickable list of errors.
- Each error item maps to the corresponding VB line; double-click an entry to jump to that line.
- The IDE briefly highlights the target line and shows a status bar hint with a concise error summary.
- The generated C++ is not shown to avoid confusion; mapping is automatic.

Notes:
- If failure pop-ups are disabled in Settings, errors are reported via the status bar only and the clickable dialog is suppressed.

## 9. Settings
Open Tools → Settings → Editor.

Editor → Colors:
- Background/Text/Current Line/Line Number colors.
- Jump Highlight: color used for the temporary highlight when navigating to an error.

Editor → Behavior:
- Jump Highlight Duration (ms): how long the error target line is highlighted (default 3000ms).
- Compile Success Pop-up: show a dialog when compilation succeeds (default on).
- Upload Success Pop-up: show a dialog when upload succeeds (default on).
- Compile Failure Pop-up: show clickable error dialog on compilation failure (default on).
- Upload Failure Pop-up: show clickable error dialog on upload failure (default on).

Tip:
- If you prefer a quieter workflow, disable success/failure pop-ups and rely on the status bar messages and manual navigation.
