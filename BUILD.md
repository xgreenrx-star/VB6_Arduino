# Building VB2Arduino IDE Standalone Executable

This guide explains how to build a standalone executable for VB2Arduino IDE that can be distributed without requiring Python or virtual environments.

## Prerequisites

- Python 3.10+ installed
- VB2Arduino repository cloned
- Virtual environment created and dependencies installed (see main README.md)

## Quick Start

### Linux/macOS

```bash
# From the project root directory
chmod +x build_executable.sh
./build_executable.sh
```

The executable will be in `dist/vb2arduino-ide/`

### Windows

```cmd
# From the project root directory
build_executable.bat
```

The executable will be in `dist\vb2arduino-ide\`

## Running the Executable

### Linux/macOS
```bash
./dist/vb2arduino-ide/vb2arduino-ide
```

### Windows
```cmd
dist\vb2arduino-ide\vb2arduino-ide.exe
```

## Distribution

### Create a Compressed Archive

**Linux/macOS:**
```bash
cd dist
tar -czf vb2arduino-ide-linux.tar.gz vb2arduino-ide/
```

**Windows:**
```bash
# Use 7-Zip, WinRAR, or Windows built-in: right-click dist\vb2arduino-ide\ → Send to → Compressed folder
```

### Upload to GitHub Releases

1. Go to your GitHub repository
2. Click "Releases" → "Draft a new release"
3. Tag version (e.g., `v1.0.0`)
4. Upload the `.tar.gz` or `.zip` file
5. Publish the release

Users can then download the executable without needing Python.

## How It Works

- **PyInstaller** bundles Python, all dependencies (PyQt6, PlatformIO, etc.), and your code into a single executable
- **`vb2arduino-ide.spec`** — Configuration file specifying what to include
- **`build_executable.sh/bat`** — Platform-specific build scripts

## Troubleshooting

### "PyInstaller not found"
```bash
source venv/bin/activate
pip install pyinstaller
```

### "Module not found" errors
Add missing modules to `hiddenimports` in `vb2arduino-ide.spec`:
```python
hiddenimports=[
    'my_missing_module',
    ...
]
```

Then rebuild.

### File size too large
The executable is typically 200-400 MB (includes Python + all libraries). To reduce:
1. Use `--onefile` instead of `--onedir` (slower startup, larger file)
2. Consider packaging as `.tar.gz` or `.zip` instead (smaller download, requires unzip)

### Slow first startup
PyInstaller executables have a ~2-3 second startup time. This is normal and will improve in future Python/PyInstaller versions.

## Build Configuration

The build is controlled by `vb2arduino-ide.spec`. Key settings:

- **Analysis** — What Python files and data to include
- **hiddenimports** — Modules not automatically detected (PyQt6, vb2arduino modules)
- **datas** — Non-Python files (README, LICENSE)
- **console=False** — No console window on Windows
- **--onedir** — Creates a folder with executable + libraries (faster build, easy to debug)
- **--onefile** — Single executable (slower build/startup, larger file)

## Advanced: Creating a Custom Icon

Add an icon to the executable:

1. Create a 256×256 PNG icon, convert to `.ico`:
   ```bash
   convert icon.png icon.ico  # ImageMagick
   ```

2. Update `vb2arduino-ide.spec`:
   ```python
   exe = EXE(
       ...
       icon='path/to/icon.ico',
       ...
   )
   ```

3. Rebuild

## See Also

- [PyInstaller Documentation](https://pyinstaller.org/)
- [README.md](../README.md) — Project overview
- [USER_GUIDE.md](../docs/USER_GUIDE.md) — IDE usage guide
