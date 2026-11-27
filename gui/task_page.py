"""Halaman Daftar Tugas dan jendela form Tambah/Ubah."""
import tkinter as tk
from tkinter import ttk

from gui.theme import (
    BG, FONT, MUTED, NAVY, PRIORITY_COLORS, PRIORITY_LABELS,
    TEXT, WHITE, make_card, make_tree, page_header,
)
from models.task import PRIORITIES


def build_task_page(parent, app):
    page = tk.Frame(parent, bg=BG)
    page.columnconfigure(0, weight=1)
    page.rowconfigure(1, weight=1)
    page_header(page, "Daftar tugas", "Atur pekerjaan, kegiatan, dan hal penting lainnya").grid(
        row=0, column=0, sticky="w", pady=(0, 14))

    table_card = make_card(page)
    table_card.grid(row=1, column=0, sticky="nsew")
    table_card.columnconfigure(0, weight=1)
    table_card.rowconfigure(1, weight=1)

    tk.Label(table_card, text="Semua tugas", bg=WHITE, fg=NAVY, font=(FONT, 12, "bold")).grid(
        row=0, column=0, sticky="w", padx=14, pady=(12, 0))
    app.task_count_label = tk.Label(table_card, bg=WHITE, fg=MUTED, font=(FONT, 9))
    app.task_count_label.grid(row=0, column=1, sticky="e", padx=14, pady=(12, 0))

    columns = [
        ("title", "Judul"), ("subject", "Kategori"), ("deadline", "Tenggat"),
        ("priority", "Prioritas"), ("status", "Status"), ("alert", "Penanda"),
    ]
    frame, app.task_tree = make_tree(table_card, columns, [205, 115, 130, 85, 115, 90], height=12)
    frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
    app.task_tree.configure(style="TaskList.Treeview")
    for priority, color in PRIORITY_COLORS.items():
        app.task_tree.tag_configure(f"p_{priority}", foreground=color)
    app.task_tree.bind("<Double-1>", lambda _e: app.view_selected_task())

    actions_bar = tk.Frame(page, bg=BG)
    actions_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))
    tk.Label(actions_bar, text="Klik dua kali tugas untuk melihat detail.",
             bg=BG, fg=MUTED, font=(FONT, 9)).pack(side="right", pady=6)
    for text, style, cmd in (
        ("+ Tambah", "Primary", app.add_task),
        ("Ubah", "Navy", app.edit_selected_task),
        ("Lihat", "Ghost", app.view_selected_task),
        ("Selesai", "Success", app.complete_selected_task),
        ("Hapus", "Danger", app.delete_selected_task),
    ):
        ttk.Button(actions_bar, text=text, style=f"{style}.TButton", command=cmd).pack(
            side="left", padx=(0, 8))
    return page


def build_task_form_window(parent, app):
    window = tk.Toplevel(parent)
    window.title("Tambah tugas")
    window.geometry("500x480")
    window.resizable(False, False)
    window.configure(bg=BG)
    window.columnconfigure(0, weight=1)
    window.rowconfigure(1, weight=1)

    app.form_title_label = tk.Label(window, text="Tambah tugas", font=(FONT, 19, "bold"), bg=BG, fg=NAVY)
    app.form_title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(18, 10))
    card = make_card(window)
    card.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 18))
    card.columnconfigure(1, weight=1)

    app.title_var = tk.StringVar()
    app.subject_var = tk.StringVar()
    app.date_var = tk.StringVar()
    app.time_var = tk.StringVar()
    app.form_priority_var = tk.StringVar(value=PRIORITY_LABELS["Medium"])

    app.title_entry = ttk.Entry(card, textvariable=app.title_var)
    app.description_text = tk.Text(card, height=4, font=(FONT, 10), relief="solid", borderwidth=1)

    rows = (
        ("Judul *", app.title_entry),
        ("Deskripsi", app.description_text),
        ("Kategori", ttk.Entry(card, textvariable=app.subject_var)),
        ("Tanggal (YYYY-MM-DD) *", ttk.Entry(card, textvariable=app.date_var)),
        ("Jam (HH:MM) *", ttk.Entry(card, textvariable=app.time_var)),
        ("Prioritas *", ttk.Combobox(card, textvariable=app.form_priority_var, state="readonly",
                                     values=[PRIORITY_LABELS[p] for p in PRIORITIES])),
    )
    for row_idx, (label, widget) in enumerate(rows):
        tk.Label(card, text=label, bg=WHITE, fg=TEXT, font=(FONT, 10, "bold")).grid(
            row=row_idx, column=0, sticky="nw", padx=(20, 12), pady=8)
        widget.grid(row=row_idx, column=1, sticky="ew", padx=(0, 20), pady=8)

    buttons = tk.Frame(card, bg=WHITE)
    buttons.grid(row=len(rows), column=1, sticky="w", pady=16)
    ttk.Button(buttons, text="Simpan", style="Primary.TButton", command=app.save_task).pack(
        side="left", padx=(0, 8))
    ttk.Button(buttons, text="Batal", style="Ghost.TButton", command=app.cancel_form).pack(side="left")
    window.bind("<Escape>", lambda _e: app.cancel_form())
    return window
