# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import pystray
from PIL import Image, ImageDraw
import webbrowser
from utils.messagebox import messagebox
import subprocess
from utils.languages import tr
import tkinter as tk
import re
from config import ICON_PATH

class ModernSystemTray:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self.current_rtt = None
        self.last_rtt_update = 0
        self.colors = {
            'bg_dark': '#1E1E24',
            'bg_medium': '#2D2D35',
            'bg_light': '#3D3D45',
            'accent': '#d0a2e9',
            'accent_green': '#4ade80',
            'accent_red': '#f87171',
            'text_primary': '#FFFFFF',
            'text_secondary': '#A0A0B0',
            'button_bg': '#2D2D35',
            'button_hover': '#3D3D45',
        }
        self.create_icon()

    def create_icon(self):
        try:
            icon_paths = [ICON_PATH]
            
            image = None
            for path in icon_paths:
                if path and path.exists():
                    try:
                        image = Image.open(str(path))
                        if image.mode != 'RGBA':
                            image = image.convert('RGBA')
                        image = image.resize((64, 64), Image.Resampling.LANCZOS)
                        break
                    except:
                        continue
            
            if image:
                draw = ImageDraw.Draw(image)
                indicator_size = 16
                indicator_x = 64 - indicator_size - 4
                indicator_y = 64 - indicator_size - 4
                
                if self.app.is_connected:
                    indicator_color = self._hex_to_rgb(self.colors['accent_green'])
                else:
                    indicator_color = self._hex_to_rgb(self.colors['accent_red'])
                
                draw.ellipse(
                    [indicator_x, indicator_y, indicator_x + indicator_size, indicator_y + indicator_size],
                    fill=indicator_color
                )
                
                draw.ellipse(
                    [indicator_x - 1, indicator_y - 1, indicator_x + indicator_size + 1, indicator_y + indicator_size + 1],
                    outline=(255, 255, 255, 255),
                    width=1
                )
            
        except Exception:
            pass

        self.update_menu(image)

    def _is_window_visible(self):
        try:
            if not self.app.root.winfo_exists():
                return False
            
            state = self.app.root.state()
            
            if state == 'iconic' or state == 'withdrawn':
                return False
            
            if not self.app.root.winfo_viewable():
                return False
            
            return True
            
        except:
            return False

    def _is_mode_selector_open(self):
        try:
            for w in self.app.root.winfo_children():
                if isinstance(w, tk.Toplevel) and w.winfo_exists():
                    try:
                        if w.title() == tr('mode_select_title'):
                            return True
                    except Exception:
                        continue
        except Exception:
            pass
        return False
        
    def toggle_window_visibility(self):
        try:
            if self._is_window_visible():
                self.app.root.withdraw()
            else:
                self.show_window()
            
            self.update_menu()
            if self.icon:
                self.icon.update_menu()
                
        except Exception:
            pass

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def get_tooltip_text(self):
        if self.app.is_connected:
            stats = self.app.stats.get_stats_dict()
            mode_text = self.app.mode_label.cget('text') if hasattr(self.app, 'mode_label') and self.app.mode_label else tr('status_connected')
            
            rtt_text = ""
            if hasattr(self.app, '_last_rtt_value'):
                rtt_val = self.app._last_rtt_value
                if rtt_val and rtt_val != "-- ms":
                    rtt_text = f"{rtt_val}\n"
            elif hasattr(self.app, 'stats_rtt_label') and self.app.stats_rtt_label:
                try:
                    rtt_value = self.app.stats_rtt_label.cget('text')
                    if rtt_value and rtt_value != "-- ms":
                        rtt_text = f"{rtt_value}\n"
                except Exception:
                    pass
            
            return (
                f"Zapret Launcher\n"
                f"{tr('mode')} {mode_text}\n"
                f"—————————————\n"
                f"{stats['session_time_str']}\n"
                f"{rtt_text}"
                f"{stats['speed_down_str']} / {stats['speed_up_str']}\n"
                f"{stats['down_str']} / {stats['up_str']}"
            )
        else:
            return (
                f"Zapret Launcher\n"
                f"{tr('status_ready')}"
            )

    def update_menu(self, image=None):
        help_menu = pystray.Menu(
            pystray.MenuItem(
                tr('menu_help_security'),
                lambda: webbrowser.open("https://github.com/avaxngard/zapret-launcher/blob/main/SECURITY.md"),
                enabled=True
            ),
            pystray.MenuItem(
                tr('menu_help_license'),
                lambda: webbrowser.open("https://github.com/avaxngard/zapret-launcher/blob/main/LICENSE"),
                enabled=True
            ),
            pystray.MenuItem(
                tr('menu_help_report'),
                lambda: webbrowser.open("https://t.me/zapret_launcher_bot"),
                enabled=True
            ),
            pystray.MenuItem(
                tr('menu_help_changelog'),
                lambda: webbrowser.open("https://zapret-launcher.ru/changelog"),
                enabled=True
            ),
            pystray.MenuItem(
                tr('menu_help_github'),
                lambda: webbrowser.open("https://github.com/avaxngard/zapret-launcher"),
                enabled=True
            ),
            pystray.MenuItem(
                tr('menu_help_donate'),
                lambda: webbrowser.open("https://www.donationalerts.com/r/tweenkedrage"),
                enabled=True
            ),
            pystray.MenuItem(
                tr('menu_help_logs'),
                lambda: self.open_logs(),
                enabled=True
            )
        )
        settings_menu = pystray.Menu(
            pystray.MenuItem(
                tr('menu_settings_copy_secret'),
                self.app.copy_tg_link_to_clipboard,
                enabled=True
            ),
            pystray.MenuItem(
                tr('menu_settings_folder'),
                self.app.open_appdata_folder,
                enabled=True
            )
        )
        
        is_connecting = hasattr(self.app, '_connecting') and self.app._connecting
        is_disconnecting = hasattr(self.app, '_disconnecting') and self.app._disconnecting
        is_busy = is_connecting or is_disconnecting
        
        if is_busy:
            if is_connecting:
                connect_text = tr('status_starting')
            else:
                connect_text = tr('status_disconnecting')
            connect_item = pystray.MenuItem(
                connect_text,
                None,
                enabled=False
            )
        else:
            if self.app.is_connected:
                connect_text = tr('menu_disconnect')
            else:
                connect_text = tr('menu_connect')
            connect_item = pystray.MenuItem(
                connect_text,
                self.toggle_connection,
                enabled=True
            )
        
        if self._is_window_visible():
            hide_text = tr('menu_minimaze')
        else:
            hide_text = tr('menu_show_app')

        menu_items = [
            pystray.MenuItem(
                hide_text,
                self.toggle_window_visibility
            ),
            pystray.Menu.SEPARATOR,
            connect_item,
        ]
        
        menu_items.extend([
            pystray.MenuItem(
                tr('menu_settings'),
                settings_menu
            ),
            pystray.MenuItem(
                tr('menu_help'),
                help_menu
            ),
            pystray.MenuItem(
                tr('menu_exit'),
                self.quit_from_tray
            )
        ])
        
        menu = pystray.Menu(*menu_items)
        
        if self.icon:
            self.icon.menu = menu
            if image:
                self.icon.icon = image
            self.icon.title = self.get_tooltip_text()
        else:
            if image is None:
                image = Image.new('RGBA', (64, 64), color=self.colors['accent'])
                draw = ImageDraw.Draw(image)
                draw.text((20, 20), "Z", fill='white')
            
            self.icon = pystray.Icon(
                "zapret_launcher",
                image,
                self.get_tooltip_text(),
                menu
            )

    def open_logs(self):
        try:
            self.show_window()
            self.app.root.after(500, lambda: self.app.show_logs_page())
        except Exception:
            pass

    def update_tooltip(self):
        if self.icon:
            try:
                self.icon.title = self.get_tooltip_text()
            except:
                pass

    def update_icon_state(self):
        try:
            if not self.icon:
                self.create_icon()
                return
            
            is_connected = False
            
            if hasattr(self.app, 'zapret') and self.app.zapret:
                if self.app.zapret.is_winws_running():
                    is_connected = True
            
            if hasattr(self.app, 'tg_proxy') and self.app.tg_proxy:
                if self.app.tg_proxy.is_running:
                    is_connected = True
            
            if not is_connected and hasattr(self.app, 'is_connected'):
                is_connected = self.app.is_connected
            
            icon_paths = [ICON_PATH]
            
            image = None
            for path in icon_paths:
                if path and path.exists():
                    try:
                        image = Image.open(str(path))
                        if image.mode != 'RGBA':
                            image = image.convert('RGBA')
                        image = image.resize((64, 64), Image.Resampling.LANCZOS)
                        break
                    except:
                        continue
            
            if image:
                draw = ImageDraw.Draw(image)
                indicator_size = 16
                indicator_x = 64 - indicator_size - 4
                indicator_y = 64 - indicator_size - 4
                
                if is_connected:
                    indicator_color = self._hex_to_rgb(self.colors['accent_green'])
                else:
                    indicator_color = self._hex_to_rgb(self.colors['accent_red'])
                
                draw.ellipse(
                    [indicator_x, indicator_y, indicator_x + indicator_size, indicator_y + indicator_size],
                    fill=indicator_color
                )
                draw.ellipse(
                    [indicator_x - 1, indicator_y - 1, indicator_x + indicator_size + 1, indicator_y + indicator_size + 1],
                    outline=(255, 255, 255, 255),
                    width=1
                )
                
                self.icon.icon = image
        except Exception:
            pass

    def force_update_menu(self):
        if self.icon:
            try:
                self.update_menu()
                self.icon.update_menu()
            except Exception:
                pass

    def quit_from_tray(self):
        if hasattr(self.app, '_disconnecting') and self.app._disconnecting:
            self.app.root.after(500, self.quit_from_tray)
            return
        
        is_any_running = False
        if hasattr(self.app, 'zapret') and self.app.zapret:
            if self.app.zapret.is_winws_running():
                is_any_running = True
        if hasattr(self.app, 'tg_proxy') and self.app.tg_proxy:
            if self.app.tg_proxy.is_running:
                is_any_running = True
        if hasattr(self.app, 'is_connected') and self.app.is_connected:
            is_any_running = True
        
        if is_any_running:
            result = messagebox.askyesno(
                tr('dialog_exit'),
                tr('dialog_exit_message')
            )
            if result:
                self._prepare_and_quit()
        else:
            self._prepare_and_quit()

    def _prepare_and_quit(self):
        try:
            self.app.save_settings()
        except:
            pass
        
        if self.icon:
            self.icon.stop()

        if hasattr(self.app, 'zapret') and self.app.zapret:
            self.app.zapret.stop_current_strategy()
        if hasattr(self.app, 'tg_proxy') and self.app.tg_proxy:
            self.app.tg_proxy.stop()
        self.app.root.after(500, self.app.quit_from_tray)

    def show_window(self):
        try:
            if not self.app.root.winfo_exists():
                return
            
            if self.app.root.state() == 'normal' and self.app.root.winfo_viewable():
                self.app.root.lift()
                self.app.root.focus_force()
                return
            
            self.app._hide_all_dialogs()
            self.app.root.attributes('-alpha', 0.0)
            
            self.app.root.deiconify()
            self.app.root.lift()
            self.app.root.focus_force()
            self.app.root.state('normal')
            
            self.app._show_all_dialogs()
            self.app.update_all_window_headers()
            self.force_update_menu()
            
            self.app.root.attributes('-alpha', 1.0)
        except Exception:
            pass

    def toggle_connection(self):
        is_connecting = hasattr(self.app, '_connecting') and self.app._connecting
        is_disconnecting = hasattr(self.app, '_disconnecting') and self.app._disconnecting
        
        if is_connecting or is_disconnecting:
            return
        
        if self._is_mode_selector_open():
            self.show_window()
            return
        
        if self.app.is_connected:
            self._do_toggle_connection()
        else:
            self.show_window()
            self.app.root.after(200, self._check_and_connect)
        
        self.update_icon_state()

    def change_mode(self):
        try:
            self.show_window()
            self.app.root.after(100, lambda: self.app.dialogs.show_mode_selector())
        except Exception:
            pass

    def _check_and_connect(self):
        self.app.toggle_connection()

    def _do_toggle_connection(self):
        if self._is_mode_selector_open():
            self.show_window()
            return
        
        if self.app.is_connected:
            self.app.disconnect()
        else:
            self.app.dialogs.show_mode_selector()

    def get_rtt(self):
        try:
            result = subprocess.run(
                ['ping', '-n', '1', '8.8.8.8'],
                capture_output=True, text=True,
                timeout=2
            )
            if result.returncode == 0:
                match = re.search(r'(?:время|time)[=<>]\s*(\d+)', result.stdout, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        except:
            pass
        return None

    def run(self):
        self.icon.run()
