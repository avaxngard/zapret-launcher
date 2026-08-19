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
CURRENT_BUILD = "3416"

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

# GitHub
GITHUB_ZAPRET_VERSION_URL = "https://raw.githubusercontent.com/avaxngard/zapret-launcher/main/docs/zapret_version.txt"
GITHUB_ZAPRET_CORE_URL = "https://raw.githubusercontent.com/avaxngard/zapret-launcher/main/updater/zapret_core.zip"
GITHUB_BUILDNUMBER_URL = "https://raw.githubusercontent.com/avaxngard/zapret-launcher/main/docs/build_number.txt"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/avaxngard/zapret-launcher/main/docs/version.txt"
GITHUB_EXE_URL = "https://raw.githubusercontent.com/avaxngard/zapret-launcher/main/updater/updater.exe"
GITHUB_ZIP_URL = "https://raw.githubusercontent.com/avaxngard/zapret-launcher/main/updater/_internal.zip"

# GitLab
GITLAB_ZAPRET_VERSION_URL = "https://gitlab.com/tweenkrage/zapret-launcher/-/raw/main/docs/zapret_version.txt"
GITLAB_ZAPRET_CORE_URL = "https://gitlab.com/tweenkrage/zapret-launcher/-/raw/main/updater/zapret_core.zip"
GITLAB_BUILDNUMBER_URL = "https://gitlab.com/tweenkrage/zapret-launcher/-/raw/main/docs/build_number.txt"
GITLAB_VERSION_URL = "https://gitlab.com/tweenkrage/zapret-launcher/-/raw/main/docs/version.txt"
GITLAB_EXE_URL = "https://gitlab.com/tweenkrage/zapret-launcher/-/raw/main/updater/updater.exe"
GITLAB_ZIP_URL = "https://gitlab.com/tweenkrage/zapret-launcher/-/raw/main/updater/_internal.zip"
