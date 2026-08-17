# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
from gui.widgets import RoundedButton
import webbrowser
from pathlib import Path
from PIL import Image, ImageTk, ImageEnhance
import sys
from utils.languages import tr
from utils.scaling import scale_size

class MainPage:
    def __init__(self, parent, app):
        self.app = app
        self.colors = app.colors
        self.font_primary = app.font_primary
        self.font_medium = app.font_medium
        self.font_bold = app.font_bold
        self.scale_factor = getattr(app, 'scale_factor', 1.0)
        
        font_size_title = scale_size(20, self.scale_factor)
        font_size_desc = scale_size(10, self.scale_factor)
        font_size_stats = scale_size(18, self.scale_factor)
        font_size_rtt = scale_size(16, self.scale_factor)
        font_size_btn = scale_size(18, self.scale_factor)
        font_size_small = scale_size(12, self.scale_factor)
        btn_width = scale_size(350, self.scale_factor)
        btn_height = scale_size(60, self.scale_factor)
        btn_radius = scale_size(15, self.scale_factor)
        right_column_width = scale_size(340, self.scale_factor)
        stats_height = scale_size(80, self.scale_factor)
        stats_width = scale_size(550, self.scale_factor)
        icon_size = scale_size(24, self.scale_factor)
        padx = scale_size(30, self.scale_factor)
        pady = scale_size(20, self.scale_factor)
        
        self.frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        
        header_frame = tk.Frame(self.frame, bg=self.colors['bg_dark'])
        header_frame.pack(fill=tk.X, padx=padx, pady=(scale_size(30, self.scale_factor), 5))
        
        title_label = tk.Label(
            header_frame, 
            text=tr('main_title'), 
            font=("Inter", font_size_title, "bold"),
            fg=self.colors['text_primary'], 
            bg=self.colors['bg_dark']
        )
        title_label.pack(anchor='w')
        
        desc_label = tk.Label(
            header_frame,
            text=tr('main_desc'),
            font=("Inter", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark']
        )
        desc_label.pack(anchor='w', pady=(5, 0))
        
        main_content = tk.Frame(self.frame, bg=self.colors['bg_dark'])
        main_content.pack(fill=tk.BOTH, expand=True, padx=padx, pady=(pady, pady))
        
        left_column = tk.Frame(main_content, bg=self.colors['bg_dark'])
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, scale_size(15, self.scale_factor)))
        
        right_column = tk.Frame(main_content, bg=self.colors['bg_dark'], width=right_column_width)
        right_column.pack(side=tk.RIGHT, fill=tk.Y, padx=(scale_size(15, self.scale_factor), 0))
        right_column.pack_propagate(False)
        
        status_frame = tk.Frame(left_column, bg=self.colors['bg_light'])
        status_frame.pack(fill=tk.X, pady=(0, scale_size(15, self.scale_factor)))
        
        tk.Label(status_frame, text=tr('status'), font=self.font_bold, 
                fg=self.colors['text_primary'], bg=self.colors['bg_light']).pack(side=tk.LEFT, padx=scale_size(15, self.scale_factor), pady=scale_size(10, self.scale_factor))
        
        self.app.main_status = tk.Label(status_frame, text=tr('status_ready'), font=self.font_medium,
                                        fg=self.colors['text_secondary'], bg=self.colors['bg_light'])
        self.app.main_status.pack(side=tk.LEFT, padx=5, pady=scale_size(10, self.scale_factor))
        
        mode_frame = tk.Frame(left_column, bg=self.colors['bg_light'])
        mode_frame.pack(fill=tk.X, pady=(0, scale_size(15, self.scale_factor)))
        
        tk.Label(mode_frame, text=tr('mode'), font=self.font_bold,
                fg=self.colors['text_primary'], bg=self.colors['bg_light']).pack(side=tk.LEFT, padx=scale_size(15, self.scale_factor), pady=scale_size(10, self.scale_factor))
        
        self.app.mode_label = tk.Label(mode_frame, text=tr('mode_not_selected'), font=self.font_medium,
                                    fg=self.colors['text_secondary'], bg=self.colors['bg_light'])
        self.app.mode_label.pack(side=tk.LEFT, padx=7, pady=scale_size(10, self.scale_factor))
        
        self.app.stats_frame = tk.Frame(left_column, bg=self.colors['bg_light'])
        self.app.stats_frame.pack(fill=tk.X, pady=(0, scale_size(15, self.scale_factor)), ipadx=scale_size(20, self.scale_factor), ipady=scale_size(15, self.scale_factor))
        
        tk.Label(self.app.stats_frame, text=tr('stats_session'), font=("Inter", scale_size(14, self.scale_factor), "bold"),
            fg=self.colors['text_primary'], bg=self.colors['bg_light']).pack(anchor='w', padx=scale_size(15, self.scale_factor), pady=(scale_size(8, self.scale_factor), 5))
        
        stats_row1 = tk.Frame(self.app.stats_frame, bg=self.colors['bg_light'])
        stats_row1.pack(fill=tk.X, padx=scale_size(15, self.scale_factor), pady=2)
        
        self.app.stats_time_label = tk.Label(stats_row1, text="00:00:00", font=("Inter", font_size_stats, "bold"),
                                            fg=self.colors['accent'], bg=self.colors['bg_light'])
        self.app.stats_time_label.pack(side=tk.LEFT)
        
        tk.Label(stats_row1, text=tr('stats_time'), font=self.font_primary,
                fg=self.colors['text_secondary'], bg=self.colors['bg_light']).pack(side=tk.LEFT, padx=(5, scale_size(20, self.scale_factor)))
        
        self.app.stats_traffic_label = tk.Label(stats_row1, text="⬇ 0 B  |  ⬆ 0 B", font=("Inter", font_size_small),
                                                fg=self.colors['text_primary'], bg=self.colors['bg_light'])
        self.app.stats_traffic_label.pack(side=tk.LEFT, padx=(0, scale_size(20, self.scale_factor)))
        self.app.stats_total_label = tk.Label(stats_row1, text="0 B", font=("Inter", font_size_small),
                                            fg=self.colors['text_secondary'], bg=self.colors['bg_light'])
        self.app.stats_total_label.pack(side=tk.LEFT)
        
        stats_speed_frame = tk.Frame(self.app.stats_frame, bg=self.colors['bg_light'])
        stats_speed_frame.pack(fill=tk.X, padx=scale_size(15, self.scale_factor), pady=(scale_size(10, self.scale_factor), 5))

        stats_container = tk.Frame(stats_speed_frame, bg=self.colors['bg_light'], width=stats_width, height=stats_height)
        stats_container.pack(anchor='w')
        stats_container.pack_propagate(False)

        speed_frame = tk.Frame(stats_container, bg=self.colors['bg_light'])
        speed_frame.place(x=0, y=0, width=scale_size(300, self.scale_factor), height=stats_height)
        
        tk.Label(speed_frame, text=tr('stats_speed'), font=self.font_bold,
                fg=self.colors['text_primary'], bg=self.colors['bg_light']).pack(anchor='w')
        
        self.app.stats_speed_up_label = tk.Label(speed_frame, text="⬆ 0 B/s", font=self.font_primary,
                                                fg=self.colors['accent'], bg=self.colors['bg_light'])
        self.app.stats_speed_up_label.pack(anchor='w', pady=(scale_size(5, self.scale_factor), 2))
        
        self.app.stats_speed_down_label = tk.Label(speed_frame, text="⬇ 0 B/s", font=self.font_primary,
                                                fg=self.colors['accent'], bg=self.colors['bg_light'])
        self.app.stats_speed_down_label.pack(anchor='w', pady=2)

        rtt_frame = tk.Frame(stats_container, bg=self.colors['bg_light'])
        rtt_frame.place(x=scale_size(320, self.scale_factor), y=0, width=scale_size(230, self.scale_factor), height=stats_height)
        
        tk.Label(rtt_frame, text=tr('stats_rtt'), font=self.font_bold,
                fg=self.colors['text_primary'], bg=self.colors['bg_light']).pack(anchor='w')
        
        self.app.stats_rtt_label = tk.Label(rtt_frame, text="-- ms", font=("Inter", font_size_rtt, "bold"),
                                            fg=self.colors['accent'], bg=self.colors['bg_light'])
        self.app.stats_rtt_label.pack(anchor='w', pady=(scale_size(5, self.scale_factor), 0))
        
        button_frame = tk.Frame(left_column, bg=self.colors['bg_dark'])
        button_frame.pack(fill=tk.X, pady=(scale_size(10, self.scale_factor), 0))
        
        self.app.connect_btn = RoundedButton(button_frame, text=tr('button_connect'), command=self.app.toggle_connection,
                                    width=btn_width, height=btn_height, bg=self.colors['accent'], 
                                    font=("Inter", font_size_btn, "bold"), corner_radius=btn_radius,
                                    theme_name=self.app.current_theme)
        self.app.connect_btn.hover_color = '#3D3D45'
        self.app.connect_btn.pack()
        
        self._create_tg_proxy_card(right_column, font_size_small)
        self.frame.update_idletasks()
        
        self.icons_frame = tk.Frame(self.frame, bg=self.colors['bg_dark'])
        self.icons_frame.pack(side=tk.BOTTOM, anchor='se', padx=scale_size(20, self.scale_factor), pady=scale_size(15, self.scale_factor))
        self._create_icon_buttons(icon_size)
        self._setup_focus_handling()
        self.load_tg_proxy_settings()

    def load_tg_proxy_settings(self):
        if hasattr(self.app, 'tg_host'):
            self.tg_host_entry.delete(0, tk.END)
            self.tg_host_entry.insert(0, self.app.tg_host)
        
        if hasattr(self.app, 'tg_port'):
            self.tg_port_entry.delete(0, tk.END)
            self.tg_port_entry.insert(0, str(self.app.tg_port))
        
        if hasattr(self.app, 'tg_fake_tls'):
            self.fake_tls_var.set(self.app.tg_fake_tls)
            if self.app.tg_fake_tls:
                self.fake_tls_text.config(text=tr('status_enabled'), fg=self.colors['accent_green'])
            else:
                self.fake_tls_text.config(text=tr('status_disabled'), fg=self.colors['text_secondary'])
        
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
            if focused and isinstance(focused, (tk.Entry, tk.Text)):
                if event and event.widget != focused:
                    self.app.root.focus_set()
        
        self.app.root.bind_all("<Button-1>", remove_focus)

    def _create_tg_proxy_card(self, parent, font_size_small):
        card = tk.Frame(parent, bg=self.colors['bg_light'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, scale_size(15, self.scale_factor)))
        
        inner = tk.Frame(card, bg=self.colors['bg_light'])
        inner.pack(fill=tk.X, padx=scale_size(15, self.scale_factor), pady=scale_size(12, self.scale_factor))
        
        title_frame = tk.Frame(inner, bg=self.colors['bg_light'])
        title_frame.pack(fill=tk.X, pady=(0, scale_size(8, self.scale_factor)))
        
        tk.Label(title_frame, text="Telegram Proxy", font=("Inter", scale_size(13, self.scale_factor), "bold"),
                fg=self.colors['accent'], bg=self.colors['bg_light']).pack(side=tk.LEFT)
        
        tk.Frame(inner, bg=self.colors['separator'], height=1).pack(fill=tk.X, pady=(0, scale_size(10, self.scale_factor)))
        
        row1 = tk.Frame(inner, bg=self.colors['bg_light'])
        row1.pack(fill=tk.X, pady=(0, scale_size(8, self.scale_factor)))
        
        host_frame = tk.Frame(row1, bg=self.colors['bg_light'])
        host_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, scale_size(10, self.scale_factor)))
        
        tk.Label(host_frame, text=tr('main_page_tg_proxy_host'), font=("Inter", scale_size(9, self.scale_factor)),
                fg=self.colors['text_secondary'], bg=self.colors['bg_light'], anchor='w').pack(anchor='w')
        
        self.tg_host_entry = tk.Entry(host_frame, font=("Inter", scale_size(10, self.scale_factor)),
                                    bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                                    relief=tk.FLAT, highlightthickness=1,
                                    highlightcolor=self.colors['accent'],
                                    highlightbackground=self.colors['separator'])
        self.tg_host_entry.pack(fill=tk.X, pady=(scale_size(2, self.scale_factor), 0), ipady=scale_size(4, self.scale_factor))
        self.tg_host_entry.insert(0, "127.0.0.1")
        
        port_frame = tk.Frame(row1, bg=self.colors['bg_light'])
        port_frame.pack(side=tk.RIGHT)
        
        tk.Label(port_frame, text=tr('main_page_tg_proxy_port'), font=("Inter", scale_size(9, self.scale_factor)),
                fg=self.colors['text_secondary'], bg=self.colors['bg_light'], anchor='w').pack(anchor='w')
        
        self.tg_port_entry = tk.Entry(port_frame, font=("Inter", scale_size(10, self.scale_factor)),
                                    bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                                    relief=tk.FLAT, highlightthickness=1,
                                    highlightcolor=self.colors['accent'],
                                    highlightbackground=self.colors['separator'],
                                    width=scale_size(7, self.scale_factor))
        self.tg_port_entry.pack(pady=(scale_size(2, self.scale_factor), 0), ipady=scale_size(4, self.scale_factor))
        self.tg_port_entry.insert(0, "1443")
        
        row2 = tk.Frame(inner, bg=self.colors['bg_light'])
        row2.pack(fill=tk.X, pady=(0, scale_size(8, self.scale_factor)))

        tk.Label(row2, text="Fake TLS", font=("Inter", scale_size(9, self.scale_factor)),
                fg=self.colors['text_secondary'], bg=self.colors['bg_light'], width=scale_size(8, self.scale_factor), anchor='w').pack(side=tk.LEFT)

        self.fake_tls_var = tk.BooleanVar(value=True)
        self.fake_tls_text = tk.Label(row2, text=tr('status_enabled'), font=("Inter", scale_size(9, self.scale_factor)),
                                    fg=self.colors['accent_green'], bg=self.colors['bg_light'])

        def on_fake_tls_toggle():
            if self.fake_tls_var.get():
                self.fake_tls_text.config(text=tr('status_enabled'), fg=self.colors['accent_green'])
            else:
                self.fake_tls_text.config(text=tr('status_disabled'), fg=self.colors['text_secondary'])

        self.fake_tls_switch = tk.Checkbutton(
            row2,
            variable=self.fake_tls_var,
            command=on_fake_tls_toggle,
            bg=self.colors['bg_light'],
            activebackground=self.colors['bg_light'],
            selectcolor=self.colors['bg_light'],
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.fake_tls_switch.pack(side=tk.LEFT, padx=(scale_size(5, self.scale_factor), 0))
        self.fake_tls_text.pack(side=tk.LEFT, padx=(scale_size(5, self.scale_factor), 0))
        
        row3 = tk.Frame(inner, bg=self.colors['bg_light'])
        row3.pack(fill=tk.X, pady=(0, scale_size(10, self.scale_factor)))
        
        tk.Label(row3, text=tr('main_page_tg_proxy_domain'), font=("Inter", scale_size(9, self.scale_factor)),
                fg=self.colors['text_secondary'], bg=self.colors['bg_light'], width=scale_size(8, self.scale_factor), anchor='w').pack(side=tk.LEFT)
        
        self.tg_domain_entry = tk.Entry(row3, font=("Inter", scale_size(10, self.scale_factor)),
                                        bg=self.colors['bg_light'], fg=self.colors['text_secondary'],
                                        relief=tk.FLAT, highlightthickness=1,
                                        highlightcolor=self.colors['accent'],
                                        highlightbackground=self.colors['separator'])
        self.tg_domain_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(scale_size(5, self.scale_factor), 0), ipady=scale_size(4, self.scale_factor))
        self.tg_domain_entry.insert(0, "www.google.com")
        
        apply_btn = RoundedButton(
            inner,
            text=tr('button_apply'),
            command=self.save_tg_proxy_settings,
            width=scale_size(200, self.scale_factor), height=scale_size(32, self.scale_factor),
            bg=self.colors['accent'],
            fg=self.colors['text_primary'],
            font=("Inter", scale_size(10, self.scale_factor)),
            corner_radius=scale_size(8, self.scale_factor),
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        apply_btn.pack(pady=(scale_size(5, self.scale_factor), 5))

    def _get_icon_path(self, filename):
        base_path = Path("resources") / filename
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS) / "resources" / filename
        return base_path

    def _create_icon_buttons(self, icon_size):
        icon_size_tuple = (icon_size, icon_size)
        
        icons = [
            ("tg.png", "https://t.me/zapret_launcher"),
            ("star.png", "https://github.com/avaxngard/zapret-launcher"),
            ("star2.png", "https://gitlab.com/tweenkrage/zapret-launcher")
        ]
        
        for icon_file, url in icons:
            icon_path = self._get_icon_path(icon_file)
            if icon_path.exists():
                img = Image.open(icon_path)
                img = img.resize(icon_size_tuple, Image.Resampling.LANCZOS)
                img = img.convert('RGBA')
                
                dark_img = img.copy()
                pixels = dark_img.load()
                for y in range(dark_img.size[1]):
                    for x in range(dark_img.size[0]):
                        r, g, b, a = pixels[x, y]
                        dark_r = int(r * 61 / 255)
                        dark_g = int(g * 61 / 255)
                        dark_b = int(b * 69 / 255)
                        pixels[x, y] = (dark_r, dark_g, dark_b, a)
                dark_photo = ImageTk.PhotoImage(dark_img)
                
                light_img = self._lighten_image(img)
                light_photo = ImageTk.PhotoImage(light_img)
                
                btn = tk.Label(self.icons_frame, image=dark_photo, bg=self.colors['bg_dark'], cursor="hand2")
                btn.image = dark_photo
                btn.light_image = light_photo
                btn.dark_image = dark_photo
                btn.url = url
                
                btn.bind("<Enter>", lambda e, b=btn: b.config(image=b.light_image))
                btn.bind("<Leave>", lambda e, b=btn: b.config(image=b.dark_image))
                btn.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
                btn.pack(side=tk.RIGHT, padx=scale_size(5, self.scale_factor))

    def _lighten_image(self, img):
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(1.3)
    
    def get_frame(self):
        return self.frame