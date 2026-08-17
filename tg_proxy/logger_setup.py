import logging
from pathlib import Path
from typing import Optional

_log_file_path: Optional[str] = None

def setup_tg_logging(log_file_path: Optional[str] = None) -> bool:
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
        
        file_handler = logging.FileHandler(_log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s  %(levelname)-5s  %(message)s', datefmt='%H:%M:%S'))
        
        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.DEBUG)
        return True
        
    except Exception:
        return False

def get_log_file_path() -> Optional[str]:
    return _log_file_path