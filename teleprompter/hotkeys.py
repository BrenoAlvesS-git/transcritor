"""Gerencia hotkeys globais usando pynput."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

from pynput import keyboard


@dataclass
class HotkeyCallbacks:
    scroll_up: Callable[[], None]
    scroll_down: Callable[[], None]
    opacity_up: Callable[[], None]
    opacity_down: Callable[[], None]
    toggle_minimize: Callable[[], None]
    next_text: Callable[[], None]
    toggle_autoscroll: Callable[[], None]


class GlobalHotkeyManager:
    """Registra atalhos globais de teclado (incluindo teclas únicas)."""

    def __init__(self, callbacks: HotkeyCallbacks) -> None:
        self.callbacks = callbacks
        self._listener: Optional[keyboard.Listener] = None
        self._hotkeys: Optional[keyboard.GlobalHotKeys] = None
        self._ctrl_pressed = False

    def start(self) -> None:
        # Mantém no GlobalHotKeys apenas atalhos sem ambiguidade de layout.
        bindings: Dict[str, Callable[[], None]] = {
            "<f9>": self.callbacks.toggle_minimize,
            "<f10>": self.callbacks.next_text,
        }
        self._hotkeys = keyboard.GlobalHotKeys(bindings)
        self._hotkeys.start()

        def on_press(key: keyboard.Key | keyboard.KeyCode) -> None:
            if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self._ctrl_pressed = True
                return

            if key == keyboard.Key.up:
                self.callbacks.scroll_up()
            elif key == keyboard.Key.down:
                self.callbacks.scroll_down()
            elif key == keyboard.Key.space:
                self.callbacks.toggle_autoscroll()

            # Ctrl + '+' / '=' (teclados US/ABNT e numpad add)
            if self._ctrl_pressed:
                if key == keyboard.KeyCode.from_char("="):
                    self.callbacks.opacity_up()
                elif key == keyboard.KeyCode.from_char("+"):
                    self.callbacks.opacity_up()
                elif key == keyboard.KeyCode.from_char("-"):
                    self.callbacks.opacity_down()

        def on_release(key: keyboard.Key | keyboard.KeyCode) -> None:
            if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self._ctrl_pressed = False

        self._listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self._listener.start()

    def stop(self) -> None:
        if self._hotkeys:
            self._hotkeys.stop()
            self._hotkeys = None
        if self._listener:
            self._listener.stop()
            self._listener = None
