# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
from tkinter import ttk
from gui.widgets import RoundedButton
from utils.languages import tr
from utils.scaling import scale_size
from config import APPDATA_DIR

class LogsPage:
    def __init__(self, parent, app):
        self.app = app
        self.colors = app.colors
        self.font_primary = app.font_primary
        self.font_medium = app.font_medium
        self.font_bold = app.font_bold
        self.scale_factor = getattr(app, 'scale_factor', 1.0)
        self.update_interval = 1000
        self._update_job = None

        font_size_title = scale_size(20, self.scale_factor)
        font_size_desc = scale_size(10, self.scale_factor)
        font_size_text = scale_size(10, self.scale_factor)
        font_size_btn = scale_size(10, self.scale_factor)
        btn_width = scale_size(120, self.scale_factor)
        btn_height = scale_size(32, self.scale_factor)
        btn_radius = scale_size(8, self.scale_factor)
        padx = scale_size(30, self.scale_factor)
        pady = scale_size(10, self.scale_factor)

        self.was_at_bottom = True
        self.old_scroll_position = 1.0
        self.last_log_count = 0
        self.auto_scroll_enabled = True

        self.frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        
        title_label = tk.Label(
            self.frame,
            text=tr('logs_title'),
            font=("Inter", font_size_title, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        title_label.pack(anchor='w', pady=(scale_size(30, self.scale_factor), 5), padx=padx)
        
        desc_label = tk.Label(
            self.frame,
            text=tr('logs_desc'),
            font=("Inter", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark']
        )
        desc_label.pack(anchor='w', pady=(0, scale_size(20, self.scale_factor)), padx=padx)
        
        control_frame = tk.Frame(self.frame, bg=self.colors['bg_dark'])
        control_frame.pack(fill=tk.X, padx=padx, pady=(0, pady))
        
        clear_btn = RoundedButton(
            control_frame,
            text=tr('logs_clear'),
            command=self.clear_logs,
            width=btn_width, height=btn_height,
            bg=self.colors['button_bg'],
            fg=self.colors['text_secondary'],
            font=("Inter", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'], 
            theme_name=self.app.current_theme
        )
        clear_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        refresh_btn = RoundedButton(
            control_frame,
            text=tr('logs_refresh'),
            command=self.refresh_logs,
            width=btn_width, height=btn_height,
            bg=self.colors['button_bg'],
            fg=self.colors['text_secondary'],
            font=("Inter", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'], 
            theme_name=self.app.current_theme
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        logs_container = tk.Frame(self.frame, bg=self.colors['bg_medium'])
        logs_container.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)
        
        self.logs_text = tk.Text(
            logs_container,
            bg=self.colors['bg_light'],
            fg=self.colors['text_secondary'],
            font=("Consolas", font_size_text),
            wrap=tk.WORD,
            borderwidth=0,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.colors['separator'],
            highlightcolor=self.colors['accent'],
            selectbackground=self.colors['accent'],
            selectforeground='white',
            padx=scale_size(10, self.scale_factor),
            pady=scale_size(10, self.scale_factor)
        )
        
        self.scrollbar = ttk.Scrollbar(
            logs_container,
            command=self.logs_text.yview,
            style="Custom.Vertical.TScrollbar"
        )
        self.logs_text.configure(yscrollcommand=self.scrollbar.set)
        
        self.logs_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.logs_text.bind("<MouseWheel>", self._on_scroll)
        self.logs_text.config(state=tk.DISABLED)
        self.update_logs_display()
        self.start_auto_update()

    def start_auto_update(self):
        if self._update_job is None:
            self._update_job = self.app.root.after(self.update_interval, self._auto_update_logs)

    def stop_auto_update(self):
        if self._update_job is not None:
            try:
                self.app.root.after_cancel(self._update_job)
            except:
                pass
            self._update_job = None

    def _auto_update_logs(self):
        if not hasattr(self, 'logs_text') or not self.logs_text.winfo_exists():
            self.stop_auto_update()
            return
        
        self.update_logs_display()
        self._update_job = self.app.root.after(self.update_interval, self._auto_update_logs)

    def _on_scroll(self, event):
        if self.logs_text and self.logs_text.winfo_exists():
            current_view = self.logs_text.yview()
            if current_view[1] >= 0.99:
                self.auto_scroll_enabled = True
            else:
                self.auto_scroll_enabled = False
                self.old_scroll_position = current_view[0]

    def _full_reload_logs(self, logs):
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.delete(1.0, tk.END)
        
        for log_line in logs:
            log_line = log_line.strip()
            if log_line:
                self.logs_text.insert(tk.END, log_line + "\n")
        
        self.logs_text.config(state=tk.DISABLED)
        self.last_log_count = len(logs)
        
        if self.auto_scroll_enabled:
            self.logs_text.see(tk.END)

    def refresh_logs(self):
        self.auto_scroll_enabled = True
        self.last_log_count = 0
        self.update_logs_display()
        if self._update_job is None:
            self.start_auto_update()

    def clear_logs(self):
        log_file = APPDATA_DIR / "logs.txt"
        try:
            if log_file.exists():
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write("")
            self.logs_text.config(state=tk.NORMAL)
            self.logs_text.delete(1.0, tk.END)
            self.logs_text.config(state=tk.DISABLED)
            self.last_log_count = 0
            self.auto_scroll_enabled = True
            self.logs_text.see(tk.END)
            self.start_auto_update()
        except Exception:
            pass
    
    def update_logs_display(self):
        if not hasattr(self, 'logs_text') or not self.logs_text.winfo_exists():
            return
        
        try:
            if self.logs_text.tag_ranges(tk.SEL):
                if self._delayed_update is None:
                    self._delayed_update = self.app.root.after(1000, self.update_logs_display)
                return
        except:
            pass
        
        try:
            sel_start = self.logs_text.index(tk.SEL_FIRST)
            sel_end = self.logs_text.index(tk.SEL_LAST)
            has_selection = True
        except tk.TclError:
            has_selection = False
            sel_start = None
            sel_end = None
        
        current_view = self.logs_text.yview()
        was_at_bottom = (current_view[1] >= 0.99)
        
        logs = self.app.load_logs()
        
        if len(logs) < self.last_log_count:
            self._full_reload_logs(logs)
            self._delayed_update = None
            return
        
        new_logs = logs[self.last_log_count:] if len(logs) > self.last_log_count else []
        
        if new_logs:
            self.logs_text.config(state=tk.NORMAL)
            for log_line in new_logs:
                log_line = log_line.strip()
                if log_line:
                    self.logs_text.insert(tk.END, log_line + "\n")
            self.logs_text.config(state=tk.DISABLED)
            self.last_log_count = len(logs)
            
            if self.auto_scroll_enabled or was_at_bottom:
                self.logs_text.see(tk.END)
                self.auto_scroll_enabled = True
        else:
            if len(logs) != self.last_log_count:
                self.last_log_count = len(logs)
        
        if has_selection and sel_start and sel_end:
            try:
                self.logs_text.tag_add(tk.SEL, sel_start, sel_end)
                self.logs_text.mark_set(tk.INSERT, sel_start)
            except:
                pass
        
        self._delayed_update = None
    
    def get_frame(self):
        return self.frame
