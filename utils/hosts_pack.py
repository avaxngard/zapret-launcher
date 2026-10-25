# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

from __future__ import annotations
import ipaddress
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import requests
from config import HOSTS_PATH, BACKUP_DIR

MAX_PACK_BYTES = 256 * 1024
MAX_LINES = 5000
MAX_ENTRIES = 20000

FORBIDDEN_IPS = {"0.0.0.0", "127.0.0.1", "::", "::1"}

PACK_ALLOWED_DOMAINS = {
    "discord": [
        "discord.com",
        "updates.discord.com",
    ],
    "github": [
        "github.com",
        "githubusercontent.com",
    ],
    "rutracker": [
        "rutracker.org",
    ],
    "spotify": [
        "spotify.com",
        "spotifycdn.com",
        "scdn.co",
    ],
    "telegram": [
        "telegram.org",
        "telegram.me",
        "telegram.dog",
        "telegram.space",
        "t.me",
        "telesco.pe",
        "tg.dev",
        "tg.dev",
    ]
}

@dataclass
class InstallResult:
    ok: bool
    added: int = 0
    updated: int = 0
    skipped: int = 0
    backup_path: Path | None = None
    error: str | None = None

_DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))*$",
    re.IGNORECASE,
)

def _normalize_ip(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        raise ValueError("empty IP")
    if raw in FORBIDDEN_IPS:
        raise ValueError(f"Forbidden IP: {raw}")

    try:
        ip = ipaddress.ip_address(raw)
    except ValueError:
        raise ValueError(f"Invalid IP: {raw!r}")

    if ip.is_unspecified or ip.is_loopback:
        raise ValueError(f"Forbidden IP: {raw}")

    if ip.is_private or ip.is_link_local or ip.is_multicast or ip.is_reserved:
        raise ValueError(f"IP not routable/allowed: {raw}")

    return str(ip)

def _normalize_domain(raw: str, allowed_suffixes: list[str]) -> str:
    d = raw.strip().lower().rstrip(".")
    if not d:
        raise ValueError("empty domain")
    if len(d) > 253:
        raise ValueError(f"Domain too long: {raw!r}")
    if d.startswith(".") or d.endswith("."):
        raise ValueError(f"Domain cannot start/end with dot: {raw!r}")
    if "*" in d:
        raise ValueError(f"Wildcards not allowed: {raw!r}")

    try:
        ipaddress.ip_address(d)
        raise ValueError(f"Domain looks like IP: {raw!r}")
    except ValueError:
        pass

    if not _DOMAIN_RE.match(d):
        raise ValueError(f"Invalid domain syntax: {raw!r}")

    ok = any(d == s or d.endswith("." + s) for s in allowed_suffixes)
    if not ok:
        raise ValueError(f"Domain not allowed for this pack: {raw!r}")

    return d

def _safe_get(url: str, expected_host: str, timeout: int = 30) -> bytes:
    if urlparse(url).scheme != "https":
        raise ValueError(f"Only https allowed: {url}")
    if urlparse(url).hostname != expected_host:
        raise ValueError(f"Host not allowed: {urlparse(url).hostname}")

    session = requests.Session()
    session.trust_env = False  # ignore HTTP(S)_PROXY from the environment

    resp = session.get(
        url,
        timeout=timeout,
        allow_redirects=False,
        headers={"User-Agent": "ZapretLauncher/pack-loader"},
    )

    redirects = 0
    while resp.is_redirect and redirects < 3:
        new_url = resp.headers.get("Location", "")
        if urlparse(new_url).hostname != expected_host:
            raise ValueError(f"Redirect to another host blocked: {new_url}")
        resp = session.get(
            new_url,
            timeout=timeout,
            allow_redirects=False,
            headers={"User-Agent": "ZapretLauncher/pack-loader"},
        )
        redirects += 1

    resp.raise_for_status()

    ctype = resp.headers.get("Content-Type", "")
    if ctype and ("text" not in ctype and "octet-stream" not in ctype):
        raise ValueError(f"Unexpected Content-Type: {ctype}")

    return resp.content

def _decode_pack(content_bytes: bytes) -> str:
    if len(content_bytes) > MAX_PACK_BYTES:
        raise ValueError("Pack too large")
    if b"\x00" in content_bytes:
        raise ValueError("Pack contains NUL bytes")

    if content_bytes.startswith(b"\xef\xbb\xbf"):
        content_bytes = content_bytes[3:]

    try:
        text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = content_bytes.decode("cp1251")

    return text.replace("\r\n", "\n").replace("\r", "\n")

def _read_hosts() -> tuple[str, str]:
    raw = HOSTS_PATH.read_bytes()

    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        enc = "utf-16"
    elif raw.startswith(b"\xef\xbb\xbf"):
        enc = "utf-8-sig"
    else:
        try:
            raw.decode("utf-8")
            enc = "utf-8"
        except UnicodeDecodeError:
            enc = "cp1251"

    return raw.decode(enc), enc

def _backup_hosts() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"hosts_{ts}.bak"
    shutil.copy2(HOSTS_PATH, backup)

    backups = sorted(BACKUP_DIR.glob("hosts_*.bak"))
    for old in backups[:-10]:
        try:
            old.unlink(missing_ok=True)
        except Exception:
            pass

    return backup

def _atomic_write(path: Path, content: str) -> None:
    tmp = path.with_name(path.name + ".zapret-tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def _merge_hosts(
    current_text: str,
    new_entries: list[tuple[str, str]],
    pack_id: str,
) -> tuple[str, int, int, int]:
    lines = current_text.splitlines()
    existing_by_domain: dict[str, tuple[int, str]] = {}

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 2:
            continue
        ip = parts[0]
        for dom in parts[1:]:
            existing_by_domain[dom.lower()] = (i, ip)

    added = 0
    updated = 0
    skipped = 0
    to_append: list[str] = []

    for ip, domain in new_entries:
        key = domain.lower()
        if key in existing_by_domain:
            idx, old_ip = existing_by_domain[key]
            if old_ip == ip:
                skipped += 1
            else:
                parts = lines[idx].split()
                parts[0] = ip
                lines[idx] = " ".join(parts)
                updated += 1
        else:
            to_append.append(f"{ip} {domain}")
            added += 1

    if to_append:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(f"# Added by Zapret Launcher - {pack_id}")
        lines.extend(to_append)

    return "\n".join(lines) + "\n", added, updated, skipped

def install_pack(
    url: str,
    pack_id: str,
    pack_name: str,
    confirm_callback=None,
) -> InstallResult:
    allowed_domains = PACK_ALLOWED_DOMAINS.get(pack_id)
    if not allowed_domains:
        return InstallResult(ok=False, error=f"Unknown pack id: {pack_id}")

    try:
        expected_host = urlparse(url).hostname
        if not expected_host:
            return InstallResult(ok=False, error=f"Bad URL: {url}")

        raw = _safe_get(url, expected_host, timeout=30)
        text = _decode_pack(raw)

        entries: list[tuple[str, str]] = []
        errors: list[str] = []
        line_count = 0

        for raw_line in text.split("\n"):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            line_count += 1
            if line_count > MAX_LINES:
                errors.append("too many lines")
                break

            parts = line.split()
            if len(parts) < 2:
                errors.append(f"bad line: {raw_line!r}")
                continue

            try:
                ip = _normalize_ip(parts[0])
            except ValueError as e:
                errors.append(str(e))
                continue

            for dom in parts[1:]:
                try:
                    dom_norm = _normalize_domain(dom, allowed_domains)
                    entries.append((ip, dom_norm))
                except ValueError as e:
                    errors.append(str(e))

        if errors:
            preview = "\n".join(errors[:20])
            more = "" if len(errors) <= 20 else f"\n... and {len(errors) - 20} more"
            return InstallResult(ok=False, error=f"Pack rejected: {len(errors)} invalid entries\n\n{preview}{more}")

        if not entries:
            return InstallResult(ok=False, error="Pack is empty after validation")

        if len(entries) > MAX_ENTRIES:
            return InstallResult(ok=False, error="Pack too large")

        current_text, _ = _read_hosts()
        new_text, added, updated, skipped = _merge_hosts(current_text, entries, pack_id)

        if added == 0 and updated == 0:
            return InstallResult(ok=True, added=0, updated=0, skipped=skipped)

        if confirm_callback is not None:
            if not confirm_callback(added, updated, skipped, pack_name):
                return InstallResult(ok=True, added=0, updated=0, skipped=skipped, error="cancelled")

        backup = _backup_hosts()
        _atomic_write(HOSTS_PATH, new_text)

        return InstallResult(
            ok=True,
            added=added,
            updated=updated,
            skipped=skipped,
            backup_path=backup,
        )

    except requests.exceptions.SSLError as e:
        return InstallResult(ok=False, error=f"TLS error: {e}")
    except requests.exceptions.ConnectionError:
        return InstallResult(ok=False, error="No connection")
    except requests.exceptions.Timeout:
        return InstallResult(ok=False, error="Timeout")
    except PermissionError:
        return InstallResult(ok=False, error="Permission denied (admin required)")
    except ValueError as e:
        return InstallResult(ok=False, error=str(e))
    except Exception as e:
        return InstallResult(ok=False, error=f"Unexpected error: {e}")
