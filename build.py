# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build():
    folders = ['build', 'dist', '__pycache__']
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            shutil.rmtree(pycache_path)
            print(f"Removed: {pycache_path}")
    
    spec_file = Path('updater.spec')
    if spec_file.exists():
        spec_file.unlink()
    print()

def create_manifest():
    manifest_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="3.2.3.2"
    processorArchitecture="*"
    name="ZapretLauncher"
    type="win32"
  />
  <description>Zapret Launcher - Bypass restrictions</description>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
    </windowsSettings>
  </application>
</assembly>'''
    
    manifest_path = Path('zapret_launcher.exe.manifest')
    manifest_path.write_text(manifest_content, encoding='utf-8')
    print("Created manifest file for DPI Awareness")
    return manifest_path

def build_exe():
    print("Building Zapret Launcher...")
    print()

    manifest_path = create_manifest()
    
    pyinstaller_paths = [
        r"C:\Users\lives\AppData\Local\Programs\Python\Python312\Scripts\pyinstaller.exe", # Change path
        'pyinstaller'
    ]
    
    pyinstaller = None
    for path in pyinstaller_paths:
        if os.path.exists(path):
            pyinstaller = path
            break
        elif path == 'pyinstaller':
            result = subprocess.run(['where', 'pyinstaller'], capture_output=True, text=True)
            if result.returncode == 0:
                pyinstaller = 'pyinstaller'
                break
    
    if not pyinstaller:
        print("pyinstaller not found!")
        sys.exit(1)
    
    cmd = [
        pyinstaller,
        '--onedir',
        '--windowed',
        '--name', 'updater',
        '--icon', 'resources/icon.ico',
        '--version-file', 'version_info.txt',
        '--uac-admin',
        '--clean',
        '--noconfirm',
        '--manifest', 'zapret_launcher.exe.manifest',
    ]
    
    hidden_imports = [
        '--hidden-import', 'pystray',
        '--hidden-import', 'PIL',
        '--hidden-import', 'cryptography',
        '--hidden-import', 'psutil',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'asyncio',
        '--hidden-import', 'ctypes',
    ]
    cmd.extend(hidden_imports)
    
    data_files = [
        '--add-data', f'gui{os.pathsep}gui',
        '--add-data', f'utils{os.pathsep}utils',
        '--add-data', f'resources{os.pathsep}resources',
        '--add-data', f'tg_proxy{os.pathsep}tg_proxy',
    ]
    
    cmd.extend(data_files)
    cmd.append('main.py')
    
    print("Command:", ' '.join(cmd))
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print()
        print("=" * 50)
        print("Build completed")
        print(f"File: {os.path.abspath('dist/updater.exe')}")
        print("=" * 50)
        
        if manifest_path.exists():
            manifest_path.unlink()
            print("Cleaned up manifest file")
    else:
        print()
        print("=" * 50)
        print("Build error!")
        print("=" * 50)
        if manifest_path.exists():
            manifest_path.unlink()
        sys.exit(1)

if __name__ == '__main__':
    print("building...")
    print()
    
    if not os.path.exists('resources/icon.ico'):
        print("Warning: resources/icon.ico not found")
        print()

    clean_build()
    build_exe()
