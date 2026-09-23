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
        font_size_card_name = scale_size(14, self.scale_factor)
        font_size_card_desc = scale_size(9, self.scale_factor)
        card_padx = scale_size(15, self.scale_factor)
        card_pady = scale_size(12, self.scale_factor)
        grid_gap = scale_size(10, self.scale_factor)
        padx = scale_size(30, self.scale_factor)
        pady = scale_size(10, self.scale_factor)

        self.frame = tk.Frame(parent, bg=self.colors['bg_dark'])

        title_label = tk.Label(
            self.frame,
            text=tr('settings_title'),
            font=("Segoe UI Variable", font_size_title, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        title_label.pack(anchor='w', pady=(scale_size(30, self.scale_factor), 5), padx=padx)

        desc_label = tk.Label(
            self.frame,
            text=tr('settings_desc'),
            font=("Segoe UI Variable", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark']
        )
        desc_label.pack(anchor='w', pady=(0, scale_size(20, self.scale_factor)), padx=padx)

        grid_frame = tk.Frame(self.frame, bg=self.colors['bg_dark'])
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)

        grid_frame.columnconfigure(0, weight=1, uniform="cards")
        grid_frame.columnconfigure(1, weight=1, uniform="cards")
        grid_frame.rowconfigure(0, weight=0)
        grid_frame.rowconfigure(1, weight=0)
        grid_frame.rowconfigure(2, weight=0)
        grid_frame.rowconfigure(3, weight=0)
        grid_frame.rowconfigure(4, weight=0)

        self.autoupdate_card = None
        self.autoupdate_name_label = None
        self.autoupdate_desc_label = None
        self.analytics_card = None
        self.analytics_name_label = None
        self.analytics_desc_label = None
        self.vpn_detect_card = None
        self.vpn_detect_name_label = None
        self.vpn_detect_desc_label = None
        self.duplicate_detect_card = None
        self.duplicate_detect_name_label = None
        self.duplicate_detect_desc_label = None

        self._create_card(
            grid_frame, row=0, col=0,
            name=tr('settings_theme'),
            desc=tr('settings_theme_desc'),
            command=self._show_theme_selector,
            padx=(0, grid_gap // 2), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady
        )

        self._create_card(
            grid_frame, row=0, col=1,
            name=tr('settings_language'),
            desc=tr('settings_language_desc'),
            command=self._show_language_selector,
            padx=(grid_gap // 2, 0), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady
        )

        self._create_card(
            grid_frame, row=1, col=0,
            name="Telegram Proxy",
            desc=tr('settings_tgproxy_desc'),
            command=self._show_tgproxy_settings,
            padx=(0, grid_gap // 2), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady
        )

        self.autoupdate_card, self.autoupdate_name_label, self.autoupdate_desc_label = self._create_card(
            grid_frame, row=2, col=0,
            name=self._get_autoupdate_card_name(),
            desc=self._get_autoupdate_card_desc(),
            command=self._toggle_auto_update,
            padx=(0, grid_gap // 2), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady,
            return_widgets=True
        )

        self.analytics_card, self.analytics_name_label, self.analytics_desc_label = self._create_card(
            grid_frame, row=1, col=1,
            name=self._get_analytics_card_name(),
            desc=self._get_analytics_card_desc(),
            command=self._toggle_analytics,
            padx=(grid_gap // 2, 0), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady,
            return_widgets=True
        )

        self._create_card(
            grid_frame, row=3, col=0,
            name=tr('settings_integrity'),
            desc=tr('settings_integrity_desc'),
            command=self._show_integrity_placeholder,
            padx=(0, grid_gap // 2), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady
        )

        self._create_card(
            grid_frame, row=2, col=1,
            name=tr('settings_reinstall'),
            desc=tr('settings_reinstall_desc'),
            command=self._reinstall_files,
            padx=(grid_gap // 2, 0), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady
        )

        self._create_card(
            grid_frame, row=3, col=1,
            name=tr('settings_autostart'),
            desc=tr('settings_autostart_desc'),
            command=self.app.toggle_autostart,
            padx=(grid_gap // 2, 0), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady
        )

        self.vpn_detect_card, self.vpn_detect_name_label, self.vpn_detect_desc_label = self._create_card(
            grid_frame, row=4, col=1,
            name=self._get_vpn_detect_card_name(),
            desc=self._get_vpn_detect_card_desc(),
            command=self._toggle_vpn_detection,
            padx=(grid_gap // 2, 0), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady,
            return_widgets=True
        )

        self.duplicate_detect_card, self.duplicate_detect_name_label, self.duplicate_detect_desc_label = self._create_card(
            grid_frame, row=4, col=0,
            name=self._get_duplicate_detect_card_name(),
            desc=self._get_duplicate_detect_card_desc(),
            command=self._toggle_duplicate_detection,
            padx=(0, grid_gap // 2), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady,
            return_widgets=True
        )

    def _create_card(self, parent, row, col, name, desc, command,
                     padx, pady, font_size_name, font_size_desc,
                     card_padx, card_pady, return_widgets=False):

        card = tk.Frame(parent, bg=self.colors['bg_light'], cursor="hand2",
                        height=scale_size(80, self.scale_factor))
        card.grid(row=row, column=col, sticky='nsew', padx=padx, pady=pady)
        card.pack_propagate(False)
        card.grid_propagate(False)

        inner = tk.Frame(card, bg=self.colors['bg_light'])
        inner.pack(fill=tk.BOTH, expand=True, padx=card_padx, pady=card_pady)

        name_label = tk.Label(
            inner,
            text=name,
            font=("Segoe UI Variable", font_size_name, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['bg_light'],
            anchor='w',
            justify=tk.LEFT
        )
        name_label.pack(anchor='w', fill=tk.X)

        desc_label = tk.Label(
            inner,
            text=desc,
            font=("Segoe UI Variable", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_light'],
            anchor='w',
            justify=tk.LEFT,
            wraplength=scale_size(300, self.scale_factor)
        )
        desc_label.pack(anchor='w', fill=tk.X, pady=(scale_size(4, self.scale_factor), 0))

        def on_enter(e):
            card.configure(bg=self.colors['bg_light_hover'])
            inner.configure(bg=self.colors['bg_light_hover'])
            name_label.configure(bg=self.colors['bg_light_hover'])
            desc_label.configure(bg=self.colors['bg_light_hover'])

        def on_leave(e):
            card.configure(bg=self.colors['bg_light'])
            inner.configure(bg=self.colors['bg_light'])
            name_label.configure(bg=self.colors['bg_light'])
            desc_label.configure(bg=self.colors['bg_light'])

        def on_click(e):
            command()

        for widget in (card, inner, name_label, desc_label):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

        if return_widgets:
            return card, name_label, desc_label
        return card

    def _get_autoupdate_card_name(self):
        return tr('settings_autoupdate')

    def _get_autoupdate_card_desc(self):
        if getattr(self.app, '_auto_update_enabled', True):
            return tr('settings_button_on')
        else:
            return tr('settings_button_off')

    def _get_analytics_card_name(self):
        return tr('settings_analytics')

    def _get_analytics_card_desc(self):
        if getattr(self.app, '_analytics_enabled', True):
            return tr('settings_button_on')
        else:
            return tr('settings_button_off')

    def _get_vpn_detect_card_name(self):
        return tr('settings_search_vpn')

    def _get_vpn_detect_card_desc(self):
        if getattr(self.app, '_show_vpn_detection', False):
            return tr('settings_button_on')
        else:
            return tr('settings_button_off')

    def _get_duplicate_detect_card_name(self):
        return tr('settings_search_dublicate')

    def _get_duplicate_detect_card_desc(self):
        if getattr(self.app, '_hide_duplicates_warning', False):
            return tr('settings_button_off')
        else:
            return tr('settings_button_on')

    def _refresh_autoupdate_card(self):
        if self.autoupdate_desc_label and self.autoupdate_desc_label.winfo_exists():
            self.autoupdate_desc_label.config(text=self._get_autoupdate_card_desc())

    def _refresh_analytics_card(self):
        if self.analytics_desc_label and self.analytics_desc_label.winfo_exists():
            self.analytics_desc_label.config(text=self._get_analytics_card_desc())

    def _refresh_vpn_detect_card(self):
        if self.vpn_detect_desc_label and self.vpn_detect_desc_label.winfo_exists():
            self.vpn_detect_desc_label.config(text=self._get_vpn_detect_card_desc())

    def _refresh_duplicate_detect_card(self):
        if self.duplicate_detect_desc_label and self.duplicate_detect_desc_label.winfo_exists():
            self.duplicate_detect_desc_label.config(text=self._get_duplicate_detect_card_desc())

    def update_buttons(self):
        self._refresh_autoupdate_card()
        self._refresh_analytics_card()
        self._refresh_vpn_detect_card()
        self._refresh_duplicate_detect_card()

    def _update_autoupdate_button(self):
        self._refresh_autoupdate_card()

    def _update_analytics_button(self):
        self._refresh_analytics_card()

    def _toggle_auto_update(self):
        self.app.toggle_auto_update()
        self._refresh_autoupdate_card()

    def _toggle_analytics(self):
        self.app.toggle_analytics()
        self._refresh_analytics_card()

    def _toggle_vpn_detection(self):
        self.app.toggle_vpn_detection()
        self._refresh_vpn_detect_card()

    def _toggle_duplicate_detection(self):
        self.app.toggle_hide_duplicates_warning()
        self._refresh_duplicate_detect_card()

    def _show_theme_selector(self):
        self.app.dialogs.show_theme_selector()

    def _show_language_selector(self):
        self.app.dialogs.show_language_selector()

    def _show_tgproxy_settings(self):
        self.app.dialogs.show_tgproxy_settings()

    def _change_theme(self, new_theme):
        current_theme = self.app.current_theme
        if new_theme != current_theme:
            result = messagebox.showwarning(
                tr('restart_manual_title'),
                tr('restart_manual_message') + "\n\n",
                type=messagebox.OKCANCEL
            )
            if result == 'ok':
                self.app.show_notification(tr('please_wait'), 1500)
                self.app.current_theme = new_theme
                self.app.save_settings()
                self.app.root.after(1500, self._restart_launcher)

    def _change_language(self, new_lang):
        current_lang = self.app.languages.get_current_language()
        if new_lang != current_lang:
            result = messagebox.showwarning(
                tr('restart_manual_title'),
                tr('restart_manual_message') + "\n\n",
                type=messagebox.OKCANCEL
            )
            if result == 'ok':
                self.app.show_notification(tr('please_wait'), 1500)
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
            ("zapret_core/bin/tls_clienthello_www_sferum_ru.bin", "tls_clienthello_www_sferum_ru.bin"),
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
            ("zapret_core/general (ALT13).bat", "general (ALT13).bat"),
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

    def _get_instruction_button_text(self):
        if getattr(self.app, '_tg_instruction', False):
            return tr('tg_instruction_settings_show')
        return tr('tg_instruction_settings_hide')

    def _show_instruction(self):
        self.app._tg_instruction = not self.app._tg_instruction
        self.app.save_settings()

        if self.app._tg_instruction:
            self.app.show_notification(tr('tg_instruction_hidden'), 1500)
        else:
            self.app.show_notification(tr('tg_instruction_shown'), 1500)

    def _regenerate_secret(self):
        self.app.regenerate_tg_secret()

    def update_secret_display(self):
        pass

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
            "zapret_core/bin/tls_clienthello_www_sferum_ru.bin",
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
            "zapret_core/general (ALT13).bat",
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
                        "general (ALT13).bat",
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

    def _restart_launcher(self):
        try:
            try:
                self.app.save_settings()
            except Exception:
                pass
            
            winws_running = False
            if hasattr(self.app, 'zapret') and self.app.zapret:
                winws_running = self.app.zapret.is_winws_running()
            
            tg_running = False
            if hasattr(self.app, 'tg_proxy') and self.app.tg_proxy:
                tg_running = self.app.tg_proxy.is_running
            
            if winws_running or tg_running or getattr(self.app, 'is_connected', False):
                if hasattr(self.app, 'zapret') and self.app.zapret:
                    try:
                        self.app.zapret.stop_current_strategy()
                    except Exception:
                        pass
                
                if tg_running and hasattr(self.app, 'tg_proxy'):
                    try:
                        self.app.tg_proxy.stop()
                    except Exception:
                        pass
                
                try:
                    subprocess.run(['sc', 'stop', 'WinDivert'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
                except Exception:
                    pass
                
                time.sleep(1)
                
                self.app.is_connected = False
                self.app.current_strategy = None
                
                if hasattr(self.app, 'mode_label') and self.app.mode_label:
                    try:
                        self.app.mode_label.config(text=tr('mode_not_selected'), fg=self.app.colors['text_secondary'])
                    except Exception:
                        pass
                
                if hasattr(self.app, 'connect_btn') and self.app.connect_btn:
                    try:
                        self.app.connect_btn.set_text(tr('button_connect'))
                    except Exception:
                        pass
        
        except Exception:
            pass
        
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = sys.argv[0]
        
        try:
            subprocess.Popen([exe_path, '--no-splash', '--from-splash'], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS, close_fds=True)
        except Exception as e:
            try:
                messagebox.showerror(tr('error'), f"{tr('error_restart_launcher')}:\n{e}")
            except Exception:
                pass
            return
        
        try:
            self.app.root.quit()
            self.app.root.destroy()
        except Exception:
            pass
        
        sys.exit(0)

    def get_frame(self):
        return self.frame
