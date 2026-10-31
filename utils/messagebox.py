# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import ctypes
import tkinter as tk
from typing import Optional
from gui.widgets import RoundedButton

try:
    import pywinstyles
    _HAS_PYWINSTYLES = True
except ImportError:
    _HAS_PYWINSTYLES = False

from utils.languages import tr
from utils.scaling import scale_size, scale_font
from gui.theme import get_theme

OK = "ok"
CANCEL = "cancel"
YES = "yes"
NO = "no"
RETRY = "retry"
IGNORE = "ignore"
ABORT = "abort"
ERROR = "error"
INFO = "info"
QUESTION = "question"
WARNING = "warning"
OKCANCEL = "okcancel"
YESNO = "yesno"
YESNOCANCEL = "yesnocancel"
RETRYCANCEL = "retrycancel"
ABORTRETRYIGNORE = "abretryign"
WARNING_ICON = "warning"

_SW_HIDE = 0

def _win32_hide(widget: tk.Misc) -> None:
    try:
        widget.update_idletasks()
        hwnd = int(widget.wm_frame(), 16)
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, _SW_HIDE)
    except Exception:
        pass

class _CustomMessageBox:
    _active_app = None

    @classmethod
    def register_app(cls, app):
        cls._active_app = app

    @classmethod
    def unregister_app(cls):
        cls._active_app = None

    @classmethod
    def _get_colors(cls) -> dict:
        app = cls._active_app
        if app is not None:
            try:
                theme_name = getattr(app, "current_theme", "Dark")
                return get_theme(theme_name)
            except Exception:
                pass
        return get_theme("Dark")

    @classmethod
    def _get_scale(cls) -> float:
        app = cls._active_app
        if app is not None:
            try:
                return float(app.scale_factor)
            except Exception:
                pass
        return 1.0

    @classmethod
    def _get_current_theme_name(cls) -> str:
        app = cls._active_app
        if app is not None:
            return getattr(app, "current_theme", "Dark")
        return "Dark"

    @classmethod
    def _get_parent(cls) -> Optional[tk.Misc]:
        app = cls._active_app
        if app is not None and hasattr(app, "root"):
            try:
                if app.root.winfo_exists():
                    return app.root
            except Exception:
                pass
        try:
            root = tk._default_root  # type: ignore[attr-defined]
            if root is not None and root.winfo_exists():
                return root
        except Exception:
            pass
        return None

    @classmethod
    def _log(cls, ctx: str, e: Exception):
        app = cls._active_app
        if app is not None and hasattr(app, "log_event"):
            try:
                app.log_event("info", f"custom_messagebox[{ctx}]: {e}")
            except Exception:
                pass

    @classmethod
    def _set_header_color(cls, dialog: tk.Toplevel, colors: dict):
        if not _HAS_PYWINSTYLES:
            return
        try:
            dialog.update_idletasks()
            pywinstyles.change_header_color(dialog, colors["bg_medium"])
        except Exception as e:
            cls._log("_set_header_color", e)

    @classmethod
    def _make_button(cls, parent, text: str, command, primary: bool, colors: dict, scale: float, key: str = ""):
        try:
            theme_name = cls._get_current_theme_name()
            normal_bg = colors["accent"] if primary else colors["button_bg"]
            normal_fg = colors["button_text_hover"] if primary else colors["button_text"]

            if key in ("cancel", "no", "ignore", "abort"):
                hover_bg = colors["accent"]
            else:
                hover_bg = normal_bg

            hover_fg = colors["button_text_hover"]

            btn = RoundedButton(
                parent,
                text=text,
                command=command,
                width=scale_size(110, scale),
                height=scale_size(34, scale),
                bg=normal_bg,
                fg=normal_fg,
                hover_fg=hover_fg,
                font=("Inter", scale_font(10, scale, softness=0.2)),
                corner_radius=scale_size(8, scale),
                hover_color=hover_bg,
                theme_name=theme_name
            )
            btn.normal_color = normal_bg
            btn.hover_color = hover_bg
            btn.normal_fg = normal_fg
            btn.hover_fg = hover_fg
            btn.itemconfig(btn.rect, fill=normal_bg)
            btn.itemconfig(btn.text_id, fill=normal_fg)
            btn.config(cursor="hand2")
            return btn

        except Exception as e:
            cls._log("_make_button fallback", e)
            return tk.Button(
                parent,
                text=text,
                command=command,
                bg=colors["accent"] if primary else colors["button_bg"],
                fg=colors["button_text_hover"] if primary else colors["button_text"],
                activebackground=colors["accent_hover"],
                activeforeground=colors["button_text_hover"],
                relief=tk.FLAT,
                bd=0,
                padx=scale_size(14, scale),
                pady=scale_size(6, scale),
                font=("Inter", scale_font(10, scale, softness=0.2)),
                cursor="hand2"
            )

    @classmethod
    def _show(
        cls,
        title: str,
        message: str,
        buttons: list,
        default: Optional[str] = None,
        parent: Optional[tk.Misc] = None,
    ) -> Optional[str]:
        colors = cls._get_colors()
        scale = cls._get_scale()

        dlg_w = scale_size(440, scale)
        dlg_h = scale_size(160, scale)
        padding = scale_size(20, scale)
        fs_msg = scale_font(10, scale, softness=0.3)

        top = parent or cls._get_parent()

        result_holder = {"value": None}

        created_root = False
        if top is None:
            top = tk.Tk()
            top.withdraw()
            created_root = True

        try:
            top.update_idletasks()
            if top.winfo_viewable():
                x = top.winfo_rootx() + (top.winfo_width() // 2) - (dlg_w // 2)
                y = top.winfo_rooty() + (top.winfo_height() // 2) - (dlg_h // 2)
            else:
                x = (top.winfo_screenwidth() - dlg_w) // 2
                y = (top.winfo_screenheight() - dlg_h) // 2
        except Exception:
            x = (top.winfo_screenwidth() - dlg_w) // 2
            y = (top.winfo_screenheight() - dlg_h) // 2

        dialog = tk.Toplevel(top)
        dialog.withdraw()
        try:
            dialog.geometry(f"+{x}+{y}")
        except Exception:
            pass
        dialog.update_idletasks()

        _win32_hide(dialog)

        try:
            dialog.attributes('-alpha', 0.0)
        except Exception:
            pass
        dialog.update_idletasks()

        dialog.title(title)
        dialog.resizable(False, False)
        dialog.configure(bg=colors["bg_medium"])
        try:
            if top is not None and top.winfo_exists() and top.winfo_viewable():
                dialog.transient(top)
        except Exception:
            pass

        def finish(value: Optional[str]):
            result_holder["value"] = value
            try:
                dialog.grab_release()
            except Exception:
                pass
            try:
                dialog.destroy()
            except Exception:
                pass
            if created_root:
                try:
                    top.destroy()
                except Exception:
                    pass

        def on_close():
            for key, _label, _primary in buttons:
                if key in ("cancel", "no", "abort", "ignore"):
                    finish(key)
                    return
            finish(None)

        dialog.protocol("WM_DELETE_WINDOW", on_close)
        dialog.bind("<Escape>", lambda e: on_close())

        msg_wrap = max(scale_size(280, scale), dlg_w - padding * 2)

        msg_frame = tk.Frame(dialog, bg=colors["bg_medium"])
        msg_frame.pack(fill=tk.BOTH, expand=True, padx=padding, pady=(padding, scale_size(12, scale)))

        msg_label = tk.Label(
            msg_frame,
            text=message,
            font=("Inter", fs_msg),
            fg=colors["text_primary"],
            bg=colors["bg_medium"],
            wraplength=msg_wrap,
            justify=tk.LEFT,
            anchor="nw"
        )
        msg_label.pack(fill=tk.BOTH, expand=True, anchor="nw")

        sep = tk.Frame(dialog, bg=colors["separator"], height=1)
        sep.pack(fill=tk.X, padx=padding)

        btn_frame = tk.Frame(dialog, bg=colors["bg_medium"])
        btn_frame.pack(fill=tk.X, padx=padding, pady=(scale_size(12, scale), padding))

        primary_btn = None
        middle_btns = []
        cancel_btn = None
        for k, l, p in buttons:
            if p:
                primary_btn = (k, l, p)
            elif k == "cancel":
                cancel_btn = (k, l, p)
            else:
                middle_btns.append((k, l, p))

        ordered = []
        if primary_btn:
            ordered.append(primary_btn)
        ordered.extend(middle_btns)
        if cancel_btn:
            ordered.append(cancel_btn)

        button_widgets = []
        for key, label, primary in ordered:
            btn = cls._make_button(
                btn_frame,
                text=label,
                command=lambda k=key: finish(k),
                primary=primary,
                colors=colors,
                scale=scale,
                key=key
            )
            btn.pack(side=tk.RIGHT, padx=(scale_size(8, scale), 0))
            button_widgets.append((key, btn))

        if default:
            for key, btn in button_widgets:
                if key == default:
                    try:
                        btn.focus_set()
                    except Exception:
                        pass
                    break
            dialog.bind("<Return>", lambda e: finish(default))

        dialog.update_idletasks()
        try:
            needed = dialog.winfo_reqheight()
            final_h = min(needed, scale_size(600, scale)) if needed > dlg_h else dlg_h
        except Exception:
            final_h = dlg_h

        try:
            if top.winfo_viewable():
                y = top.winfo_rooty() + (top.winfo_height() // 2) - (final_h // 2)
            else:
                y = (top.winfo_screenheight() - final_h) // 2
        except Exception:
            y = (top.winfo_screenheight() - final_h) // 2

        dialog.geometry(f"{dlg_w}x{final_h}+{x}+{y}")
        dialog.update_idletasks()

        try:
            hwnd = int(dialog.wm_frame(), 16)
            if hwnd:
                ctypes.windll.user32.SetWindowPos(
                    hwnd, 0, x, y, 0, 0,
                    0x0001 | 0x0004 | 0x0010,  # SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE
                )
        except Exception:
            pass
        dialog.update_idletasks()

        cls._set_header_color(dialog, colors)
        dialog.update_idletasks()

        dialog.deiconify()
        dialog.update_idletasks()
        
        try:
            dialog.grab_set()
        except Exception:
            pass
        
        try:
            dialog.lift()
            dialog.focus_force()
        except Exception:
            pass

        def fade_in(alpha=0.0):
            if not dialog.winfo_exists():
                return
            if alpha < 1.0:
                alpha += 0.15
                try:
                    dialog.attributes('-alpha', min(alpha, 1.0))
                    dialog.after(12, lambda: fade_in(alpha))
                except Exception:
                    pass
            else:
                try:
                    dialog.attributes('-alpha', 1.0)
                except Exception:
                    pass
                try:
                    dialog.lift()
                    dialog.focus_force()
                except Exception:
                    pass

        dialog.after(10, fade_in)

        try:
            top.wait_window(dialog)
        except Exception:
            pass

        return result_holder["value"]

    @classmethod
    def showinfo(cls, title: str, message: str, **kwargs) -> str:
        cls._show(
            title, message,
            [("ok", tr('msgbox_ok'), True)], default="ok",
            parent=kwargs.get("parent")
        )
        return OK

    @classmethod
    def showwarning(cls, title: str, message: str, **kwargs) -> str:
        msg_type = kwargs.get("type")
        if msg_type in (OKCANCEL, "okcancel"):
            res = cls._show(
                title, message,
                [("cancel", tr('msgbox_cancel'), False),
                 ("ok", tr('msgbox_ok'), True)],
                default="ok", parent=kwargs.get("parent")
            )
            return OK if res == "ok" else CANCEL

        cls._show(
            title, message,
            [("ok", tr('msgbox_ok'), True)], default="ok",
            parent=kwargs.get("parent")
        )
        return OK

    @classmethod
    def showerror(cls, title: str, message: str, **kwargs) -> str:
        cls._show(
            title, message,
            [("ok", tr('msgbox_ok'), True)], default="ok",
            parent=kwargs.get("parent")
        )
        return OK

    @classmethod
    def confirm(cls, title: str, message: str, **kwargs) -> bool:
        res = cls._show(
            title, message,
            [("cancel", tr('msgbox_cancel'), False),
            ("ok", tr('msgbox_ok'), True)],
            default="ok", parent=kwargs.get("parent")
        )
        return res == "ok"

    @classmethod
    def askyesno(cls, title: str, message: str, **kwargs) -> bool:
        res = cls._show(
            title, message,
            [("no", tr('msgbox_no'), False),
             ("yes", tr('msgbox_yes'), True)],
            default="yes", parent=kwargs.get("parent")
        )
        return res == "yes"

    @classmethod
    def askokcancel(cls, title: str, message: str, **kwargs) -> bool:
        res = cls._show(
            title, message,
            [("cancel", tr('msgbox_cancel'), False),
             ("ok", tr('msgbox_ok'), True)],
            default="ok", parent=kwargs.get("parent")
        )
        return res == "ok"

    @classmethod
    def askretrycancel(cls, title: str, message: str, **kwargs) -> bool:
        res = cls._show(
            title, message,
            [("cancel", tr('msgbox_cancel'), False),
             ("retry", tr('msgbox_retry'), True)],
            default="retry", parent=kwargs.get("parent")
        )
        return res == "retry"

    @classmethod
    def askyesnocancel(cls, title: str, message: str, **kwargs) -> Optional[bool]:
        res = cls._show(
            title, message,
            [("cancel", tr('msgbox_cancel'), False),
             ("no", tr('msgbox_no'), False),
             ("yes", tr('msgbox_yes'), True)],
            default="yes", parent=kwargs.get("parent")
        )
        if res == "yes":
            return True
        if res == "no":
            return False
        return None

    @classmethod
    def askquestion(cls, title: str, message: str, **kwargs) -> str:
        res = cls._show(
            title, message,
            [("no", tr('msgbox_no'), False),
             ("yes", tr('msgbox_yes'), True)],
            default="yes", parent=kwargs.get("parent")
        )
        return YES if res == "yes" else NO

    @classmethod
    def askabortretryignore(cls, title: str, message: str, **kwargs) -> str:
        res = cls._show(
            title, message,
            [("ignore", tr('msgbox_ignore'), False),
             ("retry", tr('msgbox_retry'), False),
             ("abort", tr('msgbox_abort'), True)],
            default="abort", parent=kwargs.get("parent")
        )
        if res in ("abort", "retry", "ignore"):
            return res
        return ABORT

messagebox = _CustomMessageBox()

def showinfo(title, message, **kwargs):
    return _CustomMessageBox.showinfo(title, message, **kwargs)

def showwarning(title, message, **kwargs):
    return _CustomMessageBox.showwarning(title, message, **kwargs)

def showerror(title, message, **kwargs):
    return _CustomMessageBox.showerror(title, message, **kwargs)

def askyesno(title, message, **kwargs):
    return _CustomMessageBox.askyesno(title, message, **kwargs)

def askokcancel(title, message, **kwargs):
    return _CustomMessageBox.askokcancel(title, message, **kwargs)

def askretrycancel(title, message, **kwargs):
    return _CustomMessageBox.askretrycancel(title, message, **kwargs)

def askyesnocancel(title, message, **kwargs):
    return _CustomMessageBox.askyesnocancel(title, message, **kwargs)

def askquestion(title, message, **kwargs):
    return _CustomMessageBox.askquestion(title, message, **kwargs)

def askabortretryignore(title, message, **kwargs):
    return _CustomMessageBox.askabortretryignore(title, message, **kwargs)
