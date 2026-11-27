"""Navigasi sidebar aplikasi."""
import tkinter as tk

from gui.theme import (
    BLUE, FONT, NAVY, SIDEBAR_ACTIVE, SIDEBAR_DIVIDER,
    SIDEBAR_HOVER, SIDEBAR_MUTED, SIDEBAR_TEXT, WHITE,
)

NAV_ITEMS = (
    ("dashboard", "Ringkasan"),
    ("tasks", "Daftar tugas"),
    ("focus", "Mode fokus"),
)


def build_sidebar(parent, app):
    sidebar = tk.Frame(parent, bg=NAVY, width=224)
    sidebar.grid_propagate(False)
    sidebar.rowconfigure(3, weight=1)

    brand = tk.Frame(sidebar, bg=NAVY)
    brand.grid(row=0, column=0, sticky="ew", padx=20, pady=(24, 22))
    logo = tk.Canvas(brand, width=40, height=40, bg=NAVY, highlightthickness=0)
    logo.pack(side="left", padx=(0, 10))
    _draw_logo(logo)
    brand_text = tk.Frame(brand, bg=NAVY)
    brand_text.pack(side="left", fill="y")
    tk.Label(brand_text, text="Smart To-Do", font=(FONT, 15, "bold"),
             bg=NAVY, fg=WHITE).pack(anchor="w", pady=(1, 0))
    tk.Label(brand_text, text="Rencana, lebih teratur", font=(FONT, 8),
             bg=NAVY, fg=SIDEBAR_MUTED).pack(anchor="w")

    tk.Frame(sidebar, bg=SIDEBAR_DIVIDER, height=1).grid(row=1, column=0, sticky="ew", padx=18)
    tk.Label(sidebar, text="MENU", font=(FONT, 8, "bold"),
             bg=NAVY, fg=SIDEBAR_MUTED).grid(row=2, column=0, sticky="w", padx=22, pady=(22, 8))

    nav = tk.Frame(sidebar, bg=NAVY)
    nav.grid(row=3, column=0, sticky="new", padx=12)
    app.nav_buttons = {}
    for key, title in NAV_ITEMS:
        row = tk.Frame(nav, bg=NAVY, height=44)
        row.pack(fill="x", pady=3)
        row.pack_propagate(False)
        indicator = tk.Frame(row, bg=NAVY, width=3)
        indicator.pack(side="left", fill="y", padx=(0, 8))
        content = tk.Frame(row, bg=NAVY)
        content.pack(side="left", fill="both", expand=True)
        icon = tk.Canvas(content, width=22, height=22, bg=NAVY, highlightthickness=0)
        icon.pack(side="left", padx=(9, 12))
        label = tk.Label(content, text=title, font=(FONT, 10, "bold"),
                         bg=NAVY, fg=SIDEBAR_TEXT)
        label.pack(side="left")

        item = {"row": row, "indicator": indicator, "content": content, "icon": icon, "label": label}
        app.nav_buttons[key] = item
        for widget in item.values():
            widget.bind("<Button-1>", lambda _e, k=key: app.show_page(k))
            widget.bind("<Enter>", lambda _e, k=key: _set_hover(app, k, True))
            widget.bind("<Leave>", lambda _e, k=key: _set_hover(app, k, False))

    footer = tk.Frame(sidebar, bg=NAVY)
    footer.grid(row=4, column=0, sticky="sew", padx=20, pady=18)
    tk.Frame(footer, bg=SIDEBAR_DIVIDER, height=1).pack(fill="x", pady=(0, 12))
    tk.Label(footer, text="Semua tugas, satu tempat.", font=(FONT, 9),
             bg=NAVY, fg=SIDEBAR_MUTED).pack(anchor="w")
    return sidebar


def set_active_sidebar_item(app, active_key):
    app._active_page = active_key
    for key, item in app.nav_buttons.items():
        active = key == active_key
        bg = SIDEBAR_ACTIVE if active else NAVY
        for part in ("row", "content", "icon", "label"):
            item[part].configure(bg=bg)
        item["indicator"].configure(bg=BLUE if active else NAVY)
        item["label"].configure(fg=WHITE if active else SIDEBAR_TEXT)
        _draw_nav_icon(item["icon"], key, WHITE if active else SIDEBAR_MUTED)


def _set_hover(app, key, hovering):
    if key == app._active_page:
        return
    bg = SIDEBAR_HOVER if hovering else NAVY
    item = app.nav_buttons[key]
    for part in ("row", "content", "icon", "label"):
        item[part].configure(bg=bg)


def _draw_logo(canvas):
    canvas.create_rectangle(1, 1, 39, 39, fill=BLUE, outline="")
    for y in (12, 25):
        canvas.create_line(11, y, 14, y + 3, 19, y - 3, fill=WHITE, width=2)
        canvas.create_line(23, y, 31, y, fill=WHITE, width=2)


def _draw_nav_icon(canvas, key, color):
    canvas.delete("all")
    if key == "dashboard":
        for x, y in ((3, 3), (13, 3), (3, 13), (13, 13)):
            canvas.create_rectangle(x, y, x + 6, y + 6, outline=color, width=1.6)
    elif key == "tasks":
        for y in (5, 11, 17):
            canvas.create_rectangle(3, y - 2, 6, y + 1, outline=color, width=1.4)
            canvas.create_line(10, y, 20, y, fill=color, width=1.6)
    else:
        for r in (8, 5, 2):
            canvas.create_oval(11 - r, 11 - r, 11 + r, 11 + r, outline=color, width=1.5)