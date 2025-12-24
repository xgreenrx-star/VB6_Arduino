# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for VB2Arduino IDE standalone executable.
Build with: pyinstaller vb2arduino-ide.spec
"""

block_cipher = None

a = Analysis(
    ['src/vb2arduino/ide/entry_point.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/vb2arduino', 'vb2arduino'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'vb2arduino.transpiler',
        'vb2arduino.ide.editor',
        'vb2arduino.ide.serial_monitor',
        'vb2arduino.ide.project_tree',
        'vb2arduino.ide.settings',
        'vb2arduino.ide.settings_dialog',
        'vb2arduino.ide.project_config',
        'vb2arduino.ide.pin_templates',
        'vb2arduino.ide.pin_configuration_dialog',
        'vb2arduino.ide.library_catalog',
        'vb2arduino.ide.manage_libraries_dialog',
        'vb2arduino.ide.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='vb2arduino-ide',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window on Windows
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# Create a distribution folder with all dependencies
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='vb2arduino-ide',
)

