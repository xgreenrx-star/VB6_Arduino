@echo off
REM Build standalone VB2Arduino IDE executable using PyInstaller on Windows

echo Building VB2Arduino IDE standalone executable...
echo.

REM Check for virtual environment
if not exist "venv" (
    echo Error: Virtual environment 'venv' not found.
    echo Please create it first: python -m venv venv
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install PyInstaller
echo Installing PyInstaller...
pip install --quiet pyinstaller

REM Clean old builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Run PyInstaller
echo Building executable (this may take 2-3 minutes)...
python -m PyInstaller vb2arduino-ide.spec --onedir --clean

REM Summary
echo.
echo Build complete!
echo.
echo Executable location: dist\vb2arduino-ide\
echo.
echo To run the IDE:
echo   dist\vb2arduino-ide\vb2arduino-ide.exe
echo.
echo To distribute:
echo   Zip the dist\vb2arduino-ide\ folder
