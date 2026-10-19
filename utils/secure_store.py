# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import ctypes
import hashlib
import json
import os
import re
import subprocess
import winreg
from ctypes import wintypes
from pathlib import Path
FILE_ATTRIBUTE_READONLY = 0x1
FILE_ATTRIBUTE_HIDDEN   = 0x2
FILE_ATTRIBUTE_NORMAL   = 0x80

class _DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD),
                ("pbData", ctypes.POINTER(ctypes.c_char))]

def _blob(data: bytes):
    buf = ctypes.create_string_buffer(data, len(data))
    return _DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char))), buf

def _unblob(b: _DATA_BLOB) -> bytes:
    return ctypes.string_at(b.pbData, b.cbData)

def dpapi_protect(data: bytes) -> bytes:
    in_b, _ = _blob(data)
    out = _DATA_BLOB()
    if not ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(in_b), None, None, None, None, 0, ctypes.byref(out)
    ):
        raise OSError("CryptProtectData failed")
    try:
        return _unblob(out)
    finally:
        ctypes.windll.kernel32.LocalFree(out.pbData)

def dpapi_unprotect(data: bytes) -> bytes:
    in_b, _ = _blob(data)
    out = _DATA_BLOB()
    if not ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(in_b), None, None, None, None, 0, ctypes.byref(out)
    ):
        raise OSError("CryptUnprotectData failed")
    try:
        return _unblob(out)
    finally:
        ctypes.windll.kernel32.LocalFree(out.pbData)

def _set_attr(path: Path, attr: int) -> None:
    try:
        ctypes.windll.kernel32.SetFileAttributesW(str(path), attr)
    except Exception:
        pass

def save_encrypted(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _set_attr(path, FILE_ATTRIBUTE_NORMAL)
    path.write_bytes(dpapi_protect(text.encode("utf-8")))
    _set_attr(path, FILE_ATTRIBUTE_READONLY | FILE_ATTRIBUTE_HIDDEN)

def load_encrypted(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return dpapi_unprotect(path.read_bytes()).decode("utf-8")
    except Exception:
        return None

def _machine_guid() -> str:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
        )
        val, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
        return str(val)
    except Exception:
        return ""

def _volume_serial() -> str:
    try:
        out = subprocess.check_output(
            ["cmd", "/c", "vol", "C:"],
            creationflags=subprocess.CREATE_NO_WINDOW,
            stderr=subprocess.DEVNULL,
        ).decode("cp866", errors="ignore")
        m = re.search(r"([0-9A-Fa-f]{4}-[0-9A-Fa-f]{4})", out)
        return m.group(1) if m else ""
    except Exception:
        return ""

def hardware_fingerprint() -> str:
    parts = [_machine_guid(), _volume_serial()]
    if not any(parts):
        parts = [os.environ.get("COMPUTERNAME", ""), os.environ.get("USERNAME", "")]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()