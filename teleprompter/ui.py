"""Interface principal do Teleprompter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .os_integration import WindowsWindowTools


@dataclass
class TextEntry:
    title: str
    content: str


class TeleprompterWindow(QMainWindow):
    """Janela principal com área de texto, lista de roteiros e controles."""

    request_scroll = pyqtSignal(int)
    request_opacity_change = pyqtSignal(float)
    request_toggle_autoscroll = pyqtSignal()
    request_toggle_minimize = pyqtSignal()
    request_next_text = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Teleprompter Invisível")
        self.setMinimumSize(980, 640)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self._windows_tools = WindowsWindowTools()
        self._entries: List[TextEntry] = []
        self._opacity = 0.85
        self._autoscroll_running = False

        self._build_ui()
        self._wire_signals()

        self._autoscroll_timer = QTimer(self)
        self._autoscroll_timer.timeout.connect(self._autoscroll_step)
        self._autoscroll_timer.setInterval(45)

        self.setWindowOpacity(self._opacity)

    def _build_ui(self) -> None:
        root = QWidget(self)
        self.setCentralWidget(root)
        base_layout = QHBoxLayout(root)

        # Coluna de textos carregados.
        side_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(260)
        side_layout.addWidget(QLabel("Textos"))
        side_layout.addWidget(self.list_widget)

        load_btn = QPushButton("Carregar .txt")
        load_btn.clicked.connect(self.load_text_file)
        side_layout.addWidget(load_btn)

        add_empty_btn = QPushButton("Novo texto vazio")
        add_empty_btn.clicked.connect(self.add_empty_text)
        side_layout.addWidget(add_empty_btn)

        next_btn = QPushButton("Próximo texto (F10)")
        next_btn.clicked.connect(self.next_text)
        side_layout.addWidget(next_btn)

        # Coluna principal de edição/teleprompter.
        main_layout = QVBoxLayout()
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Digite ou carregue seu roteiro...")
        self.editor.setFont(QFont("Arial", 24))
        main_layout.addWidget(self.editor)

        controls = QHBoxLayout()
        self.play_pause_btn = QPushButton("Iniciar/Pausar (Espaço)")
        self.play_pause_btn.clicked.connect(self.toggle_autoscroll)
        controls.addWidget(self.play_pause_btn)

        self.capture_checkbox = QCheckBox("Excluir da captura (Windows)")
        self.capture_checkbox.toggled.connect(self._toggle_capture_exclusion)
        controls.addWidget(self.capture_checkbox)

        self.click_through_checkbox = QCheckBox("Modo leitura click-through")
        self.click_through_checkbox.toggled.connect(self._toggle_click_through)
        controls.addWidget(self.click_through_checkbox)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(int(self._opacity * 100))
        self.opacity_slider.valueChanged.connect(self._slider_opacity_changed)
        controls.addWidget(QLabel("Opacidade"))
        controls.addWidget(self.opacity_slider)

        main_layout.addLayout(controls)

        base_layout.addLayout(side_layout)
        base_layout.addLayout(main_layout)

        self._add_menu_actions()

    def _add_menu_actions(self) -> None:
        menu = self.menuBar().addMenu("Arquivo")
        load_action = QAction("Carregar texto", self)
        load_action.triggered.connect(self.load_text_file)
        menu.addAction(load_action)

    def _wire_signals(self) -> None:
        self.list_widget.currentRowChanged.connect(self._on_text_selected)

        self.request_scroll.connect(self.manual_scroll)
        self.request_opacity_change.connect(self.adjust_opacity)
        self.request_toggle_autoscroll.connect(self.toggle_autoscroll)
        self.request_toggle_minimize.connect(self.toggle_minimize_restore)
        self.request_next_text.connect(self.next_text)

    def add_empty_text(self) -> None:
        title = f"Texto {len(self._entries) + 1}"
        self._entries.append(TextEntry(title=title, content=""))
        self.list_widget.addItem(QListWidgetItem(title))
        self.list_widget.setCurrentRow(len(self._entries) - 1)

    def load_text_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo de texto",
            "",
            "Arquivos de texto (*.txt)",
        )
        if not file_path:
            return

        path = Path(file_path)
        content = path.read_text(encoding="utf-8", errors="ignore")
        self._entries.append(TextEntry(title=path.name, content=content))
        self.list_widget.addItem(QListWidgetItem(path.name))
        self.list_widget.setCurrentRow(len(self._entries) - 1)

    def _on_text_selected(self, index: int) -> None:
        if index < 0 or index >= len(self._entries):
            return
        self.editor.setPlainText(self._entries[index].content)

    def _sync_current_entry(self) -> None:
        idx = self.list_widget.currentRow()
        if idx < 0 or idx >= len(self._entries):
            return
        self._entries[idx].content = self.editor.toPlainText()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._sync_current_entry()
        event.accept()

    def manual_scroll(self, direction: int) -> None:
        scrollbar = self.editor.verticalScrollBar()
        scrollbar.setValue(scrollbar.value() + direction * 30)

    def _autoscroll_step(self) -> None:
        self.manual_scroll(1)

    def toggle_autoscroll(self) -> None:
        self._autoscroll_running = not self._autoscroll_running
        if self._autoscroll_running:
            self._autoscroll_timer.start()
        else:
            self._autoscroll_timer.stop()

    def adjust_opacity(self, delta: float) -> None:
        self._opacity = min(1.0, max(0.3, self._opacity + delta))
        self.setWindowOpacity(self._opacity)
        self.opacity_slider.blockSignals(True)
        self.opacity_slider.setValue(int(self._opacity * 100))
        self.opacity_slider.blockSignals(False)

    def _slider_opacity_changed(self, value: int) -> None:
        self._opacity = value / 100.0
        self.setWindowOpacity(self._opacity)

    def toggle_minimize_restore(self) -> None:
        if self.isMinimized():
            self.showNormal()
            self.raise_()
            self.activateWindow()
        else:
            self.showMinimized()

    def next_text(self) -> None:
        if not self._entries:
            return
        self._sync_current_entry()
        current = self.list_widget.currentRow()
        next_idx = (current + 1) % len(self._entries)
        self.list_widget.setCurrentRow(next_idx)

    def _toggle_capture_exclusion(self, enabled: bool) -> None:
        result = self._windows_tools.set_capture_exclusion(self.winId(), enabled)
        if enabled and not result:
            QMessageBox.information(
                self,
                "Recurso indisponível",
                "Exclusão de captura está disponível apenas no Windows 10+.",
            )
            self.capture_checkbox.blockSignals(True)
            self.capture_checkbox.setChecked(False)
            self.capture_checkbox.blockSignals(False)

    def _toggle_click_through(self, enabled: bool) -> None:
        # Primeiro tenta via Qt (funciona em algumas plataformas, incluindo macOS).
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, enabled)
        self.show()

        if self._windows_tools.is_windows:
            self._windows_tools.set_click_through(self.winId(), enabled)

    # Métodos seguros para callbacks de hotkeys globais (thread -> Qt signal)
    def hotkey_scroll_up(self) -> None:
        self.request_scroll.emit(-1)

    def hotkey_scroll_down(self) -> None:
        self.request_scroll.emit(1)

    def hotkey_opacity_up(self) -> None:
        self.request_opacity_change.emit(+0.05)

    def hotkey_opacity_down(self) -> None:
        self.request_opacity_change.emit(-0.05)

    def hotkey_toggle_autoscroll(self) -> None:
        self.request_toggle_autoscroll.emit()

    def hotkey_toggle_minimize(self) -> None:
        self.request_toggle_minimize.emit()

    def hotkey_next_text(self) -> None:
        self.request_next_text.emit()
