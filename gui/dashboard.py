"""Halaman Ringkasan (Dashboard): statistik dan daftar tugas mendatang."""
import tkinter as tk

from gui.theme import (
    BG, BLUE, BLUE_ACCENT, BLUE_LIGHT, FONT, NAVY, TEXT, WHITE,
    make_card, make_tree, page_header,
)

STAT_CARDS = (
    ("due_today", "Hari ini", BLUE_LIGHT, BLUE),
    ("due_soon", "Segera", "#F2F7FF", BLUE_ACCENT),
    ("completed", "Selesai", "#E7F0FF", BLUE),
    ("total", "Semua tugas", "#F2F7FF", BLUE_ACCENT),
)


def build_dashboard(parent, app):
    page = tk.Frame(parent, bg=BG)
    page.columnconfigure(0, weight=1)
    page.rowconfigure(2, weight=1)

    page_header(page, "Ringkasan aktivitasmu", "Pantau tenggat dan progres tugasmu di satu tempat").grid(
        row=0, column=0, sticky="w", pady=(0, 14))

    stats_row = tk.Frame(page, bg=BG)
    stats_row.grid(row=1, column=0, sticky="ew", pady=(0, 14))
    stats_row.columnconfigure((0, 1, 2, 3), weight=1, uniform="stats")

    app._stat_labels = {}
    for col, (key, title, tint, accent) in enumerate(STAT_CARDS):
        card = tk.Frame(stats_row, bg=tint, padx=14, pady=12)
        card.grid(row=0, column=col, sticky="nsew", padx=(0, 10) if col < 3 else 0)
        value_label = tk.Label(card, text="0", font=(FONT, 22, "bold"), bg=tint, fg=NAVY)
        value_label.pack(anchor="w")
        tk.Label(card, text=title, font=(FONT, 9), bg=tint, fg=TEXT).pack(anchor="w")
        tk.Frame(card, bg=accent, height=3).pack(fill="x", pady=(8, 0))
        app._stat_labels[key] = value_label

    upcoming = make_card(page)
    upcoming.grid(row=2, column=0, sticky="nsew")
    upcoming.columnconfigure(0, weight=1)
    upcoming.rowconfigure(1, weight=1)
    tk.Label(upcoming, text="Tugas mendatang", font=(FONT, 12, "bold"),
             bg=WHITE, fg=NAVY).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

    frame, app.upcoming_tree = make_tree(
        upcoming, [("title", "Tugas"), ("subject", "Kategori"), ("deadline", "Tenggat")],
        [280, 160, 160], height=10)
    frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
    app.upcoming_tree.bind("<Double-1>", lambda _e: _open_selected_task(app))
    return page


def _open_selected_task(app):
    selected = app.upcoming_tree.selection()
    if selected:
        task = app.manager.find_by_id(int(selected[0]))
        if task is not None:
            app.view_task(task)
