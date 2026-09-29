# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import time
import psutil

class StatsMonitor:
    def __init__(self):
        self.session_start = None
        self.total_up_bytes = 0
        self.total_down_bytes = 0
        self.connection_count = 0
        self.disconnection_count = 0
        self.is_monitoring = False
        self._monitor_thread = None
        self._cache_duration = 1.0
        self._cached_stats = (0, 0)
        self._cached_time = 0
        self._stop_event = None
        self.last_up = 0
        self.last_down = 0
        self.current_speed_up = 0
        self.current_speed_down = 0
        self.last_update_time = 0

    def start_session(self):
        self.session_start = time.time()
        self.connection_count += 1
        self.is_monitoring = True
        self.total_up_bytes = 0
        self.total_down_bytes = 0
        self.current_speed_up = 0
        self.current_speed_down = 0
        self.last_up, self.last_down = self._get_network_stats()
        self.last_update_time = time.time()

    def end_session(self):
        self.is_monitoring = False
        self.disconnection_count += 1

    def _get_network_stats(self):
        current_time = time.time()
        if hasattr(self, '_cached_stats') and hasattr(self, '_cached_time'):
            if current_time - self._cached_time < self._cache_duration:
                return self._cached_stats

        try:
            counters = psutil.net_io_counters()
            recv = counters.bytes_recv
            sent = counters.bytes_sent
            self._cached_stats = (recv, sent)
            self._cached_time = current_time
            return recv, sent
        except Exception:
            return 0, 0

    def update_speed(self):
        if not self.is_monitoring:
            return

        try:
            current_up, current_down = self._get_network_stats()
            now = time.time()
            time_diff = now - self.last_update_time

            if current_up > self.last_up:
                self.total_up_bytes += (current_up - self.last_up)
            if current_down > self.last_down:
                self.total_down_bytes += (current_down - self.last_down)

            if time_diff >= 0.5:
                up_diff = max(0, current_up - self.last_up)
                down_diff = max(0, current_down - self.last_down)

                raw_speed_up = up_diff / time_diff if time_diff > 0 else 0
                raw_speed_down = down_diff / time_diff if time_diff > 0 else 0

                self.current_speed_up = self.current_speed_up * 0.7 + raw_speed_up * 0.3
                self.current_speed_down = self.current_speed_down * 0.7 + raw_speed_down * 0.3

                self.last_update_time = now

            self.last_up = current_up
            self.last_down = current_down

            self.current_speed_up = max(0, self.current_speed_up)
            self.current_speed_down = max(0, self.current_speed_down)
        except Exception:
            pass

    def get_session_time(self):
        if self.session_start:
            return time.time() - self.session_start
        return 0

    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def format_bytes(self, bytes_val):
        if bytes_val < 1024:
            return f"{bytes_val} B"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val / 1024:.1f} KB"
        elif bytes_val < 1024 * 1024 * 1024:
            return f"{bytes_val / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"

    def format_speed(self, bytes_per_sec):
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.0f} B/s"
        elif bytes_per_sec < 1024 * 1024:
            return f"{bytes_per_sec / 1024:.1f} KB/s"
        else:
            return f"{bytes_per_sec / (1024 * 1024):.1f} MB/s"

    def get_stats_dict(self):
        self.update_speed()
        return {
            'session_time': self.get_session_time(),
            'session_time_str': self.format_time(self.get_session_time()),
            'up_bytes': self.total_up_bytes,
            'up_str': self.format_bytes(self.total_up_bytes),
            'down_bytes': self.total_down_bytes,
            'down_str': self.format_bytes(self.total_down_bytes),
            'total_bytes': self.total_up_bytes + self.total_down_bytes,
            'total_str': self.format_bytes(self.total_up_bytes + self.total_down_bytes),
            'connections': self.connection_count,
            'disconnections': self.disconnection_count,
            'speed_up': self.current_speed_up,
            'speed_up_str': self.format_speed(self.current_speed_up),
            'speed_down': self.current_speed_down,
            'speed_down_str': self.format_speed(self.current_speed_down),
        }
