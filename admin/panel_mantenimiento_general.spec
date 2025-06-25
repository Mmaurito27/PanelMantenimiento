# panel_mantenimiento_general.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['panel_mantenimiento_general.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config/*', 'config'),
        ('launchers/*', 'launchers'),
        ('logs/*', 'logs'),
        ('subpanels/*', 'subpanels'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='panel_mantenimiento_general',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # ❌ Oculta la consola negra
    icon='Guante.ico',  # ✅ Tu icono personalizado
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='panel_mantenimiento_general'
)
