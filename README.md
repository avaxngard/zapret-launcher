# zapret-launcher ([EN](https://github.com/avaxngard/zapret-launcher/blob/main/docs/README_EN.md))

Удобный и понятный лаунчер для обхода DPI блокировок.
Внутри имеется встроенный **tg-ws-proxy** и **zapret-discord-youtube** от **Flowseal**, автообновления, постоянная поддержка и быстрая находка неисправностей.

# Установка
- Скачайте инсталлятор с [**официального сайта**](https://zapret-launcher.ru/#download)
- Установите лаунчер и его компоненты
- Запустите и пользуйтесь

# Сборка проекта
- Для **Windows 10/11**: `Python 3.12`
- Для **Windows 7**: `Python 3.8`
### Перед компиляцией в папке gui/ переименуйте папку "pages" в "page"
### После компиляции в config.json пропишите "dev_mode": "true", чтобы ошибка при старте исчезла, или же удалите внутри main.py в if __name__ == "__main__":
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

# Нашли неисправность? —> [@zapret_launcher_bot](https://t.me/zapret_launcher_bot)

# Новости
- [**Telegram**](https://t.me/zapret_launcher)

# Поддержать
- [**DonationAlerts**](https://www.donationalerts.com/r/tweenkedrage)

# Форк/Благодарности
- tg-ws-proxy, zapret-discord-youtube / Flowseal, bol-van
