# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
from tkinter import messagebox
from utils.languages import tr, tr_plural
from utils.scaling import scale_size
from utils.list_editor import ListEditor
from utils.check_lists import ListChecker
import os
from config import ZAPRET_CORE_DIR, LISTS_DIR

def check_zapret_folder():
    zapret_core_dir = ZAPRET_CORE_DIR
    if not zapret_core_dir.exists():
        messagebox.showerror(
            tr('error'),
            f"{tr('error_zapret_folder')}\n\n"
            f"{tr('expected_folder')} {zapret_core_dir}\n\n"
            f"{tr('restart_manual_title')}"
        )
        return False
    return True

def open_lists_folder():
    try:
        os.startfile(LISTS_DIR)
    except Exception as e:
        messagebox.showerror(tr('error'), f"Failed to open folder: {str(e)}")

class ListsPage:
    LIST_DEFS = [
        ('lists_custom',      "list-custom.txt",  "domain"),
        ('lists_ipset',       "ipset-all.txt",    "ipset"),
        ('lists_ipset_white', "ipset-white.txt",  "ipset"),
        ('lists_white',       "list-white.txt",   "white"),
        ('lists_google',      "list-google.txt",  "domain"),
        ('lists_general',     "list-general.txt", "domain"),
    ]

    CHECK_FILES = set(ListChecker.CHECK_FILES)

    def __init__(self, parent, app):
        self.app = app
        self.colors = app.colors
        self.font_primary = app.font_primary
        self.font_medium = app.font_medium
        self.font_bold = app.font_bold
        self.scale_factor = getattr(app, 'scale_factor', 1.0)

        font_size_title    = scale_size(20, self.scale_factor)
        font_size_desc     = scale_size(10, self.scale_factor)

        padx = scale_size(30, self.scale_factor)
        pady = scale_size(10, self.scale_factor)
        self.card_padx = scale_size(15, self.scale_factor)
        self.card_pady = scale_size(12, self.scale_factor)
        self.grid_gap  = scale_size(10, self.scale_factor)
        self.corner_radius = scale_size(10, self.scale_factor)

        self._file_stats = {}
        self.frame = tk.Frame(parent, bg=self.colors['bg_dark'])

        tk.Label(
            self.frame,
            text=tr('lists_title'),
            font=("Segoe UI Variable", font_size_title, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        ).pack(anchor='w', pady=(scale_size(30, self.scale_factor), 5), padx=padx)

        tk.Label(
            self.frame,
            text=tr('lists_desc'),
            font=("Segoe UI Variable", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark']
        ).pack(anchor='w', pady=(0, scale_size(20, self.scale_factor)), padx=padx)

        self.grid_frame = tk.Frame(self.frame, bg=self.colors['bg_dark'])
        self.grid_frame.pack(fill=tk.BOTH, expand=True,
                             padx=padx,
                             pady=(pady, scale_size(20, self.scale_factor)))
        self.grid_frame.columnconfigure(0, weight=1, uniform="cards")
        self.grid_frame.columnconfigure(1, weight=1, uniform="cards")

        self.refresh_stats()
        self._render_cards()

    def refresh_stats(self):
        self._file_stats = {}

        try:
            checker = ListChecker(LISTS_DIR)
            results = checker.check_all_files()
        except Exception:
            results = {}

        for _, filename, _ in self.LIST_DEFS:
            lines = 0
            try:
                path = LISTS_DIR / filename
                if path.exists():
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = sum(1 for _ in f)
            except Exception:
                pass

            dup_count = 0
            total = 0
            if filename in results:
                data = results[filename]
                dup_count = len(data.get('duplicates', {}) or {})
                total = data.get('total', 0)

            self._file_stats[filename] = {
                'lines': lines,
                'duplicates': dup_count,
                'total': total,
            }

    def _get_status(self, filename):
        if filename not in self.CHECK_FILES:
            return "ok"
        stats = self._file_stats.get(filename, {})
        return "warn" if stats.get('duplicates', 0) > 0 else "ok"

    def _get_lines_count(self, filename):
        return self._file_stats.get(filename, {}).get('lines', 0)

    def _get_duplicates_count(self, filename):
        return self._file_stats.get(filename, {}).get('duplicates', 0)

    def _render_cards(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        for idx, (key, filename, ctype) in enumerate(self.LIST_DEFS):
            row = idx // 2
            col = idx % 2

            padx_left  = 0 if col == 0 else self.grid_gap // 2
            padx_right = self.grid_gap // 2 if col == 0 else 0

            self._create_card(
                self.grid_frame, row, col,
                name=tr(key),
                filename=filename,
                lines=self._get_lines_count(filename),
                duplicates=self._get_duplicates_count(filename),
                status=self._get_status(filename),
                padx=(padx_left, padx_right),
                pady=(0, self.grid_gap // 2),
            )

    def _create_card(self, parent, row, col, name, filename, lines,
                     duplicates, status, padx, pady):
        card_h = scale_size(80, self.scale_factor)

        wrapper = tk.Frame(parent, bg=self.colors['bg_dark'], height=card_h)
        wrapper.grid(row=row, column=col, sticky='nsew', padx=padx, pady=pady)
        wrapper.pack_propagate(False)
        wrapper.grid_propagate(False)

        canvas = tk.Canvas(wrapper, bg=self.colors['bg_dark'],
                           highlightthickness=0, bd=0, cursor="hand2")
        canvas.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(canvas, bg=self.colors['bg_light'], cursor="hand2")
        card_window = canvas.create_window(
            (self.card_padx, self.card_pady),
            window=card,
            anchor='nw'
        )

        inner = tk.Frame(card, bg=self.colors['bg_light'])
        inner.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(inner, bg=self.colors['bg_light'])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        name_label = tk.Label(
            left, text=name,
            font=("Segoe UI Variable", scale_size(13, self.scale_factor), "bold"),
            fg=self.colors['accent'],
            bg=self.colors['bg_light'],
            anchor='w', justify=tk.LEFT
        )
        name_label.pack(anchor='w', fill=tk.X)

        file_label = tk.Label(
            left, text=filename,
            font=("Segoe UI Variable", scale_size(10, self.scale_factor)),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_light'],
            anchor='w', justify=tk.LEFT
        )
        file_label.pack(anchor='w', fill=tk.X,
                        pady=(scale_size(2, self.scale_factor), 0))

        right = tk.Frame(inner, bg=self.colors['bg_light'])
        right.pack(side=tk.RIGHT, fill=tk.Y)

        lines_label = tk.Label(
            right, text=tr_plural(lines, 'lists_lines_one', 'lists_lines_few', 'lists_lines_many'),
            font=("Segoe UI Variable", scale_size(9, self.scale_factor)),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_light'],
            anchor='e'
        )
        lines_label.pack(anchor='e')

        if status == "ok":
            badge_color = self.colors['accent_green']
            badge_text = tr('lists_status_clean')
        else:
            badge_color = self.colors['accent_red']
            badge_text = f"{tr('lists_status_duplicates')} ({duplicates})"

        badge_label = tk.Label(
            right, text=badge_text,
            font=("Segoe UI Variable", scale_size(9, self.scale_factor), "bold"),
            fg=badge_color,
            bg=self.colors['bg_light'],
            anchor='e'
        )
        badge_label.pack(anchor='e', pady=(scale_size(4, self.scale_factor), 0))

        def draw_rounded_bg(color):
            canvas.delete("bg")
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            if w <= 1 or h <= 1:
                return
            r = self.corner_radius
            points = [
                r, 0,
                w - r, 0,
                w, 0, w, r,
                w, h - r,
                w, h, w - r, h,
                r, h,
                0, h, 0, h - r,
                0, r,
                0, 0
            ]
            canvas.create_polygon(points, smooth=True, fill=color,
                                  outline='', tags="bg")
            canvas.tag_lower("bg")

        def on_canvas_resize(event):
            canvas.itemconfig(
                card_window,
                width=event.width - self.card_padx * 2,
                height=event.height - self.card_pady * 2
            )
            draw_rounded_bg(self.colors['bg_light'])

        canvas.bind("<Configure>", on_canvas_resize)

        def on_enter(_):
            draw_rounded_bg(self.colors['bg_light_hover'])
            for w in (card, inner, left, right, name_label, file_label,
                      lines_label, badge_label):
                w.configure(bg=self.colors['bg_light_hover'])

        def on_leave(_):
            draw_rounded_bg(self.colors['bg_light'])
            for w in (card, inner, left, right, name_label, file_label,
                      lines_label, badge_label):
                w.configure(bg=self.colors['bg_light'])

        def on_click(_):
            self.edit_list_file(filename)

        for w in (canvas, card, inner, left, right,
                  name_label, file_label, lines_label, badge_label):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        return wrapper

    def edit_list_file(self, filename):
        if not check_zapret_folder():
            return

        lists_path = os.path.join(self.app.zapret.zapret_dir, "lists")
        file_path = os.path.join(lists_path, filename)
        ListEditor(self.app.root, file_path, filename, app=self.app)

    def refresh(self):
        self.colors = self.app.colors
        self.refresh_stats()
        self._render_cards()

    def get_frame(self):
        return self.frame
