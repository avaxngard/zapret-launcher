# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
from tkinter import ttk, messagebox
import os
from utils.languages import tr
from utils.scaling import scale_size
from config import HOSTS_PATH

class HostsPage:
    def __init__(self, parent, app, dialogs):
        self.app = app
        self.dialogs = dialogs
        self.colors = app.colors
        self.scale_factor = getattr(app, 'scale_factor', 1.0)
        self.frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        self.hosts_path = HOSTS_PATH
        self.search_visible = False
        self.search_start_pos = "1.0"
        self.initial_content = ""
        
        font_size_title = scale_size(20, self.scale_factor)
        font_size_desc = scale_size(10, self.scale_factor)
        font_size_text = scale_size(10, self.scale_factor)
        font_size_label = scale_size(9, self.scale_factor)
        font_size_info = scale_size(8, self.scale_factor)
        padx_main = scale_size(30, self.scale_factor)
        pady_main = scale_size(20, self.scale_factor)
        btn_padx = scale_size(20, self.scale_factor)
        btn_pady = scale_size(5, self.scale_factor)
        btn_width_search = scale_size(10, self.scale_factor)
        btn_width_close = scale_size(8, self.scale_factor)
        entry_width = scale_size(30, self.scale_factor)
        
        self._build_ui(font_size_title, font_size_desc, font_size_text, font_size_label, 
                       font_size_info, padx_main, pady_main, btn_padx, btn_pady,
                       btn_width_search, btn_width_close, entry_width)
        self.load_hosts()
    
    def _build_ui(self, font_size_title, font_size_desc, font_size_text, font_size_label, 
                  font_size_info, padx_main, pady_main, btn_padx, btn_pady,
                  btn_width_search, btn_width_close, entry_width):
        title = tk.Label(
            self.frame,
            text=tr('hosts_title'),
            font=("Inter", font_size_title, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        title.pack(anchor='w', pady=(scale_size(30, self.scale_factor), 5), padx=padx_main)
        
        desc = tk.Label(
            self.frame,
            text=tr('hosts_desc'),
            font=("Inter", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark']
        )
        desc.pack(anchor='w', pady=(0, pady_main), padx=padx_main)
        
        main_frame = tk.Frame(self.frame, bg=self.colors['bg_medium'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=padx_main, pady=(0, pady_main))
        
        text_frame = tk.Frame(main_frame, bg=self.colors['bg_medium'])
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(scale_size(10, self.scale_factor), scale_size(10, self.scale_factor)))
        
        self.text_area = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", font_size_text),
            undo=True,
            height=20,
            bg=self.colors['bg_light'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['text_primary'],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor=self.colors['accent'],
            highlightbackground=self.colors['bg_medium']
        )
        
        scrollbar = ttk.Scrollbar(text_frame, style="Custom.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_area.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text_area.yview)
        
        self.text_area.focus_set()
        
        self.search_frame = tk.Frame(main_frame, bg=self.colors['bg_medium'])
        self.search_frame.bind('<Escape>', self.on_escape_search)
        
        self.search_label = tk.Label(
            self.search_frame,
            text=tr('editor_find'),
            font=("Segoe UI", font_size_label),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_secondary']
        )
        self.search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_entry = tk.Entry(
            self.search_frame,
            font=("Segoe UI", font_size_label),
            width=entry_width,
            bg=self.colors['bg_light'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor=self.colors['accent']
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<Return>', self.search_next)
        self.search_entry.bind('<Escape>', self.on_escape_search)
        
        self.search_next_btn = tk.Button(
            self.search_frame,
            text=tr('editor_find_next'),
            command=self.search_next,
            width=btn_width_search,
            bg=self.colors['accent'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            cursor='hand2',
            activebackground=self.colors['accent']
        )
        self.search_next_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_close_btn = tk.Button(
            self.search_frame,
            text=tr('editor_close'),
            command=self.toggle_search,
            width=btn_width_close,
            bg=self.colors['button_bg'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            cursor='hand2',
            activebackground=self.colors['accent']
        )
        self.search_close_btn.pack(side=tk.LEFT)
        
        self.search_info = tk.Label(
            self.search_frame,
            text="",
            font=("Segoe UI", font_size_info),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent']
        )
        self.search_info.pack(side=tk.LEFT, padx=(10, 0))
        
        self.text_area.bind('<Control-f>', self.toggle_search)
        self.text_area.bind('<Control-F>', self.toggle_search)
        self.text_area.bind('<Control-c>', self.copy_text)
        self.text_area.bind('<Control-C>', self.copy_text)
        self.text_area.bind('<Control-v>', self.paste_text)
        self.text_area.bind('<Control-V>', self.paste_text)
        self.text_area.bind('<Control-x>', self.cut_text)
        self.text_area.bind('<Control-X>', self.cut_text)
        self.text_area.bind('<Control-a>', self.select_all)
        self.text_area.bind('<Control-A>', self.select_all)
        
        button_frame = tk.Frame(main_frame, bg=self.colors['bg_medium'])
        button_frame.pack(fill=tk.X, pady=(0, scale_size(10, self.scale_factor)))
        
        self.save_btn = tk.Button(
            button_frame,
            text=tr('editor_save'),
            command=self.save_hosts,
            padx=btn_padx,
            pady=btn_pady,
            takefocus=True,
            bg=self.colors['accent'],
            fg=self.colors['text_primary'],
            activebackground=self.colors['accent'],
            activeforeground=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            cursor='hand2'
        )
        self.save_btn.pack(side=tk.RIGHT, padx=(5, scale_size(15, self.scale_factor)))
        
        self.reload_btn = tk.Button(
            button_frame,
            text=tr('hosts_reload'),
            command=self.reload_data,
            padx=btn_padx,
            pady=btn_pady,
            takefocus=True,
            bg=self.colors['button_bg'],
            fg=self.colors['text_primary'],
            activebackground=self.colors['accent'],
            activeforeground=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            cursor='hand2'
        )
        self.reload_btn.pack(side=tk.RIGHT, padx=(5, 0))

        self.download_btn = tk.Button(
            button_frame,
            text=tr('hosts_download'),
            command=self.check_templates,
            padx=btn_padx,
            pady=btn_pady,
            takefocus=True,
            bg=self.colors['button_bg'],
            fg=self.colors['text_primary'],
            activebackground=self.colors['accent'],
            activeforeground=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            cursor='hand2'
            )
        self.download_btn.pack(side=tk.RIGHT)
        
        info_frame = tk.Frame(button_frame, bg=self.colors['bg_medium'])
        info_frame.pack(side=tk.LEFT)
        
        info_label = tk.Label(
            info_frame,
            text=tr('editor_tooltip'),
            font=("Segoe UI", font_size_info),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_secondary']
        )
        info_label.pack(side=tk.LEFT, padx=10)

    def on_escape_search(self, event=None):
        if self.search_visible:
            self.toggle_search()
        return "break"

    def check_templates(self):
        self.dialogs.show_templates_dialog()
    
    def reload_data(self):
        if self.text_area.edit_modified():
            if not messagebox.askyesno(tr('warning'), tr('hosts_reload_warning')):
                return
        
        self.load_hosts()
        self.text_area.edit_modified(False)
        self.text_area.delete("undo")
    
    def toggle_search(self, event=None):
        if self.search_visible:
            self.search_frame.pack_forget()
            self.search_visible = False
            self.text_area.tag_remove("search", "1.0", "end")
            self.text_area.focus()
        else:
            self.search_frame.pack(fill=tk.X, pady=(0, scale_size(10, self.scale_factor)), before=self.text_area.master)
            self.search_visible = True
            self.search_entry.focus()
            self.search_entry.select_range(0, tk.END)
            self.text_area.tag_remove("search", "1.0", "end")
            self.search_start_pos = self.text_area.index(tk.INSERT)
            self.search_info.config(text="")
    
    def search_next(self, event=None):
        search_text = self.search_entry.get()
        if not search_text:
            self.search_info.config(text=tr('editor_enter_text'))
            return
        
        self.text_area.tag_remove("search", "1.0", "end")
        start_pos = self.search_start_pos
        
        pos = self.text_area.search(search_text, start_pos, "end", nocase=True)
        
        if not pos:
            pos = self.text_area.search(search_text, "1.0", "end", nocase=True)
            if not pos:
                self.search_info.config(text=f"'{search_text}' {tr('editor_not_found')}")
                self.search_start_pos = "1.0"
                return
            self.search_start_pos = self.text_area.index(f"{pos}+{len(search_text)}c")
        else:
            self.search_info.config(text="")
            self.search_start_pos = self.text_area.index(f"{pos}+{len(search_text)}c")
        
        end_pos = self.text_area.index(f"{pos}+{len(search_text)}c")
        self.text_area.tag_add("search", pos, end_pos)
        self.text_area.tag_config("search", background="#A46EBD", foreground="#000000")
        
        self.text_area.see(pos)
        self.text_area.mark_set(tk.INSERT, pos)
        self.text_area.focus()
    
    def copy_text(self, event=None):
        try:
            self.text_area.event_generate("<<Copy>>")
            return "break"
        except:
            pass
    
    def paste_text(self, event=None):
        try:
            self.text_area.event_generate("<<Paste>>")
            return "break"
        except:
            pass
    
    def cut_text(self, event=None):
        try:
            self.text_area.event_generate("<<Cut>>")
            return "break"
        except:
            pass
    
    def select_all(self, event=None):
        try:
            self.text_area.tag_add("sel", "1.0", "end")
            return "break"
        except:
            pass
    
    def load_hosts(self):
        try:
            self.text_area.delete('1.0', tk.END)
            
            if not self.hosts_path.exists():
                self.text_area.insert('1.0', "# File not found. Create content and save")
                return
            
            with open(self.hosts_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.text_area.insert('1.0', content)
            self.initial_content = content
            self.text_area.edit_modified(False)
            
        except Exception as e:
            self.app.log_event("info", f"Error loading hosts: {e}")
            messagebox.showerror(tr('error_no_connection'), f"{tr('editor_error_load')}: {str(e)}")
    
    def save_hosts(self):
        try:
            content = self.text_area.get('1.0', tk.END).strip()
            
            if not content:
                if not messagebox.askyesno(tr('warning'), tr('hosts_empty_warning')):
                    return
            
            if not os.access(str(self.hosts_path), os.W_OK):
                if not messagebox.askyesno(tr('warning'), tr('hosts_admin_warning')):
                    return
            
            os.makedirs(os.path.dirname(self.hosts_path), exist_ok=True)
            with open(self.hosts_path, 'w', encoding='utf-8') as f:
                f.write(content + '\n' if content else '')
            
            self.initial_content = content
            self.text_area.edit_modified(False)
            self.app.log_event("info", f"Hosts file saved")
            
        except PermissionError:
            messagebox.showerror(tr('error'), tr('hosts_permission_error'))
        except Exception as e:
            messagebox.showerror(tr('error_no_connection'), f"{tr('editor_error_save')}: {str(e)}")
            self.app.log_event("info", f"Error saving hosts: {e}")
    
    def get_frame(self):
        return self.frame