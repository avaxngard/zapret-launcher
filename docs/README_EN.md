# zapret-launcher ([RU](https://github.com/avaxngard/zapret-launcher/blob/main/README.md))

A convenient and intuitive launcher for bypassing DPI-based blocking.
It includes a built-in **tg-ws-proxy** and **zapret-discord-youtube** by **Flowseal**, along with automatic updates, ongoing support, and rapid troubleshooting.

# Installation
- Download the installer from the [**official website**](https://zapret-launcher.ru/#download)
- Install the launcher and its components
- Launch and use

# Project build
- For **Windows 10/11**: `Python 3.12`
- For **Windows 7**: `Python 3.8`
### Before compiling, rename the "pages" folder to "page" inside the gui/ directory.
### After compilation, add "dev_mode": "true" to config.json to eliminate the startup error, or alternatively, remove it from within main.py if __name__ == "__main__":
```_sig_ok, _sig_msg = _verify_current_binary()
    if not _sig_ok:
        _text, _caption = _get_launch_block_message(_sig_msg)
        ctypes.windll.user32.MessageBoxW(
            0,
            _text,
            _caption,
            0x00000010
        )
        sys.exit(1)
```

# Found a bug? —> [@zapret_launcher_bot](https://t.me/zapret_launcher_bot)

# News
- [**Telegram**](https://t.me/zapret_launcher)

# Donate
- [**DonationAlerts**](https://www.donationalerts.com/r/tweenkedrage)

# Fork/Acknowledgments
- tg-ws-proxy, zapret-discord-youtube / Flowseal, bol-van
