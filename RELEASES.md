# Releases

VB2Arduino distributes pre-built executables for Windows, Linux, and macOS. No Python installation required!

## Download Latest Release

Visit [GitHub Releases](https://github.com/xgreenrx-star/VB6_Arduino/releases) to download:

- **Windows**: `vb2arduino-ide-windows.zip`
- **Linux**: `vb2arduino-ide-linux.tar.gz`
- **macOS**: `vb2arduino-ide-macos.tar.gz`

## Installation

### Windows

1. Download `vb2arduino-ide-windows.zip`
2. Extract the ZIP file
3. Run `vb2arduino-ide-windows\vb2arduino-ide\vb2arduino-ide.exe`

That's it! No Python or virtual environment needed.

### Linux

1. Download `vb2arduino-ide-linux.tar.gz`
2. Extract: `tar -xzf vb2arduino-ide-linux.tar.gz`
3. Run: `./vb2arduino-ide/vb2arduino-ide`

### macOS

1. Download `vb2arduino-ide-macos.tar.gz`
2. Extract: `tar -xzf vb2arduino-ide-macos.tar.gz`
3. Run: `./vb2arduino-ide/vb2arduino-ide`

## System Requirements

- Windows: Windows 10+ (64-bit)
- Linux: Ubuntu 18.04+ / Debian 10+ (64-bit)
- macOS: macOS 10.13+ (64-bit)
- **No Python installation required** — everything is bundled

## How Builds Work

Releases are automatically built on GitHub Actions:

1. Create a git tag: `git tag v1.0.0`
2. Push to GitHub: `git push origin v1.0.0`
3. GitHub Actions automatically:
   - Builds Windows exe on Windows runner
   - Builds Linux executable on Ubuntu runner
   - Builds macOS executable on macOS runner
   - Uploads all to GitHub Releases

See [.github/workflows/build-executables.yml](../.github/workflows/build-executables.yml) for build configuration.

## Building Locally (Advanced)

If you want to build executables yourself:

### Linux/macOS

```bash
./build_executable.sh
```

### Windows

```cmd
build_executable.bat
```

See [BUILD.md](../BUILD.md) for details.

## Version History

- **v1.0.0** (Dec 24, 2025) — Initial release with PyInstaller builds
  - VB6 transpiler with Arduino C++ output
  - PyQt6 GUI IDE
  - Libraries Manager
  - Pin Configuration
  - Serial Monitor
  - PlatformIO integration

## Support

- [README.md](../README.md) — Project overview
- [USER_GUIDE.md](../docs/USER_GUIDE.md) — IDE usage guide
- [BUILD.md](../BUILD.md) — Building from source
- [GitHub Issues](https://github.com/xgreenrx-star/VB6_Arduino/issues) — Report bugs
