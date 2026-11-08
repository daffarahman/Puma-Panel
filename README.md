# Early Aqua panel and dock

GNOME Shell 51 theme for the existing User Themes and Dash to Dock extensions.

The panel has pale horizontal pinstripes, dark text and symbolic icons, and an
internal gradient that darkens to black along the bottom edge for a beveled
appearance. It has no drop shadow. The dock follows the supplied Cheetah/Puma reference: a rectangular
cool translucent backing at 50% opacity, fine low-contrast horizontal pinstripes,
a single thin light border, square corners, no bottom gap,
black triangular running indicators, and
pale app-name labels. Both keep their appearance in light and dark system modes.

## Install

Requires GNOME Shell 51, the enabled User Themes and Dash to Dock extensions,
Python 3, and `dconf`. Dash to Dock must be installed for the current user under
`~/.local/share/gnome-shell/extensions/`. Blur My Shell and Kiwi are optional;
the installer manages their relevant appearance settings when present.

```sh
git clone https://github.com/daffarahman/Puma-Panel.git
cd Puma-Panel
python3 panel-theme.py apply
```

The SVG panel and dock artwork is original to this project. Application icons
in your dock come from your separately selected icon theme.

Apply or reapply the theme:

```bash
python3 panel-theme.py apply
```

Restore just the previous dock appearance, keeping the pinstriped panel:

```bash
python3 panel-theme.py restore-dock
```

Restore the settings saved before the panel and dock were customized:

```bash
python3 panel-theme.py restore
```

`previous-settings.json` preserves the original values of every managed setting.
Adding the dock settings keeps the earlier panel backup intact. Reapplying reloads
the theme immediately. The installed copy lives in
`~/.local/share/themes/Puma-Panel` (or `$XDG_DATA_HOME/themes/Puma-Panel`).

Edit the files under `Puma-Panel/gnome-shell`, then reapply:

- `panel.css` and `pinstripes.svg`: panel styling and texture.
- `dock.css` and `dock-pinstripes.svg`: dock fill, native rectangular border, and texture.
- `dock-layout.css`: zero bottom margin, square corners, compact icon padding,
  and the thin separator.
- `running-triangle.svg` and `dock-divider.svg`: indicator and divider artwork.

Dash to Dock's custom background and Blur My Shell's background override are
disabled so they do not replace the theme's backing. Kiwi's dock appearance
options are also disabled. Dock position is bottom, and full-width mode is off. Icon size, pinned
apps, click actions, visibility behavior, downloads, and trash are retained.

## Blur My Shell

The extension can be enabled normally. To blur behind the dock, use its Dock
settings with **Blur on** and **Override background off**. The theme then supplies
the translucent fill, pinstripes, border, and running indicators while Blur My
Shell supplies the blur underneath. Applying the theme preserves the dock blur
switch. Keep **Panel blur off** for the opaque pinstriped top panel.

The dock uses a native CSS border. A hollow `border-image` in GNOME Shell's St
renderer can skip painting the background color while still painting the texture;
this was the cause of the darker live result compared with the earlier preview.

Dash to Dock's own stylesheet sets a bottom margin with priority over Shell
themes. The apply script appends a marked layout block to the user-installed
extension's stylesheet, and either restore command removes it. Extension updates
can replace this block; rerun `apply` to put it back.

The SVG artwork is drawn for this theme; the dock is inspired by the flat Aqua
appearance of OS X 10.0–10.4. The existing icon theme supplies application icons.
