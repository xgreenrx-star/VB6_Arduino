#!/bin/bash
# Build standalone VB2Arduino IDE executable using PyInstaller

set -e

echo "Building VB2Arduino IDE standalone executable..."
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    . venv/bin/activate
else
    echo "Error: Virtual environment 'venv' not found."
    echo "Please create it first: python3 -m venv venv && source venv/bin/activate && pip install -e ."
    exit 1
fi

# Ensure PyInstaller is installed
echo "Installing PyInstaller..."
pip install --quiet pyinstaller

# Clean old builds
echo "Cleaning previous builds..."
rm -rf build dist *.build 2>/dev/null || true

# Run PyInstaller with --onedir (distributable folder)
echo "Building executable (this may take 2-3 minutes)..."
python3 -m PyInstaller vb2arduino-ide.spec --onedir --clean

# Summary
echo ""
echo "✓ Build complete!"
echo ""
echo "Executable location: dist/vb2arduino-ide/"
echo ""
echo "To run the IDE:"
echo "  Linux/macOS:  ./dist/vb2arduino-ide/vb2arduino-ide"
echo "  Windows:      dist\\vb2arduino-ide\\vb2arduino-ide.exe"
echo ""
echo "To distribute:"
echo "  cd dist && tar -czf vb2arduino-ide.tar.gz vb2arduino-ide/"
echo "  or zip -r vb2arduino-ide.zip vb2arduino-ide/"

