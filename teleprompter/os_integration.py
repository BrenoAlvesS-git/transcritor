"""Helpers para integração com recursos de janela do sistema operacional."""

from __future__ import annotations

import ctypes
import platform
from ctypes import wintypes


class WindowsWindowTools:
    """Encapsula chamadas Win32 usadas pelo teleprompter."""

    WDA_NONE = 0x0
    WDA_EXCLUDEFROMCAPTURE = 0x11

    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020

    def __init__(self) -> None:
        self.is_windows = platform.system().lower() == "windows"
        self._user32 = ctypes.windll.user32 if self.is_windows else None

    def _hwnd_from_winid(self, win_id: int) -> int:
        return int(win_id)

    def set_capture_exclusion(self, win_id: int, enabled: bool) -> bool:
        """Ativa/desativa exclusão da janela em captura de tela (Windows 10+)."""
        if not self.is_windows:
            return False

        hwnd = self._hwnd_from_winid(win_id)
        affinity = self.WDA_EXCLUDEFROMCAPTURE if enabled else self.WDA_NONE
        result = self._user32.SetWindowDisplayAffinity(wintypes.HWND(hwnd), affinity)
        return bool(result)

    def set_click_through(self, win_id: int, enabled: bool) -> bool:
        """Ativa/desativa modo click-through em Windows usando extended style."""
        if not self.is_windows:
            return False

        hwnd = self._hwnd_from_winid(win_id)

        if ctypes.sizeof(ctypes.c_void_p) == 8:
            get_long = self._user32.GetWindowLongPtrW
            set_long = self._user32.SetWindowLongPtrW
        else:
            get_long = self._user32.GetWindowLongW
            set_long = self._user32.SetWindowLongW

        get_long.argtypes = [wintypes.HWND, ctypes.c_int]
        get_long.restype = ctypes.c_longlong
        set_long.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_longlong]
        set_long.restype = ctypes.c_longlong

        current_style = get_long(hwnd, self.GWL_EXSTYLE)
        if enabled:
            new_style = current_style | self.WS_EX_LAYERED | self.WS_EX_TRANSPARENT
        else:
            new_style = current_style & ~self.WS_EX_TRANSPARENT

        set_long(hwnd, self.GWL_EXSTYLE, new_style)
        # Força atualização da janela.
        self._user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0027)
        return True
