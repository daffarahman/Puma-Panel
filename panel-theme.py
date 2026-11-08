#!/usr/bin/env python3
"""Apply the early Aqua panel and dock, or restore their saved settings."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
THEME = "Puma-Panel"
DEST = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "themes" / THEME
STATE = ROOT / "previous-settings.json"
EXT_STYLESHEET = DEST.parent.parent / "gnome-shell/extensions/dash-to-dock@micxgx.gmail.com/stylesheet.css"
LAYOUT_BEGIN = "/* BEGIN Puma-Panel managed dock layout */"
LAYOUT_END = "/* END Puma-Panel managed dock layout */"
PANEL_SETTINGS = {
    "/org/gnome/shell/extensions/user-theme/name": "'Puma-Panel'",
    "/org/gnome/shell/extensions/blur-my-shell/panel/blur": "false",
    "/org/gnome/shell/extensions/kiwi/panel-transparency": "false",
    "/org/gnome/shell/extensions/kiwi/panel-styling": "false",
}
DOCK_SETTINGS = {
    "/org/gnome/shell/extensions/blur-my-shell/dash-to-dock/override-background": "false",
    "/org/gnome/shell/extensions/kiwi/dock-styling": "false",
    "/org/gnome/shell/extensions/kiwi/dock-adaptive-colors": "false",
    "/org/gnome/shell/extensions/kiwi/dock-blur": "false",
    "/org/gnome/shell/extensions/dash-to-dock/apply-custom-theme": "false",
    "/org/gnome/shell/extensions/dash-to-dock/custom-background-color": "false",
    "/org/gnome/shell/extensions/dash-to-dock/transparency-mode": "'DEFAULT'",
    "/org/gnome/shell/extensions/dash-to-dock/force-straight-corner": "true",
    "/org/gnome/shell/extensions/dash-to-dock/running-indicator-style": "'DEFAULT'",
    "/org/gnome/shell/extensions/dash-to-dock/dock-position": "'BOTTOM'",
    "/org/gnome/shell/extensions/dash-to-dock/extend-height": "false",
}
# Older versions managed the dock blur switch. Keep its saved value restorable,
# but let the user's blur choice persist when applying the theme from now on.
RESTORE_DOCK_KEYS = set(DOCK_SETTINGS) | {
    "/org/gnome/shell/extensions/blur-my-shell/dash-to-dock/blur",
}
SETTINGS = PANEL_SETTINGS | DOCK_SETTINGS
THEME_KEY = "/org/gnome/shell/extensions/user-theme/name"


def dconf(*args):
    return subprocess.run(["dconf", *args], check=True, capture_output=True, text=True).stdout.strip()


def write_settings(saved):
    # Restore the theme first, before the extensions resume painting the panel.
    for key, value in saved.items():
        dconf("write", key, value) if value is not None else dconf("reset", key)


def reload_theme():
    if dconf("read", THEME_KEY) == "'Puma-Panel'":
        dconf("write", THEME_KEY, "''")
        dconf("write", THEME_KEY, "'Puma-Panel'")


def dock_layout(enabled):
    """Add/remove only our marked block, preserving the extension's own CSS."""
    original = EXT_STYLESHEET.read_text()
    text = original
    if LAYOUT_BEGIN in text or LAYOUT_END in text:
        if text.count(LAYOUT_BEGIN) != 1 or text.count(LAYOUT_END) != 1:
            raise SystemExit("The managed dock layout markers need repair.")
        before, _, rest = text.partition(LAYOUT_BEGIN)
        block, end, after = rest.partition(LAYOUT_END)
        if not end:
            raise SystemExit("The managed dock layout block is incomplete.")
        text = before.removesuffix("\n") + after.removeprefix("\n")
    if enabled:
        css = (ROOT / THEME / "gnome-shell/dock-layout.css").read_text()
        text += f"\n{LAYOUT_BEGIN}\n{css}{LAYOUT_END}\n"
    if text != original:
        EXT_STYLESHEET.write_text(text)
    return original


def restore(dock_only=False):
    saved = json.loads(STATE.read_text())
    if dock_only:
        saved = {key: value for key, value in saved.items() if key in RESTORE_DOCK_KEYS}
        if not saved:
            raise SystemExit("No dock settings have been saved yet.")
        (DEST / "gnome-shell/gnome-shell.css").write_text('@import url("panel.css");\n')
    dock_layout(False)
    write_settings(saved)
    reload_theme()
    print("Restored the previous dock settings; kept the Aqua panel." if dock_only
          else "Restored the previous panel and dock settings.")


def apply():
    source = ROOT / THEME
    if DEST.exists() and not (DEST / ".puma-panel-managed").exists():
        raise SystemExit(f"Refusing to replace an unrelated theme: {DEST}")
    # Add newly managed dock keys without replacing the original panel backup.
    before = {key: dconf("read", key) or None for key in SETTINGS}
    saved = json.loads(STATE.read_text()) if STATE.exists() else {}
    for key, value in before.items():
        saved.setdefault(key, value)
    pending = STATE.with_suffix(".json.tmp")
    pending.write_text(json.dumps(saved, indent=2) + "\n")
    pending.replace(STATE)
    shutil.copytree(source, DEST, dirs_exist_ok=True)
    (DEST / "gnome-shell/dock-glass.svg").unlink(missing_ok=True)
    (DEST / ".puma-panel-managed").touch()
    old_extension_css = None
    try:
        old_extension_css = dock_layout(True)
        # Configure the extensions before selecting/reloading the theme.
        for key in reversed(SETTINGS):
            dconf("write", key, SETTINGS[key])
        reload_theme()
    except Exception:
        if old_extension_css is not None:
            EXT_STYLESHEET.write_text(old_extension_css)
        write_settings(before)
        raise
    print(f"Applied {THEME}. Installed theme: {DEST}")
    print(f"Previous settings: {STATE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["apply", "restore", "restore-dock"])
    args = parser.parse_args()
    apply() if args.action == "apply" else restore(dock_only=args.action == "restore-dock")
