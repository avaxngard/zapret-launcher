# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

_log_file_path: Optional[str] = None

_MIN_BYTES = 32 * 1024
_MIN_BACKUPS = 1
_DEFAULT_MAX_MB = 5
_DEFAULT_BACKUPS = 1

def _build_rotating_handler(path: str,
                            log_max_mb: float = _DEFAULT_MAX_MB,
                            backups: int = _DEFAULT_BACKUPS
                            ) -> logging.handlers.RotatingFileHandler:
    max_bytes = max(_MIN_BYTES, int(log_max_mb * 1024 * 1024))
    backup_count = max(_MIN_BACKUPS, int(backups))
    return logging.handlers.RotatingFileHandler(
        path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )

def setup_tg_logging(log_file_path: Optional[str] = None,
                     log_max_mb: float = _DEFAULT_MAX_MB,
                     backups: int = _DEFAULT_BACKUPS) -> bool:
    global _log_file_path

    if log_file_path:
        _log_file_path = log_file_path

    if not _log_file_path:
        return False

    try:
        log_path = Path(_log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        root_logger = logging.getLogger()

        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                root_logger.removeHandler(handler)

        file_handler = _build_rotating_handler(
            _log_file_path, log_max_mb=log_max_mb, backups=backups)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s  %(levelname)-5s  %(message)s',
                datefmt='%H:%M:%S'))

        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.DEBUG)
        return True

    except Exception:
        return False

def get_log_file_path() -> Optional[str]:
    return _log_file_path
