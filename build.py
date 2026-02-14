"""Build script para gerar executável do Teleprompter com PyInstaller.

Uso:
  python build.py
  python build.py --onefile
  python build.py --name MeuTeleprompter
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
SPEC = ROOT / "teleprompter.spec"


def run(cmd: list[str]) -> None:
    print("[build]", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build executável do Teleprompter")
    parser.add_argument("--name", default="TeleprompterInvisivel", help="Nome do executável")
    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Gera executável único (startup um pouco mais lento)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove pastas build/dist e arquivos temporários antes de compilar",
    )
    return parser.parse_args()


def clean() -> None:
    for path in (DIST, BUILD):
        if path.exists():
            shutil.rmtree(path)
    for spec in ROOT.glob("*.spec"):
        if spec.name != SPEC.name:
            spec.unlink(missing_ok=True)


def main() -> int:
    args = parse_args()

    if shutil.which("pyinstaller") is None:
        print(
            "PyInstaller não encontrado. Instale com: pip install pyinstaller",
            file=sys.stderr,
        )
        return 2

    if args.clean:
        clean()

    mode_flag = "--onefile" if args.onefile else "--onedir"

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        mode_flag,
        "--name",
        args.name,
        "--hidden-import",
        "pynput.keyboard._win32",
        "--hidden-import",
        "pynput.keyboard._darwin",
        "--hidden-import",
        "pynput.keyboard._xorg",
        "main.py",
    ]

    run(cmd)

    target = DIST / args.name
    if args.onefile:
        exe_suffix = ".exe" if sys.platform.startswith("win") else ""
        target = DIST / f"{args.name}{exe_suffix}"

    print(f"\nBuild concluído: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
