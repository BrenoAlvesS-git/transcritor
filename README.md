# Teleprompter Invisível (PyQt6)

Aplicativo desktop de teleprompter com:
- Janela **Always on Top**.
- Ajuste de opacidade/transparência.
- Múltiplos textos e carregamento de `.txt`.
- Rolagem manual e automática.
- Hotkeys globais (funcionam em segundo plano).
- Modo de exclusão de captura no Windows (`SetWindowDisplayAffinity` + `WDA_EXCLUDEFROMCAPTURE`).
- Modo leitura com tentativa de click-through.

## Requisitos

- Python 3.10+
- Windows/macOS/Linux (alguns recursos são específicos de Windows)

## Instalação (modo desenvolvimento)

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

## Gerar executável (PyInstaller)

### Instalação de dependências de build

```bash
pip install -r requirements-build.txt
```

### Build automático (recomendado)

```bash
python build.py --clean
```

Saída padrão:
- Windows (onedir): `dist/TeleprompterInvisivel/TeleprompterInvisivel.exe`
- macOS/Linux (onedir): `dist/TeleprompterInvisivel/TeleprompterInvisivel`

### Build em arquivo único

```bash
python build.py --clean --onefile
```

Saída padrão:
- Windows: `dist/TeleprompterInvisivel.exe`
- macOS/Linux: `dist/TeleprompterInvisivel`

### Build manual com spec (alternativo)

```bash
pyinstaller --noconfirm --clean teleprompter.spec
```

## Hotkeys globais

- `↑` / `↓`: rolar texto manualmente.
- `Ctrl` + `+`: aumentar opacidade.
- `Ctrl` + `-`: diminuir opacidade.
- `F9`: minimizar/restaurar janela.
- `F10`: próximo texto.
- `Espaço`: iniciar/pausar rolagem automática.

## Observações de plataforma

### Windows
- A opção **"Excluir da captura (Windows)"** usa `SetWindowDisplayAffinity` com `WDA_EXCLUDEFROMCAPTURE`.
- A opção **"Modo leitura click-through"** aplica também estilo Win32 (`WS_EX_TRANSPARENT`).
- Dependendo da versão do Windows e política de segurança, exclusão de captura pode exigir janela não minimizada e Desktop Window Manager ativo.

### macOS/Linux
- A exclusão de captura via `SetWindowDisplayAffinity` não existe.
- O modo click-through usa `Qt.WindowTransparentForInput` (suporte depende do compositor/sistema).
- No macOS, hotkeys globais podem exigir permissão em **Privacidade e Segurança > Acessibilidade**.

## Estrutura

- `main.py`: ponto de entrada.
- `teleprompter/ui.py`: janela principal e controles.
- `teleprompter/hotkeys.py`: registro de hotkeys globais com `pynput`.
- `teleprompter/os_integration.py`: integrações específicas de SO (Windows).
- `teleprompter/app.py`: bootstrap da aplicação.
- `build.py`: script para empacotar executável.
- `teleprompter.spec`: configuração alternativa de build no PyInstaller.
