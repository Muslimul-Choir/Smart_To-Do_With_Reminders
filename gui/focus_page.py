"""Halaman Mode Fokus."""
import tkinter as tk
from tkinter import ttk

from gui.theme import (
    BG, BLUE_ACCENT, FONT, GREEN, MUTED, NAVY, TEXT, WHITE, make_card, page_header,
)


def build_focus_page(parent, app):
    page = tk.Frame(parent, bg=BG)
    page.columnconfigure(0, weight=1)
    page_header(page, "Mode fokus", "Selesaikan satu hal penting dalam satu waktu").grid(
        row=0, column=0, sticky="w", pady=(0, 12))

    card = make_card(page)
    card.grid(row=1, column=0, sticky="new")
    tk.Frame(card, bg=BLUE_ACCENT, height=6).pack(fill="x")

    body = tk.Frame(card, bg=WHITE)
    body.pack(fill="x", padx=30, pady=24)
    tk.Label(body, text="BERIKUTNYA", font=(FONT, 9, "bold"), bg=WHITE, fg=MUTED).pack(anchor="w")

    app.focus_done_icon = tk.Canvas(body, width=30, height=30, bg=WHITE, highlightthickness=0)
    app.focus_done_icon.create_oval(3, 3, 27, 27, fill=GREEN, outline="")
    app.focus_done_icon.create_line(9, 15, 13, 19, 21, 10, fill=WHITE, width=2)

    app.focus_title_label = tk.Label(body, font=(FONT, 22, "bold"), bg=WHITE, fg=NAVY,
                                     wraplength=600, justify="left")
    app.focus_title_label.pack(anchor="w", pady=(4, 8))

    app.focus_info_label = tk.Label(body, font=(FONT, 11), bg=WHITE, fg=TEXT, justify="left")
    app.focus_info_label.pack(anchor="w")

    app.focus_priority_label = tk.Label(body, font=(FONT, 11, "bold"), bg=WHITE)
    app.focus_priority_label.pack(anchor="w", pady=(8, 0))

    app.focus_time_left_label = tk.Label(body, font=(FONT, 12, "bold"), bg=WHITE, fg=NAVY)
    app.focus_time_left_label.pack(anchor="w", pady=(8, 16))

    app.focus_button = ttk.Button(body, text="Tandai selesai", style="Success.TButton",
                                  command=app.complete_focus_task)
    app.focus_button.pack(anchor="w")

    tk.Label(page, text="Urutan: belum selesai, tenggat terdekat, lalu prioritas tertinggi.",
             font=(FONT, 9), bg=BG, fg=MUTED).grid(row=2, column=0, sticky="w", pady=(10, 0))
    return page
