# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
import pywinstyles
from tkinter import messagebox, ttk
from gui.pages import Pages
from tg_proxy.config import proxy_config
from tg_proxy import setup_tg_logging
from gui.page.lists_page import check_zapret_folder
from gui.tray import ModernSystemTray
from typing import Optional, Tuple, List
from utils.languages import tr, get_languages
from utils.news import NewsManager
from gui.dialogs import Dialogs
from utils.analytics import user_stats
from gui.theme import get_theme, get_theme_names
from datetime import datetime
from utils.check_lists import check_lists_for_duplicates
from gui.splash import SplashWindow
from gui.widgets import RoundedButton
try:
    from tg_proxy import run_proxy
    from tg_proxy.config import proxy_config
    TG_PROXY_AVAILABLE = True
except ImportError:
    TG_PROXY_AVAILABLE = False
    run_proxy = None
import subprocess
import os
import json
import time
import shutil
import threading
import webbrowser
import asyncio
import psutil
import socket
import winreg
from pathlib import Path
import sys
import re
import ctypes
import urllib.request
from utils.version import compare_builds, compare_zapret_versions
from utils.scaling import set_dpi_awareness, get_optimal_scale, scale_size
from config import CURRENT_VERSION, CURRENT_BUILD, APPDATA_DIR, CONFIG_FILE, ZAPRET_CORE_DIR, LISTS_DIR, TG_HOST, TG_PORT, TG_FAKE_TLS, TG_FAKE_TLS_DOMAIN, BUILDNUMBER_URL, ZAPRET_VERSION_URL, VERSION_URL, ICON_PATH, PNG_ICON_PATH, CHECK_UPDATES_INTERVAL

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
    except Exception as e:
        messagebox.showerror(tr('error_no_connection'), f"{tr('error_admin_required')}: {e}")
    sys.exit(0)

class StatsMonitor:
    def __init__(self):
        self.session_start = None
        self.total_up_bytes = 0
        self.total_down_bytes = 0
        self.connection_count = 0
        self.disconnection_count = 0
        self.is_monitoring = False
        self._monitor_thread = None
        self._cache_duration = 2.0
        self._cached_stats = (0, 0)
        self._cached_time = 0
        self._stop_event = None
        self.last_up = 0
        self.last_down = 0
        self.current_speed_up = 0
        self.current_speed_down = 0
        self.last_update_time = 0
        
    def start_session(self):
        self.session_start = time.time()
        self.connection_count += 1
        self.is_monitoring = True
        self.total_up_bytes = 0
        self.total_down_bytes = 0
        self.current_speed_up = 0
        self.current_speed_down = 0
        self.last_up, self.last_down = self._get_network_stats()
        self.last_update_time = time.time()
        
    def end_session(self):
        self.is_monitoring = False
        self.disconnection_count += 1
        
    def _get_network_stats(self):
        current_time = time.time()
        if hasattr(self, '_cached_stats') and hasattr(self, '_cached_time'):
            if current_time - self._cached_time < self._cache_duration:
                return self._cached_stats
        
        try:
            counters = psutil.net_io_counters()
            recv = counters.bytes_recv
            sent = counters.bytes_sent
            self._cached_stats = (recv, sent)
            self._cached_time = current_time
            return recv, sent
        except Exception:
            return 0, 0
    
    def update_speed(self):
        if not self.is_monitoring:
            return
        
        try:
            current_up, current_down = self._get_network_stats()
            now = time.time()
            time_diff = now - self.last_update_time
            
            if current_up > self.last_up:
                self.total_up_bytes += (current_up - self.last_up)
            if current_down > self.last_down:
                self.total_down_bytes += (current_down - self.last_down)
            
            if time_diff >= 0.5:
                up_diff = max(0, current_up - self.last_up)
                down_diff = max(0, current_down - self.last_down)
                
                raw_speed_up = up_diff / time_diff if time_diff > 0 else 0
                raw_speed_down = down_diff / time_diff if time_diff > 0 else 0
                
                self.current_speed_up = self.current_speed_up * 0.7 + raw_speed_up * 0.3
                self.current_speed_down = self.current_speed_down * 0.7 + raw_speed_down * 0.3
                
                self.last_update_time = now
            
            self.last_up = current_up
            self.last_down = current_down
            
            self.current_speed_up = max(0, self.current_speed_up)
            self.current_speed_down = max(0, self.current_speed_down)
        except:
            pass
    
    def get_session_time(self):
        if self.session_start:
            return time.time() - self.session_start
        return 0
    
    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def format_bytes(self, bytes_val):
        if bytes_val < 1024:
            return f"{bytes_val} B"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val / 1024:.1f} KB"
        elif bytes_val < 1024 * 1024 * 1024:
            return f"{bytes_val / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"
    
    def format_speed(self, bytes_per_sec):
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.0f} B/s"
        elif bytes_per_sec < 1024 * 1024:
            return f"{bytes_per_sec / 1024:.1f} KB/s"
        else:
            return f"{bytes_per_sec / (1024 * 1024):.1f} MB/s"
    
    def get_stats_dict(self):
        self.update_speed()
        return {
            'session_time': self.get_session_time(),
            'session_time_str': self.format_time(self.get_session_time()),
            'up_bytes': self.total_up_bytes,
            'up_str': self.format_bytes(self.total_up_bytes),
            'down_bytes': self.total_down_bytes,
            'down_str': self.format_bytes(self.total_down_bytes),
            'total_bytes': self.total_up_bytes + self.total_down_bytes,
            'total_str': self.format_bytes(self.total_up_bytes + self.total_down_bytes),
            'connections': self.connection_count,
            'disconnections': self.disconnection_count,
            'speed_up': self.current_speed_up,
            'speed_up_str': self.format_speed(self.current_speed_up),
            'speed_down': self.current_speed_down,
            'speed_down_str': self.format_speed(self.current_speed_down),
        }

class TGProxyServer:
    def __init__(self, host=None, port=None, fake_tls_domain=None):
        self._thread = None
        self._running = False
        self._port = port if port is not None else 1443
        self._host = host if host is not None else '127.0.0.1'
        self._fake_tls_domain = fake_tls_domain if fake_tls_domain is not None else ''
        self._secret = None
        self._stop_event = None
        self._log_callback = None

    def set_log_callback(self, callback):
        self._log_callback = callback
        #run.set_log_callback(callback)
    
    def _log(self, message):
        if self._log_callback:
            self._log_callback("info", message)

    def set_secret(self, secret):
        self._secret = secret
        proxy_config.secret = secret
        
        if self._running:
            self.stop()
            time.sleep(1)
            self.start()
    
    def _is_port_open(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        try:
            result = sock.connect_ex((self._host, port))
            return result == 0
        finally:
            sock.close()
    
    def wait_for_start(self, timeout=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._is_port_open(self._port):
                return True
            time.sleep(0.2)
        return False
    
    def start(self):
        if self._running:
            self.stop()
            time.sleep(1)

        self._stop_event = None
        
        def run_tg_proxy():
            loop = None
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self._stop_event = asyncio.Event()
                
                proxy_config.host = self._host
                proxy_config.port = self._port
                proxy_config.fake_tls_domain = self._fake_tls_domain
                
                if self._secret:
                    proxy_config.secret = self._secret
                else:
                    if self._log_callback:
                        self._log_callback("error", "No secret set for TG Proxy")
                    return
                
                if not proxy_config.dc_redirects:
                    proxy_config.dc_redirects = {
                        2: '149.154.167.220',
                        4: '149.154.167.220'
                    }
                
                run_proxy(self._stop_event)
            except Exception as e:
                if self._log_callback:
                    self._log_callback("error", f"TG Proxy error: {e}")
            finally:
                if loop is not None:
                    loop.close()

        self._thread = threading.Thread(target=run_tg_proxy, daemon=True)
        self._thread.start()
        
        if self.wait_for_start(10):
            self._running = True
            return True
        return False
    
    def stop(self):
        if not self._running and not self._thread:
            return
        
        self._running = False
        
        if self._stop_event:
            try:
                self._stop_event.set()
            except Exception:
                pass
            self._stop_event = None
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((self._host, self._port))
            sock.close()
        except Exception:
            pass
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
            if self._thread.is_alive():
                try:
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(
                        ctypes.c_long(self._thread.ident), 
                        ctypes.py_object(SystemExit)
                    )
                except:
                    pass
                self._thread.join(timeout=1)
        
        self._thread = None

    @property
    def is_running(self):
        return self._running and self._is_port_open(self._port)
    
    @property
    def host(self):
        return self._host
    
    @property
    def port(self):
        return self._port
    
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
                "Error",
                "File version.txt was not found in the launcher resources\n"
                "Reinstall the launcher"
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
            except Exception:
                pass
        return "0.0"
            
    def load_strategies(self):
        if not self.zapret_dir.exists():
            return
            
        self.available_strategies = []
        for item in self.zapret_dir.glob("general*.bat"):
            self.available_strategies.append(item.name)
        self.available_strategies.sort()
        
    def get_strategy_display_name(self, filename: str) -> str:
        name = filename.replace(".bat", "").replace("general", "")
        if not name:
            return "GENERAL"
        return name.strip()
        
    def run_strategy(self, strategy_name: str) -> Tuple[bool, str]:
        if not is_admin():
            return False, tr('error_admin_required')
        
        subprocess.run(['sc', 'stop', 'WinDivert'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(0.5)
        subprocess.run(['sc', 'start', 'WinDivert'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        if not check_zapret_folder():
            return False, tr('error_zapret_folder')

        strategy_path = self.zapret_dir / strategy_name
        if not strategy_path.exists():
            return False, f"{tr('error_strategy_not_found')} {strategy_name}"
            
        try:
            self.stop_current_strategy()
            self.log_event("info", f"Starting winws.exe with strategy {strategy_name}")

            self.current_process = subprocess.Popen(
                ["cmd.exe", "/c", str(strategy_path)],
                cwd=str(self.zapret_dir),
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            time.sleep(1.0)
            for _ in range(10):
                if self.is_winws_running():
                    return True, f"{tr('status_strategy_started')} {self.get_strategy_display_name(strategy_name)}"
                time.sleep(0.5)
            return False, tr('error_winws_not_found')
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
            except:
                pass
        return False
        
    def run_service_command(self, command: str) -> Tuple[bool, str]:
        if command == "game_filter":
            self.game_filter_enabled = not self.game_filter_enabled
            return True, f"Game Filter: {tr('status_enabled') if self.game_filter_enabled else tr('status_disabled')}\n{tr('restart_zapret')}"
            
        elif command == "ipset_filter":
            modes = ["none", "loaded", "any"]
            current_idx = modes.index(self.ipset_filter_mode)
            self.ipset_filter_mode = modes[(current_idx + 1) % 3]
            return True, f"IPSet Filter: {self.ipset_filter_mode}\n{tr('restart_zapret')}"
        return False, f"{tr('error_unknown_command')} {command}"

class ZapretLauncher:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        self.root.overrideredirect(False)
        self.root.attributes('-toolwindow', False)

        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            
            current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            current_style = current_style & ~WS_EX_TOOLWINDOW
            current_style = current_style | WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_style)
            ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0002 | 0x0001)
            self.root.title("Zapret Launcher")
            ctypes.windll.user32.ShowWindow(hwnd, 5)
            ctypes.windll.user32.SetWindowTextW(hwnd, "Zapret Launcher")
        except Exception:
            pass

        self.scale_factor = get_optimal_scale()
        
        self.base_width = 1200
        self.base_height = 800
        self.base_font_size = 10
        
        self.window_width = scale_size(self.base_width, self.scale_factor)
        self.window_height = scale_size(self.base_height, self.scale_factor)
        
        self.font_size_primary = scale_size(self.base_font_size, self.scale_factor)
        self.font_size_medium = scale_size(self.base_font_size + 2, self.scale_factor)
        self.font_size_title = scale_size(self.base_font_size + 18, self.scale_factor)
        self.font_size_bold = scale_size(self.base_font_size + 2, self.scale_factor)
        
        self.font_primary = ("Segoe UI Variable", self.font_size_primary)
        self.font_medium = ("Segoe UI Variable", self.font_size_medium)
        self.font_title = ("Segoe UI Variable", self.font_size_title, "bold")
        self.font_bold = ("Segoe UI Variable", self.font_size_bold, "bold")
        
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.resizable(False, False)
        self.center_window()
        self._update_window_title_color()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.stats = StatsMonitor()
        self.stats_update_id = None
        self._pending_mode = None

        self.mode_label = None
        self.connect_btn = None
        self._connecting = False
        self.main_status = None
        self.stats_frame = None
        self.stats_time_label = None
        self.stats_traffic_label = None
        self.stats_total_label = None
        self.stats_speed_up_label = None
        self.stats_speed_down_label = None
        self.stats_rtt_label = None

        self.tg_host = TG_HOST
        self.tg_port = TG_PORT
        self.tg_fake_tls = TG_FAKE_TLS
        self.tg_fake_tls_domain = TG_FAKE_TLS_DOMAIN

        self.strategy_var = tk.StringVar()
        self.tgws_var = tk.BooleanVar(value=False)

        self._tg_instruction = False
        self._tg_secret = None

        self._show_vpn_detection = False
        self._hide_duplicates_warning = False

        self._auto_update_enabled = True
        self._analytics_enabled = True

        self._current_notification = None

        self.update_intervals = [1]
        self.update_interval_index = 0
        self.update_interval = self.update_intervals[self.update_interval_index]
        self.update_timer_id = None

        self.rtt_timer_id = None
        self.rtt_update_interval = 60000

        self.last_selected_index = -1

        self._cached_rtt = -1
        self._cached_rtt_time = 0
        self.rtt_cache_duration = 60
        
        self.colors = get_theme('Dark')
        self.setup_scrollbar_style()
        self.root.configure(bg=self.colors['bg_dark'])

        try:
            icon_path = [ICON_PATH]
            for path in icon_path:
                if path and path.exists():
                    try:
                        if path.suffix.lower() == '.ico':
                            self.root.iconbitmap(default=str(path))
                            break
                    except:
                        continue
        except Exception:
            pass

        self.is_connected = False
        self._disconnecting = False
        self.current_strategy = None
        self.current_page = "main"

        self.ensure_appdata_dir()
        self.ensure_custom_list_file()
        
        self.zapret = ZapretCore(self)
        self.user_stats = user_stats
        
        self.languages = get_languages()
        self.load_settings()

        self.tg_proxy = TGProxyServer(host=self.tg_host, port=self.tg_port, fake_tls_domain=self.tg_fake_tls_domain if self.tg_fake_tls else '')
        self.tg_proxy.set_log_callback(self.log_event)

        try:
            log_file_path = APPDATA_DIR / "logs.txt"
            setup_tg_logging(str(log_file_path))
        except Exception:
            pass

        if not self._tg_secret:
            self._tg_secret = os.urandom(16).hex()
            self.save_settings()

        self.tg_proxy.set_secret(self._tg_secret)
        proxy_config.secret = self._tg_secret
        
        if not hasattr(self, 'current_theme'):
            self.current_theme = 'Default'
        self.apply_theme()

        self.dialogs = Dialogs(self)
        
        self.setup_ui()
        self.update_check_timer_id = None
        
        self.root.after(200, self.check_lists_for_duplicates)
        self.root.after(200, self.check_initial_status)
        self.show_main_page()
        
        self.tray_icon = ModernSystemTray(self)
        self._updating = False
        
        self.root.bind('<Unmap>', self.on_window_state_change)
        self.root.bind('<Map>', self.on_window_state_change)
        
        self._schedule_heartbeat()
        self.news_manager = NewsManager(self)
        self.news_manager.set_install_id(self.user_stats.install_id)
        self.start_update_checker()
        
        self.root.after(1500, lambda: self.news_manager.check_news(show_on_start=True))
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        self.root.update_idletasks()
        self.root.attributes('-alpha', 0.0)
        self.root.deiconify()
        self.root.update()

        def fade_in(alpha=0.0):
            if alpha < 1.0:
                alpha += 0.15
                try:
                    self.root.attributes('-alpha', alpha)
                    self.root.after(12, lambda: fade_in(alpha))
                except:
                    pass
            else:
                try:
                    self.root.attributes('-alpha', 1.0)
                except:
                    pass

        self.root.after(100, fade_in)

    def on_window_state_change(self, event=None):
        if self._updating:
            return
        
        self._updating = True

        try:
            if not self.root.winfo_exists():
                return
                
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.force_update_menu()
                self.update_all_window_headers()
        except Exception:
            pass
        finally:
            self._updating = False

    def update_all_window_headers(self):
        try:
            if not self.root.winfo_exists():
                return
            
            dialog_header_color = self.colors['bg_medium']
            
            for child in self.root.winfo_children():
                if isinstance(child, tk.Toplevel):
                    try:
                        if child.winfo_exists():
                            pywinstyles.change_header_color(child, dialog_header_color)
                    except tk.TclError:
                        continue
                    except Exception:
                        pass
                        
        except Exception:
            pass

    def ensure_custom_list_file(self):
        try:
            lists_dir = LISTS_DIR
            if not lists_dir.exists():
                lists_dir.mkdir(parents=True, exist_ok=True)
            
            custom_list_path = lists_dir / "list-custom.txt"
            if not custom_list_path.exists():
                with open(custom_list_path, 'w', encoding='utf-8') as f:
                    f.write("zapret-launcher.ru\n")
                
        except Exception:
            pass

    def update_tray_icon_state(self):
        if hasattr(self, 'tray_icon') and self.tray_icon:
            try:
                self.tray_icon.update_icon_state()
            except Exception:
                pass

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def on_closing(self):
        try:
            self.root.withdraw()
        except Exception:
            pass

    def update_ui_colors(self):
        def update_widget(widget):
            try:
                if isinstance(widget, (tk.Frame, tk.Label, tk.Canvas)):
                    current_bg = widget.cget('bg')
                    if current_bg and current_bg not in [self.colors['accent'], self.colors['accent_green'], self.colors['accent_red']]:
                        widget.configure(bg=self.colors['bg_dark'])
                
                if isinstance(widget, tk.Label):
                    current_fg = widget.cget('fg')
                    accent_colors = [self.colors['accent'], self.colors['accent_green'], self.colors['accent_red'], self.colors['accent_hover']]
                    if current_fg and current_fg not in accent_colors:
                        widget.configure(fg=self.colors['text_secondary'])
                
                if hasattr(widget, 'update_colors'):
                    widget.update_colors(self.colors['button_bg'], self.colors['text_secondary'], self.colors['button_hover'])
                
                for child in widget.winfo_children():
                    update_widget(child)
            except:
                pass
        update_widget(self.root)

    def update_nav_buttons_colors(self):
        if hasattr(self, 'left_panel'):
            for child in self.left_panel.winfo_children():
                if isinstance(child, tk.Frame):
                    for btn in child.winfo_children():
                        if hasattr(btn, 'update_theme'):
                            btn.update_theme(self.current_theme)
                        if hasattr(btn, 'update_colors'):
                            btn.update_colors(self.colors['bg_light'], self.colors['text_secondary'], self.colors['accent'])

    def apply_theme(self):
        self.colors = get_theme(self.current_theme)
        self.root.configure(bg=self.colors['bg_dark'])
        self.setup_scrollbar_style()
        self.update_ui_colors()
        self._update_window_title_color()
        self.update_all_window_headers()
        
        if hasattr(self, 'pages') and self.pages:
            self.pages.colors = self.colors
            
            for page_name in ['main_page', 'service_page', 'lists_page', 'settings_page', 'logs_page']:
                if hasattr(self.pages, page_name):
                    page = getattr(self.pages, page_name)
                    if page:
                        page.configure(bg=self.colors['bg_dark'])
                        
            if hasattr(self, 'left_panel') and self.left_panel:
                self.left_panel.configure(bg=self.colors['bg_medium'])
                
            self.update_nav_buttons_colors()

        if hasattr(self, 'pages'):
            self.pages.update_animation_color()

    def set_dialog_header_color(self, dialog):
        try:
            if not dialog or not dialog.winfo_exists():
                return
            
            header_color = self.colors['bg_medium'] if hasattr(self, 'colors') else "#1A1A1F"
            pywinstyles.change_header_color(dialog, header_color)
        except ImportError:
            pass
        except Exception:
            pass

    def _update_window_title_color(self):
        try:
            if self.current_theme == 'Default':
                header_color = "#0F0F12"
            else:
                header_color = "#1E1B2E"
            
            pywinstyles.change_header_color(self.root, header_color)
            
        except ImportError:
            pass
        except Exception:
            pass

    def _stop_windivert_before_restart(self):
        try:
            subprocess.run(['sc', 'stop', 'WinDivert'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(0.5)
        except:
            pass

    def quit_from_tray(self):
        self.save_settings()
        self._stop_windivert_before_restart()
        self.zapret.stop_current_strategy()
        if hasattr(self, 'tg_proxy'):
            self.tg_proxy.stop()

        self.stop_update_checker()
        
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        sys.exit(0)

    def _hide_all_dialogs(self):
        try:
            for child in self.root.winfo_children():
                if isinstance(child, tk.Toplevel) and child.winfo_exists():
                    try:
                        child.withdraw()
                    except:
                        pass
        except Exception:
            pass

    def _show_all_dialogs(self):
        try:
            dialog_color = self.colors['bg_medium']
            dialog_header_color = self.colors['bg_medium']
            
            for child in self.root.winfo_children():
                if isinstance(child, tk.Toplevel) and child.winfo_exists():
                    try:
                        child.configure(bg=dialog_color)
                        
                        try:
                            pywinstyles.change_header_color(child, dialog_header_color)
                        except:
                            pass
                        
                        child.deiconify()
                        child.lift()
                        child.focus_force()
                    except:
                        pass
        except Exception:
            pass

    def force_tray_menu_update(self):
        if hasattr(self, 'tray_icon') and self.tray_icon:
            try:
                self.tray_icon.force_update_menu()
            except Exception:
                pass

    def setup_ui(self):
        self.main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        left_panel_width = scale_size(250, self.scale_factor)
        self.create_left_panel(width=left_panel_width)
        
        content_x = left_panel_width
        content_width = self.window_width - left_panel_width
        content_height = self.window_height
        self.content_panel = tk.Frame(self.main_container, bg=self.colors['bg_dark'])
        self.content_panel.place(x=content_x, y=0, width=content_width, height=content_height)
        self.pages = Pages(self)

    def log_event(self, event_type: str, message: str, mode_name: str = None):
        now = datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d.%m.%Y")
        
        if event_type == "connect" and mode_name:
            log_entry = f"[{date_str} {timestamp}] Mode {mode_name} is connected"
        
        elif event_type == "disconnect" and mode_name:
            log_entry = f"[{date_str} {timestamp}] Disconnected from mode {mode_name}"
        
        elif event_type == "info":
            log_entry = f"[{date_str} {timestamp}] {message}"

        else:
            log_entry = f"[{date_str} {timestamp}] {message}"
        
        try:
            log_file = APPDATA_DIR / "logs.txt"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception:
            pass

    def _schedule_heartbeat(self):
        try:
            if hasattr(self, 'user_stats'):
                self.user_stats.on_launch()
        except Exception:
            pass

        self.root.after(300000, self._schedule_heartbeat)

    def toggle_auto_update(self):
        self._auto_update_enabled = not self._auto_update_enabled
        self.save_settings()
        
        if hasattr(self, 'pages') and hasattr(self.pages, 'settings_page_obj'):
            self.pages.settings_page_obj._update_autoupdate_button()
        
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.update_menu()
            if self.tray_icon.icon:
                self.tray_icon.icon.update_menu()

    def toggle_analytics(self):
        self._analytics_enabled = not self._analytics_enabled
        self.save_settings()
        
        self.user_stats.set_enabled(self._analytics_enabled)
        
        if self._analytics_enabled and not self.user_stats._is_active:
            self.user_stats.start()
        elif not self._analytics_enabled and self.user_stats._is_active:
            self.user_stats.stop()
        
        if hasattr(self, 'pages') and hasattr(self.pages, 'settings_page_obj'):
            self.pages.settings_page_obj._update_analytics_button()
        
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.update_menu()
            if self.tray_icon.icon:
                self.tray_icon.icon.update_menu()

    def update_all_ui(self):
        if hasattr(self, 'pages') and hasattr(self.pages, 'settings_page_obj'):
            self.pages.settings_page_obj.update_buttons()
        
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.update_menu()
            if self.tray_icon.icon:
                self.tray_icon.icon.update_menu()

    def create_left_panel(self, width=250):
        left_panel = tk.Frame(self.main_container, bg=self.colors['bg_medium'], width=width)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)
        
        logo_height = scale_size(140, self.scale_factor)
        logo_frame = tk.Frame(left_panel, bg=self.colors['bg_medium'], height=logo_height)
        logo_frame.pack(fill=tk.X, pady=(scale_size(40, self.scale_factor), scale_size(20, self.scale_factor)))
        logo_frame.pack_propagate(False)
        self.left_panel = left_panel
        
        try:
            icon_path = [PNG_ICON_PATH]
            icon_image = None
            for path in icon_path:
                if path and path.exists():
                    icon_image = tk.PhotoImage(file=str(path))
                    break
            
            if icon_image:
                icon_size = scale_size(120, self.scale_factor)
                if icon_image.width() > 0 and icon_image.height() > 0:
                    resize_ratio = max(icon_image.width() // icon_size, icon_image.height() // icon_size)
                    if resize_ratio > 1:
                        icon_image = icon_image.subsample(resize_ratio, resize_ratio)
                icon_label = tk.Label(logo_frame, image=icon_image, bg=self.colors['bg_medium'], cursor="hand2")
                icon_label.image = icon_image
                icon_label.pack(expand=True, pady=scale_size(10, self.scale_factor))
                icon_label.bind("<Button-1>", lambda e: self.show_settings_page())
                icon_label.bind("<Enter>", lambda e: icon_label.config(cursor="hand2"))
                icon_label.bind("<Leave>", lambda e: icon_label.config(cursor=""))
            else:
                raise Exception(tr('error_icon_not_found'))
        except Exception:
            pass

        nav_buttons = [
            (tr('main_title'), self.show_main_page),
            (tr('service_title'), self.show_service_page),
            (tr('lists_title'), self.show_lists_page),
            (tr('hosts_title'), self.show_hosts_page),
            (tr('logs_title'), self.show_logs_page)
        ]
        
        btn_width = scale_size(220, self.scale_factor)
        btn_height = scale_size(45, self.scale_factor)
        btn_font_size = scale_size(11, self.scale_factor)
        btn_radius = scale_size(10, self.scale_factor)
        padx = scale_size(15, self.scale_factor)
        pady = scale_size(2, self.scale_factor)
        
        for text, command in nav_buttons:
            btn_frame = tk.Frame(left_panel, bg=self.colors['bg_medium'])
            btn_frame.pack(fill=tk.X, pady=pady, padx=padx)
            
            btn = RoundedButton(
                btn_frame,
                text=text,
                command=command,
                width=btn_width, height=btn_height,
                bg=self.colors['bg_light'],
                fg=self.colors['text_secondary'],
                font=("Segoe UI Variable", btn_font_size),
                corner_radius=btn_radius,
                theme_name=self.current_theme
            )

            btn._command = command
            btn.hover_color = self.colors['accent']
            btn.normal_color = self.colors['bg_light']
            btn.update_colors(self.colors['bg_light'], self.colors['text_secondary'], self.colors['accent'])
            btn.pack()
            
            btn.bind("<Enter>", lambda e: btn.config(cursor="hand2"))
            btn.bind("<Leave>", lambda e: btn.config(cursor=""))
        
        separator = tk.Frame(left_panel, bg=self.colors['separator'], height=1)
        separator.pack(fill=tk.X, padx=padx, pady=scale_size(20, self.scale_factor))
        
        self.credit_frame = tk.Frame(left_panel, bg=self.colors['bg_medium'])
        self.credit_frame.pack(side=tk.BOTTOM, pady=(0, scale_size(15, self.scale_factor)), fill=tk.X)

        self.left_status = tk.Label(
            self.credit_frame,
            text="●",
            font=("Segoe UI Variable", scale_size(12, self.scale_factor)),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_medium']
        )
        self.left_status.pack()
        
        version_frame = tk.Frame(self.credit_frame, bg=self.colors['bg_medium'])
        version_frame.pack()

        tk.Label(
            version_frame,
            text=f"v{CURRENT_VERSION} (build {CURRENT_BUILD})",
            font=("Segoe UI Variable", scale_size(8, self.scale_factor)),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_medium']
        ).pack(side=tk.LEFT)
        
        self.credit_label = tk.Label(
            self.credit_frame,
            text="zapret-launcher.ru",
            font=("Segoe UI Variable", scale_size(8, self.scale_factor)),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_medium'],
            cursor="hand2"
        )
        self.credit_label.pack()

        self.credit_label.bind("<Enter>", lambda e: self.credit_label.config(fg=self.colors['accent']))
        self.credit_label.bind("<Leave>", lambda e: self.credit_label.config(fg=self.colors['text_secondary']))
        self.credit_label.bind("<Button-1>", lambda e: self.open_website())

    def show_update_label(self):
        if not getattr(self, '_auto_update_enabled', True):
            return
    
        try:
            if not hasattr(self, 'foundupdates_frame'):
                if hasattr(self, 'credit_frame'):
                    self.foundupdates_frame = tk.Frame(self.credit_frame, bg=self.colors['bg_medium'])
                    
                    self.foundupdates_label = tk.Label(
                        self.foundupdates_frame,
                        text=tr('update_available'),
                        font=("Segoe UI Variable", 8),
                        fg=self.colors['accent_green'],
                        bg=self.colors['bg_medium'],
                        cursor="hand2"
                    )
                    self.foundupdates_label.pack()
                    
                    self.foundupdates_label.bind("<Enter>", lambda e: self.foundupdates_label.config(fg=self.colors['accent_darkgreen']))
                    self.foundupdates_label.bind("<Leave>", lambda e: self.foundupdates_label.config(fg=self.colors['accent_green']))
                    self.foundupdates_label.bind("<Button-1>", lambda e: self.root.after(500, self.install_update))
            else:
                pass
            
            if hasattr(self, 'foundupdates_frame'):
                self.foundupdates_frame.pack(pady=(1, 0))
        except Exception:
            pass

    def hide_update_label(self):
        try:
            if hasattr(self, 'foundupdates_frame'):
                self.foundupdates_frame.pack_forget()
        except Exception:
            pass

    def check_for_updates(self):
        if not getattr(self, '_auto_update_enabled', True):
            self.root.after(0, self.hide_update_label)
            return
    
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'text/plain', 'Connection': 'close'}
            
            buildnumber_url = BUILDNUMBER_URL
            req = urllib.request.Request(buildnumber_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                latest_build = response.read().decode('utf-8').strip()
            
            current_build = CURRENT_BUILD
            need_launcher_update = compare_builds(current_build, latest_build)
            
            if need_launcher_update:
                self.root.after(0, self.show_update_label)
                return
            
            current_zapret_version = self.get_current_zapret_version()
            latest_zapret_version = None
            
            try:
                zapret_version_url = ZAPRET_VERSION_URL
                req_zapret = urllib.request.Request(zapret_version_url, headers=headers)
                
                with urllib.request.urlopen(req_zapret, timeout=10) as response:
                    latest_zapret_version = response.read().decode('utf-8').strip()
                    
            except Exception as e:
                self.log_event("info", f"Failed to check Zapret update: {e}")
                self.root.after(0, self.hide_update_label)
                return
            
            need_zapret_update = False
            if latest_zapret_version and current_zapret_version:
                need_zapret_update = compare_zapret_versions(current_zapret_version, latest_zapret_version)
            
            if need_zapret_update:
                self.root.after(0, self.show_update_label_zapret)
            else:
                self.root.after(0, self.hide_update_label)
                
        except urllib.error.URLError as e:
            self.log_event("info", f"Network error while checking updates: {e}")
            self.root.after(0, self.hide_update_label)
        except Exception as e:
            self.log_event("info", f"Unexpected error checking updates: {e}")
            self.root.after(0, self.hide_update_label)

    def get_current_zapret_version(self) -> str:
        try:
            version_file = ZAPRET_CORE_DIR / "version.txt"
            if version_file.exists():
                return version_file.read_text(encoding='utf-8').strip()
        except Exception:
            pass
        return "0.0"

    def show_update_label_zapret(self):
        if not getattr(self, '_auto_update_enabled', True):
            return
    
        try:
            if not hasattr(self, 'foundupdates_frame_zapret'):
                if hasattr(self, 'credit_frame'):
                    self.foundupdates_frame_zapret = tk.Frame(self.credit_frame, bg=self.colors['bg_medium'])
                    
                    self.foundupdates_label_zapret = tk.Label(
                        self.foundupdates_frame_zapret,
                        text=tr('update_available'),
                        font=("Segoe UI Variable", 8),
                        fg=self.colors['accent_green'],
                        bg=self.colors['bg_medium'],
                        cursor="hand2"
                    )
                    self.foundupdates_label_zapret.pack(pady=(2, 0))
                    
                    self.foundupdates_label_zapret.bind("<Enter>", lambda e: self.foundupdates_label_zapret.config(fg=self.colors['accent_darkgreen']))
                    self.foundupdates_label_zapret.bind("<Leave>", lambda e: self.foundupdates_label_zapret.config(fg=self.colors['accent_green']))
                    self.foundupdates_label_zapret.bind("<Button-1>", lambda e: self.root.after(500, self.install_zapret_update))
            else:
                pass
            
            if hasattr(self, 'foundupdates_frame_zapret'):
                self.foundupdates_frame_zapret.pack(pady=(5, 0))
        except Exception:
            pass

    def install_zapret_update(self):
        try:
            latest_zapret_version = None
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'text/plain', 'Connection': 'close'}
            
            try:
                req_zapret = urllib.request.Request(ZAPRET_VERSION_URL, headers=headers)
                with urllib.request.urlopen(req_zapret, timeout=5) as response:
                    latest_zapret_version = response.read().decode('utf-8').strip()
            except Exception:
                latest_zapret_version = "?"
            
            if latest_zapret_version != "?":
                version_text = f"v{latest_zapret_version}"
            else:
                version_text = tr('update_available')
            
            message = f"{tr('update_available_question')}: {version_text}\n{tr('update_ask_now')}\n\nhttps://zapret-launcher.ru/changelog"
            result = messagebox.askyesno(tr('update_title'), message)
            
            if result:
                self.save_settings()
                
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    exe_path = sys.argv[0]
                
                args = [exe_path, '--update-zapret-only']
                for arg in sys.argv[1:]:
                    if arg not in ['--no-splash', '--from-splash']:
                        args.append(arg)
                
                subprocess.Popen(args)
                self.root.quit()
                self.root.destroy()
                sys.exit(0)
                
        except Exception:
            pass

    def install_update(self):
        try:
            latest_version = None
            latest_build = None
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'text/plain', 'Connection': 'close'}
            
            try:
                req_version = urllib.request.Request(VERSION_URL, headers=headers)
                with urllib.request.urlopen(req_version, timeout=5) as response:
                    latest_version = response.read().decode('utf-8').strip()
            except Exception:
                latest_version = "?"
            
            try:
                req_build = urllib.request.Request(BUILDNUMBER_URL, headers=headers)
                with urllib.request.urlopen(req_build, timeout=5) as response:
                    latest_build = response.read().decode('utf-8').strip()
            except Exception:
                latest_build = "?"
            
            if latest_version != "?" and latest_build != "?":
                version_text = f"v{latest_version} (build {latest_build})"
            elif latest_version != "?":
                version_text = f"v{latest_version}"
            else:
                version_text = tr('update_available')
            
            message = f"{tr('update_available_question')}: {version_text}\n{tr('update_ask_now')}\n\nhttps://zapret-launcher.ru/changelog"
            result = messagebox.askyesno(tr('update_title'), message)
            
            if result:
                self.save_settings()
                
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    exe_path = sys.argv[0]
                
                args = [exe_path]
                for arg in sys.argv[1:]:
                    if arg not in ['--no-splash', '--from-splash']:
                        args.append(arg)
                
                subprocess.Popen(args)
                self.root.quit()
                self.root.destroy()
                sys.exit(0)
                
        except Exception:
            pass

    def start_with_mode(self, mode):
        if self.is_connected:
            return
        
        self._connecting = True
        self.force_tray_menu_update()
        
        try:
            if mode["name"] == tr('mode_zapret_tgproxy'):
                if not self.zapret.available_strategies:
                    messagebox.showerror(tr('error_no_connection'), tr('error_no_strategies'))
                    self._connecting = False
                    self.force_tray_menu_update()
                    return
                
                self._pending_mode = mode
                self.dialogs.show_strategy_selector(mode["name"])
                return
            
            if mode["name"] == "Telegram Proxy":
                self._start_tg_proxy_direct()
                return
            
            if mode["name"] == tr('mode_standard'):
                if not self.zapret.available_strategies:
                    messagebox.showerror(tr('error_no_connection'), tr('error_no_strategies'))
                    self._connecting = False
                    self.force_tray_menu_update()
                    return
                
                self._pending_mode = mode
                self.dialogs.show_strategy_selector(mode["name"])
                return

            self.update_status(tr('status_starting'), self.colors['accent'])
            if hasattr(self, 'connect_btn') and self.connect_btn:
                self.connect_btn.set_enabled(False)
            self.root.update()
            
            if mode.get("tgproxy", False):
                self.tg_proxy.start()
            
            self.is_connected = True
            self.stats.start_session()
            self.start_stats_monitoring()
            
            mode_name = mode["name"]
            if hasattr(self, 'mode_label') and self.mode_label:
                self.mode_label.config(text=mode_name, fg=self.colors['accent_green'])
            self.update_status(f"{tr('status_connected')}", self.colors['accent_green'])
            self.update_ui_state()
            self.save_settings()
            self.update_stats_display()
            self.root.after(500, self.update_tray_icon_state)
            if hasattr(self, 'connect_btn') and self.connect_btn:
                self.connect_btn.set_enabled(True)
            
            self._connecting = False
            self.force_tray_menu_update()
            
        except Exception:
            self._connecting = False
            self.force_tray_menu_update()
            raise

    def _start_tg_proxy_direct(self):
        if self.is_connected:
            return
        
        if not hasattr(self, '_tg_secret') or not self._tg_secret:
            result = messagebox.askyesno(tr('error_secret_not_found'), tr('tg_secret_required_message'))
            if result:
                self._tg_secret = os.urandom(16).hex()
                self.save_settings()
                self.show_notification(tr('notification_copied'), 2000)
                if hasattr(self, 'pages') and hasattr(self.pages, 'settings_page'):
                    self.pages.update_secret_display()
            else:
                self.update_status(tr('status_ready'), self.colors['text_secondary'])
                return
        
        self._do_start_tg_proxy()

    def regenerate_tg_secret(self):
        new_secret = os.urandom(16).hex()
        self._tg_secret = new_secret
        
        self.save_settings()
        self.tg_proxy.set_secret(new_secret)
        proxy_config.secret = new_secret
        
        if self.tg_proxy._running:
            self.tg_proxy.stop()
            time.sleep(1)
            self.tg_proxy.start()
        
        self.log_event("info", f"New secret-key generated: {new_secret[:8]}...")
        
        if hasattr(self, 'pages') and hasattr(self.pages, 'settings_page_obj'):
            self.pages.settings_page_obj.update_secret_display()
        
        if self.tg_fake_tls and self.tg_fake_tls_domain:
            domain_hex = self.tg_fake_tls_domain.encode('ascii').hex()
            link = f"ee{new_secret}{domain_hex}"
            notification_text = tr('notification_updated_secret')
        else:
            link = f"dd{new_secret}"
            notification_text = tr('notification_updated_secret')
        
        self.root.clipboard_clear()
        self.root.clipboard_append(link)
        self.root.update()
        self.show_notification(notification_text, 3000)
        
    def _do_start_tg_proxy(self):
        self.update_status(tr('status_starting'), self.colors['accent'])
        if hasattr(self, 'connect_btn') and self.connect_btn:
            self.connect_btn.set_enabled(False)
        self.root.update()
        
        secret = getattr(self, '_tg_secret', None)
        if not secret:
            secret = os.urandom(16).hex()
            self._tg_secret = secret
            self.save_settings()
        
        self.tg_proxy.set_secret(secret)
        proxy_config.secret = secret
        
        self.log_event("info", f"Starting TG Proxy with secret from config: {secret[:8]}...")
        
        def start_thread():
            try:
                success = self.tg_proxy.start()
                
                if success:
                    if self.tg_proxy.wait_for_start(8):
                        self.root.after(0, lambda: self._on_tg_proxy_started_direct())
                    else:
                        self.root.after(0, lambda: self._on_tg_proxy_failed_direct(tr('error_tgproxy_timeout')))
                else:
                    self.root.after(0, lambda: self._on_tg_proxy_failed_direct(tr('error_tgproxy_start')))
            except Exception as e:
                self.root.after(0, lambda: self._on_tg_proxy_failed_direct(str(e)))
            finally:
                if not self.is_connected:
                    self._connecting = False
                    self.force_tray_menu_update()
        
        threading.Thread(target=start_thread, daemon=True).start()

    def _on_tg_proxy_started_direct(self):
        if not self.is_connected:
            self.is_connected = True
            self.stats.start_session()
            self.start_stats_monitoring()
            
            self.mode_label.config(text="Telegram Proxy", fg=self.colors['accent_green'])
            self.update_status(tr('status_connected'), self.colors['accent_green'])
            self.update_ui_state()
            self.save_settings()
            self.update_stats_display()
            self.log_event("connect", "", "Telegram Proxy")

            if self.tg_fake_tls:
                self.root.after(1000, self.copy_tg_link_to_clipboard)

            if not self._tg_instruction:
                self.root.after(500, self.dialogs.show_tg_proxy_instruction)

            self._connecting = False
            self.force_tray_menu_update()
        
        self.connect_btn.set_enabled(True)
        self.root.after(500, self.update_tray_icon_state)

    def _on_tg_proxy_failed_direct(self, error_msg):
        self.update_status(tr('status_error'), self.colors['accent_red'])
        messagebox.showerror(tr('error_no_connection'), f"{error_msg}")
        if hasattr(self, 'connect_btn') and self.connect_btn:
            self.connect_btn.set_enabled(True)

    def _cancel_strategy_selection(self, dialog):
        dialog.destroy()
        self._connecting = False
        self.force_tray_menu_update()

    def update_stats_display(self):
        if not hasattr(self, 'stats_frame'):
            return
        
        stats = self.stats.get_stats_dict()

        if hasattr(self, 'stats_time_label'):
            self.stats_time_label.config(text=stats['session_time_str'])
        
        if hasattr(self, 'stats_traffic_label'):
            self.stats_traffic_label.config(text=f"⬇ {stats['down_str']}  |  ⬆ {stats['up_str']}")
        
        if hasattr(self, 'stats_total_label'):
            self.stats_total_label.config(text=stats['total_str'])
        
        if hasattr(self, 'stats_speed_up_label'):
            self.stats_speed_up_label.config(text=f"⬆ {stats['speed_up_str']}")
        if hasattr(self, 'stats_speed_down_label'):
            self.stats_speed_down_label.config(text=f"⬇ {stats['speed_down_str']}")

        if hasattr(self, 'tray_icon') and self.tray_icon:
            try:
                self.tray_icon.update_tooltip()
            except:
                pass

        if hasattr(self, 'tray_icon') and self.tray_icon:
            try:
                self.tray_icon.update_icon_state()
            except:
                pass

    def _update_rtt(self):
        try:
            if hasattr(self, 'stats_rtt_label') and self.stats_rtt_label.winfo_exists():
                rtt = self.measure_rtt()
                if rtt > 0:
                    self.stats_rtt_label.config(text=f"{rtt:.0f} {tr('stats_rtt_ms')}", fg=self.colors['accent'])
                else:
                    self.stats_rtt_label.config(text="-- ms", fg=self.colors['text_secondary'])
        except (tk.TclError, AttributeError):
            return
        self.rtt_timer_id = self.root.after(self.rtt_update_interval, self._update_rtt)

    def start_rtt_monitoring(self):
        self.rtt_timer_id = self.root.after(1000, self._update_rtt)

    def stop_rtt_monitoring(self):
        if self.rtt_timer_id:
            self.root.after_cancel(self.rtt_timer_id)
            self.rtt_timer_id = None

    def measure_rtt(self) -> float:
        current_time = time.time()

        if (hasattr(self, '_cached_rtt_time') and hasattr(self, '_cached_rtt') and self._cached_rtt > 0 and (current_time - self._cached_rtt_time) < self.rtt_cache_duration):
            return self._cached_rtt

        try:
            result = subprocess.run(['ping', '-n', '1', '8.8.8.8'], capture_output=True, text=True, encoding='cp866', creationflags=subprocess.CREATE_NO_WINDOW, timeout=3)
            rtt = -1
            
            if result.returncode == 0:
                output = result.stdout
                
                match = re.search(r'(?:время|time)[=<>]\s*(\d+)\s*мс', output, re.IGNORECASE)
                if match:
                    rtt = float(match.group(1))
                else:
                    match = re.search(r'time[=<>](\d+)ms', output, re.IGNORECASE)
                    if match:
                        rtt = float(match.group(1))
                    else:
                        match = re.search(r'(\d+)\s*мс', output, re.IGNORECASE)
                        if match:
                            rtt = float(match.group(1))
            
            if rtt > 0:
                self._cached_rtt = rtt
                self._cached_rtt_time = current_time
            return rtt
            
        except Exception:
            return -1

    def start_stats_monitoring(self):
        self.stop_stats_monitoring()
        self.start_rtt_monitoring()
        
        if self.is_connected:
            self._schedule_stats_update()

    def stop_stats_monitoring(self):
        if self.update_timer_id:
            self.root.after_cancel(self.update_timer_id)
            self.update_timer_id = None

    def _schedule_stats_update(self):
        if not self.is_connected:
            if self.update_interval is None:
                return
                
            if not self.root.winfo_viewable():
                interval = 5000
            elif self.update_interval == 0:
                interval = 1000
            elif self.update_interval > 0:
                interval = int(self.update_interval * 1000)
            else:
                interval = 1000
            
            self.update_timer_id = self.root.after(interval, self._schedule_stats_update)
            return
        
        self.stats.update_speed()
        self.update_stats_display()

        if self.update_interval is None:
            return
        
        if not self.root.winfo_viewable():
            interval = 5000
        elif self.update_interval == 0:
            interval = 1000
        elif self.update_interval > 0:
            interval = max(1000, int(self.update_interval * 1000))
        else:
            interval = 1000
        
        self.update_timer_id = self.root.after(interval, self._schedule_stats_update)

    def show_notification(self, message, duration=2000):
        try:
            if not self.root.winfo_viewable():
                return
            
            if hasattr(self, '_current_notification') and self._current_notification:
                try:
                    self._current_notification.destroy()
                except:
                    pass

            notif_width = scale_size(280, self.scale_factor)
            notif_height = scale_size(40, self.scale_factor)
            notif_font_size = scale_size(10, self.scale_factor)
            
            notification = tk.Toplevel(self.root)
            notification.overrideredirect(True)
            notification.configure(bg=self.colors['bg_medium'])
            notification._is_alive = True

            self._current_notification = notification

            try:
                notification.attributes('-topmost', True)
            except:
                pass
            
            def update_notification_position():
                if notification and notification.winfo_exists() and notification._is_alive:
                    try:
                        x = self.root.winfo_x() + self.root.winfo_width() - notif_width - scale_size(30, self.scale_factor)
                        y = self.root.winfo_y() + scale_size(50, self.scale_factor)
                        notification.geometry(f"{notif_width}x{notif_height}+{x}+{y}")
                    except:
                        pass
            
            def on_root_configure(event=None):
                update_notification_position()
            
            self.root.bind('<Configure>', on_root_configure)
            
            def cleanup():
                try:
                    if notification and notification.winfo_exists():
                        notification._is_alive = False
                        notification.destroy()
                except:
                    pass
                try:
                    self.root.unbind('<Configure>', on_root_configure)
                except:
                    pass
                if self._current_notification == notification:
                    self._current_notification = None
            
            def on_iconify():
                if notification and notification.winfo_exists():
                    try:
                        notification.withdraw()
                    except:
                        pass

            def on_deiconify():
                if notification and notification.winfo_exists() and notification._is_alive:
                    try:
                        notification.deiconify()
                        update_notification_position()
                    except:
                        pass
            
            self.root.bind('<Unmap>', lambda e: on_iconify())
            self.root.bind('<Map>', lambda e: on_deiconify())
            
            def check_window_state():
                if notification and notification.winfo_exists() and notification._is_alive:
                    try:
                        is_active = self.root.focus_displayof() is not None
                        is_visible = self.root.winfo_viewable()
                        is_iconic = self.root.state() == 'iconic'
                        
                        if not is_visible or is_iconic or (not is_active and is_visible):
                            if notification.winfo_viewable():
                                notification.withdraw()
                        else:
                            if not notification.winfo_viewable():
                                notification.deiconify()
                                update_notification_position()
                                notification.lift()
                    except:
                        pass
                    notification.after(10, check_window_state)
            
            try:
                notification.attributes('-alpha', 0.95)
            except:
                pass
            
            x = self.root.winfo_x() + self.root.winfo_width() - 310
            y = self.root.winfo_y() + 50
            notification.geometry(f"280x40+{x}+{y}")
            
            frame = tk.Frame(notification, bg=self.colors['accent'], padx=1, pady=1)
            frame.pack(fill=tk.BOTH, expand=True)
            
            inner = tk.Frame(frame, bg=self.colors['bg_medium'])
            inner.pack(fill=tk.BOTH, expand=True)
            
            label = tk.Label(inner, text=message, 
                        font=("Segoe UI Variable", notif_font_size),
                        fg=self.colors['text_primary'], 
                        bg=self.colors['bg_medium'],
                        padx=12, pady=8)
            label.pack()
            
            notification.lift()
            notification.attributes('-alpha', 0.0)
            
            check_window_state()
            
            def fade_in(alpha=0.0):
                if not self.root.winfo_viewable():
                    cleanup()
                    return
                if alpha < 0.95:
                    alpha += 0.1
                    try:
                        if notification and notification.winfo_exists() and notification._is_alive:
                            notification.attributes('-alpha', alpha)
                            notification.after(30, lambda: fade_in(alpha))
                    except:
                        cleanup()
                else:
                    notification.after(duration, fade_out)
            
            def fade_out(alpha=0.95):
                if alpha > 0.0:
                    alpha -= 0.1
                    try:
                        if notification and notification.winfo_exists() and notification._is_alive:
                            notification.attributes('-alpha', alpha)
                            notification.after(30, lambda: fade_out(alpha))
                    except:
                        cleanup()
                else:
                    cleanup()
            
            fade_in()
            
            def on_notification_click(event=None):
                cleanup()
            
            notification.bind("<Button-1>", on_notification_click)
            
        except Exception:
            pass

    def load_settings_data(self):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def set_autostart(self, enabled):
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            if enabled:
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    exe_path = sys.argv[0]
                
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "Zapret Launcher", 0, winreg.REG_SZ, f'"{exe_path}" --from-splash')
                
                self.log_event("info", f"Auto-start added to registry: {exe_path}")
                return True
            else:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key, "Zapret Launcher")
                    self.log_event("info", "Auto-start removed from registry")
                except FileNotFoundError:
                    pass
                return True
                
        except Exception as e:
            self.log_event("info", f"Error setting auto-start: {e}")
            return False

    def check_autostart_status(self):
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "Zapret Launcher")
                return bool(value)
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def open_appdata_folder(self):
        try:
            os.startfile(APPDATA_DIR)
        except Exception:
            pass

    def update_widget_colors(self, widget):
        try:
            widget_type = type(widget)
            
            if widget_type == tk.Frame:
                widget.configure(bg=self.colors['bg_dark'])
            elif widget_type == tk.Label:
                current_fg = widget.cget('fg')
                accent_colors = [self.colors['accent'], self.colors['accent_green'], 
                            self.colors['accent_red'], self.colors['accent_hover']]
                if current_fg and current_fg not in accent_colors:
                    widget.configure(fg=self.colors['text_secondary'])
                widget.configure(bg=self.colors['bg_dark'])
            elif widget_type == tk.Canvas:
                widget.configure(bg=self.colors['bg_dark'])
            elif widget_type == ttk.Combobox:
                widget.configure(background=self.colors['bg_light'])
            elif widget_type == tk.Text:
                widget.configure(bg=self.colors['bg_dark'], fg=self.colors['text_primary'])
            elif hasattr(widget, 'update_colors'):
                widget.update_colors(self.colors['button_bg'], self.colors['text_secondary'], self.colors['accent_hover'])
            elif hasattr(widget, 'configure') and 'bg' in widget.keys():
                try:
                    widget.configure(bg=self.colors['bg_dark'])
                except:
                    pass
            
            for child in widget.winfo_children():
                self.update_widget_colors(child)
        except Exception:
            pass

    def toggle_autostart(self):
        current = self.check_autostart_status()
        new_state = not current
        
        if self.set_autostart(new_state):
            if new_state:
                messagebox.showinfo(tr('information_desc'), tr('autostart_enabled'))
            else:
                messagebox.showinfo(tr('information_desc'), tr('autostart_disabled'))
        else:
            messagebox.showerror(tr('error_occurred'), tr('autostart_error'))

    def open_website(self):
        webbrowser.open("https://zapret-launcher.ru")

    def check_initial_status(self):
        if not check_zapret_folder():
            return
        
        if self.zapret.is_winws_running():
            self.is_connected = True

            if hasattr(self, 'mode_label') and self.mode_label:
                self.mode_label.config(text=tr('mode_standard'), fg=self.colors['accent_green'])

            self.update_status(tr('status_connected'), self.colors['accent_green'])
            self.update_ui_state()
            if hasattr(self, 'tray_icon'):
                self.tray_icon.update_menu()
            
            if self.is_connected and not self.stats.is_monitoring:
                self.stats.start_session()
                self.start_stats_monitoring()
                self.update_stats_display()

    def update_status(self, text, color=None):
        if color is None:
            color = self.colors['accent_green'] if self.is_connected else self.colors['text_secondary']
        
        if hasattr(self, 'main_status') and self.main_status:
            self.main_status.config(text=text, fg=color)
        
        if hasattr(self, 'left_status') and self.left_status:
            self.left_status.config(fg=color)

    def update_ui_state(self):
        try:
            if hasattr(self, 'connect_btn') and self.connect_btn:
                if not self.connect_btn.winfo_exists():
                    return
                    
                if self.is_connected:
                    self.connect_btn.set_text(tr('button_disconnect'))
                    self.connect_btn.normal_color = '#3D3D45'
                    self.connect_btn.hover_color = self.colors['accent']
                    self.connect_btn.update_colors('#3D3D45', '#FFFFFF', self.colors['accent'])
                else:
                    self.connect_btn.set_text(tr('button_connect'))
                    self.connect_btn.normal_color = self.colors['accent']
                    self.connect_btn.hover_color = '#3D3D45'
                    self.connect_btn.update_colors(self.colors['accent'], '#FFFFFF', '#3D3D45')
        except (tk.TclError, AttributeError, RuntimeError):
            pass
        
        if hasattr(self, 'tray_icon') and self.tray_icon:
            try:
                self.tray_icon.update_menu()
            except:
                pass

    def toggle_connection(self):
        if self._connecting:
            return
        
        if self.is_connected:
            self.disconnect()
        else:
            self._connecting = True
            try:
                if self.check_vpn_before_connect():
                    self.dialogs.show_mode_selector()
                    self._connecting = False
                    if hasattr(self, 'tray_icon') and self.tray_icon:
                        self.tray_icon.force_update_menu()

            except Exception:
                self._connecting = False
        self.root.after(500, self.update_tray_icon_state)

    def connect(self):
        strategy = self.strategy_var.get()
        if not strategy:
            messagebox.showerror(tr('information_desc'), tr('error_select_strategy'))
            return
        
        self.update_status(tr('status_starting'), self.colors['accent'])
        self.connect_btn.set_enabled(False)
        self.root.update()
        
        def start_thread():
            success, msg = self.zapret.run_strategy(strategy)
            
            if success:
                self.current_strategy = strategy
                self.is_connected = True
                
                if self.tgws_var.get():
                    self.tg_proxy.start()
                    time.sleep(0.5)
                
                self.stats.start_session()
                self.root.after(0, lambda: self._on_connect_success(strategy, msg))
            else:
                self.root.after(0, lambda: self._on_connect_failed(msg))
        
        threading.Thread(target=start_thread, daemon=True).start()

    def _on_connect_success(self, strategy, msg):
        self.update_status(f"{tr('status_connected')}", self.colors['accent_green'])
        self.update_ui_state()
        self.save_settings()
        self.start_stats_monitoring()
        self.update_stats_display()
        if hasattr(self, 'connect_btn') and self.connect_btn:
            self.connect_btn.set_enabled(True)

        self.update_tray_icon_state()

        try:
            if hasattr(self, 'user_stats'):
                self.user_stats.on_connect()
        except Exception:
            pass

        mode_name = strategy.replace(".bat", "").replace("general", "").strip() or "Стандартный"
        self.log_event("connect", "", mode_name)

        self._connecting = False
        self.force_tray_menu_update()

    def _on_connect_failed(self, msg):
        self.update_status(tr('status_error'), self.colors['accent_red'])
        messagebox.showerror(tr('error_startup'), msg)
        if hasattr(self, 'connect_btn') and self.connect_btn:
            self.connect_btn.set_enabled(True)

        self._connecting = False
        self.force_tray_menu_update()

    def disconnect(self):
        if not self.is_connected and not self.zapret.is_winws_running():
            return
        
        self._disconnecting = True
        self.force_tray_menu_update()
        
        if self.mode_label and hasattr(self.mode_label, 'cget'):
            current_mode = self.mode_label.cget('text')
            if current_mode and current_mode != tr('mode_not_selected'):
                self.log_event("disconnect", "", current_mode)
            
        self.update_status(tr('status_disconnecting'), self.colors['accent'])
        if hasattr(self, 'connect_btn') and self.connect_btn:
            self.connect_btn.set_enabled(False)
        self.root.update()
        
        def stop_all():
            try:
                if hasattr(self, 'tg_proxy') and self.tg_proxy:
                    try:
                        self.tg_proxy.stop()
                    except Exception:
                        pass
                    time.sleep(1.5)
                
                try:
                    self.zapret.stop_current_strategy()
                except Exception:
                    pass
                
                time.sleep(0.5)
                
                try:
                    subprocess.run(['taskkill', '/F', '/IM', 'winws.exe'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                except:
                    pass
                
                try:
                    self._stop_windivert_service()
                except:
                    pass
                
                try:
                    self.stats.end_session()
                except:
                    pass
                
                self.is_connected = False
                self._disconnecting = False
                self.root.after(0, self.finish_disconnect)
                
            except Exception:
                self.is_connected = False
                self._disconnecting = False
                self.root.after(0, self.finish_disconnect)
        
        threading.Thread(target=stop_all, daemon=True).start()

    def finish_disconnect(self):
        try:
            if hasattr(self, 'mode_label') and self.mode_label and self.mode_label.winfo_exists():
                self.mode_label.config(text=tr('mode_not_selected'), fg=self.colors['text_secondary'])
            self.update_status(tr('status_ready'), self.colors['text_secondary'])

            self.stats = StatsMonitor()
            self.stats_update_id = None

            if hasattr(self, 'stats_time_label') and self.stats_time_label:
                self.stats_time_label.config(text="00:00:00")
            if hasattr(self, 'stats_traffic_label') and self.stats_traffic_label:
                self.stats_traffic_label.config(text="⬇ 0 B  |  ⬆ 0 B")
            if hasattr(self, 'stats_total_label') and self.stats_total_label:
                self.stats_total_label.config(text="0 B")
            if hasattr(self, 'stats_speed_up_label') and self.stats_speed_up_label:
                self.stats_speed_up_label.config(text="⬆ 0 B/s")
            if hasattr(self, 'stats_speed_down_label') and self.stats_speed_down_label:
                self.stats_speed_down_label.config(text="⬇ 0 B/s")
            if hasattr(self, 'stats_rtt_label') and self.stats_rtt_label:
                self.stats_rtt_label.config(text="-- ms", fg=self.colors['text_secondary'])

            self.stop_stats_monitoring()
            self.stop_rtt_monitoring()
            
            def update_button():
                try:
                    if hasattr(self, 'connect_btn') and self.connect_btn:
                        if self.connect_btn.winfo_exists():
                            self.connect_btn.set_enabled(True)
                            self.connect_btn.set_text(tr('button_connect'))
                            self.connect_btn.normal_color = self.colors['accent']
                            self.connect_btn.hover_color = '#3D3D45'
                            self.connect_btn.update_colors(self.colors['accent'], '#FFFFFF', '#3D3D45')
                except:
                    pass
            
            self.root.after(100, update_button)

            if hasattr(self, 'tray_icon') and self.tray_icon:
                try:
                    self.tray_icon.update_menu()
                except:
                    pass
            
            self.update_tray_icon_state()
            self._disconnecting = False
            self.force_tray_menu_update()
        except Exception:
            self._disconnecting = False
            pass

    def run_service_command(self, command):
        if not check_zapret_folder():
            return
        
        success, result = self.zapret.run_service_command(command)
        if success:
            messagebox.showinfo(tr('success'), result)
        else:
            messagebox.showerror(tr('error_occurred'), result)

    def ensure_appdata_dir(self):
        try:
            APPDATA_DIR.mkdir(parents=True, exist_ok=True)
        except:
            pass

    def toggle_vpn_detection(self):
        current = getattr(self, '_show_vpn_detection', False)
        new_state = not current
        self._show_vpn_detection = new_state
        self.save_settings()
        
        if new_state:
            self.show_notification(tr('dialog_enabled'), 2000)
            self.log_event("info", "VPN detection enabled")
        else:
            self.show_notification(tr('dialog_disabled'), 2000)
            self.log_event("info", "VPN detection disabled")

    def toggle_hide_duplicates_warning(self):
        current = getattr(self, '_hide_duplicates_warning', False)
        new_state = not current
        self._hide_duplicates_warning = new_state
        self.save_settings()
        
        if new_state:
            self.show_notification(tr('dialog_disabled'), 2000)
            self.log_event("info", "Duplicates warning hidden")
        else:
            self.show_notification(tr('dialog_enabled'), 2000)
            self.log_event("info", "Duplicates warning shown")

    def _stop_windivert_service(self):
        try:
            result = subprocess.run(['sc', 'query', 'WinDivert'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            
            if 'RUNNING' in result.stdout:
                subprocess.run(['sc', 'stop', 'WinDivert'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
                time.sleep(2)
                
                verify = subprocess.run(['sc', 'query', 'WinDivert'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
                return 'RUNNING' not in verify.stdout
            else:
                return True   
        except (subprocess.TimeoutExpired, Exception):
            return False

    def load_settings(self):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    saved_strategy = data.get('current_strategy')
                    if saved_strategy and saved_strategy in self.zapret.available_strategies:
                        self.current_strategy = saved_strategy
                        self.strategy_var.set(saved_strategy)
                    
                    autostart_enabled = data.get('autostart_enabled', False)
                    if autostart_enabled != self.check_autostart_status():
                        self.set_autostart(autostart_enabled)
    
                    self._tg_instruction = data.get('tg_instruction', False)
                    self._tg_secret = data.get('tg_secret', None)

                    self.tg_host = data.get('tg_host', TG_HOST)
                    self.tg_port = data.get('tg_port', TG_PORT)
                    self.tg_fake_tls = data.get('tg_fake_tls', TG_FAKE_TLS)
                    self.tg_fake_tls_domain = data.get('tg_fake_tls_domain', TG_FAKE_TLS_DOMAIN)

                    self._show_vpn_detection = data.get('show_vpn_detection', False)
                    self._hide_duplicates_warning = data.get('hide_duplicates_warning', False)

                    self._auto_update_enabled = data.get('auto_update_enabled', True)
                    self._analytics_enabled = data.get('analytics_enabled', True)
                    self.user_stats.set_enabled(self._analytics_enabled)
                    
                    if self._analytics_enabled and not self.user_stats._is_active:
                        self.user_stats.start()
                    elif not self._analytics_enabled and self.user_stats._is_active:
                        self.user_stats.stop()

                    saved_theme = data.get('theme', 'Default')
                    if saved_theme in get_theme_names():
                        self.current_theme = saved_theme
                    else:
                        self.current_theme = 'Default'

                    if not self._tg_secret:
                        self._tg_secret = os.urandom(16).hex()
                        self.save_settings()
                        
        except Exception as e:
            self.log_event("info", f"Failed to load settings: {e}")
            self.log_event("info", "New secret key has been generated (first run)")
            self._tg_secret = os.urandom(16).hex()
            self.current_theme = 'Default'
            self.tg_host = TG_HOST
            self.tg_port = TG_PORT
            self.tg_fake_tls = TG_FAKE_TLS
            self.tg_fake_tls_domain = TG_FAKE_TLS_DOMAIN
            self._show_vpn_detection = True
            self._hide_duplicates_warning = False
            self._analytics_enabled = False
            self.user_stats.set_enabled(False)
            self.user_stats.start()

    def save_settings(self):
        try:
            settings = {
                'current_strategy': self.current_strategy,
                'autostart_enabled': self.check_autostart_status(),
                'tg_instruction': getattr(self, '_tg_instruction', False),
                'show_vpn_detection': getattr(self, '_show_vpn_detection', False),
                'hide_duplicates_warning': getattr(self, '_hide_duplicates_warning', False),
                'auto_update_enabled': getattr(self, '_auto_update_enabled', True),
                'analytics_enabled': getattr(self, '_analytics_enabled', True),
                'language': self.languages.get_current_language(),
                'tg_secret': getattr(self, '_tg_secret', None),
                'theme': self.current_theme,
                'tg_host': getattr(self, 'tg_host', TG_HOST),
                'tg_port': getattr(self, 'tg_port', TG_PORT),
                'tg_fake_tls': getattr(self, 'tg_fake_tls', TG_FAKE_TLS),
                'tg_fake_tls_domain': getattr(self, 'tg_fake_tls_domain', TG_FAKE_TLS_DOMAIN),
            }
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except:
            pass

    def show_main_page(self):
        self.pages.show_page_with_animation("main")
        
    def show_service_page(self):
        self.pages.show_page_with_animation("service")
        
    def show_lists_page(self):
        self.pages.show_page_with_animation("lists")

    def show_settings_page(self):
        self.pages.show_page_with_animation("settings")

    def show_hosts_page(self):
            self.pages.show_page_with_animation("hosts")

    def show_logs_page(self):
        self.pages.show_page_with_animation("logs")

    def check_lists_for_duplicates(self):
        if getattr(self, '_hide_duplicates_warning', False):
            return
        
        try:
            lists_dir = LISTS_DIR
            has_duplicates, summary = check_lists_for_duplicates(lists_dir)
            
            if has_duplicates:
                self.root.after(200, lambda: self.dialogs.show_duplicates_dialog(summary))
        except Exception as e:
            self.log_event("info", f"Failed to check lists for duplicates: {e}")

    def copy_tg_link_to_clipboard(self):
        secret = getattr(self, '_tg_secret', '')
        fake_tls = getattr(self, 'tg_fake_tls', False)
        fake_tls_domain = getattr(self, 'tg_fake_tls_domain', '')
        
        if not secret:
            return
        
        if fake_tls and fake_tls_domain:
            domain_hex = fake_tls_domain.encode('ascii').hex()
            link = f"ee{secret}{domain_hex}"
        else:
            link = f"{secret}"
        
        self.root.clipboard_clear()
        self.root.clipboard_append(link)
        self.root.update()
        self.log_event("info", f"Proxy secret-key with fake tls copied to clipboard")

    def is_any_connection_active(self):
        return self.is_connected or self.zapret.is_winws_running() or (hasattr(self, 'tg_proxy') and self.tg_proxy.is_running)

    def setup_scrollbar_style(self):
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure(
            "Custom.Vertical.TScrollbar",
            background=self.colors['bg_light'],
            troughcolor=self.colors['bg_dark'],
            bordercolor=self.colors['bg_dark'],
            arrowcolor=self.colors['text_secondary'],
            lightcolor=self.colors['bg_light'],
            darkcolor=self.colors['bg_light'],
            relief="flat"
        )
        
        style.map(
            "Custom.Vertical.TScrollbar",
            background=[
                ('pressed', self.colors['accent']),
                ('active', self.colors['accent_hover']),
                ('!active', self.colors['bg_light'])
            ],
            arrowcolor=[
                ('pressed', self.colors['text_primary']),
                ('active', self.colors['text_primary']),
                ('!active', self.colors['text_secondary'])
            ]
        )
        
        style.configure(
            "Custom.Horizontal.TScrollbar",
            background=self.colors['bg_light'],
            troughcolor=self.colors['bg_dark'],
            bordercolor=self.colors['bg_dark'],
            arrowcolor=self.colors['text_secondary'],
            lightcolor=self.colors['bg_light'],
            darkcolor=self.colors['bg_light'],
            relief="flat"
        )
        
        style.map(
            "Custom.Horizontal.TScrollbar",
            background=[
                ('pressed', self.colors['accent']),
                ('active', self.colors['accent_hover']),
                ('!active', self.colors['bg_light'])
            ],
            arrowcolor=[
                ('pressed', self.colors['text_primary']),
                ('active', self.colors['text_primary']),
                ('!active', self.colors['text_secondary'])
            ]
        )

    def check_vpn_before_connect(self):
        if not getattr(self, '_show_vpn_detection', False):
            return True
        
        try:
            vpn_keywords = [
                'openvpn', 'wireguard', 'protonvpn', 'nordvpn', 'expressvpn',
                'surfshark', 'cyberghost', 'ipvanish', 'tunnelbear', 'hotspotshield',
                'windscribe', 'vyprvpn', 'privateinternetaccess', 'pia', 'mullvad',
                'ivpn', 'airvpn', 'perfectprivacy', 'zenmate', 'hidester',
                'slickvpn', 'fastestvpn', 'buffered', 'vpn.ac', 'torguard',
                'vpnunlimited', 'vpngate', 'planetvpn', 'itopvpn', 'bebravpn',
                'softether', 'v2ray', 'shadowsocks', 'trojan', 'xray', 'naiveproxy',
                'hysteria', 'tuic', 'wireguard-go', 'wg-quick', 'openconnect',
                'anyconnect', 'forticlient', 'globalprotect', 'pulse secure', 'cisco',
                'ipsec', 'ikev2', 'l2tp', 'pptp', 'sstp', 'proxifier', 'proxycap',
                'sockscap', 'widecap', 'proxychains', 'v2rayN', 'v2rayng', 'nekoray',
                'nekobox', 'sing-box','clash-verge', 'clash.meta', 'mihomo',
                'hysteria.exe', 'tuic.exe', 'naive.exe', 'multilogin', 'gologin',
                'incogniton', 'adspower', 'octobrowser', 'hidemyacc', 'kameleo',
                'vpnkit', 'vpnagent', 'vpnservice', 'vpnclient', 'vpn.exe',
                'openvpn.exe', 'wireguard.exe', 'protonvpn.exe', 'nordvpn.exe',
                'expressvpn.exe', 'surfshark.exe', 'mullvad.exe', 'pia.exe',
                'tunnelbear.exe', 'windscribe.exe', 'cyberghost.exe', 'ovpn',
                '--vpn', '--proxy', 'vpn_', '_vpn', 'vpn-', '-vpn', 'openvpnserv', 
                'vpnui', 'vpnmgr', 'vpngui', 'openvpnas', 'ovpntray', 'ovpnadmin', 
                'hide.me', 'hideme', 'privatevpn', 'ovpn.com', 'oceanvpn', 'fastvpn', 
                'securevpn', 'supervpn', 'freevpn', 'betternet', 'hotspot', 'protect',
                'vpnhub', 'vpnarea', 'seed4me', 'vpnproxy', 'zenvpn', 'vpnzone',
                'surfeasy', 'ibvpn', 'leapvpn', 'ghostvpn', 'vpnbook', 'vpnexpress',
                'goosevpn', 'xvpn', 'vpnon', 'vpnoff', 'vpn', 'proxy',
                'bebra.exe', 'bebravpn.exe', 'amneziawg', 'surfsharkvpn', 'vpnify'
            ]
            
            has_vpn = False
            detected_processes = []
            
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                    
                    skip_processes = [
                        'svchost.exe', 'textinput.exe', 'explorer.exe', 'aggregatorhost.exe', 
                        'taskhost.exe', 'dwm.exe', 'csrss.exe', 'winlogon.exe', 'services.exe', 
                        'lsass.exe', 'wininit.exe', 'spoolsv.exe', 'searchindexer.exe', 
                        'wmpnetwk.exe', 'system', 'system idle process', 'vedetector.exe'
                    ]
                    
                    if any(skip in proc_name for skip in skip_processes):
                        continue
                    
                    for keyword in vpn_keywords:
                        if keyword in proc_name:
                            has_vpn = True
                            detected_processes.append(proc_name)
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if has_vpn:
                vpn_data = {'vpn_detected': True, 'vpn_processes': detected_processes, 'vpn_interfaces': []}
                self.dialogs.show_vpn_detected_dialog(vpn_data, self._show_mode_selector_after_vpn)
                return False
            return True
            
        except Exception as e:
            self.log_event("info", f"VPN check error: {e}")
            return True
        
    def _show_mode_selector_after_vpn(self):
        self._connecting = False
        self.dialogs.show_mode_selector()

    def _start_tg_proxy_mode(self, dialog, dont_show=False):
        if dialog:
            dialog.destroy()
        
        if dont_show:
            self._tg_instruction = True
            self.save_settings()
        
        self._do_start_tg_proxy()

    def _cancel_tg_proxy_mode(self, dialog, dont_show=False):
        if dialog:
            dialog.destroy()
        
        if dont_show:
            self._tg_instruction = True
            self.save_settings()
        
        if not self.is_connected:
            self.update_status(tr('status_ready'), self.colors['text_secondary'])
            if hasattr(self, 'connect_btn') and self.connect_btn:
                self.connect_btn.set_enabled(True)
        else:
            pass
        
    def _on_combined_start_success(self, mode_name):
        if hasattr(self, 'mode_label') and self.mode_label:
            self.mode_label.config(text=mode_name, fg=self.colors['accent_green'])

        self.update_status(f"{tr('status_connected')}", self.colors['accent_green'])
        self.update_ui_state()
        self.save_settings()
        self.update_stats_display()

        if hasattr(self, 'connect_btn') and self.connect_btn:
            self.connect_btn.set_enabled(True)

        if self.tg_fake_tls:
            self.root.after(1000, self.copy_tg_link_to_clipboard)

        if not self._tg_instruction:
            self.root.after(500, self.dialogs.show_tg_proxy_instruction)

        self.update_tray_icon_state()
        self._connecting = False
        self.force_tray_menu_update()
        self.log_event("connect", "", mode_name)

    def _on_combined_start_failed(self, error_msg):
        self.update_status(tr('status_error'), self.colors['accent_red'])
        messagebox.showerror(tr('error_startup'), f"{tr('error_startup')}: {error_msg}")
        if hasattr(self, 'connect_btn') and self.connect_btn:
            self.connect_btn.set_enabled(True)

        if hasattr(self, 'tg_proxy') and self.tg_proxy:
            self.tg_proxy.stop()
    
    def start_update_checker(self):
        self.stop_update_checker()
        self._schedule_update_check()
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.start_update_checker()

    def stop_update_checker(self):
        if hasattr(self, 'update_check_timer_id') and self.update_check_timer_id:
            try:
                self.root.after_cancel(self.update_check_timer_id)
            except:
                pass
            self.update_check_timer_id = None

    def _schedule_update_check(self):
        interval = CHECK_UPDATES_INTERVAL
        self.update_check_timer_id = self.root.after(interval, self._do_update_check)

    def _do_update_check(self):
        threading.Thread(target=self.check_for_updates, daemon=True).start()
        self._schedule_update_check()

    def load_logs(self) -> list:
        logs = []
        log_file = APPDATA_DIR / "logs.txt"
        
        try:
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = f.readlines()
        except Exception:
            pass
        return logs
    
    def clear_logs(self):
        log_file = APPDATA_DIR / "logs.txt"
        try:
            if log_file.exists():
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write("")
        except Exception:
            pass

if __name__ == "__main__":
    set_dpi_awareness()
    mutex_name = "ZapretLauncher_SingleInstance"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = ctypes.windll.kernel32.GetLastError()
    
    if last_error == 183:
        hwnd = ctypes.windll.user32.FindWindowW(None, "Zapret Launcher")
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 5)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0002 | 0x0001)
            
            try:
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x00080000
                LWA_ALPHA = 0x00000002
                
                current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                
                if current_style & WS_EX_LAYERED:
                    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA)
                    ctypes.windll.user32.RedrawWindow(hwnd, None, None, 0x0100)
                else:
                    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_style | WS_EX_LAYERED)
                    
                    for alpha in range(0, 256, 30):
                        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)
                        time.sleep(0.005)
                    
                    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA)
                
            except Exception:
                ctypes.windll.user32.ShowWindow(hwnd, 5)
                ctypes.windll.user32.SetForegroundWindow(hwnd)
        
        sys.exit(0)

    auto_start = '--auto-start' in sys.argv
    
    if auto_start:
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "Zapret Launcher")
                if not value:
                    sys.exit(0)
        except:
            sys.exit(0)
    
    if not is_admin():
        if auto_start:
            run_as_admin()
            sys.exit(0)
        else:
            result = messagebox.askyesno("Zapret Launcher", tr('dialog_admin_message'))
            if result:
                run_as_admin()
            else:
                messagebox.showerror(tr('error_no_connection'), tr('dialog_no_connection'))
                sys.exit(1)

    zapret_version = "0.0"
    try:
        version_file = APPDATA_DIR / "zapret_core" / "version.txt"
        if version_file.exists():
            zapret_version = version_file.read_text(encoding='utf-8').strip()
    except Exception:
        pass

    current_theme = 'Default'
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                current_theme = data.get('theme', 'Default')
    except Exception:
        pass
    
    auto_update_enabled = True
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                auto_update_enabled = data.get('auto_update_enabled', True)
    except Exception:
        pass
    
    show_splash = '--no-splash' not in sys.argv and not auto_start
    
    if show_splash:
        splash = SplashWindow(
            theme=current_theme, 
            current_version=CURRENT_VERSION, 
            current_build=CURRENT_BUILD,
            zapret_version=zapret_version,
            auto_update_enabled=auto_update_enabled
        )
        splash.start()
    else:
        root = tk.Tk()
        app = ZapretLauncher(root)
        root.mainloop()
        
        if mutex:
            ctypes.windll.kernel32.CloseHandle(mutex)
