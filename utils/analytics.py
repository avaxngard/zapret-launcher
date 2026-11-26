# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import json
import logging
import platform
import re
import struct
import threading
import time
import uuid
import winreg
from datetime import datetime
import requests
from config import (
    CONFIG_FILE,
    APPDATA_DIR,
    ZAPRET_CORE_DIR,
    CURRENT_VERSION,
    CURRENT_BUILD,
    API_URL_STATS
)
from utils.secure_store import (
    save_encrypted,
    load_encrypted,
    hardware_fingerprint
)

ID_FILE      = APPDATA_DIR / "install_id.dat"
LEGACY_FILE  = APPDATA_DIR / "install_id.json"

logger = logging.getLogger("analytics")
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.NullHandler())

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

_SQL_LEAK_RE = re.compile(
    r"(sqlstate|base\s+table\s+or\s+view\s+not\s+found|"
    r"table\s+'[^']+'|database\s+'[^']+'|column\s+'[^']+'|"
    r"unknown\s+(database|table|column)|mysql|mariadb|pdoexception|"
    r"update\s+error|insert\s+error|select\s+error|delete\s+error)",
    re.IGNORECASE
)

class UserStats:
    HEARTBEAT_INTERVAL = 300
    REQUEST_TIMEOUT    = 5
    SETTINGS_CACHE_TTL = 30

    def __init__(self):
        self.install_id = self._get_install_id()
        self.hw_fingerprint = hardware_fingerprint()
        self.api_stats_url = API_URL_STATS
        self._last_heartbeat = 0
        self._enabled = True
        self._is_active = False
        self._heartbeat_timer = None
        self._lock = threading.Lock()
        self.os_info = self._get_os_info()
        self.cached_stats = None
        self.on_identity_changed = None

        self._settings_cache = None
        self._settings_cache_at = 0

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

    def _read_settings(self) -> dict:
        now = time.time()
        cached = self._settings_cache
        if cached is not None and now - self._settings_cache_at < self.SETTINGS_CACHE_TTL:
            return cached

        data = {}
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        data = loaded
        except Exception as e:
            logger.debug("settings read failed: %s", e)
            data = {}

        self._settings_cache = data
        self._settings_cache_at = now
        return data

    def _build_payload(self, action: str, extra: dict | None) -> dict:
        settings = self._read_settings()

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

    @staticmethod
    def _safe_error_code(data: dict) -> str:
        if not isinstance(data, dict):
            return "unknown"
        err = data.get("error")
        if not err:
            return "unknown"
        if not isinstance(err, str):
            return "invalid_error_field"
        if _SQL_LEAK_RE.search(err):
            return "server_db_error"
        if re.fullmatch(r"[A-Za-z0-9_:.\-]{1,64}", err):
            return err
        return "server_error"

    def _post(self, payload: dict, allow_regen: bool = True) -> dict | None:
        action = payload.get("action")
        try:
            resp = requests.post(
                self.api_stats_url,
                json=payload,
                timeout=self.REQUEST_TIMEOUT,
                headers={"User-Agent": f"Zapret-Launcher/{CURRENT_VERSION}"},
            )
        except Exception as e:
            logger.warning("stats POST failed (%s): %s", action, type(e).__name__)
            return None

        if resp.status_code >= 400:
            logger.warning("stats POST HTTP %s (%s)", resp.status_code, action)

        try:
            data = resp.json()
        except Exception:
            logger.warning("stats POST non-JSON response (%s)", action)
            return None

        if (isinstance(data, dict)
                and data.get("error") == "duplicate_install_id"
                and allow_regen):
            self.regenerate_identity()
            payload["install_id"] = self.install_id
            payload["hw"] = self.hw_fingerprint
            return self._post(payload, allow_regen=False)

        if isinstance(data, dict) and data.get("success") is False:
            logger.info("stats POST rejected (%s): error=%s",
                        action, self._safe_error_code(data))

        return data

    def _send(self, action: str, extra_data: dict | None = None) -> None:
        if not self._enabled:
            return

        now = time.time()
        if action == "heartbeat":
            if now - self._last_heartbeat < self.HEARTBEAT_INTERVAL:
                return
            self._last_heartbeat = now

        payload = self._build_payload(action, extra_data)

        def worker():
            result = self._post(payload)
            if result is None:
                logger.debug("stats action %s not delivered", action)

        threading.Thread(target=worker, daemon=True).start()

    def set_enabled(self, enabled: bool) -> None:
        if self._enabled == enabled:
            return
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
        was_active = self._is_active
        self._is_active = False
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()
            self._heartbeat_timer = None

        if was_active:
            payload = self._build_payload("logout", None)
            try:
                self._post(payload)
            except Exception as e:
                logger.debug("logout send failed: %s", e)

    def _schedule_heartbeat(self) -> None:
        if not self._is_active or not self._enabled:
            return

        self._heartbeat_timer = threading.Timer(self.HEARTBEAT_INTERVAL, self._heartbeat_tick)
        self._heartbeat_timer.daemon = True
        self._heartbeat_timer.start()

    def _heartbeat_tick(self) -> None:
        if not self._is_active or not self._enabled:
            return
        self._send("heartbeat")
        self._schedule_heartbeat()

    def on_launch(self) -> None:
        self.start()

    def fetch_user_stats(self) -> None:
        def worker():
            payload = {
                "install_id": self.install_id,
                "hw": self.hw_fingerprint,
                "action": "get_user_stats",
            }
            data = self._post(payload)
            if isinstance(data, dict) and data.get("success"):
                self.cached_stats = data.get("stats")
            else:
                logger.info("fetch_user_stats failed")
        threading.Thread(target=worker, daemon=True).start()

    def send_session_progress(self, mode: str | None = None,
                              duration_seconds: int = 0) -> None:
        if not self._enabled or duration_seconds <= 0:
            return
        extra = {"duration": int(duration_seconds)}
        if mode:
            extra["mode"] = mode
        self._send("session_progress", extra)

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
            if self._post(payload) is None:
                logger.debug("send_ping not delivered: %s ms", ping_ms)

        threading.Thread(target=worker, daemon=True).start()

    def send_page_view(self, page: str) -> None:
        if not self._enabled or not page:
            return

        def worker():
            payload = {
                "install_id": self.install_id,
                "hw": self.hw_fingerprint,
                "action": "page_view",
                "page": page,
            }
            if self._post(payload) is None:
                logger.debug("send_page_view not delivered: %s", page)

        threading.Thread(target=worker, daemon=True).start()

user_stats = UserStats()
