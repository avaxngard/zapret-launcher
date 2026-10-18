# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict
from gui.widgets import RoundedButton
from gui.theme import get_theme_names
from utils.scaling import scale_size
from utils.languages import tr
from gui.theme import get_theme_display_name
import requests
import psutil
import time
import threading
import os

class Dialogs:
    def __init__(self, app):
        self.app = app
        self.colors = app.colors
        self.current_theme = app.current_theme
        self.scale_factor = getattr(app, 'scale_factor', 1.0)

    def _log(self, ctx: str, e: Exception):
        try:
            self.app.log_event("info", f"{ctx}: {e}")
        except Exception:
            pass
        
    def show_mode_selector(self):
        dialog_width = scale_size(500, self.scale_factor)
        dialog_height = scale_size(420, self.scale_factor)
        font_size_title = scale_size(16, self.scale_factor)
        font_size_name = scale_size(12, self.scale_factor)
        font_size_desc = scale_size(9, self.scale_factor)
        font_size_btn = scale_size(10, self.scale_factor)
        btn_width = scale_size(100, self.scale_factor)
        btn_height = scale_size(35, self.scale_factor)
        btn_width_cancel = scale_size(90, self.scale_factor)
        btn_radius = scale_size(8, self.scale_factor)
        padx = scale_size(20, self.scale_factor)
        pady = scale_size(10, self.scale_factor)
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(tr('mode_select_title'))
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['bg_medium'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.focus_force()
        
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - dialog_width // 2
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - dialog_height // 2
        
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        dialog.withdraw()
        self.app.set_dialog_header_color(dialog)
        dialog.update_idletasks()
        
        tk.Label(dialog, text=tr('mode_select'), font=("Segoe UI Variable", font_size_title, "bold"),
                fg=self.colors['text_primary'], bg=self.colors['bg_medium']).pack(pady=(scale_size(20, self.scale_factor), scale_size(10, self.scale_factor)))
        
        main_frame = tk.Frame(dialog, bg=self.colors['bg_medium'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)
        
        canvas = tk.Canvas(main_frame, bg=self.colors['bg_medium'], highlightthickness=0)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_medium'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=dialog_width - scale_size(60, self.scale_factor))
        canvas.configure(yscrollcommand=None)
        canvas.pack(side="left", fill="both", expand=True)
        
        modes = [
            {"name": tr('mode_standard'), "key": "Standard", "desc": tr('mode_standard_desc'), "zapret": True, "tgproxy": False},
            {"name": "Telegram Proxy", "key": "Telegram Proxy", "desc": tr('mode_tgproxy_desc'), "zapret": False, "tgproxy": True},
            {"name": tr('mode_zapret_tgproxy'), "key": "Combined", "desc": tr('mode_zapret_tgproxy_desc'), "zapret": True, "tgproxy": True}
        ]
        
        selected_index = [-1]
        selected_mode = [None]
        selected_widget = [None]
        mode_frames = []
        select_btn = [None]
        
        corner_radius = scale_size(10, self.scale_factor)
        card_padx = scale_size(15, self.scale_factor)
        card_pady = scale_size(8, self.scale_factor)
        
        def draw_rounded_bg(canvas_widget, color):
            canvas_widget.delete("bg")
            w = canvas_widget.winfo_width()
            h = canvas_widget.winfo_height()
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
            canvas_widget.create_polygon(points, smooth=True, fill=color, outline='', tags="bg")
            canvas_widget.tag_lower("bg")
        
        def update_select_button():
            if select_btn[0]:
                if selected_mode[0]:
                    select_btn[0].set_enabled(True)
                    select_btn[0].normal_color = self.colors['accent']
                    select_btn[0].hover_color = self.colors['accent']
                    select_btn[0].update_colors(
                        self.colors['accent'],
                        self.colors['button_text_hover'],
                        self.colors['accent']
                    )
                    select_btn[0].config(cursor="hand2")
                else:
                    select_btn[0].set_enabled(False)
                    select_btn[0].normal_color = self.colors['accent']
                    select_btn[0].hover_color = self.colors['accent']
                    select_btn[0].update_colors(
                        self.colors['button_bg'],
                        self.colors['button_text_hover'],
                        self.colors['button_bg']
                    )
                    select_btn[0].config(cursor="arrow")
        
        def select_mode_by_index(index):
            if not (0 <= index < len(mode_frames)):
                return
            
            if selected_widget[0]:
                prev_canvas, prev_card, prev_name, prev_desc, prev_idx = selected_widget[0]
                draw_rounded_bg(prev_canvas, self.colors['bg_light'])
                prev_card.configure(bg=self.colors['bg_light'])
                prev_name.configure(fg=self.colors['accent'], bg=self.colors['bg_light'])
                prev_desc.configure(fg=self.colors['text_secondary'], bg=self.colors['bg_light'])
            
            canvas_widget, card, name_label, desc_label = mode_frames[index]
            draw_rounded_bg(canvas_widget, self.colors['accent'])
            card.configure(bg=self.colors['accent'])
            name_label.configure(fg=self.colors['button_text_hover'], bg=self.colors['accent'])
            desc_label.configure(fg=self.colors['button_text_hover'], bg=self.colors['accent'])
            
            selected_widget[0] = (canvas_widget, card, name_label, desc_label, index)
            selected_mode[0] = modes[index]
            selected_index[0] = index
            update_select_button()
            canvas.yview_moveto(index / len(modes) if len(modes) > 0 else 0)
        
        def on_double_click(mode):
            if mode:
                dialog.destroy()
                self.app.start_with_mode(mode)
        
        def on_select_click():
            if selected_mode[0]:
                dialog.destroy()
                self.app.start_with_mode(selected_mode[0])
        
        def move_selection(delta):
            new_index = selected_index[0] + delta
            if 0 <= new_index < len(modes):
                select_mode_by_index(new_index)
        
        def on_key_press(event):
            if event.keysym == 'Up':
                move_selection(-1)
                return "break"
            elif event.keysym == 'Down':
                move_selection(1)
                return "break"
            elif event.keysym == 'Return':
                if selected_mode[0]:
                    dialog.destroy()
                    self.app.start_with_mode(selected_mode[0])
                return "break"
            elif event.keysym == 'Escape':
                dialog.destroy()
                return "break"
        
        dialog.bind('<Up>', on_key_press)
        dialog.bind('<Down>', on_key_press)
        dialog.bind('<Return>', on_key_press)
        dialog.bind('<Escape>', on_key_press)
        
        for idx, mode in enumerate(modes):
            card_height = scale_size(70, self.scale_factor)
            
            card_canvas = tk.Canvas(
                scrollable_frame,
                bg=self.colors['bg_medium'],
                highlightthickness=0,
                bd=0,
                cursor="hand2",
                height=card_height
            )
            card_canvas.pack(fill=tk.X, padx=scale_size(10, self.scale_factor), pady=scale_size(5, self.scale_factor))
            
            card = tk.Frame(card_canvas, bg=self.colors['bg_light'], cursor="hand2")
            card_window = card_canvas.create_window(
                (card_padx, card_pady),
                window=card,
                anchor='nw'
            )
            
            original_bg = self.colors['bg_light']
            
            name_label = tk.Label(card, text=mode["name"],
                                font=("Segoe UI Variable", font_size_name, "bold"),
                                fg=self.colors['accent'], bg=original_bg, anchor='w')
            name_label.pack(anchor='w', fill=tk.X)
            
            desc_label = tk.Label(card, text=mode["desc"],
                                font=("Segoe UI Variable", font_size_desc),
                                fg=self.colors['text_secondary'], bg=original_bg,
                                anchor='w', justify=tk.LEFT)
            desc_label.pack(anchor='w', fill=tk.X, pady=(scale_size(2, self.scale_factor), 0))
            
            mode_frames.append((card_canvas, card, name_label, desc_label))
            
            def make_on_canvas_resize(canvas_widget, window, pad_x, pad_y, orig_bg):
                def on_canvas_resize(event):
                    canvas_widget.itemconfig(
                        window,
                        width=event.width - pad_x * 2,
                        height=event.height - pad_y * 2
                    )
                    draw_rounded_bg(canvas_widget, orig_bg)
                return on_canvas_resize
            
            card_canvas.bind("<Configure>", make_on_canvas_resize(
                card_canvas, card_window, card_padx, card_pady, original_bg
            ))
            
            def make_on_enter(canvas_widget, card, nl, dl, idx_local):
                def on_enter_func(e):
                    if selected_widget[0] and selected_widget[0][4] == idx_local:
                        return
                    draw_rounded_bg(canvas_widget, self.colors['bg_light_hover'])
                    card.configure(bg=self.colors['bg_light_hover'])
                    nl.configure(bg=self.colors['bg_light_hover'])
                    dl.configure(bg=self.colors['bg_light_hover'])
                return on_enter_func
            
            def make_on_leave(canvas_widget, card, nl, dl, orig_bg, idx_local):
                def on_leave_func(e):
                    if selected_widget[0] and selected_widget[0][4] == idx_local:
                        return
                    draw_rounded_bg(canvas_widget, orig_bg)
                    card.configure(bg=orig_bg)
                    nl.configure(bg=orig_bg)
                    dl.configure(bg=orig_bg)
                return on_leave_func
            
            def make_on_click(idx_local):
                def on_click(e):
                    select_mode_by_index(idx_local)
                return on_click
            
            def make_on_double(m):
                return lambda e: on_double_click(m)
            
            on_enter_h = make_on_enter(card_canvas, card, name_label, desc_label, idx)
            on_leave_h = make_on_leave(card_canvas, card, name_label, desc_label, original_bg, idx)
            on_click_h = make_on_click(idx)
            on_double_h = make_on_double(mode)
            
            for widget in (card_canvas, card, name_label, desc_label):
                widget.bind("<Enter>", on_enter_h)
                widget.bind("<Leave>", on_leave_h)
                widget.bind("<Button-1>", on_click_h)
                widget.bind("<Double-Button-1>", on_double_h)
        
        bottom_frame = tk.Frame(dialog, bg=self.colors['bg_medium'])
        bottom_frame.pack(fill=tk.X, padx=padx, pady=scale_size(15, self.scale_factor))
        
        select_btn[0] = RoundedButton(
            bottom_frame,
            text=tr('mode_select_button'),
            command=on_select_click,
            width=btn_width, height=btn_height,
            bg=self.colors['accent'],
            fg=self.colors['button_text_hover'],
            hover_fg=self.colors['button_text_hover'],
            font=("Segoe UI Variable", font_size_btn),
            corner_radius=btn_radius
        )
        select_btn[0].normal_color = self.colors['accent']
        select_btn[0].hover_color = self.colors['accent']
        select_btn[0].set_enabled(True)
        select_btn[0].config(cursor="hand2")
        select_btn[0].pack(side=tk.RIGHT, padx=(scale_size(10, self.scale_factor), 0))
        
        cancel_btn = RoundedButton(
            bottom_frame,
            text=tr('mode_cancel'),
            command=dialog.destroy,
            width=btn_width_cancel, height=btn_height,
            bg=self.colors['button_bg'],
            fg=self.colors['button_text'],
            hover_fg=self.colors['button_text_hover'],
            font=("Segoe UI Variable", font_size_btn),
            corner_radius=btn_radius
        )
        cancel_btn.normal_color = self.colors['button_bg']
        cancel_btn.hover_color = self.colors['accent']
        cancel_btn.config(cursor="hand2")
        cancel_btn.pack(side=tk.RIGHT)
        dialog.deiconify()
        
    def show_strategy_selector(self, mode_name):
        dialog_width  = scale_size(520, self.scale_factor)
        dialog_height = scale_size(620, self.scale_factor)
        padx          = scale_size(20, self.scale_factor)
        fs_title  = scale_size(16, self.scale_factor)
        fs_input  = scale_size(11, self.scale_factor)
        fs_btn    = scale_size(10, self.scale_factor)
        fs_card   = scale_size(11, self.scale_factor)
        fs_badge  = scale_size(8,  self.scale_factor)
        btn_h     = scale_size(36, self.scale_factor)
        btn_rad   = scale_size(8,  self.scale_factor)

        dialog = tk.Toplevel(self.app.root)
        dialog.title(tr('select_strategy_title'))
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['bg_medium'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.withdraw()
        dialog.attributes('-alpha', 0.0)

        x = self.app.root.winfo_x() + (self.app.root.winfo_width()  // 2) - dialog_width  // 2
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - dialog_height // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.app.set_dialog_header_color(dialog)

        def on_close():
            self.app._cancel_strategy_selection(dialog)

        dialog.protocol("WM_DELETE_WINDOW", on_close)

        header = tk.Frame(dialog, bg=self.colors['bg_medium'])
        header.pack(fill=tk.X, padx=padx,
                    pady=(scale_size(16, self.scale_factor), scale_size(6, self.scale_factor)))

        tk.Label(
            header, text=tr('select_strategy'),
            font=("Segoe UI Variable", fs_title, "bold"),
            fg=self.colors['text_primary'], bg=self.colors['bg_medium'],
            anchor='center'
        ).pack(anchor='center')

        search_row = tk.Frame(dialog, bg=self.colors['bg_medium'])
        search_row.pack(fill=tk.X, padx=padx, pady=(0, scale_size(10, self.scale_factor)))

        search_wrap = tk.Frame(search_row, bg=self.colors['bg_light'],
                            highlightthickness=1,
                            highlightbackground=self.colors['bg_light'],
                            highlightcolor=self.colors['accent'])
        search_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True,
                        padx=(0, scale_size(8, self.scale_factor)))

        search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_wrap, textvariable=search_var,
            font=("Segoe UI Variable", fs_input),
            bg=self.colors['bg_light'], fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief=tk.FLAT, bd=0
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True,
                          ipady=scale_size(8, self.scale_factor),
                          padx=(scale_size(12, self.scale_factor), scale_size(12, self.scale_factor)))

        placeholder_label = tk.Label(
            search_wrap,
            text=tr('strategy_search_placeholder'),
            font=("Segoe UI Variable", fs_input),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_light'],
            anchor='w',
            cursor="xterm"
        )
        placeholder_label.place(in_=search_entry, x=0, rely=0.5, anchor='w')

        def _place_placeholder():
            placeholder_label.place(in_=search_entry, x=0, rely=0.5, anchor='w')

        def _remove_placeholder():
            placeholder_label.place_forget()

        def _on_var_write(*_):
            if search_var.get():
                _remove_placeholder()
            else:
                _place_placeholder()

        def _on_focus_in(_):
            search_wrap.configure(highlightbackground=self.colors['accent'])
            _remove_placeholder()

        def _on_focus_out(_):
            search_wrap.configure(highlightbackground=self.colors['bg_light'])
            if not search_var.get():
                _place_placeholder()

        def _on_placeholder_click(_):
            search_entry.focus_set()

        placeholder_label.bind("<Button-1>", _on_placeholder_click)
        search_var.trace_add("write", _on_var_write)
        search_entry.bind("<FocusIn>", _on_focus_in)
        search_entry.bind("<FocusOut>", _on_focus_out)

        def _is_descendant(widget, ancestor):
            w = widget
            while w is not None:
                if w == ancestor:
                    return True
                try:
                    w = w.master
                except Exception:
                    return False
            return False

        def _blur_search_entry():
            try:
                focused = dialog.focus_get()
            except Exception:
                focused = None
            if focused is search_entry:
                dialog.focus_force()

        def _on_any_click(event):
            try:
                clicked = event.widget
            except Exception:
                return
            if clicked is None:
                return
            if not _is_descendant(clicked, dialog):
                return
            if _is_descendant(clicked, search_wrap):
                return
            _blur_search_entry()

        def _bind_click_to_all(widget):
            try:
                widget.bind("<Button-1>", _on_any_click, add="+")
            except Exception:
                pass
            for child in widget.winfo_children():
                _bind_click_to_all(child)

        _bind_click_to_all(dialog)

        footer = tk.Frame(dialog, bg=self.colors['bg_medium'], highlightthickness=1, highlightbackground=self.colors['separator'])
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        footer_inner = tk.Frame(footer, bg=self.colors['bg_medium'])
        footer_inner.pack(fill=tk.X, padx=padx, pady=scale_size(12, self.scale_factor))

        list_outer = tk.Frame(dialog, bg=self.colors['bg_medium'])

        canvas = tk.Canvas(list_outer, bg=self.colors['bg_medium'], highlightthickness=0)
        vsb = ttk.Scrollbar(list_outer, orient=tk.VERTICAL, command=canvas.yview, style="Custom.Vertical.TScrollbar")
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = tk.Frame(canvas, bg=self.colors['bg_medium'])
        inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _sync_scrollregion(_=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", _sync_scrollregion)

        def _sync_inner_width(event):
            canvas.itemconfig(inner_id, width=event.width)
        canvas.bind("<Configure>", _sync_inner_width)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_wheel(_):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_wheel(_):
            try:
                canvas.unbind_all("<MouseWheel>")
            except Exception:
                pass

        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)
        dialog.bind("<Destroy>", lambda e: _unbind_wheel(None) if e.widget is dialog else None)

        empty_frame = tk.Frame(dialog, bg=self.colors['bg_medium'])
        tk.Label(
            empty_frame,
            text=tr('strategy_not_found'),
            font=("Segoe UI Variable", fs_card),
            fg=self.colors['text_secondary'], bg=self.colors['bg_medium']
        ).pack(pady=(scale_size(30, self.scale_factor), scale_size(8, self.scale_factor)))

        all_strategies = list(self.app.zapret.available_strategies)
        last_used = getattr(self.app, 'current_strategy', None)

        filtered = []
        selected_idx = [-1]
        card_widgets = []
        search_after_id = [None]

        start_btn = RoundedButton(
            footer_inner, text=tr('button_start'),
            command=lambda: launch_selected(),
            width=scale_size(110, self.scale_factor), height=btn_h,
            bg=self.colors['accent'], fg=self.colors['button_text_hover'],
            hover_fg=self.colors['button_text_hover'],
            font=("Segoe UI Variable", fs_btn),
            corner_radius=btn_rad, hover_color=self.colors['accent'],
            theme_name=self.current_theme
        )
        start_btn.pack(side=tk.RIGHT)

        cancel_btn = RoundedButton(
            footer_inner, text=tr('mode_cancel'), command=on_close,
            width=scale_size(90, self.scale_factor), height=btn_h,
            bg=self.colors['button_bg'], fg=self.colors['button_text'],
            hover_fg=self.colors['button_text_hover'],
            font=("Segoe UI Variable", fs_btn),
            corner_radius=btn_rad, hover_color=self.colors['accent'],
            theme_name=self.current_theme
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(0, scale_size(8, self.scale_factor)))

        strategies_count_label = tk.Label(
            footer_inner,
            text="",
            font=("Segoe UI Variable", scale_size(9, self.scale_factor)),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_medium'],
            anchor='w'
        )
        strategies_count_label.pack(side=tk.LEFT)

        gen_btn = RoundedButton(
            search_row,
            text=tr('generate'),
            command=lambda: messagebox.showinfo(tr('information_desc'), tr('dev')),
            width=scale_size(140, self.scale_factor), height=btn_h,
            bg=self.colors['accent'], fg=self.colors['button_text_hover'],
            hover_fg=self.colors['button_text_hover'],
            font=("Segoe UI Variable", fs_btn),
            corner_radius=btn_rad, hover_color=self.colors['accent'],
            theme_name=self.current_theme
        )
        gen_btn.pack(side=tk.RIGHT)

        def ordered_list(query: str):
            q = query.strip().lower()
            base = [s for s in all_strategies if (not q or q in s.lower())]
            if last_used and last_used in base:
                base = [last_used] + [s for s in base if s != last_used]
            return base

        def make_card(parent, name: str, idx: int, is_last: bool, query: str):
            corner_radius = scale_size(10, self.scale_factor)
            card_padx = scale_size(10, self.scale_factor)
            card_pady = scale_size(6, self.scale_factor)
            card_h = scale_size(46, self.scale_factor)

            wrapper = tk.Frame(parent, bg=self.colors['bg_medium'], height=card_h)
            wrapper.pack(fill=tk.X, padx=scale_size(6, self.scale_factor),
                         pady=scale_size(3, self.scale_factor))
            wrapper.pack_propagate(False)

            cv = tk.Canvas(wrapper, bg=self.colors['bg_medium'], highlightthickness=0, bd=0, cursor="hand2")
            cv.pack(fill=tk.BOTH, expand=True)

            card = tk.Frame(cv, bg=self.colors['bg_light'], cursor="hand2")
            card_win = cv.create_window((card_padx, card_pady), window=card, anchor='nw')

            inner_row = tk.Frame(card, bg=self.colors['bg_light'])
            inner_row.pack(fill=tk.BOTH, expand=True)

            name_box = tk.Frame(inner_row, bg=self.colors['bg_light'])
            name_box.pack(side=tk.LEFT, fill=tk.X, expand=True,
                          padx=scale_size(10, self.scale_factor),
                          pady=scale_size(6, self.scale_factor))

            q = query.strip()
            labels = []
            chunks_frame = None

            if not q:
                lbl = tk.Label(name_box, text=name, anchor='w',
                            font=("Segoe UI Variable", fs_card, "bold"),
                            fg=self.colors['accent_hover'], bg=self.colors['bg_light'])
                lbl.pack(anchor='w', fill=tk.X)
                labels.append(lbl)
            else:
                chunks_frame = tk.Frame(name_box, bg=self.colors['bg_light'])
                chunks_frame.pack(anchor='w', fill=tk.X)

                low = name.lower()
                qlow = q.lower()
                q_len = len(qlow)
                pos = 0
                n_len = len(name)

                while pos < n_len:
                    found = low.find(qlow, pos)
                    if found == -1:
                        chunk = name[pos:]
                        if chunk:
                            lbl = tk.Label(chunks_frame, text=chunk, anchor='w',
                                        font=("Segoe UI Variable", fs_card, "bold"),
                                        fg=self.colors['accent_hover'],
                                        bg=self.colors['bg_light'])
                            lbl.pack(side=tk.LEFT)
                            labels.append(lbl)
                        break

                    if found > pos:
                        chunk = name[pos:found]
                        lbl = tk.Label(chunks_frame, text=chunk, anchor='w',
                                    font=("Segoe UI Variable", fs_card, "bold"),
                                    fg=self.colors['accent_hover'],
                                    bg=self.colors['bg_light'])
                        lbl.pack(side=tk.LEFT)
                        labels.append(lbl)

                    match_chunk = name[found:found + q_len]
                    lbl = tk.Label(chunks_frame, text=match_chunk, anchor='w',
                                font=("Segoe UI Variable", fs_card, "bold"),
                                fg=self.colors['accent_green'],
                                bg=self.colors['bg_light'])
                    lbl.pack(side=tk.LEFT)
                    labels.append(lbl)

                    pos = found + q_len

            badge_lbl = None
            badge_canvas = None
            badge_draw = None
            badge_bg_state = {'color': None}

            if is_last:
                badge_text = tr('badge_last')
                badge_padx = scale_size(8, self.scale_factor)
                badge_pady = scale_size(2, self.scale_factor)
                badge_r = scale_size(8, self.scale_factor)

                _tmp = tk.Label(inner_row, text=badge_text, font=("Segoe UI Variable", fs_badge, "bold"))
                _tmp.update_idletasks()
                tw = _tmp.winfo_reqwidth()
                th = _tmp.winfo_reqheight()
                _tmp.destroy()

                badge_w = tw + badge_padx * 2
                badge_h = th + badge_pady * 2

                badge_canvas = tk.Canvas(
                    inner_row, width=badge_w, height=badge_h,
                    bg=self.colors['bg_light'], highlightthickness=0, bd=0
                )
                badge_canvas.pack(side=tk.RIGHT,
                                padx=(0, scale_size(10, self.scale_factor)),
                                pady=scale_size(6, self.scale_factor))

                badge_lbl = tk.Label(
                    badge_canvas, text=badge_text,
                    font=("Segoe UI Variable", fs_badge, "bold"),
                    fg=self.colors['bg_dark'], bg=self.colors['accent_green']
                )
                badge_lbl.place(relx=0.5, rely=0.5, anchor='center')

                def badge_draw(bg_outer, force=False):
                    if not force and badge_bg_state['color'] == bg_outer:
                        return
                    badge_bg_state['color'] = bg_outer
                    badge_canvas.delete("badge")
                    badge_canvas.configure(bg=bg_outer)
                    r = badge_r
                    pts = [r, 0, badge_w - r, 0, badge_w, 0, badge_w, r,
                        badge_w, badge_h - r, badge_w, badge_h,
                        badge_w - r, badge_h, r, badge_h,
                        0, badge_h, 0, badge_h - r,
                        0, r, 0, 0]
                    badge_canvas.create_polygon(pts, smooth=True,
                                                fill=self.colors['accent_green'],
                                                outline='', tags="badge")
                    badge_canvas.tag_lower("badge")

                badge_draw(self.colors['bg_light'], force=True)

            state = {'color': None, 'size': (0, 0)}

            def draw_bg(color, force=False):
                w, h = cv.winfo_width(), cv.winfo_height()
                if w <= 1 or h <= 1:
                    return
                size = (w, h)
                if not force and state['color'] == color and state['size'] == size:
                    return
                state['color'] = color
                state['size'] = size
                cv.delete("bg")
                r = corner_radius
                pts = [r, 0, w - r, 0, w, 0, w, r,
                    w, h - r, w, h, w - r, h,
                    r, h, 0, h, 0, h - r,
                    0, r, 0, 0]
                cv.create_polygon(pts, smooth=True, fill=color, outline='', tags="bg")
                cv.tag_lower("bg")

            def on_canvas_resize(event):
                cv.itemconfig(card_win,
                            width=event.width - card_padx * 2,
                            height=event.height - card_pady * 2)
                draw_bg(state['color'] or self.colors['bg_light'])

            cv.bind("<Configure>", on_canvas_resize)

            def _set_bg(color):
                for w in (card, inner_row, name_box, chunks_frame):
                    if w is None:
                        continue
                    try:
                        w.configure(bg=color)
                    except Exception:
                        pass
                for l in labels:
                    try:
                        l.configure(bg=color)
                    except Exception:
                        pass
                if badge_draw is not None:
                    try:
                        badge_draw(color)
                    except Exception:
                        pass

            def on_enter(_e):
                if selected_idx[0] == idx:
                    return
                draw_bg(self.colors['bg_light_hover'])
                _set_bg(self.colors['bg_light_hover'])

            def on_leave(_e):
                if selected_idx[0] == idx:
                    return
                draw_bg(self.colors['bg_light'])
                _set_bg(self.colors['bg_light'])

            def on_click(_e=None):
                select_index(idx)

            def on_dbl(_e=None):
                select_index(idx)
                launch_selected()

            click_widgets = [cv, wrapper, card, inner_row, name_box]
            if chunks_frame is not None:
                click_widgets.append(chunks_frame)
            click_widgets += labels
            if badge_canvas is not None:
                click_widgets.append(badge_canvas)
            if badge_lbl is not None:
                click_widgets.append(badge_lbl)

            for w in click_widgets:
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.bind("<Button-1>", on_click)
                w.bind("<Double-Button-1>", on_dbl)

            wrapper.after(1, lambda: draw_bg(self.colors['bg_light'], force=True))

            return {
                'name': name,
                'frame': wrapper,
                'canvas': cv,
                'card': card,
                'inner': inner_row,
                'name_box': name_box,
                'chunks_frame': chunks_frame,
                'labels': labels,
                'badge': badge_lbl,
                'badge_canvas': badge_canvas,
                'badge_draw': badge_draw,
                'draw_bg': draw_bg,
                'set_bg': _set_bg,
            }

        def apply_selection_style(idx: int, selected: bool):
            if not (0 <= idx < len(card_widgets)):
                return
            data = card_widgets[idx]
            bg = self.colors['accent'] if selected else self.colors['bg_light']
            try:
                data['draw_bg'](bg)
                data['set_bg'](bg)
            except Exception:
                pass

            fg = self.colors['button_text_hover'] if selected else self.colors['accent_hover']
            for l in data['labels']:
                try:
                    l.configure(fg=fg)
                except Exception:
                    pass

        def select_index(idx: int):
            if not (0 <= idx < len(card_widgets)):
                return
            for i in range(len(card_widgets)):
                apply_selection_style(i, selected=(i == idx))
            selected_idx[0] = idx
            update_start_btn()

        def update_start_btn():
            enabled = (0 <= selected_idx[0] < len(filtered))
            if enabled:
                start_btn.set_enabled(True)
                start_btn.update_colors(self.colors['accent'], '#FFFFFF', self.colors['accent'])
                start_btn.config(cursor="hand2")
            else:
                start_btn.set_enabled(False)
                start_btn.update_colors(self.colors['button_bg'],
                                        self.colors['text_secondary'],
                                        self.colors['button_bg'])
                start_btn.config(cursor="arrow")

        def redraw_list():
            for w in inner.winfo_children():
                w.destroy()
            card_widgets.clear()

            query = search_var.get()
            filtered[:] = ordered_list(query)

            if not filtered:
                list_outer.pack_forget()
                empty_frame.pack(fill=tk.BOTH, expand=True,
                                pady=scale_size(20, self.scale_factor))
                update_start_btn()
                return

            empty_frame.pack_forget()
            if not list_outer.winfo_ismapped():
                list_outer.pack(fill=tk.BOTH, expand=True,
                                padx=scale_size(14, self.scale_factor),
                                pady=(0, scale_size(6, self.scale_factor)),
                                before=footer)

            if selected_idx[0] >= len(filtered):
                selected_idx[0] = -1

            for i, name in enumerate(filtered):
                is_last = (name == last_used)
                card_widgets.append(make_card(inner, name, i, is_last, query))

            for i in range(len(card_widgets)):
                apply_selection_style(i, selected=(i == selected_idx[0]))

            update_start_btn()
            update_strategies_count()

        def update_strategies_count():
            total = len(all_strategies)
            shown = len(filtered)
            if shown == total:
                text = f"{tr('strategies_count')}: {total}"
            else:
                text = f"{tr('strategies_count')}: {shown} / {total}"
            try:
                strategies_count_label.config(text=text)
            except Exception:
                pass

        def _ensure_visible(idx: int):
            if not (0 <= idx < len(card_widgets)):
                return
            try:
                inner.update_idletasks()
                canvas.update_idletasks()

                frame = card_widgets[idx]['frame']
                card_y = frame.winfo_y()
                card_h = frame.winfo_height()

                inner_h = max(1, inner.winfo_height())
                canvas_h = canvas.winfo_height()

                top_frac, bottom_frac = canvas.yview()
                view_top = top_frac * inner_h
                view_bottom = bottom_frac * inner_h

                card_top = card_y
                card_bottom = card_y + card_h

                if card_top < view_top:
                    new_top = max(0, card_top - card_h * 0.2)
                    canvas.yview_moveto(new_top / inner_h)
                elif card_bottom > view_bottom:
                    new_top = max(0, card_bottom - canvas_h + card_h * 0.2)
                    canvas.yview_moveto(new_top / inner_h)
            except Exception:
                pass

        def on_search_change(*_):
            if search_after_id[0]:
                dialog.after_cancel(search_after_id[0])
            search_after_id[0] = dialog.after(200, do_filter)

        def do_filter():
            search_after_id[0] = None
            selected_idx[0] = -1
            redraw_list()

        search_var.trace_add("write", on_search_change)

        def on_key(event):
            if event.keysym == 'Escape':
                on_close()
                return "break"
            if event.keysym in ('Down', 'Up'):
                n = len(filtered)
                if not n:
                    return "break"
                cur = selected_idx[0]
                if event.keysym == 'Down':
                    new_idx = 0 if cur < 0 else min(cur + 1, n - 1)
                else:
                    new_idx = n - 1 if cur < 0 else max(cur - 1, 0)
                select_index(new_idx)
                _ensure_visible(new_idx)
                return "break"
            if event.keysym == 'Return':
                if 0 <= selected_idx[0] < len(filtered):
                    launch_selected()
                return "break"
            return None

        dialog.bind('<Escape>', on_key)
        dialog.bind('<Down>', on_key)
        dialog.bind('<Up>', on_key)
        dialog.bind('<Return>', on_key)
        search_entry.bind('<Escape>', on_key)
        search_entry.bind('<Down>', on_key)
        search_entry.bind('<Up>', on_key)
        search_entry.bind('<Return>', on_key)

        def set_last_used(name: str):
            nonlocal last_used
            last_used = name
            try:
                self.app.current_strategy = name
                self.app.save_settings()
            except Exception as e:
                self._log("set_last_used save", e)

        def launch_selected():
            if not (0 <= selected_idx[0] < len(filtered)):
                return

            name = filtered[selected_idx[0]]
            set_last_used(name)

            mode = self.app._pending_mode
            dialog.destroy()
            self.app._connecting = False
            self.app.force_tray_menu_update()

            self.app.strategy_var.set(name)
            self.app.update_status(f"{tr('status_starting')}", self.colors['accent'])
            if hasattr(self.app, 'connect_btn') and self.app.connect_btn:
                self.app.connect_btn.set_enabled(False)
            self.app.root.update()

            if mode and mode.get("name") == tr('mode_zapret_tgproxy'):
                def start_combined():
                    success, msg = self.app.zapret.run_strategy(name)
                    if not success:
                        self.app.root.after(0, lambda: self.app._on_combined_start_failed(msg))
                        return

                    self.app.current_strategy = name
                    self.app.save_settings()

                    tg_success = self.app.tg_proxy.start()
                    if not tg_success:
                        self.app.zapret.stop_current_strategy()
                        self.app.root.after(0, lambda: self.app._on_combined_start_failed(tr('error_tgproxy_start')))
                        return

                    if not self.app.tg_proxy.wait_for_start(8):
                        self.app.zapret.stop_current_strategy()
                        self.app.tg_proxy.stop()
                        self.app.root.after(0, lambda: self.app._on_combined_start_failed(tr('error_tgproxy_timeout')))
                        return

                    self.app.is_connected = True
                    self.app.stats.start_session()
                    self.app.start_stats_monitoring()

                    self.app._current_mode_key = mode["key"]
                    self.app.root.after(0, lambda: self.app._on_combined_start_success(mode["name"]))

                threading.Thread(target=start_combined, daemon=True).start()
                return

            success, msg = self.app.zapret.run_strategy(name)
            if not success:
                self.app.update_status(tr('status_error'), self.colors['accent_red'])
                messagebox.showerror(tr('error_startup'), msg)
                if hasattr(self.app, 'connect_btn') and self.app.connect_btn:
                    self.app.connect_btn.set_enabled(True)
                return

            self.app.current_strategy = name
            self.app.save_settings()

            if mode and mode.get("tgproxy", False):
                self.app.tg_proxy.start()

            self.app.is_connected = True
            self.app.stats.start_session()
            self.app.start_stats_monitoring()

            if hasattr(self.app, 'mode_label') and self.app.mode_label and mode:
                strategy_display = self.app.zapret.get_strategy_display_name(name)
                self.app.mode_label.config(
                    text=f"{mode['name']} ({strategy_display})",
                    fg=self.colors['accent_green']
                )
            self.app.update_status(f"{tr('status_connected')}", self.colors['accent_green'])
            self.app.update_ui_state()
            self.app.save_settings()
            self.app.root.after(500, self.app.update_tray_icon_state)
            if hasattr(self.app, 'connect_btn') and self.app.connect_btn:
                self.app.connect_btn.set_enabled(True)

            if mode:
                self.app._current_mode_key = mode["key"]
            try:
                if hasattr(self.app, 'user_stats') and mode:
                    self.app.user_stats.on_connect(mode["key"])
            except Exception as e:
                self._log("user_stats.on_connect", e)

            self.app.force_tray_menu_update()

        redraw_list()
        _bind_click_to_all(dialog)
        dialog.deiconify()
        dialog.update_idletasks()

        def _fade(alpha=0.0):
            if not dialog.winfo_exists():
                return
            alpha = min(1.0, alpha + 0.2)
            try:
                dialog.attributes('-alpha', alpha)
            except Exception:
                return
            if alpha < 1.0:
                dialog.after(10, lambda: _fade(alpha))

        _fade()

    def show_tg_proxy_instruction(self):
        dialog_width = scale_size(500, self.scale_factor)
        dialog_height = scale_size(520, self.scale_factor)
        font_size_title = scale_size(20, self.scale_factor)
        font_size_sub = scale_size(11, self.scale_factor)
        font_size_step = scale_size(13, self.scale_factor)
        font_size_text = scale_size(11, self.scale_factor)
        font_size_small = scale_size(10, self.scale_factor)
        font_size_btn = scale_size(10, self.scale_factor)
        btn_width = scale_size(100, self.scale_factor)
        btn_height = scale_size(35, self.scale_factor)
        btn_radius = scale_size(8, self.scale_factor)
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(tr('instruction_title_window'))
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['bg_medium'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.focus_force()
        
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - dialog_width // 2
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - dialog_height // 2
        
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        dialog.withdraw()
        self.app.set_dialog_header_color(dialog)
        dialog.update_idletasks()

        secret = getattr(self.app, '_tg_secret', None)
        if not secret:
            secret = tr('error_secret_not_found')
        
        title_frame = tk.Frame(dialog, bg=self.colors['bg_medium'])
        title_frame.pack(fill=tk.X, pady=(scale_size(20, self.scale_factor), scale_size(5, self.scale_factor)))
        
        title_label = tk.Label(title_frame, text=tr('tg_instruction_title'), 
                            font=("Segoe UI Variable", font_size_title, "bold"),
                            fg=self.colors['accent'], bg=self.colors['bg_medium'])
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text=tr('tg_instruction_subtitle'),
                                font=("Segoe UI Variable", font_size_sub),
                                fg=self.colors['text_secondary'], bg=self.colors['bg_medium'])
        subtitle_label.pack(pady=(scale_size(5, self.scale_factor), 0))
        separator = tk.Frame(dialog, bg=self.colors['separator'], height=2)
        separator.pack(fill=tk.X, padx=scale_size(30, self.scale_factor), pady=scale_size(10, self.scale_factor))
        instruction_frame = tk.Frame(dialog, bg=self.colors['bg_light'])
        instruction_frame.pack(fill=tk.BOTH, expand=True, padx=scale_size(30, self.scale_factor), pady=scale_size(5, self.scale_factor))
        
        steps = [
            ("1.", tr('tg_step1')),
            ("", tr('tg_step1_desc')),
            ("2.", tr('tg_step2')),
            ("", tr('tg_step2_desc')),
            ("3.", tr('tg_step3')),
            ("", tr('tg_type')),
            ("", tr('tg_host')),
            ("", tr('tg_port')),
        ]
        
        current_step = 0
        
        for i, step in enumerate(steps):
            text, desc = step
            if text:
                step_frame = tk.Frame(instruction_frame, bg=self.colors['bg_light'])
                step_frame.pack(fill=tk.X, pady=(scale_size(10, self.scale_factor) if current_step > 0 else 0, scale_size(2, self.scale_factor)))
                
                step_num = tk.Label(step_frame, text=text, font=("Segoe UI Variable", font_size_step, "bold"),
                                fg=self.colors['accent'], bg=self.colors['bg_light'])
                step_num.pack(side=tk.LEFT)
                
                step_text = tk.Label(step_frame, text=desc, font=("Segoe UI Variable", font_size_text),
                                    fg=self.colors['text_primary'], bg=self.colors['bg_light'])
                step_text.pack(side=tk.LEFT, padx=(scale_size(5, self.scale_factor), 0))
                current_step += 1
            else:
                sub_frame = tk.Frame(instruction_frame, bg=self.colors['bg_light'])
                sub_frame.pack(fill=tk.X, pady=scale_size(1, self.scale_factor))
                
                spacer = tk.Label(sub_frame, text="   ", font=("Segoe UI Variable", font_size_text),
                                fg=self.colors['text_primary'], bg=self.colors['bg_light'])
                spacer.pack(side=tk.LEFT)
                
                bullet = tk.Label(sub_frame, text="▸", font=("Segoe UI Variable", font_size_small),
                                fg=self.colors['accent'], bg=self.colors['bg_light'])
                bullet.pack(side=tk.LEFT, padx=(scale_size(10, self.scale_factor), scale_size(5, self.scale_factor)))
                
                sub_text = tk.Label(sub_frame, text=desc, font=("Segoe UI Variable", font_size_small),
                                fg=self.colors['text_secondary'], bg=self.colors['bg_light'])
                sub_text.pack(side=tk.LEFT)
        
        link_frame = tk.Frame(instruction_frame, bg=self.colors['bg_light'])
        link_frame.pack(fill=tk.X, pady=(scale_size(10, self.scale_factor), scale_size(5, self.scale_factor)))
        
        spacer = tk.Label(link_frame, text="   ", font=("Segoe UI Variable", font_size_text),
                        fg=self.colors['text_primary'], bg=self.colors['bg_light'])
        spacer.pack(side=tk.LEFT)
        
        bullet = tk.Label(link_frame, text="▸", font=("Segoe UI Variable", font_size_small),
                        fg=self.colors['accent'], bg=self.colors['bg_light'])
        bullet.pack(side=tk.LEFT, padx=(scale_size(10, self.scale_factor), scale_size(5, self.scale_factor)))
        
        copy_frame = tk.Frame(link_frame, bg=self.colors['bg_light'], cursor="hand2")
        copy_frame.pack(side=tk.LEFT, padx=(0, scale_size(10, self.scale_factor)))
        
        link_text = tr('tg_copy_secret')
        copy_label = tk.Label(copy_frame, text=link_text, font=("Segoe UI Variable", font_size_small),
                            fg=self.colors['accent'], bg=self.colors['bg_light'])
        copy_label.pack()
        
        def copy_link(event=None):
            secret = getattr(self.app, '_tg_secret', None)
            if not secret:
                secret = tr('error_secret_not_found')
            
            if self.app.tg_fake_tls and self.app.tg_fake_tls_domain:
                domain_hex = self.app.tg_fake_tls_domain.encode('ascii').hex()
                link = f"ee{secret}{domain_hex}"
                notification = tr('notification_copied_secret')
            else:
                link = f"{secret}"
                notification = tr('notification_copied_secret')
            
            self.app.root.clipboard_clear()
            self.app.root.clipboard_append(link)
            self.app.root.update()
            copy_label.config(text=tr('tg_copied'), fg=self.colors['accent_green'])
            self.app.show_notification(notification, 1500)
        
        copy_label.bind("<Button-1>", copy_link)
        
        def on_enter(event):
            copy_label.config(fg=self.colors['accent_hover'], font=("Segoe UI Variable", font_size_small, "underline"))
            copy_frame.config(cursor="hand2")
        
        def on_leave(event):
            copy_label.config(fg=self.colors['accent'], font=("Segoe UI Variable", font_size_small))
        
        copy_label.bind("<Enter>", on_enter)
        copy_label.bind("<Leave>", on_leave)
        
        bottom_frame = tk.Frame(dialog, bg=self.colors['bg_medium'])
        bottom_frame.pack(fill=tk.X, padx=scale_size(30, self.scale_factor), pady=scale_size(15, self.scale_factor))
        dont_show_var = tk.BooleanVar(value=False)

        dont_show_cb = tk.Checkbutton(
            bottom_frame,
            text=tr('tg_dont_show'),
            variable=dont_show_var,
            bg=self.colors['bg_medium'],
            fg=self.colors['text_secondary'],
            selectcolor=self.colors['bg_medium'],
            activebackground=self.colors['bg_medium'],
            activeforeground=self.colors['text_secondary'],
            highlightthickness=0,
            bd=0,
            padx=0,
            font=("Segoe UI Variable", font_size_small)
        )
        dont_show_cb.pack(side=tk.LEFT)

        def on_close():
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_close)
        dialog.bind('<Escape>', lambda e: on_close())

        close_btn = RoundedButton(
            bottom_frame,
            text=tr('button_close'),
            command=lambda: self.app._cancel_tg_proxy_mode(dialog, dont_show_var.get()),
            width=btn_width, height=btn_height,
            bg=self.colors['accent'],
            fg=self.colors['button_text_hover'],
            hover_fg=self.colors['button_text_hover'],
            font=("Segoe UI Variable", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'], 
            theme_name=self.current_theme
        )
        close_btn.pack(side=tk.RIGHT)
        dialog.deiconify()

    def show_duplicates_dialog(self, duplicates_text: str):
        dialog_width = scale_size(700, self.scale_factor)
        dialog_height = scale_size(550, self.scale_factor)
        font_size_title = scale_size(20, self.scale_factor)
        font_size_sub = scale_size(11, self.scale_factor)
        font_size_text = scale_size(9, self.scale_factor)
        font_size_btn = scale_size(10, self.scale_factor)
        btn_width = scale_size(120, self.scale_factor)
        btn_height = scale_size(35, self.scale_factor)
        btn_radius = scale_size(8, self.scale_factor)
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(tr('error_warning'))
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['bg_medium'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.focus_force()
        
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - dialog_width // 2
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - dialog_height // 2
        
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        dialog.withdraw()
        self.app.set_dialog_header_color(dialog)
        dialog.update_idletasks()
        
        title_frame = tk.Frame(dialog, bg=self.colors['bg_medium'])
        title_frame.pack(fill=tk.X, pady=(scale_size(20, self.scale_factor), scale_size(5, self.scale_factor)))
        
        title_label = tk.Label(
            title_frame,
            text=tr('duplicates_title'),
            font=("Segoe UI Variable", font_size_title, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['bg_medium']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text=tr('duplicates_subtitle'),
            font=("Segoe UI Variable", font_size_sub),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_medium']
        )
        subtitle_label.pack(pady=(scale_size(5, self.scale_factor), 0))
        
        separator = tk.Frame(dialog, bg=self.colors['separator'], height=2)
        separator.pack(fill=tk.X, padx=scale_size(30, self.scale_factor), pady=scale_size(10, self.scale_factor))
        
        message_frame = tk.Frame(dialog, bg=self.colors['bg_light'])
        message_frame.pack(fill=tk.BOTH, expand=True, padx=scale_size(15, self.scale_factor), pady=scale_size(3, self.scale_factor))
        
        text_frame = tk.Frame(message_frame, bg=self.colors['bg_light'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=scale_size(5, self.scale_factor), pady=scale_size(5, self.scale_factor))
        
        text_widget = tk.Text(
            text_frame,
            font=("Consolas", font_size_text),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark'],
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(
            text_frame,
            orient=tk.VERTICAL,
            command=text_widget.yview,
            style="Custom.Vertical.TScrollbar"
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.insert(tk.END, duplicates_text)
        text_widget.config(state=tk.DISABLED)
        
        bottom_frame = tk.Frame(dialog, bg=self.colors['bg_medium'], height=scale_size(70, self.scale_factor))
        bottom_frame.pack(fill=tk.X, padx=scale_size(30, self.scale_factor), pady=(scale_size(10, self.scale_factor), scale_size(15, self.scale_factor)))
        bottom_frame.pack_propagate(False)
        
        def on_close():
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_close)
        dialog.bind('<Escape>', lambda e: on_close())
        
        button_frame = tk.Frame(bottom_frame, bg=self.colors['bg_medium'])
        button_frame.place(relx=1.0, y=scale_size(17, self.scale_factor), anchor='ne')
        
        ignore_btn = RoundedButton(
            button_frame,
            text=tr('vpn_ignore'),
            command=on_close,
            width=btn_width, height=btn_height,
            bg=self.colors['button_bg'],
            fg=self.colors['button_text'],
            hover_fg=self.colors['button_text_hover'],
            font=("Segoe UI Variable", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'],
            theme_name=self.current_theme
        )
        ignore_btn.pack(side=tk.RIGHT, padx=(0, scale_size(5, self.scale_factor)))
        dialog.deiconify()

    def show_vpn_detected_dialog(self, vpn_data: Dict = None, callback=None):
        dialog_width = scale_size(500, self.scale_factor)
        dialog_height = scale_size(350, self.scale_factor)
        font_size_title = scale_size(20, self.scale_factor)
        font_size_text = scale_size(10, self.scale_factor)
        font_size_btn = scale_size(10, self.scale_factor)
        btn_width = scale_size(110, self.scale_factor)
        btn_width_ignore = scale_size(120, self.scale_factor)
        btn_height = scale_size(35, self.scale_factor)
        btn_radius = scale_size(8, self.scale_factor)
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(tr('error_warning'))
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['bg_medium'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.focus_force()

        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - dialog_width // 2
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - dialog_height // 2
        
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        dialog.withdraw()
        self.app.set_dialog_header_color(dialog)
        dialog.update_idletasks()
        
        title_frame = tk.Frame(dialog, bg=self.colors['bg_medium'])
        title_frame.pack(fill=tk.X, pady=(scale_size(20, self.scale_factor), scale_size(5, self.scale_factor)))
        
        title_label = tk.Label(
            title_frame, 
            text=tr('vpn_detected_title'), 
            font=("Segoe UI Variable", font_size_title, "bold"),
            fg=self.colors['accent'], 
            bg=self.colors['bg_medium']
        )
        title_label.pack()
        
        separator = tk.Frame(dialog, bg=self.colors['separator'], height=2)
        separator.pack(fill=tk.X, padx=scale_size(30, self.scale_factor), pady=scale_size(10, self.scale_factor))
        
        message_frame = tk.Frame(dialog, bg=self.colors['bg_light'])
        message_frame.pack(fill=tk.BOTH, expand=True, padx=scale_size(30, self.scale_factor), pady=scale_size(5, self.scale_factor))
        
        inner = tk.Frame(message_frame, bg=self.colors['bg_light'])
        inner.pack(fill=tk.BOTH, expand=True, padx=scale_size(15, self.scale_factor), pady=scale_size(10, self.scale_factor))
        
        message_text = tr('vpn_detected_message')
        
        if vpn_data and vpn_data.get('vpn_processes'):
            procs = ', '.join(vpn_data['vpn_processes'][:3])
            message_text += f"\n\n{tr('vpn_detected_processes')}: {procs}"
        
        if vpn_data and vpn_data.get('vpn_interfaces'):
            ifaces = ', '.join(vpn_data['vpn_interfaces'][:3])
            message_text += f"\n{tr('vpn_detected_interfaces')}: {ifaces}"
        
        message_label = tk.Label(
            inner,
            text=message_text,
            font=("Segoe UI Variable", font_size_text),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_light'],
            wraplength=scale_size(400, self.scale_factor),
            justify=tk.LEFT
        )
        message_label.pack(pady=scale_size(10, self.scale_factor))
        
        bottom_frame = tk.Frame(dialog, bg=self.colors['bg_medium'], height=scale_size(70, self.scale_factor))
        bottom_frame.pack(fill=tk.X, padx=scale_size(30, self.scale_factor), pady=(scale_size(10, self.scale_factor), scale_size(15, self.scale_factor)))
        bottom_frame.pack_propagate(False)
        
        def on_dialog_close():
            on_ignore()
                
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        dialog.bind('<Escape>', lambda e: on_dialog_close())

        def on_ignore():
            dialog.destroy()
            if callback:
                self.app.root.after(100, callback)
            else:
                self.app.dialogs.show_mode_selector()

        def on_disable():
            dialog.destroy()
            
            if vpn_data and vpn_data.get('vpn_processes'):
                killed_count = 0
                for proc_name in vpn_data['vpn_processes']:
                    try:
                        for proc in psutil.process_iter(['name', 'pid']):
                            try:
                                if proc.info['name'] and proc_name.lower() in proc.info['name'].lower():
                                    proc.kill()
                                    killed_count += 1
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                continue
                    except Exception as e:
                        self._log(f"kill vpn proc {proc_name}", e)

            if callback:
                self.app.root.after(100, callback)
            else:
                self.app.dialogs.show_mode_selector()

        button_frame = tk.Frame(bottom_frame, bg=self.colors['bg_medium'])
        button_frame.place(relx=1.0, y=scale_size(17, self.scale_factor), anchor='ne')

        disable_btn = RoundedButton(
            button_frame,
            text=tr('vpn_disable'),
            command=on_disable,
            width=btn_width, height=btn_height,
            bg=self.colors['accent'],
            fg=self.colors['button_text_hover'],
            hover_fg=self.colors['button_text_hover'],
            font=("Segoe UI Variable", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'],
            theme_name=self.current_theme
        )
        disable_btn.pack(side=tk.RIGHT, padx=(0, scale_size(5, self.scale_factor)))

        ignore_btn = RoundedButton(
            button_frame,
            text=tr('vpn_ignore'),
            command=on_ignore,
            width=btn_width_ignore, height=btn_height,
            bg=self.colors['button_bg'],
            fg=self.colors['button_text'],
            hover_fg=self.colors['button_text_hover'],
            font=("Segoe UI Variable", font_size_btn),
            corner_radius=btn_radius,
            hover_color=self.colors['accent'],
            theme_name=self.current_theme
        )
        ignore_btn.pack(side=tk.RIGHT, padx=(0, scale_size(5, self.scale_factor)))
        dialog.deiconify()

    def show_templates_dialog(self):
        dialog_width = scale_size(500, self.scale_factor)
        dialog_height = scale_size(550, self.scale_factor)
        font_size_title = scale_size(16, self.scale_factor)
        font_size_name = scale_size(12, self.scale_factor)
        font_size_desc = scale_size(9, self.scale_factor)
        font_size_btn = scale_size(10, self.scale_factor)
        btn_width = scale_size(100, self.scale_factor)
        btn_width_cancel = scale_size(90, self.scale_factor)
        btn_height = scale_size(35, self.scale_factor)
        btn_radius = scale_size(8, self.scale_factor)
        padx = scale_size(20, self.scale_factor)
        pady = scale_size(10, self.scale_factor)
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(tr('hosts_download'))
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['bg_medium'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.focus_force()
        
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - dialog_width // 2
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - dialog_height // 2
        
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        dialog.withdraw()
        self.app.set_dialog_header_color(dialog)
        dialog.update_idletasks()
        
        tk.Label(dialog, text=tr('hosts_templates_title'), font=("Segoe UI Variable", font_size_title, "bold"),
                fg=self.colors['text_primary'], bg=self.colors['bg_medium']).pack(pady=(scale_size(20, self.scale_factor), scale_size(10, self.scale_factor)))
        
        main_frame = tk.Frame(dialog, bg=self.colors['bg_medium'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)
        
        canvas = tk.Canvas(main_frame, bg=self.colors['bg_medium'], highlightthickness=0)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_medium'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=dialog_width - scale_size(60, self.scale_factor))
        canvas.configure(yscrollcommand=None)
        canvas.pack(side="left", fill="both", expand=True)
        
        templates = [
            {
                'id': 'telegram',
                'name': 'Telegram Web',
                'desc': tr('hosts_template_telegram'),
                'url': 'https://zapret-launcher.ru/updater/docs/packs/telegram.txt'
            },
            {
                'id': 'rutracker',
                'name': 'RuTracker',
                'desc': tr('hosts_template_rutracker'),
                'url': 'https://zapret-launcher.ru/updater/docs/packs/rutracker.txt'
            },
            {
                'id': 'spotify',
                'name': 'Spotify',
                'desc': tr('hosts_template_spotify'),
                'url': 'https://zapret-launcher.ru/updater/docs/packs/spotify.txt'
            },
            {
                'id': 'github',
                'name': 'GitHub',
                'desc': tr('hosts_template_github'),
                'url': 'https://zapret-launcher.ru/updater/docs/packs/github.txt'
            },
            {
                'id': 'discord',
                'name': 'Discord',
                'desc': tr('hosts_template_discord'),
                'url': 'https://zapret-launcher.ru/updater/docs/packs/discord.txt'
            }
        ]
        
        selected_index = [-1]
        selected_template = [None]
        selected_widget = [None]
        template_frames = []
        select_btn = [None]
        
        corner_radius = scale_size(10, self.scale_factor)
        card_padx = scale_size(15, self.scale_factor)
        card_pady = scale_size(8, self.scale_factor)
        
        def draw_rounded_bg(canvas_widget, color):
            canvas_widget.delete("bg")
            w = canvas_widget.winfo_width()
            h = canvas_widget.winfo_height()
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
            canvas_widget.create_polygon(points, smooth=True, fill=color, outline='', tags="bg")
            canvas_widget.tag_lower("bg")
        
        def update_select_button():
            if select_btn[0]:
                if selected_template[0]:
                    select_btn[0].set_enabled(True)
                    select_btn[0].normal_color = self.colors['accent']
                    select_btn[0].hover_color = self.colors['accent']
                    select_btn[0].update_colors(
                        self.colors['accent'],
                        self.colors['button_text_hover'],
                        self.colors['accent']
                    )
                    select_btn[0].config(cursor="hand2")
                else:
                    select_btn[0].set_enabled(False)
                    select_btn[0].normal_color = self.colors['accent']
                    select_btn[0].hover_color = self.colors['accent']
                    select_btn[0].update_colors(
                        self.colors['button_bg'],
                        self.colors['button_text_hover'],
                        self.colors['button_bg']
                    )
                    select_btn[0].config(cursor="arrow")
        
        def select_template_by_index(index):
            if not (0 <= index < len(template_frames)):
                return
            
            if selected_widget[0]:
                prev_canvas, prev_card, prev_name, prev_desc, prev_idx = selected_widget[0]
                draw_rounded_bg(prev_canvas, self.colors['bg_light'])
                prev_card.configure(bg=self.colors['bg_light'])
                prev_name.configure(fg=self.colors['accent'], bg=self.colors['bg_light'])
                prev_desc.configure(fg=self.colors['text_secondary'], bg=self.colors['bg_light'])
            
            canvas_widget, card, name_label, desc_label = template_frames[index]
            draw_rounded_bg(canvas_widget, self.colors['accent'])
            card.configure(bg=self.colors['accent'])
            name_label.configure(fg=self.colors['button_text_hover'], bg=self.colors['accent'])
            desc_label.configure(fg=self.colors['button_text_hover'], bg=self.colors['accent'])
            
            selected_widget[0] = (canvas_widget, card, name_label, desc_label, index)
            selected_template[0] = templates[index]
            selected_index[0] = index
            update_select_button()
            canvas.yview_moveto(index / len(templates) if len(templates) > 0 else 0)
        
        def on_double_click(template):
            if template:
                dialog.destroy()
                download_template_direct(template)
        
        def on_select_click():
            if selected_template[0]:
                dialog.destroy()
                download_template_direct(selected_template[0])
        
        def move_selection(delta):
            new_index = selected_index[0] + delta
            if 0 <= new_index < len(templates):
                select_template_by_index(new_index)
        
        def on_key_press(event):
            if event.keysym == 'Up':
                move_selection(-1)
                return "break"
            elif event.keysym == 'Down':
                move_selection(1)
                return "break"
            elif event.keysym == 'Return':
                if selected_template[0]:
                    dialog.destroy()
                    download_template_direct(selected_template[0])
                return "break"
            elif event.keysym == 'Escape':
                dialog.destroy()
                return "break"
        
        dialog.bind('<Up>', on_key_press)
        dialog.bind('<Down>', on_key_press)
        dialog.bind('<Return>', on_key_press)
        dialog.bind('<Escape>', on_key_press)
        
        def download_template_direct(template):
            if not messagebox.askyesno(tr('confirm_title'), f"{tr('hosts_confirm_download')}\n\n{template['desc']}"):
                return
            
            try:
                response = requests.get(template['url'], timeout=30)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    messagebox.showerror(tr('error'), f"HTTP {response.status_code}")
                    return
                
                template_content = response.text
                
                if not template_content.strip():
                    messagebox.showerror(tr('error'), tr('hosts_empty_content'))
                    return
                
                hosts_page_obj = self.app.pages.hosts_page_obj
                hosts_path = hosts_page_obj.hosts_path
                
                current_content = ""
                if hosts_path.exists():
                    with open(hosts_path, 'r', encoding='utf-8') as f:
                        current_content = f.read()
                
                template_entries = []
                for line in template_content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 2:
                            ip = parts[0]
                            domains = parts[1:]
                            for domain in domains:
                                template_entries.append({'ip': ip, 'domain': domain})
                
                existing_entries = []
                for line in current_content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 2:
                            ip = parts[0]
                            domains = parts[1:]
                            for domain in domains:
                                existing_entries.append({'ip': ip, 'domain': domain})
                
                existing_set = {(e['ip'], e['domain']) for e in existing_entries}
                template_set = {(e['ip'], e['domain']) for e in template_entries}
                
                missing_entries = template_set - existing_set
                
                if not missing_entries:
                    messagebox.showinfo(tr('information_desc'), f"{tr('hosts_pack')} {template['name']} {tr('hosts_already_exists')}")
                    return
                
                has_any = bool(template_set & existing_set)
                
                if has_any:
                    missing_list = list(missing_entries)
                    if messagebox.askyesno(
                        tr('hosts_update_title'), 
                        f"{tr('hosts_pack')} {template['name']} {tr('hosts_partial_exists')}\n\n"
                        f"{tr('hosts_missing_entries')}:\n" + 
                        "\n".join([f"{ip} {domain}" for ip, domain in missing_list[:5]]) + 
                        (f"\n... {tr('and')} {len(missing_list) - 5}" if len(missing_list) > 5 else "") + 
                        f"\n\n{tr('hosts_update_question')}"
                    ):
                        with open(hosts_path, 'a', encoding='utf-8') as f:
                            if current_content and not current_content.endswith('\n'):
                                f.write('\n')
                            f.write(f'\n# Added by Zapret Launcher - {template["name"]} (update)\n')
                            for ip, domain in missing_list:
                                f.write(f"{ip} {domain}\n")
                        
                        hosts_page_obj.load_hosts()
                        self.app.log_event("information_desc", f"Updated template: {template['name']}")
                        messagebox.showinfo(tr('information_desc'), f"{tr('hosts_pack')} {template['name']} {tr('hosts_updated')}")
                        return
                    else:
                        return
                
                os.makedirs(os.path.dirname(hosts_path), exist_ok=True)
                
                with open(hosts_path, 'a', encoding='utf-8') as f:
                    if current_content and not current_content.endswith('\n'):
                        f.write('\n')
                    
                    f.write(f'\n# Added by Zapret Launcher - {template["name"]}\n')
                    f.write(template_content)
                    if not template_content.endswith('\n'):
                        f.write('\n')
                
                hosts_page_obj.load_hosts()
                
                self.app.log_event("information_desc", f"Installed template: {template['name']}")
                messagebox.showinfo(tr('information_desc'), f"{tr('hosts_pack')} {template['name']} {tr('hosts_installed')}")
                
            except requests.exceptions.ConnectionError:
                messagebox.showerror(tr('error'), tr('error_no_connection'))
            except requests.exceptions.Timeout:
                messagebox.showerror(tr('error'), tr('error_timeout'))
            except Exception as e:
                messagebox.showerror(tr('error'), f"{tr('error')}: {str(e)}")
                self.app.log_event("error", f"Error downloading template: {e}")
        
        for idx, template in enumerate(templates):
            card_canvas = tk.Canvas(
                scrollable_frame,
                bg=self.colors['bg_medium'],
                highlightthickness=0,
                bd=0,
                cursor="hand2",
                height=scale_size(70, self.scale_factor)
            )
            card_canvas.pack(fill=tk.X, padx=scale_size(10, self.scale_factor), pady=scale_size(5, self.scale_factor))
            
            card = tk.Frame(card_canvas, bg=self.colors['bg_light'], cursor="hand2")
            card_window = card_canvas.create_window(
                (card_padx, card_pady),
                window=card,
                anchor='nw'
            )
            
            original_bg = self.colors['bg_light']
            
            name_label = tk.Label(
                card, text=template["name"],
                font=("Segoe UI Variable", font_size_name, "bold"),
                fg=self.colors['accent'], bg=original_bg, anchor='w'
            )
            name_label.pack(anchor='w', fill=tk.X)
            
            desc_label = tk.Label(
                card, text=template["desc"],
                font=("Segoe UI Variable", font_size_desc),
                fg=self.colors['text_secondary'], bg=original_bg,
                anchor='w', justify=tk.LEFT
            )
            desc_label.pack(anchor='w', fill=tk.X, pady=(scale_size(2, self.scale_factor), 0))
            
            template_frames.append((card_canvas, card, name_label, desc_label))
            
            def make_on_canvas_resize(canvas_widget, window, pad_x, pad_y, orig_bg):
                def on_canvas_resize(event):
                    canvas_widget.itemconfig(
                        window,
                        width=event.width - pad_x * 2,
                        height=event.height - pad_y * 2
                    )
                    draw_rounded_bg(canvas_widget, orig_bg)
                return on_canvas_resize
            
            card_canvas.bind("<Configure>", make_on_canvas_resize(
                card_canvas, card_window, card_padx, card_pady, original_bg
            ))
            
            def make_on_enter(canvas_widget, card, nl, dl, idx_local):
                def on_enter_func(e):
                    if selected_widget[0] and selected_widget[0][4] == idx_local:
                        return
                    draw_rounded_bg(canvas_widget, self.colors['bg_light_hover'])
                    card.configure(bg=self.colors['bg_light_hover'])
                    nl.configure(bg=self.colors['bg_light_hover'])
                    dl.configure(bg=self.colors['bg_light_hover'])
                return on_enter_func
            
            def make_on_leave(canvas_widget, card, nl, dl, orig_bg, idx_local):
                def on_leave_func(e):
                    if selected_widget[0] and selected_widget[0][4] == idx_local:
                        return
                    draw_rounded_bg(canvas_widget, orig_bg)
                    card.configure(bg=orig_bg)
                    nl.configure(bg=orig_bg)
                    dl.configure(bg=orig_bg)
                return on_leave_func
            
            def make_on_click(idx_local):
                def on_click(e):
                    select_template_by_index(idx_local)
                return on_click
            
            def make_on_double(t):
                return lambda e: on_double_click(t)
            
            on_enter_h = make_on_enter(card_canvas, card, name_label, desc_label, idx)
            on_leave_h = make_on_leave(card_canvas, card, name_label, desc_label, original_bg, idx)
            on_click_h = make_on_click(idx)
            on_double_h = make_on_double(template)
            
            for widget in (card_canvas, card, name_label, desc_label):
                widget.bind("<Enter>", on_enter_h)
                widget.bind("<Leave>", on_leave_h)
                widget.bind("<Button-1>", on_click_h)
                widget.bind("<Double-Button-1>", on_double_h)
        
        bottom_frame = tk.Frame(dialog, bg=self.colors['bg_medium'])
        bottom_frame.pack(fill=tk.X, padx=padx, pady=scale_size(15, self.scale_factor))
        
        select_btn[0] = RoundedButton(
            bottom_frame,
            text=tr('hosts_install_btn'),
            command=on_select_click,
            width=btn_width, height=btn_height,
            bg=self.colors['accent'],
            fg=self.colors['button_text_hover'],
            hover_fg=self.colors['button_text_hover'],
            font=("Segoe UI Variable", font_size_btn),
            corner_radius=btn_radius
        )
        select_btn[0].normal_color = self.colors['accent']
        select_btn[0].hover_color = self.colors['accent']
        select_btn[0].set_enabled(True)
        select_btn[0].config(cursor="hand2")
        select_btn[0].pack(side=tk.RIGHT, padx=(scale_size(10, self.scale_factor), 0))
        
        cancel_btn = RoundedButton(
            bottom_frame,
            text=tr('mode_cancel'),
            command=dialog.destroy,
            width=btn_width_cancel, height=btn_height,
            bg=self.colors['button_bg'],
            fg=self.colors['button_text'],
            hover_fg=self.colors['button_text_hover'],
            font=("Segoe UI Variable", font_size_btn),
            corner_radius=btn_radius
        )
        cancel_btn.normal_color = self.colors['button_bg']
        cancel_btn.hover_color = self.colors['accent']
        cancel_btn.config(cursor="hand2")
        cancel_btn.pack(side=tk.RIGHT)
        dialog.deiconify()

    def show_theme_selector(self):
        dialog = tk.Toplevel(self.app.root)
        dialog.title(tr('dialog_settings_choosetheme'))
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['bg_medium'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.focus_force()

        w, h = scale_size(400, self.scale_factor), scale_size(250, self.scale_factor)
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - w // 2
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - h // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        dialog.withdraw()
        self.app.set_dialog_header_color(dialog)
        dialog.update_idletasks()

        tk.Label(dialog, text=tr('settings_theme'), font=("Segoe UI Variable", scale_size(16, self.scale_factor), "bold"),
                 fg=self.colors['text_primary'],
                 bg=self.colors['bg_medium']).pack(pady=(scale_size(15, self.scale_factor), scale_size(3, self.scale_factor)))

        list_frame = tk.Frame(dialog, bg=self.colors['bg_medium'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=scale_size(30, self.scale_factor), pady=scale_size(10, self.scale_factor))

        for theme_name in get_theme_names():
            is_active = (theme_name == self.app.current_theme)
            btn = RoundedButton(
                list_frame,
                text=get_theme_display_name(theme_name),
                command=lambda t=theme_name, d=dialog: (d.destroy(), self.app.pages.settings_page_obj._change_theme(t)),
                width=scale_size(340, self.scale_factor),
                height=scale_size(35, self.scale_factor),
                bg=self.colors['accent'] if is_active else self.colors['bg_light'],
                fg=self.colors['button_text_hover'] if is_active else self.colors['text_secondary'],
                hover_fg=self.colors['button_text_hover'],
                font=("Segoe UI Variable", scale_size(11, self.scale_factor)),
                corner_radius=scale_size(8, self.scale_factor),
                hover_color=self.colors['accent'],
                theme_name=self.current_theme
            )
            btn.pack(pady=scale_size(3, self.scale_factor))
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        dialog.deiconify()

    def show_language_selector(self):
        dialog = tk.Toplevel(self.app.root)
        dialog.title(tr('dialog_settings_chooselang'))
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['bg_medium'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.focus_force()

        w, h = scale_size(400, self.scale_factor), scale_size(170, self.scale_factor)
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - w // 2
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - h // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        dialog.withdraw()
        self.app.set_dialog_header_color(dialog)
        dialog.update_idletasks()

        tk.Label(dialog, text=tr('settings_language'), font=("Segoe UI Variable", scale_size(16, self.scale_factor), "bold"),
                 fg=self.colors['text_primary'],
                 bg=self.colors['bg_medium']).pack(pady=(scale_size(15, self.scale_factor), scale_size(3, self.scale_factor)))

        list_frame = tk.Frame(dialog, bg=self.colors['bg_medium'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=scale_size(30, self.scale_factor), pady=scale_size(10, self.scale_factor))

        current_lang = self.app.languages.get_current_language()
        for lang_code, lang_name in self.app.languages.get_available_languages().items():
            is_active = (lang_code == current_lang)
            btn = RoundedButton(
                list_frame,
                text=lang_name,
                command=lambda lc=lang_code, d=dialog: (d.destroy(), self.app.pages.settings_page_obj._change_language(lc)),
                width=scale_size(340, self.scale_factor),
                height=scale_size(35, self.scale_factor),
                bg=self.colors['accent'] if is_active else self.colors['bg_light'],
                fg=self.colors['button_text_hover'] if is_active else self.colors['text_secondary'],
                hover_fg=self.colors['button_text_hover'],
                font=("Segoe UI Variable", scale_size(11, self.scale_factor)),
                corner_radius=scale_size(8, self.scale_factor),
                hover_color=self.colors['accent'],
                theme_name=self.current_theme
            )
            btn.pack(pady=scale_size(3, self.scale_factor))
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        dialog.deiconify()

    def show_tgproxy_settings(self):
        dialog = tk.Toplevel(self.app.root)
        dialog.title(tr('dialog_settings_tgproxy'))
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['bg_medium'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.focus_force()

        w, h = scale_size(450, self.scale_factor), scale_size(200, self.scale_factor)
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - w // 2
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - h // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        dialog.withdraw()
        self.app.set_dialog_header_color(dialog)
        dialog.update_idletasks()

        tk.Label(
            dialog,
            text="Telegram Proxy",
            font=("Segoe UI Variable", scale_size(16, self.scale_factor), "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium']
        ).pack(pady=(scale_size(15, self.scale_factor), scale_size(3, self.scale_factor)))

        secret_label = tk.Label(
            dialog,
            text="",
            font=("Segoe UI Variable", scale_size(9, self.scale_factor)),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_medium'],
            wraplength=scale_size(400, self.scale_factor)
        )
        secret_label.pack(pady=(scale_size(2, self.scale_factor), scale_size(8, self.scale_factor)))

        def refresh_secret_label():
            if not secret_label.winfo_exists():
                return
            secret_value = getattr(self.app, '_tg_secret', None) or ''
            secret_label.config(text=f"{tr('settings_current_tg_secret')} {secret_value}")

        refresh_secret_label()

        def on_regen():
            self.app.regenerate_tg_secret()
            refresh_secret_label()

        regen_btn = RoundedButton(
            dialog,
            text=tr('tg_generate_secret'),
            command=on_regen,
            width=scale_size(300, self.scale_factor),
            height=scale_size(35, self.scale_factor),
            bg=self.colors['accent'],
            fg=self.colors['button_text_hover'],
            hover_fg=self.colors['button_text_hover'],
            font=("Segoe UI Variable", scale_size(10, self.scale_factor)),
            corner_radius=scale_size(8, self.scale_factor),
            hover_color=self.colors['accent'],
            theme_name=self.current_theme
        )
        regen_btn.pack(pady=(scale_size(5, self.scale_factor), scale_size(2, self.scale_factor)))

        instr_btn = RoundedButton(
            dialog,
            text="",
            command=None,
            width=scale_size(300, self.scale_factor),
            height=scale_size(35, self.scale_factor),
            bg=self.colors['bg_light'],
            fg=self.colors['text_primary'],
            hover_fg=self.colors['button_text_hover'],
            font=("Segoe UI Variable", scale_size(10, self.scale_factor)),
            corner_radius=scale_size(8, self.scale_factor),
            hover_color=self.colors['accent'],
            theme_name=self.current_theme
        )
        instr_btn.pack(pady=(scale_size(2, self.scale_factor), scale_size(5, self.scale_factor)))

        def refresh_instruction_button():
            if not instr_btn.winfo_exists():
                return
            text = self.app.pages.settings_page_obj._get_instruction_button_text()
            instr_btn.set_text(text)

        def on_toggle_instruction():
            self.app.pages.settings_page_obj._show_instruction()
            refresh_instruction_button()

        instr_btn._command = on_toggle_instruction
        instr_btn.command = on_toggle_instruction
        refresh_instruction_button()

        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        dialog.deiconify()

    def show_update_source_selector(self):
        dialog = tk.Toplevel(self.app.root)
        dialog.title(tr('settings_update_source_title_dialog'))
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['bg_medium'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.focus_force()

        w, h = scale_size(400, self.scale_factor), scale_size(200, self.scale_factor)
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - w // 2
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - h // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        dialog.withdraw()
        self.app.set_dialog_header_color(dialog)
        dialog.update_idletasks()

        tk.Label(
            dialog,
            text=tr('settings_update_source'),
            font=("Segoe UI Variable", scale_size(16, self.scale_factor), "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium']
        ).pack(pady=(scale_size(15, self.scale_factor), scale_size(3, self.scale_factor)))

        tk.Label(
            dialog,
            text=tr('settings_update_source_desc'),
            font=("Segoe UI Variable", scale_size(9, self.scale_factor)),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_medium'],
            wraplength=scale_size(360, self.scale_factor),
            justify=tk.CENTER
        ).pack(pady=(0, scale_size(12, self.scale_factor)))

        list_frame = tk.Frame(dialog, bg=self.colors['bg_medium'])
        list_frame.pack(fill=tk.BOTH, expand=True,
                        padx=scale_size(30, self.scale_factor),
                        pady=scale_size(5, self.scale_factor))

        sources = [
            ('main',   tr('settings_update_source_main')),
            ('github', tr('settings_update_source_github')),
        ]

        current_source = getattr(self.app, '_update_source', 'main')

        for source_id, source_label in sources:
            is_active = (source_id == current_source)
            btn = RoundedButton(
                list_frame,
                text=source_label,
                command=lambda sid=source_id, d=dialog: self._apply_update_source(sid, d),
                width=scale_size(340, self.scale_factor),
                height=scale_size(35, self.scale_factor),
                bg=self.colors['accent'] if is_active else self.colors['bg_light'],
                fg=self.colors['button_text_hover'] if is_active else self.colors['text_secondary'],
                hover_fg=self.colors['button_text_hover'],
                font=("Segoe UI Variable", scale_size(11, self.scale_factor)),
                corner_radius=scale_size(8, self.scale_factor),
                hover_color=self.colors['accent'],
                theme_name=self.current_theme
            )
            btn.pack(pady=scale_size(4, self.scale_factor))

        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        dialog.deiconify()

    def _apply_update_source(self, source_id: str, dialog):
        current = getattr(self.app, '_update_source', 'main')
        if source_id != current:
            self.app._update_source = source_id
            try:
                self.app.save_settings()
            except Exception as e:
                self._log("_apply_update_source save", e)

            try:
                page = self.app.pages.settings_page_obj
                if hasattr(page, '_refresh_update_source_card'):
                    page._refresh_update_source_card()
            except Exception as e:
                self._log("_apply_update_source refresh", e)

        dialog.destroy()
