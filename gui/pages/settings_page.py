# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
import sys
import tempfile
import threading
import shutil
import time
import psutil
import zipfile
import subprocess
import urllib.request
from config import APPDATA_DIR, ZAPRET_CORE_URL
from pathlib import Path
from tkinter import messagebox
from gui.theme import get_theme_names
from gui.widgets import RoundedButton
from utils.languages import tr
from utils.scaling import scale_size

class SettingsPage:
    def __init__(self, parent, app):
        self.app = app
        self.colors = app.colors
        self.font_primary = app.font_primary
        self.font_medium = app.font_medium
        self.font_bold = app.font_bold
        self.scale_factor = getattr(app, 'scale_factor', 1.0)
        
        font_size_title = scale_size(20, self.scale_factor)
        font_size_desc = scale_size(10, self.scale_factor)
        font_size_sub = scale_size(12, self.scale_factor)
        font_size_btn = scale_size(9, self.scale_factor)
        font_size_btn_small = scale_size(10, self.scale_factor)
        btn_width_small = scale_size(80, self.scale_factor)
        btn_height_small = scale_size(28, self.scale_factor)
        btn_width_medium = scale_size(180, self.scale_factor)
        btn_height_medium = scale_size(32, self.scale_factor)
        btn_width_large = scale_size(200, self.scale_factor)
        btn_height_large = scale_size(30, self.scale_factor)
        btn_radius = scale_size(6, self.scale_factor)
        btn_radius_large = scale_size(8, self.scale_factor)
        padx = scale_size(30, self.scale_factor)
        pady = scale_size(4, self.scale_factor)
        
        self.frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        
        title_label = tk.Label(
            self.frame,
            text=tr('settings_title'),
            font=("Inter", font_size_title, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        title_label.pack(anchor='w', pady=(scale_size(30, self.scale_factor), 5), padx=padx)
        
        desc_label = tk.Label(
            self.frame,
            text=tr('settings_desc'),
            font=("Inter", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark']
        )
        desc_label.pack(anchor='w', pady=(0, scale_size(20, self.scale_factor)), padx=padx)
        
        main_container = tk.Frame(self.frame, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=padx, pady=scale_size(4, self.scale_factor))
        cards_frame = tk.Frame(main_container, bg=self.colors['bg_dark'])
        cards_frame.pack(fill=tk.BOTH, expand=True)
        left_column = tk.Frame(cards_frame, bg=self.colors['bg_dark'])
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, scale_size(12, self.scale_factor)))
        right_column = tk.Frame(cards_frame, bg=self.colors['bg_dark'])
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(scale_size(12, self.scale_factor), 0))

        theme_card = tk.Frame(left_column, bg=self.colors['bg_light'], relief=tk.FLAT, bd=0)
        theme_card.pack(fill=tk.X, pady=scale_size(6, self.scale_factor))
        theme_inner = tk.Frame(theme_card, bg=self.colors['bg_light'])
        theme_inner.pack(fill=tk.X, padx=scale_size(10, self.scale_factor), pady=scale_size(8, self.scale_factor))

        tk.Label(theme_inner, text=tr('settings_theme'), font=("Inter", font_size_sub, "bold"),
                fg=self.colors['accent'], bg=self.colors['bg_light']).pack(anchor='w', pady=(0, 5))

        theme_buttons_frame = tk.Frame(theme_inner, bg=self.colors['bg_light'])
        theme_buttons_frame.pack(anchor='w', pady=5)

        theme_names = get_theme_names()
        for theme_name in theme_names:
            theme_btn = RoundedButton(
                theme_buttons_frame,
                text=theme_name.capitalize(),
                command=lambda t=theme_name: self._change_theme(t),
                width=btn_width_small, height=btn_height_small,
                bg=self.colors['accent'] if theme_name == self.app.current_theme else self.colors['button_bg'],
                fg=self.colors['text_primary'] if theme_name == self.app.current_theme else self.colors['text_secondary'],
                font=("Inter", font_size_btn),
                corner_radius=btn_radius,
                hover_color=self.colors['accent'],
                theme_name=self.app.current_theme
            )
            theme_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        lang_card = tk.Frame(left_column, bg=self.colors['bg_light'], relief=tk.FLAT, bd=0)
        lang_card.pack(fill=tk.X, pady=scale_size(6, self.scale_factor))
        lang_inner = tk.Frame(lang_card, bg=self.colors['bg_light'])
        lang_inner.pack(fill=tk.X, padx=scale_size(10, self.scale_factor), pady=scale_size(8, self.scale_factor))

        tk.Label(lang_inner, text=tr('settings_language'), font=("Inter", font_size_sub, "bold"),
            fg=self.colors['accent'], bg=self.colors['bg_light']).pack(anchor='w', pady=(0, 5))

        lang_buttons_frame = tk.Frame(lang_inner, bg=self.colors['bg_light'])
        lang_buttons_frame.pack(anchor='w', pady=5)

        current_lang = self.app.languages.get_current_language()
        for lang_code, lang_name in self.app.languages.LANGUAGES.items():
            lang_btn = RoundedButton(
                lang_buttons_frame,
                text=lang_name,
                command=lambda l=lang_code: self._change_language(l),
                width=btn_width_small, height=btn_height_small,
                bg=self.colors['accent'] if lang_code == current_lang else self.colors['button_bg'],
                fg=self.colors['text_primary'] if lang_code == current_lang else self.colors['text_secondary'],
                font=("Inter", font_size_btn),
                corner_radius=btn_radius,
                hover_color=self.colors['accent'],
                theme_name=self.app.current_theme
            )
            lang_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        tg_card = tk.Frame(right_column, bg=self.colors['bg_light'], relief=tk.FLAT, bd=0)
        tg_card.pack(fill=tk.X, pady=scale_size(6, self.scale_factor))
        tg_inner = tk.Frame(tg_card, bg=self.colors['bg_light'])
        tg_inner.pack(fill=tk.X, padx=scale_size(10, self.scale_factor), pady=scale_size(8, self.scale_factor))

        tk.Label(tg_inner, text="Telegram Proxy", font=("Inter", font_size_sub, "bold"),
                fg=self.colors['accent'], bg=self.colors['bg_light']).pack(anchor='w', pady=(0, 5))

        secret_value = getattr(self.app, '_tg_secret', None)
        if secret_value and len(secret_value) > 16:
            secret_text = f"{tr('settings_current_tg_secret')} {secret_value[:16]}..."
        elif secret_value:
            secret_text = f"{tr('settings_current_tg_secret')} {secret_value}"
        else:
            secret_text = tr('settings_current_tg_secret')

        self.secret_label = tk.Label(tg_inner, text=secret_text,
                            font=("Inter", font_size_btn), fg=self.colors['text_secondary'], bg=self.colors['bg_light'])
        self.secret_label.pack(anchor='w', pady=(0, 5))

        self.secret_value_label = self.secret_label

        regenerate_btn = RoundedButton(
            tg_inner,
            text=tr('tg_generate_secret'),
            command=self._regenerate_secret,
            width=btn_width_large, height=btn_height_large,
            bg=self.colors['accent'],
            fg=self.colors['text_primary'],
            font=("Inter", font_size_btn_small),
            corner_radius=btn_radius_large,
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        regenerate_btn.pack(anchor='w', pady=2)

        def copy_current_link():
            secret = getattr(self.app, '_tg_secret', None)
            if secret:
                if self.app.tg_fake_tls and self.app.tg_fake_tls_domain:
                    domain_hex = self.app.tg_fake_tls_domain.encode('ascii').hex()
                    link = f"ee{secret}{domain_hex}"
                    notification = tr('notification_copied_secret')
                else:
                    link = secret
                    notification = tr('notification_copied_secret')
                
                self.app.root.clipboard_clear()
                self.app.root.clipboard_append(link)
                self.app.root.update()
                self.app.show_notification(notification, 2000)
            else:
                messagebox.showwarning(tr('error_secret_not_found'), tr('error_telegram_proxy_start'))

        copy_btn = RoundedButton(
            tg_inner,
            text=tr('tg_copy_secret'),
            command=copy_current_link,
            width=btn_width_large, height=btn_height_large,
            bg=self.colors['button_bg'],
            fg=self.colors['text_secondary'],
            font=("Inter", font_size_btn_small),
            corner_radius=btn_radius_large,
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        copy_btn.pack(anchor='w', pady=2)

        self.tg_instruction_btn = RoundedButton(
            tg_inner,
            text=self._get_instruction_button_text(),
            command=self._show_instruction,
            width=btn_width_large, height=btn_height_large,
            bg=self.colors['button_bg'],
            fg=self.colors['text_secondary'],
            font=("Inter", font_size_btn_small),
            corner_radius=btn_radius_large,
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        self.tg_instruction_btn.pack(anchor='w', pady=2)

        maintenance_card = tk.Frame(left_column, bg=self.colors['bg_light'], relief=tk.FLAT, bd=0)
        maintenance_card.pack(fill=tk.X, pady=scale_size(6, self.scale_factor))
        maintenance_inner = tk.Frame(maintenance_card, bg=self.colors['bg_light'])
        maintenance_inner.pack(fill=tk.X, padx=scale_size(10, self.scale_factor), pady=scale_size(8, self.scale_factor))

        tk.Label(maintenance_inner, text=tr('settings_recovery'), font=("Inter", font_size_sub, "bold"), 
            fg=self.colors['accent'], bg=self.colors['bg_light']).pack(anchor='w', pady=(0, 5))

        buttons_frame = tk.Frame(maintenance_inner, bg=self.colors['bg_light'])
        buttons_frame.pack(fill=tk.X, pady=(0, 3))

        integrity_btn = RoundedButton(
            buttons_frame,
            text=tr('settings_integrity'),
            command=self._show_integrity_placeholder,
            width=btn_width_medium, height=btn_height_medium,
            bg=self.colors['button_bg'],
            fg=self.colors['text_secondary'],
            font=("Inter", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        integrity_btn.pack(side=tk.LEFT, padx=(0, scale_size(10, self.scale_factor)))

        reinstall_btn = RoundedButton(
            buttons_frame,
            text=tr('settings_reinstall'),
            command=self._reinstall_files,
            width=btn_width_medium, height=btn_height_medium,
            bg=self.colors['button_bg'],
            fg=self.colors['text_secondary'],
            font=("Inter", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        reinstall_btn.pack(side=tk.LEFT)

        buttons_frame2 = tk.Frame(maintenance_inner, bg=self.colors['bg_light'])
        buttons_frame2.pack(fill=tk.X, pady=(0, 3))

        self.autoupdate_btn = RoundedButton(
            buttons_frame2,
            text=self._get_autoupdate_button_text(),
            command=self._toggle_auto_update,
            width=btn_width_medium, height=btn_height_medium,
            bg=self.colors['button_bg'],
            fg=self.colors['text_secondary'],
            font=("Inter", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        self.autoupdate_btn.pack(side=tk.LEFT, padx=(0, scale_size(10, self.scale_factor)))

        self.analytics_btn = RoundedButton(
            buttons_frame2,
            text=self._get_analytics_button_text(),
            command=self._toggle_analytics,
            width=btn_width_medium, height=btn_height_medium,
            bg=self.colors['button_bg'],
            fg=self.colors['text_secondary'],
            font=("Inter", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        self.analytics_btn.pack(side=tk.LEFT, padx=(0, scale_size(10, self.scale_factor)))

        buttons_frame3 = tk.Frame(maintenance_inner, bg=self.colors['bg_light'])
        buttons_frame3.pack(fill=tk.X, pady=(0, 3))

        show_vpndetect_btn = RoundedButton(
            buttons_frame3,
            text=tr('settings_search_vpn'),
            command=self.app.toggle_vpn_detection,
            width=btn_width_medium, height=btn_height_medium,
            bg=self.colors['button_bg'],
            fg=self.colors['text_secondary'],
            font=("Inter", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        show_vpndetect_btn.pack(side=tk.LEFT, padx=(0, scale_size(10, self.scale_factor)))

        show_dublicatedetect_btn = RoundedButton(
            buttons_frame3,
            text=tr('settings_search_dublicate'),
            command=self.app.toggle_hide_duplicates_warning,
            width=btn_width_medium, height=btn_height_medium,
            bg=self.colors['button_bg'],
            fg=self.colors['text_secondary'],
            font=("Inter", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        show_dublicatedetect_btn.pack(side=tk.LEFT, padx=(0, scale_size(10, self.scale_factor)))

        buttons_frame4 = tk.Frame(maintenance_inner, bg=self.colors['bg_light'])
        buttons_frame4.pack(fill=tk.X)

        appdata_btn = RoundedButton(
            buttons_frame4,
            text=tr('settings_open_folder'),
            command=self.app.open_appdata_folder,
            width=btn_width_medium, height=btn_height_medium,
            bg=self.colors['button_bg'],
            fg=self.colors['text_secondary'],
            font=("Inter", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        appdata_btn.pack(side=tk.LEFT, padx=(0, scale_size(10, self.scale_factor)))

        autostart_btn = RoundedButton(
            buttons_frame4,
            text=tr('settings_autostart'),
            command=self.app.toggle_autostart,
            width=btn_width_medium, height=btn_height_medium,
            bg=self.colors['button_bg'],
            fg=self.colors['text_secondary'],
            font=("Inter", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        autostart_btn.pack(side=tk.LEFT, padx=(0, scale_size(10, self.scale_factor)))

    def _update_autoupdate_button(self):
        if hasattr(self, 'autoupdate_btn') and self.autoupdate_btn:
            try:
                self.autoupdate_btn.set_text(self._get_autoupdate_button_text())
            except:
                pass

    def _update_analytics_button(self):
        if hasattr(self, 'analytics_btn') and self.analytics_btn:
            try:
                self.analytics_btn.set_text(self._get_analytics_button_text())
            except:
                pass

    def update_buttons(self):
        self._update_autoupdate_button()
        self._update_analytics_button()

    def _get_autoupdate_button_text(self):
        if getattr(self.app, '_auto_update_enabled', True):
            return tr('settings_toggle_off_autoupdate')
        else:
            return tr('settings_toggle_on_autoupdate')

    def _get_analytics_button_text(self):
        if getattr(self.app, '_analytics_enabled', True):
            return tr('settings_toggle_off_analytics')
        else:
            return tr('settings_toggle_on_analytics')

    def _get_instruction_button_text(self):
        if getattr(self.app, '_tg_instruction', False):
            return tr('tg_instruction_settings_show')
        else:
            return tr('tg_instruction_settings_hide')
        
    def _toggle_auto_update(self):
        self.app.toggle_auto_update()

    def _toggle_analytics(self):
        self.app.toggle_analytics()

    def _change_theme(self, new_theme):
        current_theme = self.app.current_theme
        
        if new_theme != current_theme:
            restart_msg = tr('restart_manual_message')
            restart_title = tr('restart_manual_title')
            
            result = messagebox.showwarning(restart_title, restart_msg + "\n\n", type=messagebox.OKCANCEL)
            
            if result == 'ok':
                self.app.show_notification(tr('please_wait'), 1500)
                self.app.log_event("info", f"Theme changed: {current_theme} -> {new_theme}")
                self.app.current_theme = new_theme
                self.app.save_settings()
                self.app.root.after(1500, self._restart_launcher)

    def _change_language(self, new_lang):
        current_lang = self.app.languages.get_current_language()
        
        if new_lang != current_lang:
            restart_msg = tr('restart_manual_message')
            restart_title = tr('restart_manual_title')
            
            result = messagebox.showwarning(restart_title, restart_msg + "\n\n", type=messagebox.OKCANCEL)
            
            if result == 'ok':
                self.app.show_notification(tr('please_wait'), 1500)
                self.app.log_event("info", f"Interface language changed: {current_lang} -> {new_lang}")
                self.app.languages.set_language(new_lang)
                self.app.save_settings()
                self.app.root.after(1500, self._restart_launcher)

    def _show_integrity_placeholder(self):
        missing_files = []
        ok_count = 0
        
        checks = [
            ("zapret_core/bin/winws.exe", "winws.exe"),
            ("zapret_core/bin/WinDivert.dll", "WinDivert.dll"),
            ("zapret_core/bin/WinDivert64.sys", "WinDivert64.sys"),
            ("zapret_core/bin/quic_initial_rutube_ru.bin", "quic_initial_rutube_ru.bin"),
            ("zapret_core/bin/quic_initial_www_google_com.bin", "quic_initial_www_google_com.bin"),
            ("zapret_core/bin/stun.bin", "stun.bin"),
            ("zapret_core/bin/stun2.bin", "stun2.bin"),
            ("zapret_core/bin/quic_initial_4pda_to.bin", "quic_initial_4pda_to.bin"),
            ("zapret_core/bin/ACTIVE_DISCORD_UDP.bin", "ACTIVE_DISCORD_UDP.bin"),
            ("zapret_core/bin/ACTIVE_GAME_UDP.bin", "ACTIVE_GAME_UDP.bin"),
            ("zapret_core/bin/tls_clienthello_4pda_to.bin", "tls_clienthello_4pda_to.bin"),
            ("zapret_core/bin/tls_clienthello_5ka_ru.bin", "tls_clienthello_5ka_ru.bin"),
            ("zapret_core/bin/quic_initial_steamcommunity_com.bin", "quic_initial_steamcommunity_com.bin"),
            ("zapret_core/bin/quic_initial_tencent_com.bin", "quic_initial_tencent_com.bin"),
            ("zapret_core/bin/tls_clienthello_max_ru.bin", "tls_clienthello_max_ru.bin"),
            ("zapret_core/bin/tls_clienthello_www_google_com.bin", "tls_clienthello_www_google_com.bin"),
            ("zapret_core/bin/cygwin1.dll", "cygwin1.dll"),

            ("zapret_core/service.bat", "service.bat"),
            ("zapret_core/general.bat", "general.bat"),
            ("zapret_core/general (ALT).bat", "general (ALT).bat"),
            ("zapret_core/general (ALT2).bat", "general (ALT2).bat"),
            ("zapret_core/general (ALT3).bat", "general (ALT3).bat"),
            ("zapret_core/general (ALT4).bat", "general (ALT4).bat"),
            ("zapret_core/general (ALT5).bat", "general (ALT5).bat"),
            ("zapret_core/general (ALT6).bat", "general (ALT6).bat"),
            ("zapret_core/general (ALT7).bat", "general (ALT7).bat"),
            ("zapret_core/general (ALT8).bat", "general (ALT8).bat"),
            ("zapret_core/general (ALT9).bat", "general (ALT9).bat"),
            ("zapret_core/general (ALT10).bat", "general (ALT10).bat"),
            ("zapret_core/general (ALT11).bat", "general (ALT11).bat"),
            ("zapret_core/general (ALT12).bat", "general (ALT12).bat"),
            ("zapret_core/general (EXP).bat", "general (EXP).bat"),
            ("zapret_core/general (FAKE TLS AUTO).bat", "general (FAKE TLS AUTO).bat"),
            ("zapret_core/general (FAKE TLS AUTO ALT).bat", "general (FAKE TLS AUTO ALT).bat"),
            ("zapret_core/general (FAKE TLS AUTO ALT2).bat", "general (FAKE TLS AUTO ALT2).bat"),
            ("zapret_core/general (FAKE TLS AUTO ALT3).bat", "general (FAKE TLS AUTO ALT3).bat"),
            ("zapret_core/general (SIMPLE FAKE).bat", "general (SIMPLE FAKE).bat"),
            ("zapret_core/general (SIMPLE FAKE ALT).bat", "general (SIMPLE FAKE ALT).bat"),
            ("zapret_core/general (SIMPLE FAKE ALT2).bat", "general (SIMPLE FAKE ALT2).bat"),

            ("resources/icon.ico", "icon.ico"),
            ("config.json", "config.json"),
        ]
        
        for path, name in checks:
            full_path = APPDATA_DIR / path
            if full_path.exists():
                ok_count += 1
            else:
                missing_files.append(name)
        
        lists_dir = APPDATA_DIR / "zapret_core/lists"
        if lists_dir.exists():
            list_files = ["ipset-all.txt", 
                        "ipset-all.txt.backup", 
                        "ipset-white.txt",
                        "ipset-white-user.txt", 
                        "list-white.txt",
                        "list-custom.txt",
                        "list-general.txt", 
                        "list-google.txt"]
            
            for list_file in list_files:
                if (lists_dir / list_file).exists():
                    ok_count += 1
                else:
                    missing_files.append(f"lists/{list_file}")
        else:
            missing_files.append(f"zapret_core/lists ({tr('settings_integrity_folder_missing')})")
        
        utils_dir = APPDATA_DIR / "zapret_core/utils"
        if not utils_dir.exists():
            missing_files.append(f"zapret_core/utils ({tr('settings_integrity_folder_missing')})")
        else:
            ok_count += 1
        
        bin_dir = APPDATA_DIR / "zapret_core/bin"
        if not bin_dir.exists():
            missing_files.append(f"zapret_core/bin ({tr('settings_integrity_folder_missing')})")
        else:
            ok_count += 1
        
        if missing_files:
            result_text = f"{tr('settings_integrity_missing_count')} "
            result_text += ", ".join(missing_files)
            
            messagebox.showwarning(tr('settings_integrity_title'), result_text)
        else:
            result_text = f"{tr('settings_integrity_success')}"
            messagebox.showinfo(tr('settings_integrity_title'), result_text)

    def _show_instruction(self):
        self.app._tg_instruction = not self.app._tg_instruction
        self.app.save_settings()
        
        if hasattr(self, 'tg_instruction_btn'):
            self.tg_instruction_btn.set_text(self._get_instruction_button_text())
        
        if self.app._tg_instruction:
            self.app.show_notification(tr('tg_instruction_hidden'), 1500)
        else:
            self.app.show_notification(tr('tg_instruction_shown'), 1500)

    def _regenerate_secret(self):
        self.app.regenerate_tg_secret()
        self.update_secret_display()

    def _reinstall_files(self):
        all_files_exist = self._check_all_files_exist()
            
        if all_files_exist:
            result = messagebox.askyesno(tr('settings_reinstall_title'), tr('settings_reinstall_all_exists'))
            if not result:
                return
        else:
            result = messagebox.askyesno(tr('settings_reinstall_title'), tr('settings_reinstall_missing'))
            if not result:
                return
            
        winws_running = False
        for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() == 'winws.exe':
                        winws_running = True
                        break
                except:
                    pass
            
        if winws_running:
            result = messagebox.askyesno(tr('settings_reinstall_active'), tr('settings_reinstall_disconnect'))
            if not result:
                return
            self.app.disconnect()
            time.sleep(1)

        self.app.show_notification(tr('please_wait'), 5000)
        self.app.root.after(500, lambda: threading.Thread(target=self._download_and_install_zapret_core, daemon=True).start())

    def _check_all_files_exist(self):
        missing_files = []
        
        checks = [
            "zapret_core/bin/winws.exe",
            "zapret_core/bin/WinDivert.dll",
            "zapret_core/bin/WinDivert64.sys",
            "zapret_core/bin/quic_initial_rutube_ru.bin",
            "zapret_core/bin/tls_clienthello_5ka_ru.bin",
            "zapret_core/bin/ACTIVE_DISCORD_UDP.bin",
            "zapret_core/bin/ACTIVE_GAME_UDP.bin",
            "zapret_core/bin/quic_initial_4pda_to.bin",
            "zapret_core/bin/quic_initial_steamcommunity_com.bin",
            "zapret_core/bin/quic_initial_tencent_com.bin",
            "zapret_core/bin/stun2.bin",
            "zapret_core/bin/quic_initial_www_google_com.bin",
            "zapret_core/bin/stun.bin",
            "zapret_core/bin/tls_clienthello_4pda_to.bin",
            "zapret_core/bin/tls_clienthello_max_ru.bin",
            "zapret_core/bin/tls_clienthello_www_google_com.bin",
            "zapret_core/bin/cygwin1.dll",
            "zapret_core/service.bat",
            "zapret_core/general.bat",
            "zapret_core/general (ALT).bat",
            "zapret_core/general (ALT2).bat",
            "zapret_core/general (ALT3).bat",
            "zapret_core/general (ALT4).bat",
            "zapret_core/general (ALT5).bat",
            "zapret_core/general (ALT6).bat",
            "zapret_core/general (ALT7).bat",
            "zapret_core/general (ALT8).bat",
            "zapret_core/general (ALT9).bat",
            "zapret_core/general (ALT10).bat",
            "zapret_core/general (ALT11).bat",
            "zapret_core/general (ALT12).bat",
            "zapret_core/general (EXP).bat",
            "zapret_core/general (FAKE TLS AUTO).bat",
            "zapret_core/general (FAKE TLS AUTO ALT).bat",
            "zapret_core/general (FAKE TLS AUTO ALT2).bat",
            "zapret_core/general (FAKE TLS AUTO ALT3).bat",
            "zapret_core/general (SIMPLE FAKE).bat",
            "zapret_core/general (SIMPLE FAKE ALT).bat",
            "zapret_core/general (SIMPLE FAKE ALT2).bat",
            "resources/icon.ico",
            "config.json",
        ]
        
        for path in checks:
            full_path = APPDATA_DIR / path
            if not full_path.exists():
                missing_files.append(path)
        
        lists_dir = APPDATA_DIR / "zapret_core/lists"
        if lists_dir.exists():
            list_files = [
                "ipset-all.txt",
                "ipset-all.txt.backup",
                "ipset-white.txt",
                "ipset-white-user.txt",
                "list-white.txt",
                "list-custom.txt",
                "list-general.txt",
                "list-google.txt"
            ]
            for list_file in list_files:
                if not (lists_dir / list_file).exists():
                    missing_files.append(f"zapret_core/lists/{list_file}")
        else:
            missing_files.append("zapret_core/lists (Folder missing)")
        
        for folder in ["utils", "bin"]:
            folder_path = APPDATA_DIR / f"zapret_core/{folder}"
            if not folder_path.exists():
                missing_files.append(f"zapret_core/{folder} (Folder missing)")
        return len(missing_files) == 0

    def _download_and_install_zapret_core(self):
        def install_thread():
            temp_zip = None
            saved_custom_files = {}
            
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'winws.exe'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                subprocess.run(['sc', 'stop', 'WinDivert'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(1.5)
                
                zapret_dir = APPDATA_DIR / "zapret_core"
                
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
                
                req = urllib.request.Request(ZAPRET_CORE_URL, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=30) as response:
                    temp_zip = tempfile.mktemp(suffix='.zip')
                    with open(temp_zip, 'wb') as f:
                        f.write(response.read())
                
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
                        "general (EXP).bat",
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
                
                if temp_zip and Path(temp_zip).exists():
                    Path(temp_zip).unlink()
                
                self.app.root.after_idle(lambda: self._show_success_and_restart())
            
            except Exception as e:
                self.app.root.after_idle(lambda: messagebox.showerror("Error", f"Unable to reinstall kernel: {str(e)}"))
        threading.Thread(target=install_thread, daemon=True).start()

    def _show_success_and_restart(self):
        self.app.root.after(1500, self._restart_launcher)

    def _restart_launcher(self):
        try:
            winws_running = False
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() == 'winws.exe':
                        winws_running = True
                        break
                except:
                    pass
            
            tg_running = False
            if hasattr(self.app, 'tg_proxy') and self.app.tg_proxy:
                tg_running = self.app.tg_proxy.is_running
            
            if winws_running or tg_running or self.app.is_connected:
                if hasattr(self.app, 'zapret') and self.app.zapret:
                    self.app.zapret.stop_current_strategy()
                
                if tg_running and hasattr(self.app, 'tg_proxy'):
                    self.app.tg_proxy.stop()
                
                try:
                    subprocess.run(['sc', 'stop', 'WinDivert'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                except:
                    pass
                
                time.sleep(1)
                
                self.app.is_connected = False
                self.app.current_strategy = None
                
                if hasattr(self.app, 'mode_label') and self.app.mode_label:
                    self.app.mode_label.config(text=tr('mode_not_selected'), fg=self.app.colors['text_secondary'])
                if hasattr(self.app, 'connect_btn') and self.app.connect_btn:
                    self.app.connect_btn.set_text(tr('button_connect'))
        
        except Exception:
            pass
        
        self.app.save_settings()
        
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = sys.argv[0]
        
        subprocess.Popen([exe_path, '--no-splash', '--from-splash'])
        self.app.root.quit()
        self.app.root.destroy()
        sys.exit(0)
    
    def update_secret_display(self):
        if not hasattr(self, 'secret_label') or not self.secret_label:
            return
        
        try:
            if not self.secret_label.winfo_exists():
                return
        except:
            return

        if hasattr(self, 'secret_label') and self.secret_label:
            new_secret = getattr(self.app, '_tg_secret', None)
            if new_secret and len(new_secret) > 16:
                self.secret_label.config(text=f"{tr('settings_current_tg_secret')} {new_secret[:16]}...")
            elif new_secret:
                self.secret_label.config(text=f"{tr('settings_current_tg_secret')} {new_secret}")
            else:
                self.secret_label.config(text=tr('settings_current_tg_secret'))

        self.secret_label.update_idletasks()
    
    def _create_settings_card(self, parent, title, options):
        font_size_sub = self.font_size_sub if hasattr(self, 'font_size_sub') else scale_size(12, self.scale_factor)
        font_size_btn = self.font_size_btn if hasattr(self, 'font_size_btn') else scale_size(9, self.scale_factor)
        btn_width_medium = self.btn_width_medium if hasattr(self, 'btn_width_medium') else scale_size(180, self.scale_factor)
        btn_height_medium = self.btn_height_medium if hasattr(self, 'btn_height_medium') else scale_size(32, self.scale_factor)
        btn_radius = self.btn_radius if hasattr(self, 'btn_radius') else scale_size(6, self.scale_factor)
        
        card = tk.Frame(parent, bg=self.colors['bg_light'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=scale_size(4, self.scale_factor))
        
        inner = tk.Frame(card, bg=self.colors['bg_light'])
        inner.pack(fill=tk.X, padx=scale_size(8, self.scale_factor), pady=scale_size(6, self.scale_factor))
        
        title_frame = tk.Frame(inner, bg=self.colors['bg_light'])
        title_frame.pack(fill=tk.X, pady=(0, scale_size(4, self.scale_factor)))
        
        title_label = tk.Label(title_frame, text=title, font=("Inter", font_size_sub, "bold"),
                            fg=self.colors['accent'], bg=self.colors['bg_light'])
        title_label.pack(side=tk.LEFT)
        
        title_sep = tk.Frame(inner, bg=self.colors['separator'], height=1)
        title_sep.pack(fill=tk.X, pady=(0, scale_size(4, self.scale_factor)))
        
        options_container = tk.Frame(inner, bg=self.colors['bg_light'])
        options_container.pack(fill=tk.X)
        
        for i in range(0, len(options), 2):
            row = tk.Frame(options_container, bg=self.colors['bg_light'])
            row.pack(fill=tk.X, pady=1)
            
            opt1_text, opt1_cmd = options[i]
            if opt1_cmd:
                btn1 = RoundedButton(row, text=opt1_text, command=opt1_cmd,
                    width=btn_width_medium, height=btn_height_medium,
                    bg=self.colors['button_bg'],
                    fg=self.colors['text_secondary'],
                    font=("Inter", font_size_btn),
                    corner_radius=btn_radius,
                    hover_color=self.colors['accent'],
                    theme_name=self.app.current_theme)
                btn1.pack(side=tk.LEFT, padx=(0, scale_size(6, self.scale_factor)))
            
            if i + 1 < len(options):
                opt2_text, opt2_cmd = options[i + 1]
                if opt2_cmd:
                    btn2 = RoundedButton(row, text=opt2_text, command=opt2_cmd,
                        width=btn_width_medium, height=btn_height_medium,
                        bg=self.colors['button_bg'],
                        fg=self.colors['text_secondary'],
                        font=("Inter", font_size_btn),
                        corner_radius=btn_radius,
                        hover_color=self.colors['accent'],
                        theme_name=self.app.current_theme)
                    btn2.pack(side=tk.LEFT, padx=(scale_size(6, self.scale_factor), 0))
    
    def get_frame(self):
        return self.frame
