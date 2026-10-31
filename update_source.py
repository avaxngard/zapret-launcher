# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

from dataclasses import dataclass
from config import (
    # Site
    BUILDNUMBER_URL,
    ZAPRET_VERSION_URL,
    VERSION_URL,
    UPDATECONTROL_URL,
    EXE_URL,
    ZIP_URL,
    ZAPRET_CORE_URL,
    INSTALLER_URL,
    # Github
    GITHUB_BUILDNUMBER_URL,
    GITHUB_ZAPRET_VERSION_URL,
    GITHUB_VERSION_URL,
    GITHUB_UPDATECONTROL_URL,
    GITHUB_EXE_URL,
    GITHUB_ZIP_URL,
    GITHUB_ZAPRET_CORE_URL,
    GITHUB_INSTALLER_URL
)

SOURCE_MAIN = "main"
SOURCE_GITHUB = "github"

_ALIASES = {
    "build": "build_number",
    "buildnumber": "build_number",
    "launcher_version": "launcher_version",
    "version": "launcher_version",
    "zapret_version": "zapret_version",
    "zapret_core": "zapret_core",
    "zapret": "zapret_core",
    "exe": "exe",
    "updater": "exe",
    "zip": "zip",
    "internal": "zip",
    "installer": "installer"
}

@dataclass(frozen=True)
class UpdateSource:
    name: str
    build_number_url: str
    zapret_version_url: str
    launcher_version_url: str
    exe_url: str
    zip_url: str
    zapret_core_url: str
    installer_url: str
    update_control_url: str

    def get(self, key: str) -> str:
        normalized = _ALIASES.get(key.lower(), key.lower())
        mapping = {
            "build_number": self.build_number_url,
            "zapret_version": self.zapret_version_url,
            "launcher_version": self.launcher_version_url,
            "exe": self.exe_url,
            "zip": self.zip_url,
            "zapret_core": self.zapret_core_url,
            "installer": self.installer_url,
            "update_control": self.update_control_url
        }
        if normalized not in mapping:
            raise KeyError(f"Unknown update source key: {key}")
        return mapping[normalized]

_MAIN = UpdateSource(
    name=SOURCE_MAIN,
    build_number_url=BUILDNUMBER_URL,
    zapret_version_url=ZAPRET_VERSION_URL,
    launcher_version_url=VERSION_URL,
    exe_url=EXE_URL,
    zip_url=ZIP_URL,
    zapret_core_url=ZAPRET_CORE_URL,
    installer_url=INSTALLER_URL,
    update_control_url=UPDATECONTROL_URL
)

_GITHUB = UpdateSource(
    name=SOURCE_GITHUB,
    build_number_url=GITHUB_BUILDNUMBER_URL,
    zapret_version_url=GITHUB_ZAPRET_VERSION_URL,
    launcher_version_url=GITHUB_VERSION_URL,
    exe_url=GITHUB_EXE_URL,
    zip_url=GITHUB_ZIP_URL,
    zapret_core_url=GITHUB_ZAPRET_CORE_URL,
    installer_url=GITHUB_INSTALLER_URL,
    update_control_url=GITHUB_UPDATECONTROL_URL
)

_SOURCES = {
    SOURCE_MAIN: _MAIN,
    SOURCE_GITHUB: _GITHUB
}

def normalize_source_name(name: str | None) -> str:
    if not name:
        return SOURCE_MAIN
    lowered = str(name).strip().lower()
    if lowered in (SOURCE_GITHUB, "git", "gh"):
        return SOURCE_GITHUB
    return SOURCE_MAIN

def get_source(name: str | None) -> UpdateSource:
    return _SOURCES[normalize_source_name(name)]

def get_url(name: str | None, key: str) -> str:
    return get_source(name).get(key)

def get_all_sources() -> list[UpdateSource]:
    return [_MAIN, _GITHUB]
