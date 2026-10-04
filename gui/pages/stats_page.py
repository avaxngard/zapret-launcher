# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
from utils.scaling import scale_size
from utils.languages import tr, tr_plural

MODE_TRANSLATION_KEYS = {
    "Standard": "mode_standard",
    "Combined": "mode_zapret_tgproxy"
}

class StatsPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.colors["bg_dark"])
        self.app = app
        self.colors = app.colors
        self.sf = app.scale_factor
        self._labels = {}

        self._build()
        self._load_stats()

    def get_frame(self):
        return self

    def _build(self):
        c = self.colors
        sf = self.sf

        padx = scale_size(30, sf)
        pady = scale_size(20, sf)

        header_frame = tk.Frame(self, bg=c["bg_dark"])
        header_frame.pack(fill=tk.X, padx=padx, pady=(scale_size(30, sf), 5))

        tk.Label(
            header_frame,
            text=tr("stats_title"),
            font=("Segoe UI Variable", scale_size(20, sf), "bold"),
            fg=c["text_primary"], bg=c["bg_dark"],
        ).pack(anchor="w")

        tk.Label(
            header_frame,
            text=tr("stats_desc"),
            font=("Segoe UI Variable", scale_size(10, sf)),
            fg=c["text_secondary"], bg=c["bg_dark"],
        ).pack(anchor="w", pady=(5, 0))

        outer = tk.Frame(self, bg=c["bg_dark"])
        outer.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)

        hero = tk.Frame(outer, bg=c["bg_medium"], height=scale_size(140, sf))
        hero.pack(fill=tk.X)
        hero.pack_propagate(False)

        tk.Frame(hero, bg=c["accent"], width=scale_size(4, sf)).place(x=0, y=0, relheight=1.0)

        hero_inner = tk.Frame(hero, bg=c["bg_medium"])
        hero_inner.place(x=scale_size(32, sf), rely=0.5, anchor="w")

        tk.Label(
            hero_inner,
            text=tr("stats_since_upper"),
            font=("Segoe UI Variable", scale_size(10, sf)),
            fg=c["text_secondary"], bg=c["bg_medium"],
        ).pack(anchor="w")

        self._labels["first_connect"] = tk.Label(
            hero_inner,
            text="—",
            font=("Segoe UI Variable", scale_size(26, sf), "bold"),
            fg=c["text_primary"], bg=c["bg_medium"],
        )
        self._labels["first_connect"].pack(anchor="w", pady=(scale_size(4, sf), 0))

        self._labels["hero_sub"] = tk.Label(
            hero_inner,
            text="—",
            font=("Segoe UI Variable", scale_size(10, sf)),
            fg=c["text_secondary"], bg=c["bg_medium"],
        )
        self._labels["hero_sub"].pack(anchor="w", pady=(scale_size(6, sf), 0))

        grid = tk.Frame(outer, bg=c["bg_dark"])
        grid.pack(fill=tk.X, pady=(scale_size(20, sf), 0))

        for i in range(4):
            grid.columnconfigure(i, weight=1, uniform="stats")

        self._labels["total_sessions"] = self._make_card(
            grid, tr("stats_sessions_total"), "—", "—", "accent", col=0
        )
        self._labels["last_session"] = self._make_card(
            grid, tr("stats_longest"), "—", "—", "default", col=1
        )
        self._labels["fav_mode"] = self._make_card(
            grid, tr("stats_fav_mode"), "—", "—", "accent", col=2
        )
        self._labels["current_strategy"] = self._make_card(
            grid, tr("stats_ping"), "—", "—", "duo", col=3
        )

    def _make_card(self, parent, label, value, sub, vtype, col):
        c = self.colors
        sf = self.sf

        card = tk.Frame(
            parent, bg=c["bg_medium"],
            highlightthickness=1, highlightbackground=c["separator"],
        )
        card.configure(padx=scale_size(20, sf), pady=scale_size(18, sf))
        card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else scale_size(8, sf), 0))

        tk.Label(
            card, text=label.upper(),
            font=("Segoe UI Variable", scale_size(9, sf)),
            fg=c["text_secondary"], bg=c["bg_medium"], anchor="w",
        ).pack(fill=tk.X)

        if vtype == "duo":
            row = tk.Frame(card, bg=c["bg_medium"])
            row.pack(fill=tk.X, anchor="w", pady=(scale_size(10, sf), 0))

            v1 = tk.Label(row, text=value,
                          font=("Segoe UI Variable", scale_size(18, sf), "bold"),
                          fg=c["accent"], bg=c["bg_medium"])
            v1.pack(side=tk.LEFT)

            tk.Label(row, text="/",
                     font=("Segoe UI Variable", scale_size(16, sf)),
                     fg=c["text_secondary"], bg=c["bg_medium"],
                     ).pack(side=tk.LEFT, padx=scale_size(6, sf))

            v2 = tk.Label(row, text="—",
                          font=("Segoe UI Variable", scale_size(18, sf), "bold"),
                          fg=c["accent"], bg=c["bg_medium"])
            v2.pack(side=tk.LEFT)

            value_label = (v1, v2)
        else:
            color = c["accent"] if vtype == "accent" else c["accent"]
            value_label = tk.Label(
                card, text=value,
                font=("Segoe UI Variable", scale_size(18, sf), "bold"),
                fg=color, bg=c["bg_medium"], anchor="w",
            )
            value_label.pack(fill=tk.X, pady=(scale_size(10, sf), 0))

        sub_label = tk.Label(
            card, text=sub,
            font=("Segoe UI Variable", scale_size(9, sf)),
            fg=c["text_secondary"], bg=c["bg_medium"], anchor="w",
        )
        sub_label.pack(fill=tk.X, pady=(scale_size(8, sf), 0))
        return {"value": value_label, "sub": sub_label}

    def _load_stats(self):
        user_stats = getattr(self.app, "user_stats", None)
        if user_stats is None:
            return

        if user_stats.cached_stats:
            self._apply_stats(user_stats.cached_stats)
        else:
            self._wait_for_cache(attempts=20)

    def _wait_for_cache(self, attempts):
        user_stats = getattr(self.app, "user_stats", None)
        if user_stats and user_stats.cached_stats:
            self._apply_stats(user_stats.cached_stats)
            return
        if attempts > 0:
            self.after(250, lambda: self._wait_for_cache(attempts - 1))

    def _apply_stats(self, stats):
        if not stats:
            return

        days = stats.get("days_since", 0)
        total = stats.get("total_sessions", 0)
        self._labels["first_connect"].config(text=stats.get("created_at", "—"))

        days_word = tr_plural(
            days,
            "stats_days_word_one",
            "stats_days_word_few",
            "stats_days_word_many",
        ).split(" ", 1)[-1]

        sessions_word = tr_plural(
            total,
            "stats_sessions_word_one",
            "stats_sessions_word_few",
            "stats_sessions_word_many",
        ).split(" ", 1)[-1]

        self._labels["hero_sub"].config(
            text=tr(
                "stats_since_days",
                days=days,
                days_word=days_word,
                total=total,
                sessions_word=sessions_word,
            )
        )

        avg = stats.get("avg_per_day", 0)
        self._labels["total_sessions"]["value"].config(text=str(total))
        self._labels["total_sessions"]["sub"].config(text=tr("stats_avg_per_day", avg=avg))

        secs = stats.get("longest_session_seconds", 0) or 0
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        duration_str = f"{h:02d}:{m:02d}:{s:02d}"

        self._labels["last_session"]["value"].config(text=duration_str)
        self._labels["last_session"]["sub"].config(text=stats.get("longest_session_date", "—"))

        fav_raw = stats.get("fav_mode", "—")
        key = MODE_TRANSLATION_KEYS.get(fav_raw)
        fav_val = tr(key) if key else fav_raw

        pct = stats.get("fav_mode_percent", 0)
        self._labels["fav_mode"]["value"].config(text=fav_val)
        self._labels["fav_mode"]["sub"].config(text=tr("stats_fav_mode_pct", pct=pct))

        min_p = stats.get("min_ping")
        max_p = stats.get("max_ping")
        v1, v2 = self._labels["current_strategy"]["value"]
        v1.config(text=str(min_p) if min_p is not None else "—")
        v2.config(text=str(max_p) if max_p is not None else "—")
        self._labels["current_strategy"]["sub"].config(text=tr("stats_ping_minmax"))