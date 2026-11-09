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
import os
import pywinstyles
from gui.theme import get_theme
from pathlib import Path
from utils.languages import tr
from utils.scaling import scale_size
try:
    from config import APPDATA_DIR
except Exception:
    APPDATA_DIR = None

class ListEditor:
    def __init__(self, parent, file_path, title, app=None):
        self.app = app
        self.parent = parent
        self.file_path = file_path
        self.initial_content = ""
        self.title = title
        self.search_frame = None
        self.search_start_pos = "1.0"
        self.search_visible = False

        self.scale_factor = getattr(app, 'scale_factor', 1.0) if app else 1.0

        theme_name = getattr(app, 'current_theme', 'Dark') if app else 'Dark'
        self.colors = get_theme(theme_name)

        dialog_width = scale_size(600, self.scale_factor)
        dialog_height = scale_size(500, self.scale_factor)
        font_size_text = scale_size(10, self.scale_factor)
        font_size_label = scale_size(12, self.scale_factor)
        font_size_info = scale_size(11, self.scale_factor)

        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(f"{tr('edit_title_window')} {title}")
        self.dialog.minsize(scale_size(500, self.scale_factor), scale_size(400, self.scale_factor))
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(fg_color=self.colors['bg_medium'])

        self.dialog.withdraw()
        try:
            self.dialog.attributes('-alpha', 0.0)
        except Exception:
            pass

        self._set_dialog_icon(self.dialog)

        x = parent.winfo_x() + (parent.winfo_width() // 2) - dialog_width // 2
        y = parent.winfo_y() + (parent.winfo_height() // 2) - dialog_height // 2
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog_width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog_height // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self._set_dialog_header_color(self.dialog)

        main_frame = ctk.CTkFrame(self.dialog, fg_color=self.colors['bg_medium'], corner_radius=0)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['bg_medium'], corner_radius=0)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

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
            highlightbackground=self.colors['bg_medium'],
            bd=0,
        )

        scrollbar = ctk.CTkScrollbar(text_frame, command=self.text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_area.config(yscrollcommand=scrollbar.set)
        self.text_area.focus_set()

        self.search_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['bg_medium'], corner_radius=0)

        self.search_label = ctk.CTkLabel(
            self.search_frame,
            text=tr('editor_find'),
            font=("Inter", font_size_label),
            text_color=self.colors['text_secondary'],
        )
        self.search_label.pack(side=tk.LEFT, padx=(0, 5))

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            font=("Inter", font_size_info),
            width=scale_size(220, self.scale_factor),
            fg_color=self.colors['bg_light'],
            text_color=self.colors['text_primary'],
            border_color=self.colors['accent'],
            border_width=1,
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<Return>', self.search_next)

        btn_w_search = scale_size(80, self.scale_factor)
        btn_w_close = scale_size(80, self.scale_factor)
        btn_h = scale_size(28, self.scale_factor)

        self.search_next_btn = ctk.CTkButton(
            self.search_frame,
            text=tr('editor_find_next'),
            command=self.search_next,
            width=btn_w_search,
            height=btn_h,
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            text_color=self.colors['button_text_hover'],
        )
        self.search_next_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.search_close_btn = ctk.CTkButton(
            self.search_frame,
            text=tr('editor_close'),
            command=self.toggle_search,
            width=btn_w_close,
            height=btn_h,
            fg_color=self.colors['button_bg'],
            hover_color=self.colors['accent'],
            text_color=self.colors['button_text'],
        )
        self.search_close_btn.pack(side=tk.LEFT)

        self.search_info = ctk.CTkLabel(
            self.search_frame,
            text="",
            font=("Inter", font_size_info),
            text_color=self.colors['accent'],
        )
        self.search_info.pack(side=tk.LEFT, padx=(10, 0))

        self.text_area.bind('<Control-f>', self.toggle_search)
        self.text_area.bind('<Control-F>', self.toggle_search)
        self.text_area.bind('<Escape>', self.on_escape)
        self.text_area.bind('<Control-c>', self.copy_text)
        self.text_area.bind('<Control-C>', self.copy_text)
        self.text_area.bind('<Control-v>', self.paste_text)
        self.text_area.bind('<Control-V>', self.paste_text)
        self.text_area.bind('<Control-x>', self.cut_text)
        self.text_area.bind('<Control-X>', self.cut_text)
        self.text_area.bind('<Control-a>', self.select_all)
        self.text_area.bind('<Control-A>', self.select_all)

        self.text_area.bind('<Key>', self._on_key_handler, add='+')

        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        self.text_area.bind('<Escape>', lambda e: self.dialog.destroy())
        self.search_entry.bind('<Escape>', lambda e: self.dialog.destroy())

        self.load_content()

        button_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['bg_medium'], corner_radius=0)
        button_frame.pack(fill=tk.X)

        btn_w = scale_size(100, self.scale_factor)
        btn_h_main = scale_size(32, self.scale_factor)

        self.save_btn = ctk.CTkButton(
            button_frame,
            text=tr('editor_save'),
            command=self.save_content,
            width=btn_w,
            height=btn_h_main,
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent'],
            text_color=self.colors['button_text_hover'],
        )
        self.save_btn.pack(side=tk.RIGHT, padx=(5, 0))

        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text=tr('editor_cancel'),
            command=self.dialog.destroy,
            width=btn_w,
            height=btn_h_main,
            fg_color=self.colors['button_bg'],
            hover_color=self.colors['accent'],
            text_color=self.colors['button_text'],
        )
        self.cancel_btn.pack(side=tk.RIGHT)
        self.buttons = [self.save_btn, self.cancel_btn]

        info_frame = ctk.CTkFrame(button_frame, fg_color=self.colors['bg_medium'], corner_radius=0)
        info_frame.pack(side=tk.LEFT)

        info_label = ctk.CTkLabel(
            info_frame,
            text=tr('editor_tooltip'),
            font=("Inter", font_size_info),
            text_color=self.colors['text_secondary'],
        )
        info_label.pack(side=tk.LEFT, padx=10)

        self.dialog.update_idletasks()
        self.dialog.deiconify()
        self.dialog.focus_force()

        def fade_in(alpha=0.0):
            if not self.dialog.winfo_exists():
                return
            if alpha < 1.0:
                alpha += 0.15
                try:
                    self.dialog.attributes('-alpha', alpha)
                    self.dialog.after(12, lambda: fade_in(alpha))
                except Exception:
                    pass
            else:
                try:
                    self.dialog.attributes('-alpha', 1.0)
                except Exception:
                    pass

        self.dialog.after(50, fade_in)

    def _log(self, ctx: str, e: Exception):
        try:
            if self.app and hasattr(self.app, 'log_event'):
                self.app.log_event("info", f"{ctx}: {e}")
        except Exception:
            pass

    def _resolve_icon_path(self):
        try:
            base = APPDATA_DIR
            if base is None:
                appdata = os.environ.get("APPDATA")
                if not appdata:
                    return None
                base = Path(appdata) / "Zapret Launcher"

            icon_path = Path(base) / "resources" / "icon.ico"
            if icon_path.exists() and icon_path.suffix.lower() == ".ico":
                return icon_path
        except Exception as e:
            self._log("_resolve_icon_path", e)
        return None

    def _set_dialog_icon(self, dialog):
        try:
            icon_path = self._resolve_icon_path()
            if not icon_path:
                return
            icon_str = str(icon_path)
            dialog.iconbitmap(default=icon_str)
        except Exception as e:
            self._log("_set_dialog_icon", e)

    def _set_dialog_header_color(self, dialog):
        try:
            dialog.update_idletasks()
            pywinstyles.change_header_color(dialog, self.colors['bg_medium'])
        except ImportError:
            pass
        except Exception as e:
            self._log("_set_dialog_header_color", e)

    def toggle_search(self, event=None):
        if self.search_visible:
            self.search_frame.pack_forget()
            self.search_visible = False
            self.text_area.tag_remove("search", "1.0", "end")
            self.text_area.focus()
        else:
            self.search_frame.pack(fill=tk.X, pady=(0, 10), before=self.text_area.master)
            self.search_visible = True
            self.search_entry.focus()
            self.search_entry.select_range(0, tk.END)
            self.text_area.tag_remove("search", "1.0", "end")
            self.search_start_pos = self.text_area.index(tk.INSERT)
            self.search_info.configure(text="")

    def on_escape(self, event=None):
        if self.search_visible:
            self.toggle_search()
        return "break"

    def search_next(self, event=None):
        search_text = self.search_entry.get()
        if not search_text:
            self.search_info.configure(text=tr('editor_enter_text'))
            return

        self.text_area.tag_remove("search", "1.0", "end")
        start_pos = self.search_start_pos

        pos = self.text_area.search(search_text, start_pos, "end", nocase=True)

        if not pos:
            pos = self.text_area.search(search_text, "1.0", "end", nocase=True)
            if not pos:
                self.search_info.configure(text=f"'{search_text}' {tr('editor_not_found')}")
                self.search_start_pos = "1.0"
                return
            self.search_start_pos = self.text_area.index(f"{pos}+{len(search_text)}c")
        else:
            self.search_info.configure(text="")
            self.search_start_pos = self.text_area.index(f"{pos}+{len(search_text)}c")

        end_pos = self.text_area.index(f"{pos}+{len(search_text)}c")
        self.text_area.tag_add("search", pos, end_pos)
        self.text_area.tag_config("search", background="#A46EBD", foreground="#000000")

        self.text_area.see(pos)
        self.text_area.mark_set(tk.INSERT, pos)
        self.text_area.focus()

    def _on_key_handler(self, event):
        if not (event.state & 0x4):
            return None
        if event.keycode == 70:
            return self.toggle_search(event)
        if event.keycode == 67:
            return self.copy_text(event)
        if event.keycode == 86:
            return self.paste_text(event)
        if event.keycode == 88:
            return self.cut_text(event)
        if event.keycode == 65:
            return self.select_all(event)
        return None

    def copy_text(self, event=None):
        try:
            self.text_area.event_generate("<<Copy>>")
            return "break"
        except Exception as e:
            self._log("copy_text", e)

    def paste_text(self, event=None):
        try:
            self.text_area.event_generate("<<Paste>>")
            return "break"
        except Exception as e:
            self._log("paste_text", e)

    def cut_text(self, event=None):
        try:
            self.text_area.event_generate("<<Cut>>")
            return "break"
        except Exception as e:
            self._log("cut_text", e)

    def select_all(self, event=None):
        try:
            self.text_area.tag_add("sel", "1.0", "end")
            return "break"
        except Exception as e:
            self._log("select_all", e)

    def load_content(self):
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_area.insert('1.0', content)
                self.initial_content = content
            else:
                self.text_area.insert('1.0', "# File not found. Create content and save")
        except Exception as e:
            self._log(f"load_content {os.path.basename(self.file_path)}", e)
            messagebox.showerror(tr('error_no_connection'), f"{tr('editor_error_load')}: {str(e)}")

    def save_content(self):
        try:
            content = self.text_area.get('1.0', tk.END).strip()

            if not content:
                if not messagebox.askyesno(tr('error_warning'), tr('hosts_empty_warning')):
                    return

            if not os.access(self.file_path, os.W_OK):
                if not messagebox.askyesno(tr('error_warning'), tr('hosts_admin_warning')):
                    return

            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(content + '\n' if content else '')

            self.initial_content = content
            self.text_area.edit_modified(False)
            
            if self.app:
                self.app.log_event("info", f"File {os.path.basename(self.file_path)} saved")
            
            zapret_running = False
            try:
                if self.app and hasattr(self.app, 'zapret') and self.app.zapret:
                    zapret_running = bool(self.app.zapret.is_winws_running())
                elif self.app and getattr(self.app, 'is_connected', False):
                    zapret_running = True
            except Exception as e:
                self._log("check winws running", e)

            if zapret_running:
                messagebox.showinfo(tr('success'), f"{tr('editor_success')}\n{tr('restart_zapret')}")
            else:
                messagebox.showinfo(tr('success'), tr('editor_success'))

            self.dialog.destroy()
            
            try:
                if self.app and hasattr(self.app, 'pages') and hasattr(self.app.pages, 'lists_page_obj'):
                    self.app.pages.lists_page_obj.refresh()
            except Exception as e:
                self._log("refresh lists page", e)

        except PermissionError:
            messagebox.showerror(tr('error'), tr('hosts_permission_error'))
        except Exception as e:
            messagebox.showerror(tr('error_no_connection'), f"{tr('editor_error_save')}: {str(e)}")
            if self.app:
                self.app.log_event("info", f"Error saving {os.path.basename(self.file_path)}: {e}")
