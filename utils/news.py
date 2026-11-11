# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import threading
import requests
import tkinter as tk
import customtkinter as ctk
from utils.languages import tr
from config import CURRENT_VERSION, CURRENT_BUILD, API_URL_NEWS
from utils.scaling import scale_size

class NewsManager:
    def __init__(self, app):
        self.app = app
        self.install_id = None
        self.api_url = API_URL_NEWS
        self._check_interval = 3600
        self._is_visible = False
        self.scale_factor = getattr(app, 'scale_factor', 1.0)
        
    def set_install_id(self, install_id):
        self.install_id = install_id
    
    def check_news(self, show_on_start=True):
        if not self.install_id:
            return
        
        def check():
            try:
                response = requests.get(self.api_url, params={'install_id': self.install_id, 'build': str(CURRENT_BUILD)}, timeout=5, headers={'User-Agent': f'Zapret-Launcher/{CURRENT_VERSION}'})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('news'):
                        news_list = data['news'][:2]
                        if show_on_start and news_list:
                            self.app.root.after(100, lambda: self._show_news(news_list))
                    
            except Exception:
                pass
        
        threading.Thread(target=check, daemon=True).start()
    
    def _show_news(self, news_list):
        if self._is_visible:
            return
        self._is_visible = True
        
        dialog_width = scale_size(600, self.scale_factor)
        dialog_height = scale_size(450, self.scale_factor)
        font_size_title = scale_size(21, self.scale_factor)
        font_size_sub = scale_size(13, self.scale_factor)
        font_size_date = scale_size(11, self.scale_factor)
        font_size_content = scale_size(12, self.scale_factor)
        padx = scale_size(20, self.scale_factor)
        pady = scale_size(10, self.scale_factor)
        wrap_width = scale_size(520, self.scale_factor)
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"Zapret Launcher - {tr('news_title')}")
        dialog.resizable(False, False)
        dialog.configure(bg=self.app.colors['bg_medium'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.focus_force()
        
        def on_dialog_close():
            self._close_news(dialog, news_list)

        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        dialog.bind('<Escape>', lambda e: on_dialog_close())
        
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - dialog_width // 2
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - dialog_height // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        dialog.withdraw()
        try:
            dialog.attributes('-alpha', 0.0)
        except Exception:
            pass
            
        self.app.set_dialog_header_color(dialog)
        dialog.update_idletasks()
        
        title_lbl = ctk.CTkLabel(
            dialog,
            text=tr('information_desc'),
            font=("Inter", font_size_title, "bold"),
            text_color=self.app.colors['accent']
        )
        title_lbl.pack(pady=(scale_size(8, self.scale_factor), scale_size(4, self.scale_factor)))
        
        scroll_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)
        
        for news in news_list:
            self._create_news_item(scroll_frame, news, dialog, font_size_sub, font_size_date, font_size_content, wrap_width)
            
        dialog.update_idletasks()
        dialog.update()
        dialog.deiconify()
        
        def fade_in(alpha=0.0):
            if not dialog.winfo_exists():
                return
            if alpha < 1.0:
                alpha += 0.1
                try:
                    dialog.attributes('-alpha', alpha)
                    dialog.after(15, lambda: fade_in(alpha))
                except Exception:
                    pass
            else:
                try:
                    dialog.attributes('-alpha', 1.0)
                except Exception:
                    pass
                    
        dialog.after(50, fade_in)
    
    def _create_news_item(self, parent, news, dialog, font_size_sub, font_size_date, font_size_content, wrap_width):
        item_frame = ctk.CTkFrame(
            parent, 
            fg_color=self.app.colors['bg_light'],
            corner_radius=scale_size(8, self.scale_factor)
        )
        item_frame.pack(fill=tk.X, pady=scale_size(5, self.scale_factor), padx=scale_size(5, self.scale_factor))
        
        title_color = self.app.colors['accent']
        
        title_label = ctk.CTkLabel(
            item_frame,
            text=f"{news.get('title', 'News')}",
            font=("Inter", font_size_sub, "bold"),
            text_color=title_color,
            anchor="w",
            justify="left"
        )
        title_label.pack(anchor='w', fill=tk.X, padx=scale_size(15, self.scale_factor), pady=(scale_size(10, self.scale_factor), 0))
        
        date_label = ctk.CTkLabel(
            item_frame,
            text=news.get('created_at', '')[:10],
            font=("Inter", font_size_date),
            text_color=self.app.colors['text_secondary'],
            anchor="w"
        )
        date_label.pack(anchor='w', fill=tk.X, padx=scale_size(15, self.scale_factor), pady=(0, scale_size(1, self.scale_factor)))
        
        content_label = ctk.CTkLabel(
            item_frame,
            text=news.get('content', ''),
            font=("Inter", font_size_content),
            text_color=self.app.colors['text_primary'],
            wraplength=wrap_width,
            justify="left",
            anchor="w"
        )
        content_label.pack(anchor='w', fill=tk.X, padx=scale_size(15, self.scale_factor), pady=(scale_size(2, self.scale_factor), scale_size(6, self.scale_factor)))
        
        item_frame.news_id = news.get('id')
    
    def _close_news(self, dialog, news_list):
        self._is_visible = False
        dialog.destroy()
        
        def mark_read():
            for news in news_list:
                try:
                    requests.post(self.api_url, json={'action': 'mark_read', 'install_id': self.install_id, 'news_id': news.get('id')}, timeout=3)
                except Exception:
                    pass
        
        threading.Thread(target=mark_read, daemon=True).start()
