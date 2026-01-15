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
  - Auto-detect on startup: attempts to select a detected board and port.
  - Hover hints: tooltips show when a board/port was auto-detected.
  - Auto badge: the selected Board/Port label includes "[Auto]" when detection succeeds (clears when you change it).
  - Auto chips: small "Auto" tags appear next to Board/Port when detection succeeds (they hide when you change selection).
  - ESP32-S3 convenience: PlatformIO is generated with USB CDC flags and 115200 monitor speed; upload speed defaults to 921600 for S3 boards.
 - **Libraries Manager**: Curated catalog with board-aware recommendations, category tabs, and custom adds; selections persist and emit `lib_deps` in `platformio.ini` so PlatformIO automatically downloads required libraries.
- **Visual Designer (WYSIWYG)**: A dockable form designer for placing controls visually, editing properties in the Inspector, previewing forms (modeless preview, live-sync), rulers and snaplines for alignment, and saving/loading forms as JSON templates. See the Visual Designer section in the User Guide for details.
 - **Pins Configuration**: Board templates auto-load on selection; edit pins by category (Basic/TFT/I2C/SPI). Save your current pins+flags as named templates and reload/delete later.
 - **Build Flags**: A dedicated tab to add/remove compiler defines (e.g., `-D...`), merged with board-required flags in `platformio.ini`.
 - **Error Copy**: Right-click errors in the error list to copy a single error or all errors to the clipboard.
- **Menus**:
  - File: New/Open/Save/Save As/Quit (unsaved-changes prompt).
  - Edit: Undo/Redo/Cut/Copy/Paste.
  - Sketch: Compile, Upload, Include Library...
  - Tools:
    - **Serial Monitor** (Ctrl+Shift+M): Toggle serial monitor visibility.
    - **Manage Libraries** (Ctrl+Shift+L): Browse and install Arduino libraries with board-aware recommendations.
    - **Configure Pins** (Ctrl+Shift+P): Edit board pin assignments and load/save pin templates.
    - **Build Flags**: Add/remove custom compiler defines for the selected board.
    - **Clean Build**: Remove build artifacts from the generated folder (PlatformIO clean).
    - **Device Monitor**: Open PlatformIO device monitor in a new terminal for real-time serial debugging.
    - **Preview Form** (Ctrl+Alt+R): Open a modeless preview window showing the runtime appearance of the current form; can be live-synced with editor changes.
    - **Live Sync Preview**: Toggle automatic updates to the modeless preview while you edit (useful for iterative design).
    - **Settings**: Customize editor colors, behavior, and notification preferences.
  - Help: Programmer's Reference, About.

## Visual Designer

The Visual Designer is a dockable WYSIWYG designer for placing and arranging controls on a form. Key features:

- Drag & drop controls: Buttons, Labels, TextBoxes, PictureBoxes, CheckBoxes, OptionButtons, ComboBoxes, ListBoxes, Sliders.
- Form chrome: a Form frame with caption and background color to make forms stand out.
- Inspector: edit properties (Caption/Text, X/Y, W/H, Color, control-specific settings). When nothing is selected, the inspector edits the Form properties (Caption, background color, size).
- Modeless preview: Tools → Preview Form opens a modeless preview window; Tools → Live Sync Preview keeps it updated automatically as you edit.
- Rulers & Snaplines: View → Rulers shows rulers; alignment snaplines appear during drag to assist layout.
- Save/Open forms: form templates are JSON files under `visualasic/examples/form_templates/` (e.g., `classic.form.json`).

Screenshots:

![Designer form](/docs/images/visual_designer_form.png)

![Preview dialog](/docs/images/visual_designer_preview.png)

![Rulers & Snaplines](/docs/images/visual_designer_snaplines.png)

Usage notes:

1. Open Visual Designer from File → Visual Designer (or Tools/View) and select the dock.
2. Use the left toolbox to place controls. After placing a control the tool reverts to Select mode.
3. Select the form (click empty canvas) to edit form-level properties in the Inspector.
4. Use Tools → Preview Form and Tools → Live Sync Preview to check runtime appearance as you edit.
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
 3) (Optional) Tools → Manage Libraries to add dependencies; Tools → Configure Pins to load/edit board templates and define build flags.
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

### New constructs (added)
- `Every <ms> Do ... End Do` — non-blocking periodic task that executes the block approximately every `<ms>` milliseconds. Example:

```
Every 1000 Do
    SerialPrintLine "tick"
End Do
```

- `Enum` support — define named constants:
```
Enum Colors
    RED = 1
    BLUE
End Enum
```

- `For Each <item> In <array>` — iterate arrays easily:
```
For Each x In arr
    SerialPrint x
Next
```

- Sprite methods: `CREATE_SPRITE name, w, h`, `SPRITE_FILL_ELLIPSE name, x, y, rx, ry, color`, `SPRITE_PUSH name, x, y[, bg]`, `SPRITE_DELETE name` (use sprite delete to free resources).

- Linter suppression: add a comment on the line above a statement to suppress a rule:
```
' LINTER:DISABLE blocking-delay
Delay 1000
```

These features help write non-blocking MCU-friendly code and improve code clarity.

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
- **Auto-detect didn’t select anything**: Ensure your board is connected and recognized by `pio device list`. The IDE heuristically maps USB VID vendors (Espressif/Arduino/Raspberry Pi) to common boards. You can always pick the exact board/port manually.
- **How to tell it worked**: Watch the status bar for "Detected board/port" (now shown for ~8s), hover the dropdowns for "Auto-detected: ..." tooltips, and look for the "[Auto]" badge or small "Auto" chips next to the Board/Port fields.
- **BLE setValue(String) error**: use `command.c_str()` (already applied in examples).
- **Preferences flush error**: removed; ESP32 Preferences does not expose `flush`.
- **Qt accessibility warning**: benign message on Linux; does not affect functionality.
 - **Missing library headers (e.g., `TFT_eSPI.h`)**: Use Tools → Manage Libraries to add `TFT_eSPI`. The IDE writes `lib_deps` for PlatformIO, which automatically fetches libraries at build time.

## 7. Examples
Examples are organized as `examples/<name>/<name>.vb`.

- Blink: `examples/blink/blink.vb`
- Button LED: `examples/button_led/button_led.vb`
- Serial Echo: `examples/serial_echo/serial_echo.vb`
- LCD Hello: `examples/lcd_hello/lcd_hello.vb`
- TicTacToe (BOOT): `examples/tictactoe_boot_button/tictactoe_boot_button.vb`
- Arrays TicTacToe: `examples/tictactoe_array/tictactoe_array.vb`
- Split/Join/Filter demo: `examples/split_join_filter_demo/split_join_filter_demo.vb`

## 8. Developer Smoke Tests
Headless compile check (no GUI), from repo root with venv active:
```bash
PYTHONPATH=$(pwd) QT_QPA_PLATFORM=offscreen .venv/bin/python scripts/verify_ide_compile.py
```
Runs `verify_code()` against the blink example and suppresses popups.

## 9. Compile Errors & VB Line Mapping
- When compilation/upload fails, the IDE parses compiler output and shows a clickable list of errors.
- Each error item maps to the corresponding VB line; double-click an entry to jump to that line.
- The IDE briefly highlights the target line and shows a status bar hint with a concise error summary.
- The generated C++ is not shown to avoid confusion; mapping is automatic.

Notes:
- If failure pop-ups are disabled in Settings, errors are reported via the status bar only and the clickable dialog is suppressed.

## 10. Libraries Management
- Open Tools → Manage Libraries to browse curated categories and board-aware recommendations.
- Selected libraries are persisted to the project config and emitted as `lib_deps` in `platformio.ini`.
- PlatformIO automatically downloads missing libraries listed in `lib_deps` during build.
- You can add custom library names or PlatformIO registry identifiers.

## 11. Pins & Templates
- Open Tools → Configure Pins.
- Pins tab shows board pin categories; load board template (if available) via the button or by changing the board in the toolbar.
- Templates tab lets you:
  - Save Current…: Save the current pins and build flags under a name (templates are filtered per-board).
  - Load: Apply a saved template; pins and flags update immediately.
  - Delete: Remove an unused template.
- Build Flags tab: Add/remove flags like `-DST7789_DRIVER` or `-DUSE_HSPI_PORT`. These merge with board-required flags in the generated `platformio.ini`.

## 12. Board-Specific Defaults
### ESP32-S3 LCD 1.47 (ST7789)
Selecting the "ESP32-S3-LCD-1.47" board variant in the toolbar applies a default display setup for TFT_eSPI with ST7789. The IDE sets pins and build flags automatically:

Pins (HSPI on ESP32-S3):
- MOSI: 45
- SCLK: 40
- CS: 42
- DC: 41
- RST: -1 (not used)
- BL: 46

Default build flags:
- `-DST7789_DRIVER`
- `-DTFT_WIDTH=172`
- `-DTFT_HEIGHT=320`
- `-DTFT_ROTATION=0`
- `-DTFT_MOSI=45`
- `-DTFT_SCLK=40`
- `-DTFT_CS=42`
- `-DTFT_DC=41`
- `-DTFT_RST=-1`
- `-DTFT_BL=46`
- `-DTOUCH_CS=-1`
- `-DUSE_HSPI_PORT`
- `-DTFT_BL_ON=HIGH`
- `-DSPI_FREQUENCY=40000000`

These defaults are applied automatically when the board selection contains "LCD-1.47". You can further customize them in Tools → Configure Pins → Build Flags.

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
