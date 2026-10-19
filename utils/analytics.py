# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import json
import platform
import struct
import threading
import time
import uuid
import winreg
from datetime import datetime
from pathlib import Path
import requests
from config import (
    CONFIG_FILE,
    APPDATA_DIR,
    ZAPRET_CORE_DIR,
    CURRENT_VERSION,
    CURRENT_BUILD,
    API_URL_STATS,
)
from utils.secure_store import (
    save_encrypted,
    load_encrypted,
    hardware_fingerprint,
)

ID_FILE      = APPDATA_DIR / "install_id.dat"
LEGACY_FILE  = APPDATA_DIR / "install_id.json"

class UserStats:
    def __init__(self):
        self.install_id = self._get_install_id()
        self.hw_fingerprint = hardware_fingerprint()
        self.api_stats_url = API_URL_STATS
        self._last_send = 0
        self._enabled = True
        self._is_active = False
        self._heartbeat_timer = None
        self.os_info = self._get_os_info()
        self.cached_stats = None
        self.on_identity_changed = None

    def _load_payload(self) -> dict | None:
        raw = load_encrypted(ID_FILE)
        if not raw:
            return None
        try:
            data = json.loads(raw)
            if not isinstance(data, dict):
                return None
            return data
        except Exception:
            return None

    def _save_payload(self, data: dict) -> None:
        save_encrypted(ID_FILE, json.dumps(data, separators=(",", ":")))

    def _get_install_id(self) -> str:
        data = self._load_payload()

        if data and data.get("install_id"):
            stored_hw = data.get("hw", "")
            cur_hw = hardware_fingerprint()
            if stored_hw and cur_hw and stored_hw != cur_hw:
                return self._create_new_identity()
            if data.get("hw") != cur_hw:
                data["hw"] = cur_hw
                self._save_payload(data)
            return data["install_id"]

        if LEGACY_FILE.exists():
            try:
                with open(LEGACY_FILE, "r", encoding="utf-8") as f:
                    legacy = json.load(f)
                old_id = legacy.get("install_id")
                if old_id:
                    self._save_payload({
                        "install_id": old_id,
                        "hw": hardware_fingerprint(),
                    })
                    try:
                        LEGACY_FILE.unlink()
                    except Exception:
                        pass
                    return old_id
            except Exception:
                pass

        return self._create_new_identity()

    def _create_new_identity(self) -> str:
        new_id = str(uuid.uuid4())
        self._save_payload({
            "install_id": new_id,
            "hw": hardware_fingerprint(),
        })
        return new_id

    def regenerate_identity(self) -> None:
        self.install_id = self._create_new_identity()
        self.hw_fingerprint = hardware_fingerprint()
        self.cached_stats = None
        if callable(self.on_identity_changed):
            try:
                self.on_identity_changed(self.install_id)
            except Exception:
                pass

    def _get_zapret_version(self) -> str:
        try:
            version_file = ZAPRET_CORE_DIR / "version.txt"
            if version_file.exists():
                return version_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass
        return "0.0"

    def _get_os_info(self) -> str:
        try:
            arch = self._get_os_arch()
            try:
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                ) as key:
                    try:
                        current_build = int(winreg.QueryValueEx(key, "CurrentBuild")[0])
                    except Exception:
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

    def _get_os_arch(self) -> str:
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            ) as key:
                arch = winreg.QueryValueEx(key, "PROCESSOR_ARCHITECTURE")[0]

            return {
                "AMD64": "x64",
                "x86": "x32",
                "ARM64": "ARM64",
            }.get(arch, arch)
        except Exception:
            return "x64" if struct.calcsize("P") * 8 == 64 else "x32"

    def _build_payload(self, action: str, extra: dict | None) -> dict:
        settings = {}
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
        except Exception:
            pass

        payload = {
            "install_id": self.install_id,
            "hw": self.hw_fingerprint,
            "version": CURRENT_VERSION,
            "build": CURRENT_BUILD,
            "zapret": self._get_zapret_version(),
            "os": self.os_info,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "auto_update_enabled": settings.get("auto_update_enabled", True),
            "autostart_enabled": settings.get("autostart_enabled", False),
            "current_strategy": settings.get("current_strategy"),
            "language": settings.get("language", "Russian"),
            "theme": settings.get("theme", "Dark"),
            "update_source": settings.get("update_source", "main"),
        }
        if extra:
            payload.update(extra)
        return payload

    def _post(self, payload: dict, allow_regen: bool = True) -> dict | None:
        try:
            resp = requests.post(
                self.api_stats_url,
                json=payload,
                timeout=5,
                headers={"User-Agent": f"Zapret-Launcher/{CURRENT_VERSION}"},
            )
            try:
                data = resp.json()
            except Exception:
                return None

            if (isinstance(data, dict)
                    and data.get("error") == "duplicate_install_id"
                    and allow_regen):
                self.regenerate_identity()
                payload["install_id"] = self.install_id
                payload["hw"] = self.hw_fingerprint
                return self._post(payload, allow_regen=False)

            return data
        except Exception:
            return None

    def _send(self, action: str, extra_data: dict | None = None) -> None:
        if not self._enabled:
            return

        now = time.time()
        if action == "heartbeat" and now - self._last_send < 300:
            return
        self._last_send = now

        payload = self._build_payload(action, extra_data)

        def worker():
            self._post(payload)

        threading.Thread(target=worker, daemon=True).start()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        if not enabled and self._is_active:
            self.stop()
        elif enabled and not self._is_active:
            self.start()

    def on_connect(self, mode: str | None = None) -> None:
        if not self._enabled:
            return
        extra = {"mode": mode} if mode else None
        self._send("connect", extra)

    def on_disconnect(self, mode: str | None = None, duration_seconds: int = 0) -> None:
        if not self._enabled:
            return
        extra = {"duration": int(duration_seconds)}
        if mode:
            extra["mode"] = mode
        self._send("disconnect", extra)

    def start(self) -> None:
        if not self._enabled or self._is_active:
            return
        self._is_active = True
        self._send("heartbeat")
        self._schedule_heartbeat()

    def stop(self) -> None:
        self._is_active = False
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()
            self._heartbeat_timer = None
        self._send("logout")

    def _schedule_heartbeat(self) -> None:
        if not self._is_active or not self._enabled:
            return
        self._send("heartbeat")
        self._heartbeat_timer = threading.Timer(30, self._schedule_heartbeat)
        self._heartbeat_timer.daemon = True
        self._heartbeat_timer.start()

    def on_launch(self) -> None:
        self.start()

    def fetch_user_stats(self) -> None:
        if self.cached_stats is not None:
            return

        def worker():
            payload = {
                "install_id": self.install_id,
                "hw": self.hw_fingerprint,
                "action": "get_user_stats",
            }
            data = self._post(payload)
            if isinstance(data, dict) and data.get("success"):
                self.cached_stats = data.get("stats")

        threading.Thread(target=worker, daemon=True).start()

    def send_session_progress(self, mode: str | None = None,
                              duration_seconds: int = 0) -> None:
        if not self._enabled or duration_seconds <= 0:
            return
        extra = {"duration": int(duration_seconds)}
        if mode:
            extra["mode"] = mode
        self._send("disconnect", extra)

    def send_ping(self, ping_ms: int) -> None:
        if not self._enabled or ping_ms <= 0:
            return

        def worker():
            payload = {
                "install_id": self.install_id,
                "hw": self.hw_fingerprint,
                "action": "ping",
                "ping": int(ping_ms),
            }
            self._post(payload)

        threading.Thread(target=worker, daemon=True).start()

user_stats = UserStats()
