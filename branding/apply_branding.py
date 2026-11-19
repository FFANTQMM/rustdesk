"""Apply branding/branding.json and optional branding/icon.png, branding/logo.png to the sources.

Run from the repository root before building (the Build vepidesk workflow does this).
Needs Pillow only when icon.png is present.
"""

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRANDING = ROOT / "branding"


def replace_once(path: Path, pattern: str, repl: str) -> None:
    text = path.read_bytes().decode("utf-8")  # keep CRLF line endings as they are
    new, n = re.subn(pattern, lambda _: repl, text, count=1, flags=re.M)
    if n != 1:
        sys.exit(f"apply_branding: pattern not found in {path}: {pattern}")
    path.write_bytes(new.encode("utf-8"))


def rc_escape(s: str) -> str:
    return s.replace('"', '""')


def apply_text(name: str, description: str) -> None:
    replace_once(
        ROOT / "src/branding.rs",
        r'^const APP_NAME: &str = ".*";\r?$',
        f'const APP_NAME: &str = "{name}";',
    )
    rc = ROOT / "flutter/windows/runner/Runner.rc"
    replace_once(rc, r'VALUE "FileDescription", ".*?" "\\0"',
                 f'VALUE "FileDescription", "{rc_escape(description)}" "\\0"')
    replace_once(rc, r'VALUE "ProductName", ".*?" "\\0"',
                 f'VALUE "ProductName", "{rc_escape(name)}" "\\0"')


def apply_icon(src: Path) -> None:
    from PIL import Image

    img = Image.open(src).convert("RGBA")
    if img.width != img.height:
        sys.exit("apply_branding: icon.png must be square")
    if img.width < 256:
        sys.exit("apply_branding: icon.png must be at least 256x256")

    def ico(dst: str, sizes):
        img.save(ROOT / dst, format="ICO", sizes=[(s, s) for s in sizes])

    def png(dst: str, size: int):
        img.resize((size, size), Image.LANCZOS).save(ROOT / dst, format="PNG")

    full = [16, 24, 32, 48, 64, 128, 256]
    ico("res/icon.ico", full)
    ico("flutter/windows/runner/resources/app_icon.ico", full)
    ico("flutter/assets/icon.ico", full)
    ico("res/tray-icon.ico", [16, 20, 24, 32, 48, 64])
    png("res/icon.png", 256)
    png("res/32x32.png", 32)
    png("res/64x64.png", 64)
    png("res/128x128.png", 128)
    png("res/128x128@2x.png", 256)
    # The tray and the in-app icon prefer this file over the built-in SVG.
    png("flutter/assets/icon.png", 256)


def main() -> None:
    cfg = json.loads((BRANDING / "branding.json").read_text(encoding="utf-8"))
    name = str(cfg.get("name", "")).strip()
    description = str(cfg.get("description", "")).strip() or name
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", name):
        sys.exit("apply_branding: name must be 1-32 latin letters, digits, '-' or '_'")

    apply_text(name, description)
    print(f"apply_branding: name={name!a} description={description!a}")

    icon = BRANDING / "icon.png"
    if icon.is_file():
        apply_icon(icon)
        print("apply_branding: icons generated from icon.png")

    logo = BRANDING / "logo.png"
    if logo.is_file():
        shutil.copyfile(logo, ROOT / "flutter/assets/logo.png")
        print("apply_branding: logo.png copied")


if __name__ == "__main__":
    main()
