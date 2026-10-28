# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
import threading
import subprocess
import ctypes
import time
import json
from utils.languages import tr
from utils.scaling import scale_size
from config import ZAPRET_CORE_DIR, LISTS_DIR, CONFIG_FILE

class ServicePage:
    def __init__(self, parent, app):
        self.app = app
        self.colors = app.colors
        self.font_primary = app.font_primary
        self.font_medium = app.font_medium
        self.font_bold = app.font_bold
        self.scale_factor = getattr(app, 'scale_factor', 1.0)

        font_size_title = scale_size(20, self.scale_factor)
        font_size_desc = scale_size(10, self.scale_factor)
        font_size_card_name = scale_size(13, self.scale_factor)
        font_size_card_desc = scale_size(9, self.scale_factor)
        card_padx = scale_size(15, self.scale_factor)
        card_pady = scale_size(12, self.scale_factor)
        grid_gap = scale_size(10, self.scale_factor)
        padx = scale_size(30, self.scale_factor)
        pady = scale_size(10, self.scale_factor)

        self._card_name_font_size = font_size_card_name

        self.frame = tk.Frame(parent, bg=self.colors['bg_dark'])

        title_label = tk.Label(
            self.frame,
            text=tr('service_title'),
            font=("Inter", font_size_title, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        title_label.pack(anchor='w', pady=(scale_size(30, self.scale_factor), 5), padx=padx)

        desc_label = tk.Label(
            self.frame,
            text=tr('service_desc'),
            font=("Inter", font_size_desc),
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

        self._create_card(
            grid_frame, row=0, col=0,
            name=tr('service_game_filter'),
            desc=tr('service_game_filter_desc'),
            command=lambda: self._on_game_filter_click(),
            padx=(0, grid_gap // 2), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady,
            is_game_filter=True
        )

        self._create_card(
            grid_frame, row=0, col=1,
            name=tr('service_ipset_filter'),
            desc=tr('service_ipset_filter_desc'),
            command=lambda: self._on_ipset_filter_click(),
            padx=(grid_gap // 2, 0), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady,
            is_ipset_filter=True
        )

        self._create_card(
            grid_frame, row=1, col=0,
            name=tr('service_run_diagnostic'),
            desc=tr('service_run_diagnostic_desc'),
            command=self.run_diagnostics,
            padx=(0, grid_gap // 2), pady=(grid_gap // 2, 0),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady
        )

        self._create_card(
            grid_frame, row=1, col=1,
            name=tr('service_run_tests'),
            desc=tr('service_run_tests_desc'),
            command=self.run_tests,
            padx=(grid_gap // 2, 0), pady=(grid_gap // 2, 0),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady
        )

    def _create_card(self, parent, row, col, name, desc, command,
                     padx, pady, font_size_name, font_size_desc,
                     card_padx, card_pady, is_game_filter=False, is_ipset_filter=False):

        card_wrapper = tk.Frame(parent, bg=self.colors['bg_dark'], height=scale_size(80, self.scale_factor))
        card_wrapper.grid(row=row, column=col, sticky='nsew', padx=padx, pady=pady)
        card_wrapper.pack_propagate(False)
        card_wrapper.grid_propagate(False)

        card_canvas = tk.Canvas(card_wrapper, bg=self.colors['bg_dark'], highlightthickness=0, bd=0, cursor="hand2")
        card_canvas.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(card_canvas, bg=self.colors['bg_light'], cursor="hand2")
        card_window = card_canvas.create_window(
            (card_padx, card_pady),
            window=card,
            anchor='nw'
        )

        inner = tk.Frame(card, bg=self.colors['bg_light'])
        inner.pack(fill=tk.BOTH, expand=True)

        name_header = None
        name_labels = []

        if is_game_filter or is_ipset_filter:
            parts = (self._get_game_filter_status_parts() if is_game_filter
                     else self._get_ipset_status_parts())

            name_header = tk.Frame(inner, bg=self.colors['bg_light'])
            name_header.pack(anchor='w', fill=tk.X)

            name_labels = self._build_header_labels(
                name_header, parts, font_size_name
            )

            if is_game_filter:
                self.game_filter_name_header = name_header
                self.game_filter_name_labels = name_labels
            else:
                self.ipset_name_header = name_header
                self.ipset_name_labels = name_labels

            name_header.bind("<Button-1>", lambda e: command())
            for lbl in name_labels:
                lbl.bind("<Button-1>", lambda e: command())

            name_widget = name_header
        else:
            name_widget = tk.Label(
                inner,
                text=name,
                font=("Inter", font_size_name, "bold"),
                fg=self.colors['accent'],
                bg=self.colors['bg_light'],
                anchor='w',
                justify=tk.LEFT
            )
            name_widget.pack(anchor='w', fill=tk.X)

        desc_label = tk.Label(
            inner,
            text=desc,
            font=("Inter", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_light'],
            anchor='w',
            justify=tk.LEFT,
            wraplength=scale_size(300, self.scale_factor)
        )
        desc_label.pack(anchor='w', fill=tk.X, pady=(scale_size(6, self.scale_factor), 0))

        corner_radius = scale_size(10, self.scale_factor)

        def draw_rounded_bg(color):
            card_canvas.delete("bg")
            w = card_canvas.winfo_width()
            h = card_canvas.winfo_height()

            if w <= 1 or h <= 1:
                return

            r = corner_radius
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
            card_canvas.create_polygon(points, smooth=True, fill=color,
                                        outline='', tags="bg")
            card_canvas.tag_lower("bg")

        def on_canvas_resize(event):
            card_canvas.itemconfig(
                card_window,
                width=event.width - card_padx * 2,
                height=event.height - card_pady * 2
            )
            draw_rounded_bg(self.colors['bg_light'])

        card_canvas.bind("<Configure>", on_canvas_resize)

        def _apply_bg(color):
            draw_rounded_bg(color)
            card.configure(bg=color)
            inner.configure(bg=color)
            desc_label.configure(bg=color)
            if is_game_filter or is_ipset_filter:
                name_header.configure(bg=color)
                for lbl in name_labels:
                    lbl.configure(bg=color)
            else:
                name_widget.configure(bg=color)

        def on_enter(e):
            _apply_bg(self.colors['bg_light_hover'])

        def on_leave(e):
            _apply_bg(self.colors['bg_light'])

        def on_click(e):
            command()

        widgets_to_bind = [card_canvas, card, inner, desc_label]
        if not (is_game_filter or is_ipset_filter):
            widgets_to_bind.append(name_widget)

        for widget in widgets_to_bind:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

        if is_game_filter or is_ipset_filter:
            name_header.bind("<Enter>", on_enter)
            name_header.bind("<Leave>", on_leave)
            for lbl in name_labels:
                lbl.bind("<Enter>", on_enter)
                lbl.bind("<Leave>", on_leave)

    def _build_header_labels(self, header, parts, font_size_name):
        color_map = {
            'accent': self.colors['accent'],
            'green': self.colors['accent_green'],
            'red': self.colors['accent_red'],
        }
        labels = []
        for text, tag in parts:
            lbl = tk.Label(
                header,
                text=text,
                font=("Inter", font_size_name, "bold"),
                fg=color_map.get(tag, self.colors['accent']),
                bg=self.colors['bg_light'],
                anchor='w',
                padx=0, pady=0, bd=0,
            )
            lbl.pack(side=tk.LEFT, anchor='w')
            labels.append(lbl)
        return labels

    def _rebuild_header(self, header, labels, parts):
        for lbl in labels:
            lbl.destroy()
        labels.clear()

        new_labels = self._build_header_labels(header, parts, self._card_name_font_size)
        labels.extend(new_labels)

        enter_cb = header.bind("<Enter>")
        leave_cb = header.bind("<Leave>")
        click_cb = header.bind("<Button-1>")
        for lbl in new_labels:
            if enter_cb:
                lbl.bind("<Enter>", lambda e, f=enter_cb: header.event_generate("<Enter>"))
            if leave_cb:
                lbl.bind("<Leave>", lambda e, f=leave_cb: header.event_generate("<Leave>"))
            if click_cb:
                lbl.bind("<Button-1>", lambda e, f=click_cb: header.event_generate("<Button-1>"))

    def _get_game_filter_status_parts(self):
        mode_file = ZAPRET_CORE_DIR / "utils" / "game_filter.enabled"
        mode = "disabled"
        if mode_file.exists():
            try:
                for line in mode_file.read_text(encoding='utf-8').splitlines():
                    if line.lower().startswith("mode="):
                        mode = line.split("=", 1)[1].strip().lower()
                        break
            except Exception:
                pass

        if mode in ("all", "any"):
            tcp_tag, udp_tag = 'green', 'green'
        elif mode == "tcp":
            tcp_tag, udp_tag = 'green', 'red'
        elif mode == "udp":
            tcp_tag, udp_tag = 'red', 'green'
        else:
            tcp_tag, udp_tag = 'red', 'red'

        base = tr('service_game_filter')
        return [
            (f"{base} (", 'accent'),
            ("TCP", tcp_tag),
            ("/", 'accent'),
            ("UDP", udp_tag),
            (")", 'accent'),
        ]

    def _get_ipset_status_parts(self):
        mode = None

        flag_candidates = [
            ZAPRET_CORE_DIR / "utils" / "ipset.enabled",
            ZAPRET_CORE_DIR / "utils" / "ipset.txt",
            ZAPRET_CORE_DIR / "utils" / "ipset-all.enabled",
            ZAPRET_CORE_DIR / "ipset.enabled",
            ZAPRET_CORE_DIR / "ipset.txt",
        ]
        for flag_file in flag_candidates:
            if not flag_file.exists():
                continue
            try:
                for line in flag_file.read_text(encoding='utf-8', errors='ignore').splitlines():
                    s = line.strip()
                    low = s.lower()
                    val = None
                    for sep in ("=", ":"):
                        if low.startswith("mode" + sep) or low.startswith("mode " + sep):
                            val = s.split(sep, 1)[1].strip().lower()
                            break
                    if val:
                        mode = val
                        break
                    if low in ("any", "loaded", "none"):
                        mode = low
                        break
            except Exception:
                pass
            if mode is not None:
                break

        if mode is None:
            list_file = LISTS_DIR / "ipset-all.txt"
            if not list_file.exists():
                mode = "none"
            else:
                try:
                    content = list_file.read_text(encoding='utf-8', errors='ignore').strip()
                    if not content:
                        mode = "any"
                    else:
                        non_stub_lines = [
                            ln for ln in content.splitlines()
                            if ln.strip() and "203.0.113.113/32" not in ln
                        ]
                        mode = "loaded" if non_stub_lines else "none"
                except Exception:
                    mode = "none"

        if mode in ("any", "all", "both"):
            state, tag = "Any", 'green'
        elif mode in ("loaded", "load", "on", "true", "1"):
            state, tag = "Loaded", 'green'
        else:
            state, tag = "None", 'red'

        base = tr('service_ipset_filter')
        return [
            (f"{base} (", 'accent'),
            (state, tag),
            (")", 'accent'),
        ]

    def _on_game_filter_click(self):
        self.app.run_service_command("game_filter", callback=self._update_card_names)

    def _on_ipset_filter_click(self):
        self.app.run_service_command("ipset_filter", callback=self._update_card_names)

    def _update_card_names(self):
        if hasattr(self, 'game_filter_name_header') and self.game_filter_name_header.winfo_exists():
            self._rebuild_header(
                self.game_filter_name_header,
                self.game_filter_name_labels,
                self._get_game_filter_status_parts(),
            )

        if hasattr(self, 'ipset_name_header') and self.ipset_name_header.winfo_exists():
            self._rebuild_header(
                self.ipset_name_header,
                self.ipset_name_labels,
                self._get_ipset_status_parts(),
            )

    def run_diagnostics(self):
        def run():
            try:
                lang = 'Russian'
                try:
                    if CONFIG_FILE.exists():
                        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            lang = data.get('language', 'Russian')
                except Exception:
                    pass

                if lang == 'English':
                    bat_name = "service_en.bat"
                else:
                    bat_name = "service.bat"

                service_bat = ZAPRET_CORE_DIR / bat_name

                subprocess.Popen(
                    [str(service_bat)],
                    cwd=str(ZAPRET_CORE_DIR),
                    shell=False,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )

                time.sleep(2)

                ctypes.windll.user32.keybd_event(0x36, 0, 0, 0)
                time.sleep(0.2)
                ctypes.windll.user32.keybd_event(0x36, 0, 2, 0)
                time.sleep(0.2)
                ctypes.windll.user32.keybd_event(0x0D, 0, 0, 0)
                time.sleep(0.1)
                ctypes.windll.user32.keybd_event(0x0D, 0, 2, 0)

            except Exception as e:
                self.app.log_event("info", f"Diagnostics error: {e}")

        threading.Thread(target=run, daemon=True).start()

    def run_tests(self):
        def run():
            try:
                lang = 'Russian'
                try:
                    if CONFIG_FILE.exists():
                        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            lang = data.get('language', 'Russian')
                except Exception:
                    pass

                if lang == 'English':
                    bat_name = "service_en.bat"
                else:
                    bat_name = "service.bat"

                service_bat = ZAPRET_CORE_DIR / bat_name

                subprocess.Popen(
                    [str(service_bat)],
                    cwd=str(ZAPRET_CORE_DIR),
                    shell=False,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )

                time.sleep(2)

                ctypes.windll.user32.keybd_event(0x37, 0, 0, 0)
                time.sleep(0.2)
                ctypes.windll.user32.keybd_event(0x37, 0, 2, 0)
                time.sleep(0.2)
                ctypes.windll.user32.keybd_event(0x0D, 0, 0, 0)
                time.sleep(0.1)
                ctypes.windll.user32.keybd_event(0x0D, 0, 2, 0)

            except Exception as e:
                self.app.log_event("info", f"Tests error: {e}")

        threading.Thread(target=run, daemon=True).start()

    def get_frame(self):
        return self.frame
