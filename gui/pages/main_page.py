# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
import customtkinter as ctk
from utils.messagebox import messagebox
import webbrowser
from pathlib import Path
from PIL import Image, ImageTk, ImageEnhance
import sys
from utils.languages import tr
from utils.scaling import scale_size

class CTkButtonWrapper(ctk.CTkButton):
    def set_text(self, text):
        try:
            self.configure(text=text)
        except Exception:
            pass

    def set_enabled(self, enabled):
        fg = tc = hc = None
        try:
            fg = self.cget("fg_color")
        except Exception:
            pass
        try:
            tc = self.cget("text_color")
        except Exception:
            pass
        try:
            hc = self.cget("hover_color")
        except Exception:
            pass

        try:
            self.configure(state="normal" if enabled else "disabled")
        except Exception:
            pass

        try:
            if fg is not None:
                self.configure(fg_color=fg)
        except Exception:
            pass
        try:
            if tc is not None:
                self.configure(text_color=tc)
        except Exception:
            pass
        try:
            if hc is not None:
                self.configure(hover_color=hc)
        except Exception:
            pass

    def update_colors(self, bg_color, fg_color, hover_color):
        try:
            self.configure(fg_color=bg_color, text_color=fg_color, hover_color=hover_color)
        except Exception:
            for kw, val in (("fg_color", bg_color), ("text_color", fg_color), ("hover_color", hover_color)):
                try:
                    if val is not None:
                        self.configure(**{kw: val})
                except Exception:
                    pass

class MainPage:
    def __init__(self, parent, app):
        self.app = app
        self.colors = app.colors
        self.font_primary = app.font_primary
        self.font_medium = app.font_medium
        self.font_bold = app.font_bold
        self.scale_factor = getattr(app, 'scale_factor', 1.0)
        
        font_mono_title = ("Inter", scale_size(24, self.scale_factor), "bold")
        font_mono_desc = ("Inter", scale_size(12, self.scale_factor))
        font_mono_large = ("Inter", scale_size(18, self.scale_factor), "bold")
        font_mono_med = ("Inter", scale_size(14, self.scale_factor), "bold")
        font_mono_small = ("Inter", scale_size(11, self.scale_factor))
        font_mono_btn = ("Inter", scale_size(15, self.scale_factor), "bold")

        padx = scale_size(30, self.scale_factor)
        pady = scale_size(20, self.scale_factor)
        corner_r = scale_size(6, self.scale_factor)

        self.frame = ctk.CTkFrame(parent, fg_color=self.colors['bg_dark'], corner_radius=0)
        
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent", corner_radius=0)
        header_frame.pack(fill=tk.X, padx=padx, pady=(scale_size(30, self.scale_factor), scale_size(10, self.scale_factor)))
        
        ctk.CTkLabel(
            header_frame,
            text=tr('main_title'),
            font=font_mono_title,
            text_color=self.colors['text_primary']
        ).pack(anchor='w')
        
        ctk.CTkLabel(
            header_frame,
            text=tr('main_desc'),
            font=font_mono_desc,
            text_color=self.colors['text_secondary']
        ).pack(anchor='w', pady=(2, 0))

        ctk.CTkFrame(self.frame, fg_color=self.colors['separator'], height=1, corner_radius=0).pack(fill=tk.X, padx=padx, pady=(0, scale_size(15, self.scale_factor)))

        info_grid = ctk.CTkFrame(self.frame, fg_color="transparent", corner_radius=0)
        info_grid.pack(fill=tk.X, padx=padx, pady=(0, scale_size(15, self.scale_factor)))
        
        info_grid.columnconfigure(0, weight=1, uniform="col")
        info_grid.columnconfigure(1, weight=1, uniform="col")

        def make_info_block(parent, row, col, label, initial_text, text_color=None):
            block = ctk.CTkFrame(
                parent, 
                fg_color=self.colors['bg_medium'], 
                border_width=1, 
                border_color=self.colors['separator'],
                corner_radius=corner_r
            )
            block.grid(row=row, column=col, sticky="nsew", padx=(0 if col == 0 else scale_size(10, self.scale_factor), 0), pady=(0 if row == 0 else scale_size(10, self.scale_factor), 0))
            
            inner = ctk.CTkFrame(block, fg_color="transparent", corner_radius=0)
            inner.pack(padx=scale_size(15, self.scale_factor), pady=scale_size(10, self.scale_factor), fill=tk.BOTH, expand=True)
            
            ctk.CTkLabel(
                inner, 
                text=label.upper(), 
                font=font_mono_small, 
                text_color=self.colors['text_secondary']
            ).pack(anchor='w')
            
            val_lbl = ctk.CTkLabel(
                inner, 
                text=initial_text, 
                font=font_mono_large, 
                text_color=text_color if text_color else self.colors['text_primary']
            )
            val_lbl.pack(anchor='w', pady=(scale_size(2, self.scale_factor), 0))
            return val_lbl

        self.app.main_status = make_info_block(info_grid, 0, 0, tr('status'), tr('status_ready').upper(), self.colors['text_secondary'])
        self.app.mode_label = make_info_block(info_grid, 0, 1, tr('mode'), tr('mode_not_selected').upper(), self.colors['text_secondary'])
        
        self.app.stats_time_label = make_info_block(info_grid, 1, 0, tr('stats_time'), "00:00:00")
        self.app.stats_traffic_label = make_info_block(info_grid, 1, 1, tr('traffic'), "⬇ 0 B | ⬆ 0 B")

        self.app.stats_speed_up_label = ctk.CTkLabel(self.frame, text="", width=0, height=0)
        self.app.stats_speed_down_label = ctk.CTkLabel(self.frame, text="", width=0, height=0)
        self.app.stats_total_label = ctk.CTkLabel(self.frame, text="", width=0, height=0)
        self.app.stats_rtt_label = ctk.CTkLabel(self.frame, text="-- ms", width=0, height=0)
        self.app.stats_frame = info_grid

        config_card = ctk.CTkFrame(
            self.frame, 
            fg_color=self.colors['bg_medium'], 
            border_width=1,
            border_color=self.colors['separator'],
            corner_radius=corner_r
        )
        config_card.pack(fill=tk.X, padx=padx, pady=(0, scale_size(15, self.scale_factor)))
        
        config_inner = ctk.CTkFrame(config_card, fg_color="transparent", corner_radius=0)
        config_inner.pack(fill=tk.X, padx=scale_size(20, self.scale_factor), pady=scale_size(15, self.scale_factor))
        
        ctk.CTkLabel(config_inner, text="TELEGRAM PROXY", font=font_mono_med, text_color=self.colors['accent']).pack(anchor='w', pady=(0, scale_size(10, self.scale_factor)))
        
        row_1 = ctk.CTkFrame(config_inner, fg_color="transparent", corner_radius=0)
        row_1.pack(fill=tk.X, pady=(0, scale_size(10, self.scale_factor)))
        
        host_f = ctk.CTkFrame(row_1, fg_color="transparent", corner_radius=0)
        host_f.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, scale_size(10, self.scale_factor)))
        ctk.CTkLabel(host_f, text=tr('main_page_tg_proxy_host'), font=font_mono_small, text_color=self.colors['text_secondary']).pack(anchor='w')
        self.tg_host_entry = ctk.CTkEntry(host_f, font=font_mono_small, height=scale_size(28, self.scale_factor), fg_color=self.colors['bg_dark'], text_color=self.colors['text_primary'], border_color=self.colors['separator'], corner_radius=corner_r)
        self.tg_host_entry.pack(fill=tk.X, pady=(2,0))
        
        port_f = ctk.CTkFrame(row_1, fg_color="transparent", corner_radius=0, width=scale_size(80, self.scale_factor))
        port_f.pack(side=tk.RIGHT)
        ctk.CTkLabel(port_f, text=tr('main_page_tg_proxy_port'), font=font_mono_small, text_color=self.colors['text_secondary']).pack(anchor='w')
        self.tg_port_entry = ctk.CTkEntry(port_f, font=font_mono_small, height=scale_size(28, self.scale_factor), fg_color=self.colors['bg_dark'], text_color=self.colors['text_primary'], border_color=self.colors['separator'], corner_radius=corner_r)
        self.tg_port_entry.pack(fill=tk.X, pady=(2,0))

        row_2 = ctk.CTkFrame(config_inner, fg_color="transparent", corner_radius=0)
        row_2.pack(fill=tk.X, pady=(0, scale_size(10, self.scale_factor)))
        
        tls_f = ctk.CTkFrame(row_2, fg_color="transparent", corner_radius=0)
        tls_f.pack(side=tk.LEFT, padx=(0, scale_size(10, self.scale_factor)))
        ctk.CTkLabel(tls_f, text="FAKE TLS:", font=font_mono_small, text_color=self.colors['text_secondary']).pack(anchor='w')
        
        self.fake_tls_var = tk.BooleanVar(value=True)
        self.fake_tls_switch = ctk.CTkSwitch(tls_f, text="", variable=self.fake_tls_var, width=scale_size(40, self.scale_factor), progress_color=self.colors['accent'], button_color=self.colors['text_primary'])
        self.fake_tls_switch.pack(anchor='w', pady=(2,0))

        dom_f = ctk.CTkFrame(row_2, fg_color="transparent", corner_radius=0)
        dom_f.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ctk.CTkLabel(dom_f, text=tr('main_page_tg_proxy_domain'), font=font_mono_small, text_color=self.colors['text_secondary']).pack(anchor='w')
        self.tg_domain_entry = ctk.CTkEntry(dom_f, font=font_mono_small, height=scale_size(28, self.scale_factor), fg_color=self.colors['bg_dark'], text_color=self.colors['text_primary'], border_color=self.colors['separator'], corner_radius=corner_r)
        self.tg_domain_entry.pack(fill=tk.X, pady=(2,0))

        btn_row = ctk.CTkFrame(config_inner, fg_color="transparent", corner_radius=0)
        btn_row.pack(fill=tk.X, pady=(scale_size(5, self.scale_factor), 0))
        
        apply_btn = ctk.CTkButton(btn_row, text=tr('button_apply').upper(), command=self.save_tg_proxy_settings, height=scale_size(28, self.scale_factor), fg_color=self.colors['bg_light'], hover_color=self.colors['accent'], text_color=self.colors['text_primary'], font=font_mono_small, corner_radius=corner_r)
        apply_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, scale_size(5, self.scale_factor)))
        
        copy_btn = ctk.CTkButton(btn_row, text=tr('tg_copy_secret').upper(), command=self.copy_current_link, height=scale_size(28, self.scale_factor), fg_color=self.colors['bg_light'], hover_color=self.colors['accent'], text_color=self.colors['text_primary'], font=font_mono_small, corner_radius=corner_r)
        copy_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(scale_size(5, self.scale_factor), 0))

        btn_container = ctk.CTkFrame(self.frame, fg_color="transparent", corner_radius=0)
        btn_container.pack(fill=tk.X, padx=padx, pady=(0, scale_size(10, self.scale_factor)))
        
        self.app.connect_btn = CTkButtonWrapper(
            btn_container,
            text=tr('button_connect').upper(),
            command=self.app.toggle_connection,
            height=scale_size(45, self.scale_factor),
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent'],
            text_color=self.colors['button_text_hover'],
            font=font_mono_btn,
            corner_radius=corner_r
        )
        self.app.connect_btn.pack(fill=tk.X)

        self.icons_frame = ctk.CTkFrame(self.frame, fg_color="transparent", corner_radius=0)
        self.icons_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=padx, pady=(0, scale_size(15, self.scale_factor)))
        self._create_icon_buttons(scale_size(24, self.scale_factor))
        
        self.load_tg_proxy_settings()
        self._setup_focus_handling()

    def load_tg_proxy_settings(self):
        if hasattr(self.app, 'tg_host'):
            self.tg_host_entry.delete(0, tk.END)
            self.tg_host_entry.insert(0, self.app.tg_host)
        
        if hasattr(self.app, 'tg_port'):
            self.tg_port_entry.delete(0, tk.END)
            self.tg_port_entry.insert(0, str(self.app.tg_port))
            
        if hasattr(self.app, 'tg_fake_tls'):
            self.fake_tls_var.set(self.app.tg_fake_tls)
        
        if hasattr(self.app, 'tg_fake_tls_domain'):
            self.tg_domain_entry.delete(0, tk.END)
            self.tg_domain_entry.insert(0, self.app.tg_fake_tls_domain)

    def save_tg_proxy_settings(self):
        try:
            new_host = self.tg_host_entry.get().strip()
            new_port = int(self.tg_port_entry.get().strip())
            new_fake_tls = self.fake_tls_var.get()
            new_domain = self.tg_domain_entry.get().strip()

            settings_changed = (
                new_host != self.app.tg_host or
                new_port != self.app.tg_port or
                new_fake_tls != self.app.tg_fake_tls or
                new_domain != self.app.tg_fake_tls_domain
            )

            if not settings_changed:
                return

            if new_host == "0.0.0.0":
                confirm = messagebox.askyesno(
                    tr('error_warning'),
                    tr('tg_proxy_bind_all_warning')
                )
                if not confirm:
                    self.load_tg_proxy_settings()
                    return

            self.app.tg_host = new_host
            self.app.tg_port = new_port
            self.app.tg_fake_tls = new_fake_tls
            self.app.tg_fake_tls_domain = new_domain

            if hasattr(self.app, 'tg_proxy'):
                self.app.tg_proxy._host = new_host
                self.app.tg_proxy._port = new_port
                self.app.tg_proxy._fake_tls_domain = new_domain if new_fake_tls else ''

            self.app.save_settings()
            self.app.show_notification(tr('notification_save_settings'), 2000)

        except ValueError:
            self.app.show_notification(tr('error_port_have_words'), 2000)

    def _setup_focus_handling(self):
        def remove_focus(event=None):
            focused = self.app.root.focus_get()
            if focused and isinstance(focused, (ctk.CTkEntry, tk.Entry, tk.Text)):
                if event and event.widget != focused:
                    self.app.root.focus_set()
        
        self.app.root.bind_all("<Button-1>", remove_focus)

    def copy_current_link(self):
        secret = getattr(self.app, '_tg_secret', None)
        if secret:
            if self.app.tg_fake_tls and self.app.tg_fake_tls_domain:
                domain_hex = self.app.tg_fake_tls_domain.encode('ascii').hex()
                link = f"ee{secret}{domain_hex}"
            else:
                link = secret
                    
            self.app.root.clipboard_clear()
            self.app.root.clipboard_append(link)
            self.app.root.update()
            self.app.show_notification(tr('notification_copied_secret'), 2000)
        else:
            messagebox.showwarning(tr('error_secret_not_found'), tr('error_telegram_proxy_start'))

    def _get_icon_path(self, filename):
        base_path = Path("resources") / filename
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS) / "resources" / filename
        return base_path

    def _create_icon_buttons(self, icon_size):
        icon_size_tuple = (icon_size, icon_size)
        
        icons = [
            ("tg.png", "https://t.me/zapret_launcher"),
            ("star.png", "https://github.com/avaxngard/zapret-launcher")
        ]
        
        for icon_file, url in icons:
            icon_path = self._get_icon_path(icon_file)
            if icon_path.exists():
                img = Image.open(icon_path)
                img = img.resize(icon_size_tuple, Image.Resampling.LANCZOS)
                img = img.convert('RGBA')
                
                if icon_file == "star.png":
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(0.6)
                
                photo = ImageTk.PhotoImage(img)
                
                btn = ctk.CTkLabel(self.icons_frame, image=photo, text="", fg_color="transparent", cursor="hand2")
                btn.image = photo
                btn.url = url
                
                btn.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
                btn.pack(side=tk.RIGHT, padx=scale_size(5, self.scale_factor))
    
    def get_frame(self):
        return self.frame
