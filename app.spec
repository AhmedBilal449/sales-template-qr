# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect Gradio data files
gradio_datas = collect_data_files('gradio')

# Collect additional data files for other packages
qrcode_datas = collect_data_files('qrcode')
pil_datas = collect_data_files('PIL')

# Collect all submodules for packages that might have dynamic imports
gradio_hiddenimports = collect_submodules('gradio')
pandas_hiddenimports = collect_submodules('pandas')
PIL_hiddenimports = collect_submodules('PIL')
qrcode_hiddenimports = collect_submodules('qrcode')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=gradio_datas + qrcode_datas + pil_datas,
    hiddenimports=[
        'gradio',
        'gradio.components',
        'gradio.interface',
        'gradio.blocks',
        'gradio.themes',
        'gradio.themes.soft',
        'pandas',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'qrcode',
        'qrcode.constants',
        'qrcode.image.pil',
        'tempfile',
        'zipfile',
        'shutil',
        'math',
        're',
        'typing',
        'uvicorn',
        'uvicorn.main',
        'fastapi',
        'websockets',
        'websockets.server',
        'websockets.client',
        'httpx',
        'httpx._client',
        'jinja2',
        'jinja2.loaders',
        'markupsafe',
        'aiofiles',
        'python_multipart',
        'orjson',
        'pydantic',
        'pydantic.dataclasses',
        'starlette',
        'starlette.applications',
        'starlette.routing',
        'starlette.middleware',
        'starlette.responses',
        'starlette.staticfiles',
    ] + gradio_hiddenimports + pandas_hiddenimports + PIL_hiddenimports + qrcode_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'numpy.distutils',
        'test',
        'tests',
        'testing',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CSV_Template_Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CSV_Template_Generator',
)
