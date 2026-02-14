"""Bootstrap do aplicativo."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from .hotkeys import GlobalHotkeyManager, HotkeyCallbacks
from .ui import TeleprompterWindow


def run() -> int:
    app = QApplication(sys.argv)

    window = TeleprompterWindow()
    window.show()

    hotkeys = GlobalHotkeyManager(
        HotkeyCallbacks(
            scroll_up=window.hotkey_scroll_up,
            scroll_down=window.hotkey_scroll_down,
            opacity_up=window.hotkey_opacity_up,
            opacity_down=window.hotkey_opacity_down,
            toggle_minimize=window.hotkey_toggle_minimize,
            next_text=window.hotkey_next_text,
            toggle_autoscroll=window.hotkey_toggle_autoscroll,
        )
    )
    hotkeys.start()

    app.aboutToQuit.connect(hotkeys.stop)
    return app.exec()
