# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import threading
import requests
import json
import winreg
import platform
import struct
import uuid
import time
from datetime import datetime
from config import APPDATA_DIR, ZAPRET_CORE_DIR, CURRENT_VERSION, CURRENT_BUILD, API_URL_STATS

class UserStats:
    def __init__(self):
        self.install_id = self._get_install_id()
        self.api_stats_url = API_URL_STATS
        self._last_send = 0
        self._enabled = True
        self._is_active = False
        self._heartbeat_timer = None
        self.os_info = self._get_os_info()

    def set_enabled(self, enabled):
        self._enabled = enabled
        if not enabled and self._is_active:
            self.stop()
        elif enabled and not self._is_active:
            self.start()
        
    def _get_install_id(self):
        id_file = APPDATA_DIR / 'install_id.json'
        
        if id_file.exists():
            try:
                with open(id_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('install_id')
            except:
                pass
        
        new_id = str(uuid.uuid4())
        id_file.parent.mkdir(parents=True, exist_ok=True)
        with open(id_file, 'w', encoding='utf-8') as f:
            json.dump({'install_id': new_id}, f)
        
        return new_id
    
    def _get_zapret_version(self):
        try:
            version_file = ZAPRET_CORE_DIR / "version.txt"
            if version_file.exists():
                version = version_file.read_text(encoding='utf-8').strip()
                return version
        except Exception:
            pass
        return "0.0"
    
    def _get_os_info(self):
        try:
            arch = "x64" if struct.calcsize("P") * 8 == 64 else "x32"
            
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                    try:
                        current_build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                        current_build = int(current_build)
                    except:
                        current_build = 0
                    
                    if current_build >= 22000:
                        version = "11"
                    elif current_build >= 10240:
                        version = "10"
                    elif current_build >= 9200:
                        version = "8.1"
                    elif current_build >= 7600:
                        version = "7"
                    else:
                        version = "Unknown"
                        
            except Exception:
                version = platform.release()
            return f"Windows {version} ({arch})"
            
        except Exception:
            return "Windows Unknown"

    def _send(self, action):
        if not self._enabled:
            return
        
        now = time.time()
        
        if action == 'heartbeat' and now - self._last_send < 120:
            return
        
        self._last_send = now
        
        def send():
            try:
                payload = {
                    'install_id': self.install_id,
                    'version': CURRENT_VERSION,
                    'build': CURRENT_BUILD,
                    'zapret': self._get_zapret_version(),
                    'os': self.os_info,
                    'action': action,
                    'timestamp': datetime.now().isoformat()
                }
                
                response = requests.post(
                    self.api_stats_url,
                    json=payload,
                    timeout=5,
                    headers={'User-Agent': f'Zapret-Launcher/{CURRENT_VERSION}'}
                )
                    
            except Exception:
                pass
        
        threading.Thread(target=send, daemon=True).start()
    
    def start(self):
        if not self._enabled or self._is_active:
            return
        
        self._is_active = True
        self._send('heartbeat')
        self._schedule_heartbeat()
    
    def stop(self):
        self._is_active = False
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()
            self._heartbeat_timer = None
        self._send('logout')
    
    def _schedule_heartbeat(self):
        if not self._is_active or not self._enabled:
            return
        
        self._send('heartbeat')
        
        self._heartbeat_timer = threading.Timer(30, self._schedule_heartbeat)
        self._heartbeat_timer.daemon = True
        self._heartbeat_timer.start()
    
    def on_launch(self):
        self.start()
    
    def on_connect(self):
        self._send('heartbeat')

user_stats = UserStats()
