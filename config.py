# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

from pathlib import Path
import os

BASE_DIR = Path(__file__).parent
APPDATA_DIR = Path(os.getenv('APPDATA')) / 'Zapret Launcher'
CONFIG_FILE = APPDATA_DIR / 'config.json'
LISTS_DIR = APPDATA_DIR / "zapret_core" / "lists"
ZAPRET_CORE_DIR = APPDATA_DIR / "zapret_core"
ICON_PATH = BASE_DIR / "resources" / "icon.ico"
PNG_ICON_PATH = BASE_DIR / "resources" / "icon.png"
HOSTS_PATH = Path(r"C:\Windows\System32\drivers\etc\hosts")

CURRENT_VERSION = "3.2.3.2"
CURRENT_BUILD = "3413"

CHECK_UPDATES_INTERVAL = 60 * 60 * 1000

TG_HOST = "127.0.0.1"
TG_PORT = 1443
TG_FAKE_TLS = True
TG_FAKE_TLS_DOMAIN = "www.google.com"

API_URL_STATS = "https://zapret-launcher.ru/api/stats.php"
API_URL_NEWS = "https://zapret-launcher.ru/api/news.php"

# Site
ZAPRET_VERSION_URL = "https://zapret-launcher.ru/updater/docs/zapret_version.txt"
ZAPRET_CORE_URL = "https://zapret-launcher.ru/updater/zapret_core.zip"
BUILDNUMBER_URL = "https://zapret-launcher.ru/updater/docs/build_number.txt"
VERSION_URL = "https://zapret-launcher.ru/updater/docs/version_launcher.txt"
EXE_URL = "https://zapret-launcher.ru/updater/updater.exe"
ZIP_URL = "https://zapret-launcher.ru/updater/_internal.zip"
INSTALLER_URL = "https://zapret-launcher.ru/updater/zapret-launcher-installer-win10.exe"

# GitHub (Temporarily unavailable)
#RAW_ZAPRET_VERSION_URL = "https://raw.githubusercontent.com/tweenkedrage/zapret-launcher/main/docs/zapret_version.txt"
#RAW_ZAPRET_CORE_URL = "https://raw.githubusercontent.com/tweenkedrage/zapret-launcher/main/updater/zapret_core.zip"
#RAW_BUILDNUMBER_URL = "https://raw.githubusercontent.com/tweenkedrage/zapret-launcher/main/docs/build_number.txt"
#RAW_VERSION_URL = "https://raw.githubusercontent.com/tweenkedrage/zapret-launcher/main/docs/version.txt"
#RAW_EXE_URL = "https://raw.githubusercontent.com/tweenkedrage/zapret-launcher/main/updater/Zapret%20Launcher.exe"
#RAW_ZIP_URL = "https://raw.githubusercontent.com/tweenkedrage/zapret-launcher/main/updater/_internal.zip"
#RAW_INSTALLER_URL = "https://raw.githubusercontent.com/tweenkedrage/zapret-launcher/main/updater/zapret-launcher-installer-win10.exe"

# GitLab
RAW_ZAPRET_VERSION_URL = "https://gitlab.com/tweenkrage/zapret-launcher/-/raw/main/docs/zapret_version.txt"
RAW_ZAPRET_CORE_URL = "https://gitlab.com/tweenkrage/zapret-launcher/-/raw/main/updater/zapret_core.zip"
RAW_BUILDNUMBER_URL = "https://gitlab.com/tweenkrage/zapret-launcher/-/raw/main/docs/build_number.txt"
RAW_VERSION_URL = "https://gitlab.com/tweenkrage/zapret-launcher/-/raw/main/docs/version.txt"
RAW_EXE_URL = "https://gitlab.com/tweenkrage/zapret-launcher/-/raw/main/updater/updater.exe"
RAW_ZIP_URL = "https://gitlab.com/tweenkrage/zapret-launcher/-/raw/main/updater/_internal.zip"
