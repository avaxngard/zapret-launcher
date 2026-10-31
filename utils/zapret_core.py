# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import os
import re
import time
import shutil
import subprocess
import psutil
import sys
from pathlib import Path
from utils.messagebox import messagebox
from typing import Optional, Tuple, List
from config import ZAPRET_CORE_DIR
from utils.languages import tr
from gui.page.lists_page import check_zapret_folder
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class ZapretCore:
    def __init__(self, parent):
        self.parent = parent
        self.zapret_dir = ZAPRET_CORE_DIR
        self.bin_dir = self.zapret_dir / "bin"
        self.lists_dir = self.zapret_dir / "lists"
        self.utils_dir = self.zapret_dir / "utils"
        self.current_process: Optional[subprocess.Popen] = None
        self.game_filter_enabled = False
        self.ipset_filter_mode = "none"
        self.available_strategies: List[str] = []
        self.ensure_resources()
        self.load_strategies()

    def log_event(self, event_type: str, message: str, mode_name: str = None):
        if hasattr(self, 'parent') and hasattr(self.parent, 'log_event'):
            self.parent.log_event(event_type, message, mode_name)
        
    def get_resource_path(self, relative_path):
        exe_dir = Path(sys.executable).parent
        local_path = exe_dir / relative_path
        
        if local_path.exists():
            return local_path
        
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
            return base_path / relative_path
        else:
            return Path(__file__).parent / relative_path
        
    def ensure_resources(self):
        required_version = self.get_resource_core_version()
        
        if required_version == "0.0":
            messagebox.showerror(
                tr('error'),
                f"{tr('error_version_missing')}\n{tr('reinstall_launcher')}"
            )
            sys.exit(1)
        
        version_file = self.zapret_dir / "version.txt"
        
        if version_file.exists():
            current_version = version_file.read_text(encoding='utf-8').strip()
            
            if current_version == required_version and self.bin_dir.exists():
                return
        
        self._copy_zapret_core_from_resources()

    def _copy_zapret_core_from_resources(self):
        try:
            source_dir = self.get_resource_path("zapret_core")
            
            if self.zapret_dir.exists():
                shutil.rmtree(self.zapret_dir)
            
            self.zapret_dir.mkdir(parents=True, exist_ok=True)
            
            for item in source_dir.iterdir():
                dest_item = self.zapret_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest_item)
                else:
                    shutil.copy2(item, dest_item)
            
            version_file = self.zapret_dir / "version.txt"
            if not version_file.exists():
                required_version = self.get_resource_core_version()
                version_file.write_text(required_version, encoding='utf-8')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install zapret_core:\n{str(e)}")
            sys.exit(1)

    def get_resource_core_version(self):
        resource_version_file = self.get_resource_path("zapret_core/version.txt")
        if resource_version_file.exists():
            try:
                return resource_version_file.read_text(encoding='utf-8').strip()
            except Exception as e:
                self.log_event("info", f"get_resource_core_version: {e}")
        return "0.0"
            
    def load_strategies(self):
        if not self.zapret_dir.exists():
            return
            
        self.available_strategies = []
        for item in self.zapret_dir.glob("general*.bat"):
            self.available_strategies.append(item.name)
        self.available_strategies.sort()
        
    def get_strategy_display_name(self, filename: str) -> str:
        name = filename.replace(".bat", "").replace("general", "").strip()
        if not name:
            return "GENERAL"

        if name.startswith("(") and name.endswith(")"):
            name = name[1:-1].strip()

        name = re.sub(r'([A-Za-z]+)(\d+)', r'\1 \2', name)
        return name
        
    def run_strategy(self, strategy_name: str) -> Tuple[bool, str]:
        if not is_admin():
            return False, tr('error_admin_required')
        
        if not check_zapret_folder():
            return False, tr('error_zapret_folder')

        strategy_path = self.zapret_dir / strategy_name
        if not strategy_path.exists():
            return False, f"{tr('error_strategy_not_found')} {strategy_name}"

        winws_path = self.bin_dir / "winws.exe"
        if not winws_path.exists():
            return False, tr('error_winws_missing')

        try:
            file_size = strategy_path.stat().st_size
            if file_size < 100:
                return False, f"{tr('error_strategy_corrupted_size')}: {strategy_name}"

            content = strategy_path.read_text(encoding='utf-8', errors='ignore')
            
            if "winws.exe" not in content:
                return False, f"{tr('error_strategy_corrupted_content')}: {strategy_name}"

            content_lower = content.lower()

            allowed_prefixes = (
                "@echo", "chcp", "::", "cd ", "set ", "call ", 
                "echo", "powershell", "start ", "exit", "rem "
            )
            for line in content.splitlines():
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                if line_stripped.startswith("::") or line_stripped.startswith("rem "):
                    continue
                if not line_stripped.lower().startswith(allowed_prefixes):
                    self.log_event("info", f"Strategy {strategy_name} contains invalid command: {line_stripped[:30]}")
                    return False, f"{tr('error_strategy_invalid_command')}: {line_stripped[:30]}"

            dangerous_patterns = [
                r"\bdel\b", r"\berase\b", r"\brmdir\b", r"\brd\s+/s\b", r"\bformat\b", r"\bdiskpart\b",
                r"\bcipher\b", r"\bwbadmin\b", r"\bvssadmin\b", r"\bfsutil\b",
                
                r"\breg\s+add\b", r"\breg\s+delete\b", r"\breg\s+import\b", r"\bregedit\b", 
                r"\bschtasks\b", r"\bsc\s+create\b", r"\bsc\s+delete\b", r"\bsc\s+stop\b",
                r"\bsecedit\b", r"\bauditpol\b", r"\bbcdedit\b",
                
                r"\bcertutil\b", r"\bbitsadmin\b", r"\bcurl\b", r"\bwget\b", 
                r"\bmshta\b", r"\brundll32\b", r"\bregsvr32\b", r"\besentutl\b",
                r"\bexpand\b", r"\bextrac32\b", r"\bmakecab\b", r"\bforfiles\b",
                r"\bpcalua\b", r"\bwscript\b", r"\bcscript\b", r"\brpcping\b", r"\breplace\b",
                r"\binvoke-webrequest\b", r"\bdownloadstring\b", r"\biex\b", r"\bencodedcommand\b",
                
                r"\bnet\s+user\b", r"\bnet\s+localgroup\b", r"\bnet\s+start\b", r"\bnet\s+stop\b",
                r"\bnetsh\b", r"\btasklist\b", r"\btaskkill\b", r"\bwhoami\b", r"\bsysteminfo\b",
                
                r"\bshutdown\b", r"\blogoff\b", r"\brestart\b", r"\bpowercfg\b",
                r"\btakeown\b", r"\bicacls\b", r"\bcacls\b", r"\bwmic\b", r"\battrib\b", r"\bfltmc\b",
                
                r"%0",
                r"\bstart\s+cmd\b"
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, content_lower):
                    self.log_event("info", f"Strategy {strategy_name} contains a prohibited command: {pattern}")
                    return False, f"{tr('error_strategy_dangerous_command')}: {pattern}"

        except Exception as e:
            self.log_event("info", f"Strategy validation error {strategy_name}: {e}")
            return False, f"{tr('error_strategy_read')}: {strategy_name}"

        try:
            subprocess.run(['sc', 'stop', 'WinDivert'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(0.5)
            subprocess.run(['sc', 'start', 'WinDivert'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            self.log_event("info", f"WinDivert restart error: {e}")

        try:
            self.stop_current_strategy()
            self.current_process = subprocess.Popen(
                ["cmd.exe", "/c", str(strategy_path)],
                cwd=str(self.zapret_dir),
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            time.sleep(1.0)
            winws_started = False
            for _ in range(10):
                if self.is_winws_running():
                    winws_started = True
                    break
                time.sleep(0.5)
                
            if not winws_started:
                return False, tr('error_winws_not_found')

            time.sleep(2.0)
            if not self.is_winws_running():
                return False, tr('error_winws_crashed')

            return True, f"{tr('status_strategy_started')} {self.get_strategy_display_name(strategy_name)}"
            
        except Exception as e:
            self.log_event("info", f"Error starting strategy {strategy_name} {str(e)}")
            return False, f"{tr('error_startup')} {str(e)}"
            
    def stop_current_strategy(self):
        if self.current_process:
            self.current_process.terminate()
            try:
                self.current_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.current_process.kill()
            self.current_process = None
        
        current_pid = self.current_process.pid if self.current_process else None
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == 'winws.exe':
                    if current_pid is None or proc.info['pid'] == current_pid:
                        proc.terminate()
                        proc.wait(timeout=2)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
                
    def is_winws_running(self) -> bool:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == 'winws.exe':
                    return True
            except Exception as e:
                self.log_event("info", f"is_winws_running: {e}")
        return False
        
    def run_service_command(self, command: str) -> Tuple[bool, str]:
        if command == "game_filter":
            return self._toggle_game_filter()

        elif command == "ipset_filter":
            return self._toggle_ipset_filter()

        return False, f"{tr('error_unknown_command')} {command}"

    def _read_game_filter_mode(self) -> str:
        filter_file = self.utils_dir / "game_filter.enabled"
        if not filter_file.exists():
            return "disabled"
        try:
            for line in filter_file.read_text(encoding='utf-8').splitlines():
                if line.lower().startswith("mode="):
                    mode = line.split("=", 1)[1].strip().lower()
                    if mode in ("disabled", "all", "tcp", "udp"):
                        return mode
        except Exception as e:
            self.log_event("info", f"_read_game_filter_mode: {e}")
        return "disabled"

    def _write_game_filter_mode(self, mode: str):
        filter_file = self.utils_dir / "game_filter.enabled"
        filter_file.parent.mkdir(parents=True, exist_ok=True)

        tcp_range = "1024-65535"
        udp_range = "1024-65535"

        if filter_file.exists():
            try:
                for line in filter_file.read_text(encoding='utf-8').splitlines():
                    low = line.lower().strip()
                    if low.startswith("tcp="):
                        val = line.split("=", 1)[1].strip()
                        if val:
                            tcp_range = val
                    elif low.startswith("udp="):
                        val = line.split("=", 1)[1].strip()
                        if val:
                            udp_range = val
            except Exception as e:
                self.log_event("info", f"_write_game_filter_mode: {e}")

        content = f"mode={mode}\ntcp={tcp_range}\nudp={udp_range}\n"
        filter_file.write_text(content, encoding='utf-8')

    def _toggle_game_filter(self) -> Tuple[bool, str]:
        try:
            current = self._read_game_filter_mode()
            cycle = ["disabled", "all", "tcp", "udp"]
            next_mode = cycle[(cycle.index(current) + 1) % 4]
            self._write_game_filter_mode(next_mode)
            self.game_filter_enabled = (next_mode != "disabled")
            return True, f"Game Filter: {next_mode}\n{tr('restart_zapret')}"
        except Exception as e:
            return False, f"Game Filter error: {e}"

    def _read_ipset_state(self) -> str:
        list_file = self.lists_dir / "ipset-all.txt"
        if not list_file.exists():
            return "any"
        try:
            content = list_file.read_text(encoding='utf-8', errors='ignore').strip()
            if not content:
                return "any"
            if "203.0.113.113/32" in content:
                return "none"
            return "loaded"
        except Exception as e:
            self.log_event("info", f"_read_ipset_state: {e}")
            return "any"

    def _apply_ipset_mode(self, mode: str):
        list_file = self.lists_dir / "ipset-all.txt"
        backup_file = self.lists_dir / "ipset-all.txt.backup"

        if mode == "none":
            if list_file.exists():
                if backup_file.exists():
                    backup_file.unlink()
                list_file.rename(backup_file)
            list_file.write_text("203.0.113.113/32\n", encoding='utf-8')

        elif mode == "any":
            list_file.write_text("", encoding='utf-8')

        elif mode == "loaded":
            if not backup_file.exists():
                raise FileNotFoundError("No .backup to restore")
            if list_file.exists():
                list_file.unlink()
            backup_file.rename(list_file)

    def _toggle_ipset_filter(self) -> Tuple[bool, str]:
        try:
            current = self._read_ipset_state()
            cycle = ["loaded", "none", "any"]
            next_mode = cycle[(cycle.index(current) + 1) % 3]
            self._apply_ipset_mode(next_mode)
            self.ipset_filter_mode = next_mode
            return True, f"IPSet Filter: {next_mode}\n{tr('restart_zapret')}"
        except FileNotFoundError:
            return False, "No backup to restore. Update list first"
        except Exception as e:
            return False, f"IPSet error: {e}"
