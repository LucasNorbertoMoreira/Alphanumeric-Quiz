# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['jogo_letras_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('fundo.png', '.'), ('acerto.mp3', '.'), ('erro.mp3', '.'), ('musica_fundo.mp3', '.'), ('DejaVuSans.ttf', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Adivinhe a Letra',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
