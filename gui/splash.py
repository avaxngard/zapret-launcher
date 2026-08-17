# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk
from utils.languages import tr
from typing import Optional
from gui.theme import get_theme
from utils.version import compare_builds, compare_zapret_versions
from config import APPDATA_DIR, ZAPRET_VERSION_URL, ZAPRET_CORE_URL, ZIP_URL, EXE_URL, BUILDNUMBER_URL, INSTALLER_URL, ICON_PATH
from config import GITHUB_ZAPRET_VERSION_URL, GITHUB_ZAPRET_CORE_URL, GITHUB_BUILDNUMBER_URL, GITHUB_EXE_URL, GITHUB_ZIP_URL
from config import GITLAB_ZAPRET_VERSION_URL, GITLAB_ZAPRET_CORE_URL, GITLAB_BUILDNUMBER_URL, GITLAB_EXE_URL, GITLAB_ZIP_URL
import urllib.request
import subprocess
import sys
import pywinstyles
import webbrowser
import tempfile
import threading
import re
import ctypes
import psutil
import json
import time
import zipfile
import shutil
import os

class SplashWindow:
    def __init__(self, theme='Default', current_version=None, current_build=None, zapret_version=None, auto_update_enabled=True):
        self.window = tk.Tk()
        self.colors_name = theme
        self.colors = get_theme(theme)
        
        if current_version is None:
            for arg in sys.argv:
                if arg.startswith('--version='):
                    current_version = arg.split('=')[1]
                    break
        self.current_version = current_version if current_version else "0.0"
        
        if current_build is None:
            for arg in sys.argv:
                if arg.startswith('--build='):
                    current_build = arg.split('=')[1]
                    break
        self.current_build = current_build if current_build else "0"

        if zapret_version is None:
            for arg in sys.argv:
                if arg.startswith('--zapret-version='):
                    zapret_version = arg.split('=')[1]
                    break
        self.current_zapret_version = zapret_version if zapret_version else "0.0"

        self.width = 320
        self.height = 260
        self._is_closing = False

        self.auto_update_enabled = auto_update_enabled

        self.sources = [
            {
                'name': 'main',
                'zapret_version': ZAPRET_VERSION_URL,
                'build': BUILDNUMBER_URL,
                'exe': EXE_URL,
                'zip': ZIP_URL,
                'zapret': ZAPRET_CORE_URL
            },
            {
                'name': 'github',
                'zapret_version': GITHUB_ZAPRET_VERSION_URL,
                'build': GITHUB_BUILDNUMBER_URL,
                'exe': GITHUB_EXE_URL,
                'zip': GITHUB_ZIP_URL,
                'zapret': GITHUB_ZAPRET_CORE_URL
            },
            {
                'name': 'gitlab',
                'zapret_version': GITLAB_ZAPRET_VERSION_URL,
                'build': GITLAB_BUILDNUMBER_URL,
                'exe': GITLAB_EXE_URL,
                'zip': GITLAB_ZIP_URL,
                'zapret': GITLAB_ZAPRET_CORE_URL
            }
        ]

        self.current_source_index = 0
        
        self.appdata_path = APPDATA_DIR
        self.internal_path = self.appdata_path / "_internal"

        self._target_progress = 0
        self._animation_id = None

        self.setup_window()
        self.setup_ui()

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self):
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()
        
    def after(self, ms, func):
        if not self._is_closing:
            try:
                return self.window.after(ms, func)
            except:
                pass
        return None

    def _get_url(self, url_type):
        if 0 <= self.current_source_index < len(self.sources):
            return self.sources[self.current_source_index][url_type]
        return None

    def _get_source_name(self, index):
        if 0 <= index < len(self.sources):
            return self.sources[index]['name'].capitalize()
        return "Unknown"

    def _switch_to_next_source(self):
        if self.current_source_index < len(self.sources) - 1:
            self.current_source_index += 1
            return True
        return False
        
    def setup_window(self):
        self.window.overrideredirect(False)
        self.window.title("Zapret Launcher")
        self.window.configure(bg=self.colors['bg_dark'])
        self.window.resizable(False, False)

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

        try:
            icon_paths = [ICON_PATH]
            
            for path in icon_paths:
                if path and path.exists():
                    try:
                        if path.suffix.lower() == '.ico':
                            self.window.iconbitmap(default=str(path))
                            break
                    except:
                        continue
        except Exception:
            pass

        self.window.attributes('-alpha', 0.0)
        self._update_window_title_color()
        self.window.update_idletasks()
        self.window.attributes('-alpha', 1.0)

    def _update_window_title_color(self):
        try:
            if self.colors_name == 'Default':
                header_color = "#0F0F12"
            elif self.colors_name == 'Pink':
                header_color = "#1E1B2E"
            else:
                header_color = self.colors['bg_dark']
            pywinstyles.change_header_color(self.window, header_color)
            
        except ImportError:
            pass
        except Exception:
            pass
        
    def center_window(self):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
    def setup_ui(self):
        main_frame = tk.Frame(self.window, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        center_container = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        center_container.place(relx=0.5, rely=0.45, anchor="center")
        
        self.logo_label = tk.Label(center_container, bg=self.colors['bg_dark'])
        self.logo_label.pack(pady=(0, 3))
        self.load_logo()
        
        self.status_label = tk.Label(
            center_container,
            text=tr('splash_check_connecting'),
            font=("Segoe UI Variable", 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark']
        )
        self.status_label.pack(pady=(0, 6))
        
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(
            center_container,
            variable=self.progress_var,
            length=260,
            mode='determinate',
            maximum=100
        )
        self.progress_bar.pack()
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            'TProgressbar',
            background=self.colors['accent_hover'],
            troughcolor=self.colors['bg_light'],
            thickness=6
        )
        
        bottom_frame = tk.Frame(center_container, bg=self.colors['bg_dark'])
        bottom_frame.pack(fill=tk.X, pady=(15, 0))
        
        manual_label = tk.Label(
            bottom_frame,
            text=tr('splash_help_update'),
            font=("Segoe UI Variable", 8),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark'],
            cursor="hand2"
        )
        manual_label.pack()
        
        def on_enter_manual(event):
            manual_label.config(fg=self.colors['accent'])
        
        def on_leave_manual(event):
            manual_label.config(fg=self.colors['text_secondary'])
        
        def on_click_manual(event):
            webbrowser.open(INSTALLER_URL)
        
        manual_label.bind("<Enter>", on_enter_manual)
        manual_label.bind("<Leave>", on_leave_manual)
        manual_label.bind("<Button-1>", on_click_manual)
        
    def load_logo(self):
        try:
            icon_paths = [ICON_PATH]
            
            for path in icon_paths:
                if path.exists():
                    img = Image.open(path)
                    img = img.resize((140, 140), Image.Resampling.LANCZOS)
                    self.logo_image = ImageTk.PhotoImage(img)
                    self.logo_label.config(image=self.logo_image)
                    return
                    
            self.logo_label.config(image='', text='')
        except Exception:
            self.logo_label.config(image='', text='')
    
    def update_status(self, text, progress=None):
        if self._is_closing:
            return
        
        try:
            if self.status_label and self.status_label.winfo_exists():
                if text is not None:
                    self.status_label.config(text=text)
            if progress is not None:
                self._target_progress = progress
                if self._animation_id:
                    try:
                        self.window.after_cancel(self._animation_id)
                    except:
                        pass
                    self._animation_id = None
                self._animate_progress()
        except:
            pass
    
    def _animate_progress(self):
        if self._is_closing:
            return
        
        current = self.progress_var.get()
        target = self._target_progress
        
        if abs(current - target) <= 1:
            if current != target:
                self.progress_var.set(target)
            return
        
        if current < target:
            diff = target - current
            step = max(1, diff // 8)
            new_value = min(current + step, target)
        else:
            diff = current - target
            step = max(1, diff // 8)
            new_value = max(current - step, target)
        
        self.progress_var.set(new_value)
        self._animation_id = self.window.after(16, self._animate_progress)
    
    def start(self):
        if not self.is_admin():
            self.run_as_admin()
            return
        
        threading.Thread(target=self.cleanup_old_internal_folders, daemon=True).start()
        threading.Thread(target=self.cleanup_old_exclude_files, daemon=True).start()
    
        self._check_internet()
        self.window.mainloop()

    def _check_internet(self):
        self.update_status(tr('splash_check_connecting'), 10)
        def check():
            try:
                if self._is_winws_running():
                    self.after(0, self._check_for_update)
                    return
                
                if self.auto_update_enabled:
                    self.after(0, self._check_for_update)
                else:
                    self.after(200, lambda: self.update_status(tr('splash_starting_exe'), 100))
                    self.after(1000, self._launch_main_app)

            except Exception:
                self.after(0, lambda: self._show_no_internet_dialog())
        
        threading.Thread(target=check, daemon=True).start()

    def _is_winws_running(self):
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() == 'winws.exe':
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass
        return False
        
    def get_current_zapret_version(self):
        try:
            version_file = self.appdata_path / "zapret_core" / "version.txt"
            if version_file.exists():
                version = version_file.read_text(encoding='utf-8').strip()
                version = re.sub(r'[^\d\.a-z]', '', version.lower())
                return version
        except Exception:
            pass
        return "0.0"
    
    def _get_current_strategy(self):
        try:
            config_file = self.appdata_path / "config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('current_strategy')
        except Exception:
            pass
        return None
    
    def _run_strategy_and_restart(self):
        try:
            strategy = self._get_current_strategy()
            if not strategy:
                return
            
            zapret_dir = self.appdata_path / "zapret_core"
            strategy_path = zapret_dir / strategy
            
            if strategy_path.exists():
                subprocess.Popen(["cmd.exe", "/c", str(strategy_path)], cwd=str(zapret_dir), creationflags=subprocess.CREATE_NO_WINDOW)
            
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = sys.argv[0]
            
            subprocess.Popen([exe_path], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)
            self.close()
            
        except Exception:
            pass

    def _show_no_internet_dialog(self):
        strategy = self._get_current_strategy()
        
        if strategy:
            strategy_display = strategy.replace(".bat", "").replace("general", "").strip() or tr('splash_no_internet_default_strategy')
        else:
            strategy_display = tr('splash_no_internet_default_strategy')
        
        text = tr('splash_no_internet_text').format(strategy=strategy_display)
        result = messagebox.askyesno(tr('splash_no_internet_title'), text)
        
        if result:
            self._run_strategy_and_restart()
        else:
            self._launch_main_app()

    def _download_file_with_fallback(self, url_type, dest_path, start_progress=0, end_progress=100):
        for i in range(self.current_source_index, len(self.sources)):
            try:
                source_name = self._get_source_name(i)
                if i > self.current_source_index:
                    current_source = source_name
                    self.after(0, lambda: self.update_status(tr('splash_trying_source').format(source=current_source), start_progress))
                
                url = self.sources[i][url_type]
                result = self._download_with_progress(url, dest_path, start_progress, end_progress)
                if result:
                    self.current_source_index = i
                    return True
            except Exception:
                continue
        raise Exception(f"Failed to download {url_type} from all sources")

    def _check_for_update(self):
        self.update_status(tr('splash_check_updates'), 30)
        
        def check():
            for source_index in range(len(self.sources)):
                try:
                    source_name = self._get_source_name(source_index)
                    current_source = source_name
                    
                    if source_index == 0:
                        self.after(0, lambda: self.update_status(tr('splash_check_updates'), 30))
                    else:
                        self.after(0, lambda: self.update_status(tr('splash_trying_source').format(source=current_source), 30))
                    
                    url = self.sources[source_index]['build']
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Connection': 'close'})
                    with urllib.request.urlopen(req, timeout=15) as response:
                        latest_build = response.read().decode('utf-8').strip()
                        latest_build = re.sub(r'[^\d]', '', latest_build)
                        current_build = self.current_build
                        need_launcher_update = compare_builds(current_build, latest_build)
                        
                        self.current_source_index = source_index
                        
                        need_zapret_update, latest_zapret = self._check_zapret_core_update()
                        
                        if need_launcher_update:
                            self.after(1000, lambda: self._start_update(latest_build))
                        elif need_zapret_update:
                            self.after(1000, lambda: self._update_zapret_core_only(latest_zapret))
                        else:
                            self.after(0, lambda: self.update_status(tr('splash_starting_exe'), 100))
                            self.after(1000, self._launch_main_app)
                        return
                        
                except Exception as e:
                    if source_index < len(self.sources) - 1:
                        continue
                    else:
                        self.after(0, lambda: self.update_status(tr('splash_all_sources_failed'), 100))
                        self.after(1000, self._launch_main_app)
                        return
            
        threading.Thread(target=check, daemon=True).start()

    def _check_zapret_core_update(self) -> tuple[bool, Optional[str]]:
        for source_index in range(self.current_source_index, len(self.sources)):
            try:
                source_name = self._get_source_name(source_index)
                if source_index > self.current_source_index:
                    self.after(0, lambda: self.update_status(tr('splash_trying_zapret_source').format(source=source_name), 40))
                
                url = self.sources[source_index]['zapret_version']
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Connection': 'close'})
                with urllib.request.urlopen(req, timeout=15) as response:
                    latest_version = response.read().decode('utf-8').strip()
                    self.current_source_index = source_index
                    current_version = self.get_current_zapret_version()
                    need_update = compare_zapret_versions(current_version, latest_version)
                    return need_update, latest_version
            except Exception:
                continue
        return False, None

    def _start_update(self, new_build):
        source_name = self._get_source_name(self.current_source_index)
        self.after(0, lambda: self.update_status(tr('splash_using_source').format(source=source_name), 50))
        self.after(500, self._download_and_update)

    def _download_with_progress(self, url, dest_path, start_progress=0, end_progress=100):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Connection': 'close'})
            
            with urllib.request.urlopen(req, timeout=120) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                
                with open(dest_path, 'wb') as f:
                    chunk_size = 8192
                    last_update = 0
                    
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = start_progress + int((downloaded / total_size) * (end_progress - start_progress))
                            progress = min(end_progress, max(start_progress, progress))
                            
                            now = time.time() * 1000
                            if now - last_update > 50:
                                last_update = now
                                if not self._is_closing:
                                    self._target_progress = progress
                                    self._animate_progress()
            return True
        except Exception:
            return False
        
    def _update_zapret_core_only(self, new_version):
        self.update_status(tr('splash_updating_zapret'), 80)
        
        def update_zapret_thread():
            try:
                self._stop_zapret_processes()
                success = self._download_zapret_core()
                
                if success:
                    version_file = self.appdata_path / "zapret_core" / "version.txt"
                    version_file.write_text(new_version, encoding='utf-8')
                    
                    self.after(0, lambda: self.update_status(None, 100))
                    self.after(1000, self._launch_main_app)
                else:
                    self.after(0, lambda: self.update_status(tr('splash_update_error'), 100))
                    self.after(2000, self._launch_main_app)
                    
            except Exception:
                self.after(0, lambda: self.update_status(tr('splash_update_error'), 100))
                self.after(2000, self._launch_main_app)
        
        threading.Thread(target=update_zapret_thread, daemon=True).start()
        
    def _download_zapret_core(self):
        temp_zip = None
        saved_custom_files = {}
        
        try:
            zapret_dir = self.appdata_path / "zapret_core"
            temp_zip = self.appdata_path / "zapret_core_temp.zip"
            
            self.update_status(tr('splash_downloading_zapret'), 80)
            success = self._download_file_with_fallback('zapret', temp_zip, 80, 88)
            
            if not success:
                raise Exception("Failed to download zapret_core.zip")
            
            self.update_status(tr('splash_extracting_zapret'), 88)
            
            self._stop_zapret_processes()
            time.sleep(1.5)
            
            lists_dir = zapret_dir / "lists"
            if lists_dir.exists():
                custom_file = lists_dir / "list-custom.txt"
                if custom_file.exists():
                    with open(custom_file, 'r', encoding='utf-8') as f:
                        saved_custom_files['list-custom.txt'] = f.read()
                
                white_user_file = lists_dir / "ipset-white-user.txt"
                if white_user_file.exists():
                    with open(white_user_file, 'r', encoding='utf-8') as f:
                        saved_custom_files['ipset-white-user.txt'] = f.read()
            
            if zapret_dir.exists():
                version_file = zapret_dir / "version.txt"
                if version_file.exists():
                    version_file.unlink()
                
                bat_files_to_delete = [
                    "service.bat",
                    "general.bat",
                    "general (ALT).bat",
                    "general (ALT2).bat",
                    "general (ALT3).bat",
                    "general (ALT4).bat",
                    "general (ALT5).bat",
                    "general (ALT6).bat",
                    "general (ALT7).bat",
                    "general (ALT8).bat",
                    "general (ALT9).bat",
                    "general (ALT10).bat",
                    "general (ALT11).bat",
                    "general (ALT12).bat",
                    "general (FAKE TLS AUTO).bat",
                    "general (FAKE TLS AUTO ALT2).bat",
                    "general (FAKE TLS AUTO ALT3).bat",
                    "general (SIMPLE FAKE).bat",
                    "general (SIMPLE FAKE ALT).bat",
                    "general (SIMPLE FAKE ALT2).bat"
                ]
                
                for bat_file in bat_files_to_delete:
                    bat_path = zapret_dir / bat_file
                    if bat_path.exists():
                        bat_path.unlink()
                
                if lists_dir.exists():
                    for file in lists_dir.iterdir():
                        if file.is_file():
                            if file.name not in ['list-custom.txt', 'ipset-white-user.txt']:
                                file.unlink()
                
                utils_dir = zapret_dir / "utils"
                if utils_dir.exists():
                    shutil.rmtree(utils_dir)
                
                bin_dir = zapret_dir / "bin"
                if bin_dir.exists():
                    shutil.rmtree(bin_dir)
            
            with zipfile.ZipFile(temp_zip, 'r') as zf:
                temp_extract = tempfile.mkdtemp()
                zf.extractall(temp_extract)
                
                extracted_core = Path(temp_extract) / "zapret_core"
                if not extracted_core.exists():
                    extracted_core = Path(temp_extract)
                
                for item in extracted_core.iterdir():
                    dest = zapret_dir / item.name
                    
                    if item.is_dir() and item.name == "lists":
                        lists_dest = dest
                        lists_dest.mkdir(parents=True, exist_ok=True)
                        
                        for file_in_archive in item.iterdir():
                            if file_in_archive.is_file():
                                if file_in_archive.name not in ['list-custom.txt', 'ipset-white-user.txt']:
                                    dest_file = lists_dest / file_in_archive.name
                                    shutil.copy2(file_in_archive, dest_file)
                    
                    elif item.is_dir():
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)
                
                shutil.rmtree(temp_extract)
            
            if saved_custom_files:
                lists_dest = zapret_dir / "lists"
                lists_dest.mkdir(parents=True, exist_ok=True)
                
                for filename, content in saved_custom_files.items():
                    dest_file = lists_dest / filename
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        f.write(content)
            
            if temp_zip.exists():
                temp_zip.unlink()
            
            self.update_status(None, 98)
            return True
            
        except Exception:
            return False
        finally:
            if temp_zip and temp_zip.exists():
                try:
                    temp_zip.unlink()
                except:
                    pass

    def _download_and_update(self):
        def update_worker():
            temp_exe = None
            temp_zip = None
            update_script = None
            
            try:
                current_exe = Path(sys.executable)
                temp_exe = current_exe.parent / f"{current_exe.stem}_new.exe"
                temp_zip = current_exe.parent / "_internal_temp.zip"
                update_script = current_exe.parent / "update_temp.bat"
                
                self.after(0, lambda: self.update_status(tr('splash_downloading_exe'), 0))
                exe_success = self._download_file_with_fallback('exe', temp_exe, 0, 30)
                
                if not exe_success:
                    raise Exception("Failed to download exe file")
                
                self.after(0, lambda: self.update_status(tr('splash_downloading_zip'), 30))
                zip_success = self._download_file_with_fallback('zip', temp_zip, 30, 60)
                
                if not zip_success:
                    raise Exception("Failed to download zip file")
                
                self.after(0, lambda: self.update_status(tr('splash_downloading_zip'), 60))
                self.after(0, lambda: self.update_status(tr('splash_install_update'), 90))
                self._stop_zapret_processes()
                time.sleep(2)
                
                bat_content = f'''@echo off
                timeout /t 2 /nobreak > nul
                set "source_exe={temp_exe}"
                set "target_exe={current_exe}"
                set "temp_zip={temp_zip}"

                :retry_copy
                copy /y "%source_exe%" "%target_exe%" > nul
                if errorlevel 1 (
                    echo Waiting for file...
                    timeout /t 1 /nobreak > nul
                    goto retry_copy
                )

                if exist "%source_exe%" del /f /q "%source_exe%" 2>nul
                if exist "%temp_zip%" del /f /q "%temp_zip%" 2>nul

                timeout /t 1 /nobreak > nul
                start "" "%target_exe%"
                del /f /q "%~f0" 2>nul
                '''
                
                with open(update_script, 'w', encoding='utf-8') as f:
                    f.write(bat_content)
                
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                subprocess.Popen(['cmd.exe', '/c', str(update_script)], startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                self.after(100, self.close)
                sys.exit(0)
                                
            except Exception:
                self.after(0, lambda: self.update_status(tr('splash_update_error'), 100))
                self.after(2000, self._launch_main_app)
                
                if temp_exe and temp_exe.exists():
                    try:
                        temp_exe.unlink()
                    except Exception:
                        pass

                if temp_zip and temp_zip.exists():
                    try:
                        temp_zip.unlink()
                    except Exception:
                        pass

                if update_script and update_script.exists():
                    try:
                        update_script.unlink()
                    except Exception:
                        pass
        
        threading.Thread(target=update_worker, daemon=True).start()
    
    def _stop_zapret_processes(self):
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'winws.exe'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(['sc', 'stop', 'WinDivert'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(['taskkill', '/F', '/IM', 'nfqws.exe'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(1)
        except:
            pass

    def cleanup_old_internal_folders(self):
        try:
            appdata_path = APPDATA_DIR
            if not appdata_path.exists():
                return
            
            for item in appdata_path.iterdir():
                if item.is_dir() and item.name.startswith('_internal_old_'):
                    for root, files in os.walk(item):
                        for file in files:
                            try:
                                file_path = Path(root) / file
                                os.chmod(file_path, 0o666)
                            except:
                                pass
                    
                    try:
                        shutil.rmtree(item)
                    except PermissionError:
                        try:
                            new_name = item.parent / f"_internal_old_del_{int(time.time())}"
                            item.rename(new_name)
                            shutil.rmtree(new_name, ignore_errors=True)
                        except:
                            pass
                    except Exception:
                        pass
        except Exception:
            pass
    
    def cleanup_old_exclude_files(self):
        try:
            lists_dir = APPDATA_DIR / "zapret_core" / "lists"
            if not lists_dir.exists():
                return
            
            files_to_remove = [
                "ipset-exclude-user.txt",
                "ipset-exclude.txt", 
                "list-exclude-user.txt",
                "list-exclude.txt",
                "list-general-user.txt"
            ]
            
            removed_count = 0
            for filename in files_to_remove:
                file_path = lists_dir / filename
                if file_path.exists():
                    try:
                        os.chmod(file_path, 0o666)
                        file_path.unlink()
                        removed_count += 1
                    except Exception:
                        pass
                
        except Exception:
            pass

    def _launch_main_app(self):
        if self._is_closing:
            return
        
        zapret_dir = self.appdata_path / "zapret_core"
        if not zapret_dir.exists() or not (zapret_dir / "bin" / "winws.exe").exists():
            self.update_status(tr('splash_downloading_zapret'), 50)
            self._download_zapret_core()
        
        self.update_status(tr('splash_starting_exe'), 100)
        time.sleep(0.5)
        self.close()
        
        try:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = sys.argv[0]
            
            subprocess.Popen([exe_path, '--no-splash', '--from-splash'], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)
        except Exception:
            pass
    
    def close(self):
        if self._animation_id:
            try:
                self.window.after_cancel(self._animation_id)
            except:
                pass
            self._animation_id = None
        
        self._is_closing = True
        try:
            self.window.destroy()
        except:
            pass
