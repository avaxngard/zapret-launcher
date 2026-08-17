from tg_proxy.config import parse_dc_ip_list, proxy_config, coerce_domain_list
from tg_proxy.utils import get_link_host, build_github_opener
from .tg_ws_proxy import run_proxy
from .logger_setup import setup_tg_logging, get_log_file_path

__version__ = "1.10.0"

__all__ = [
    "__version__", 
    "get_link_host", 
    "proxy_config", 
    "parse_dc_ip_list", 
    "build_github_opener", 
    "coerce_domain_list", 
    "run_proxy",
    "setup_tg_logging",
    "get_log_file_path"
]
