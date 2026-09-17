# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import ctypes
import ctypes.wintypes as wintypes
import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple, Optional
from utils.certificate import _CERT_B64

class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_byte * 8),
    ]

class WINTRUST_FILE_INFO(ctypes.Structure):
    _fields_ = [
        ("cbStruct", wintypes.DWORD),
        ("pcwszFilePath", wintypes.LPCWSTR),
        ("hFile", wintypes.HANDLE),
        ("pgKnownSubject", ctypes.POINTER(GUID)),
    ]

class WINTRUST_DATA(ctypes.Structure):
    _fields_ = [
        ("cbStruct", wintypes.DWORD),
        ("pPolicyCallbackData", ctypes.c_void_p),
        ("pSIPClientData", ctypes.c_void_p),
        ("dwUIChoice", wintypes.DWORD),
        ("fdwRevocationChecks", wintypes.DWORD),
        ("dwUnionChoice", wintypes.DWORD),
        ("pFile", ctypes.POINTER(WINTRUST_FILE_INFO)),
        ("dwStateAction", wintypes.DWORD),
        ("hWVTStateData", wintypes.HANDLE),
        ("pwszURLReference", wintypes.LPCWSTR),
        ("dwProvFlags", wintypes.DWORD),
        ("dwUIContext", wintypes.DWORD),
    ]

WTD_UI_NONE = 2
WTD_REVOKE_NONE = 0
WTD_CHOICE_FILE = 1
WTD_STATEACTION_VERIFY = 1
WTD_STATEACTION_CLOSE = 2
WTD_PROV_FLAGS = 0x00000010  # WTD_REVOCATION_CHECK_CHAIN_EXCLUDE_ROOT

WINTRUST_ACTION_GENERIC_VERIFY_V2 = GUID(
    0x00AAC56B,
    0xCD44,
    0x11D0,
    (ctypes.c_byte * 8)(0x8C, 0xC2, 0x00, 0xC0, 0x4F, 0xC2, 0x95, 0xEE),
)

ERROR_SUCCESS = 0

def _verify_via_wintrust(file_path: str) -> Tuple[bool, int]:
    if sys.platform != 'win32':
        return False, -1
    
    file_path = str(Path(file_path).resolve())
    
    file_info = WINTRUST_FILE_INFO()
    file_info.cbStruct = ctypes.sizeof(WINTRUST_FILE_INFO)
    file_info.pcwszFilePath = file_path
    file_info.hFile = None
    file_info.pgKnownSubject = None
    
    trust_data = WINTRUST_DATA()
    trust_data.cbStruct = ctypes.sizeof(WINTRUST_DATA)
    trust_data.pPolicyCallbackData = None
    trust_data.pSIPClientData = None
    trust_data.dwUIChoice = WTD_UI_NONE
    trust_data.fdwRevocationChecks = WTD_REVOKE_NONE
    trust_data.dwUnionChoice = WTD_CHOICE_FILE
    trust_data.pFile = ctypes.pointer(file_info)
    trust_data.dwStateAction = WTD_STATEACTION_VERIFY
    trust_data.hWVTStateData = None
    trust_data.pwszURLReference = None
    trust_data.dwProvFlags = WTD_PROV_FLAGS
    trust_data.dwUIContext = 0
    
    try:
        wintrust = ctypes.windll.wintrust
        result = wintrust.WinVerifyTrust(
            None,
            ctypes.byref(WINTRUST_ACTION_GENERIC_VERIFY_V2),
            ctypes.byref(trust_data)
        )
        
        trust_data.dwStateAction = WTD_STATEACTION_CLOSE
        wintrust.WinVerifyTrust(
            None,
            ctypes.byref(WINTRUST_ACTION_GENERIC_VERIFY_V2),
            ctypes.byref(trust_data)
        )
        
        return result == ERROR_SUCCESS, result
        
    except Exception as e:
        return False, -1

def _get_signer_certificate_b64(file_path: str) -> Optional[str]:
    if sys.platform != 'win32':
        return None
    
    file_path = str(Path(file_path).resolve())
    
    ps_command = (
        f"$sig = Get-AuthenticodeSignature -FilePath '{file_path}'; "
        f"if ($sig.SignerCertificate) {{ "
        f"  [Convert]::ToBase64String($sig.SignerCertificate.Export('Cert')) "
        f"}} else {{ "
        f"  Write-Output 'INVALID' "
        f"}}"
    )
    
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        output = result.stdout.strip()
        
        if not output or output == "INVALID":
            return None
        
        return output
        
    except Exception:
        return None

def is_safe_to_install(file_path: str) -> Tuple[bool, str]:
    if not os.path.exists(file_path):
        return False, "Update file not found"
    
    ext = Path(file_path).suffix.lower()
    if ext not in ('.exe', '.dll', '.msi'):
        return False, f"Unsupported file type: {ext}"
    
    if sys.platform != 'win32':
        return False, "Signature verification is available only on Windows"
    
    signer_cert_b64 = _get_signer_certificate_b64(file_path)
    
    if not signer_cert_b64:
        return False, "File is not signed or the signature is invalid"
    
    our_cert_b64 = _CERT_B64.replace("\n", "").replace(" ", "").replace("\r", "")
    file_cert_b64 = signer_cert_b64.replace("\n", "").replace(" ", "").replace("\r", "")
    
    if our_cert_b64 == file_cert_b64:
        return True, "Signature verified"
    return False, "File is signed with a different certificate (Possible tampering!)"
