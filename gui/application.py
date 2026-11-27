"""Pengendali utama aplikasi Smart To-Do."""
import os
import tkinter as tk
from datetime import date
from tkinter import messagebox

from core.reminder_manager import ReminderManager
from core.task_manager import TaskManager
from gui.dashboard import build_dashboard
from gui.focus_page import build_focus_page
from gui.sidebar import build_sidebar, set_active_sidebar_item
from gui.task_page import build_task_form_window, build_task_page
from gui.theme import (
    BG, PRIORITY_COLORS, PRIORITY_LABELS, STATUS_LABELS, center_window, setup_styles,
)
from utils.validators import ValidationError, validate_task_form, validate_task_id

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(PROJECT_DIR, "data", "tasks.json")


class SmartTodoApp(tk.Tk):
    CHECK_INTERVAL_MS = 30_000

    def __init__(self):
        super().__init__()
        self.title("Smart To-Do | Pengelola Tugas")
        self.geometry("1040x660")
        self.minsize(860, 560)
        self.configure(bg=BG)
        setup_styles(self)

        self.manager = TaskManager()
        self._form_window = None
        self.editing_id = None
        self._closing = False

        self._load_data()
        self.reminder = ReminderManager(self.manager)
        self.manager.add_listener(self._on_data_changed)

        self._build_layout()
        self.pages = {
            "dashboard": build_dashboard(self.content, self),
            "tasks": build_task_page(self.content, self),
            "focus": build_focus_page(self.content, self),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("dashboard")
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._reminder_after = self.after(1500, self._reminder_tick)

    # ---------- data & siklus hidup ----------
    def _load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                self.manager.load_json(DATA_FILE)
            else:
                self.manager.load_sample_data()
        except (OSError, ValueError, TypeError, KeyError) as error:
            messagebox.showerror("Gagal memuat data", f"File data tidak bisa dibaca ({error}). Memulai dari kosong.")
            self.manager = TaskManager()

    def _save_data(self):
        try:
            self.manager.save_json(DATA_FILE)
        except OSError as error:
            messagebox.showerror("Gagal menyimpan", f"Data tidak bisa disimpan: {error}")

    def _on_data_changed(self):
        self._save_data()
        if hasattr(self, "pages"):
            self.refresh_all()

    def _on_close(self):
        self._closing = True
        self.cancel_form()
        if self._reminder_after is not None:
            try:
                self.after_cancel(self._reminder_after)
            except tk.TclError:
                pass
            self._reminder_after = None
        self._save_data()
        self.destroy()

    # ---------- tata letak & navigasi ----------
    def _build_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        build_sidebar(self, self).grid(row=0, column=0, sticky="ns")
        self.content = tk.Frame(self, bg=BG)
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

    def show_page(self, page_name):
        self._refresh_page(page_name)
        self.pages[page_name].tkraise()
        set_active_sidebar_item(self, page_name)

    # ---------- form tambah / ubah tugas ----------
    def open_form(self, task=None):
        if self._form_window is None or not self._form_window.winfo_exists():
            self._form_window = build_task_form_window(self, self)
            self._form_window.transient(self)
            self._form_window.protocol("WM_DELETE_WINDOW", self.cancel_form)

        self.editing_id = task.task_id if task else None
        heading = "Ubah tugas" if task else "Tambah tugas"
        self._form_window.title(heading)
        self.form_title_label.config(text=heading)
        self.title_var.set(task.title if task else "")
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", task.description if task else "")
        self.subject_var.set(task.subject if task else "")
        self.date_var.set(task.deadline.date().isoformat() if task else date.today().isoformat())
        self.time_var.set(task.deadline.strftime("%H:%M") if task else "23:59")
        self.form_priority_var.set(PRIORITY_LABELS[task.priority] if task else PRIORITY_LABELS["Medium"])

        center_window(self._form_window, self)
        self._form_window.lift()
        self._form_window.grab_set()
        self.title_entry.focus_set()

    def add_task(self):
        self.open_form()

    def save_task(self):
        try:
            data = validate_task_form(
                self.title_var.get(),
                self.description_text.get("1.0", "end"),
                self.subject_var.get(),
                self.date_var.get(),
                self.time_var.get(),
                self.form_priority_var.get(),
            )
            if self.editing_id is None:
                self.manager.add_task(**data)
                msg = "Tugas baru berhasil ditambahkan."
            else:
                self.manager.edit_task(self.editing_id, **data)
                msg = "Tugas berhasil diperbarui."
        except ValidationError as error:
            messagebox.showerror("Input tidak valid", str(error))
            return
        except KeyError as error:
            messagebox.showerror("Gagal", str(error))
            return
        messagebox.showinfo("Berhasil", msg)
        self.cancel_form()

    def cancel_form(self):
        form, self._form_window = self._form_window, None
        self.editing_id = None
        if form is None:
            return
        try:
            if form.winfo_exists():
                form.grab_release()
                form.destroy()
        except tk.TclError:
            pass

    # ---------- aksi tabel tugas ----------
    def _selected_task(self):
        selected = self.task_tree.selection()
        try:
            if not selected:
                raise ValidationError("Pilih salah satu tugas dulu di tabel.")
            task_id = validate_task_id(selected[0])
            task = self.manager.find_by_id(task_id)
            if task is None:
                raise ValidationError(f"Tugas dengan ID {task_id} tidak ditemukan.")
            return task
        except ValidationError as error:
            messagebox.showerror("Gagal", str(error))
            return None

    def edit_selected_task(self):
        task = self._selected_task()
        if task:
            self.open_form(task)

    def view_selected_task(self):
        task = self._selected_task()
        if task:
            self.view_task(task)

    def view_task(self, task):
        messagebox.showinfo(
            "Detail Tugas",
            f"ID: {task.task_id}\nJudul: {task.title}\n"
            f"Deskripsi: {task.description or '-'}\n"
            f"Kategori: {task.subject}\n"
            f"Tenggat waktu: {task.deadline_text()} ({task.time_left_text()})\n"
            f"Prioritas: {PRIORITY_LABELS[task.priority]}\n"
            f"Status: {STATUS_LABELS[task.status]}\n"
            f"Dibuat: {task.created.strftime('%Y-%m-%d %H:%M')}",
        )

    def complete_selected_task(self):
        task = self._selected_task()
        if not task:
            return
        if task.is_completed():
            messagebox.showinfo("Info", "Tugas ini sudah ditandai selesai.")
            return
        self._complete_task(task, f"Tugas '{task.title}' ditandai selesai.")

    def _complete_task(self, task, message):
        try:
            self.manager.complete_task(task.task_id)
        except KeyError as error:
            messagebox.showerror("Gagal", f"Tidak bisa menyelesaikan tugas: {error}")
            return
        messagebox.showinfo("Berhasil", message)

    def delete_selected_task(self):
        task = self._selected_task()
        if not task or not messagebox.askyesno("Konfirmasi", f"Hapus tugas '{task.title}'?"):
            return
        try:
            self.manager.delete_task(task.task_id)
        except KeyError as error:
            messagebox.showerror("Gagal", f"Tidak bisa menghapus tugas: {error}")
            return
        messagebox.showinfo("Berhasil", "Tugas berhasil dihapus.")

    # ---------- refresh tiap halaman ----------
    def refresh_all(self):
        for page_name in self.pages:
            self._refresh_page(page_name)

    def _refresh_page(self, page_name):
        {
            "dashboard": self._refresh_dashboard,
            "tasks": self._refresh_tasks,
            "focus": self._refresh_focus,
        }[page_name]()

    def _refresh_dashboard(self):
        stats = self.manager.statistics()
        stats["due_soon"] = len(self.manager.due_soon(hours=24))
        for key, label in self._stat_labels.items():
            label.config(text=str(stats[key]))

        self.upcoming_tree.delete(*self.upcoming_tree.get_children())
        for t in self.manager.upcoming(limit=5):
            self.upcoming_tree.insert("", "end", iid=str(t.task_id),
                                      values=(t.title, t.subject, t.deadline_text()))

    def _refresh_tasks(self):
        selected = self.task_tree.selection()
        selected_id = selected[0] if selected else None
        self.task_tree.delete(*self.task_tree.get_children())

        tasks = self.manager.sorted_by_deadline()
        for t in tasks:
            alert = t.alert_label(hours=self.reminder.soon_hours)
            alert_text = "Terlambat" if alert == "Overdue" else alert
            tag = ("done" if t.is_completed()
                   else "overdue" if alert == "Overdue"
                   else "soon" if alert in ("Hari ini", "Segera")
                   else f"p_{t.priority}")
            self.task_tree.insert(
                "", "end", iid=str(t.task_id), tags=(tag,),
                values=(t.title, t.subject, t.deadline_text(),
                        PRIORITY_LABELS[t.priority], STATUS_LABELS[t.status], alert_text),
            )
        self.task_count_label.config(text=f"{len(tasks)} tugas")
        if selected_id and self.task_tree.exists(selected_id):
            self.task_tree.selection_set(selected_id)

    def _refresh_focus(self):
        task = self._focus_current_task = self.manager.recommend_next()
        if task is None:
            self.focus_done_icon.pack(anchor="w", pady=(0, 4))
            self.focus_title_label.config(text="Semua tugas sudah selesai")
            self.focus_info_label.config(
                text="Tidak ada tugas yang perlu diselesaikan. Tambahkan tugas baru atau beristirahat dulu.")
            self.focus_priority_label.config(text="")
            self.focus_time_left_label.config(text="")
            self.focus_button.state(["disabled"])
            return

        self.focus_button.state(["!disabled"])
        self.focus_done_icon.pack_forget()
        self.focus_title_label.config(text=task.title)
        self.focus_info_label.config(
            text=f"Kategori      : {task.subject}\n"
                 f"Tenggat waktu: {task.deadline_text()}\n"
                 f"Deskripsi: {task.description or '-'}")
        self.focus_priority_label.config(text=f"Prioritas: {PRIORITY_LABELS[task.priority]}",
                                         fg=PRIORITY_COLORS[task.priority])
        self.focus_time_left_label.config(text=task.time_left_text())

    def complete_focus_task(self):
        task = self._focus_current_task and self.manager.find_by_id(self._focus_current_task.task_id)
        if task is None:
            messagebox.showinfo("Info", "Tidak ada tugas yang direkomendasikan.")
            return
        self._complete_task(task, f"Mantap! '{task.title}' selesai.")

    # ---------- pengingat otomatis ----------
    def run_reminder_check(self):
        overdue, soon = self.reminder.collect_new_alerts()
        if overdue or soon:
            messagebox.showwarning("Pengingat tenggat", ReminderManager.build_message(overdue, soon))

    def _reminder_tick(self):
        if self._closing:
            return
        try:
            self.run_reminder_check()
        except (OSError, ValueError, KeyError, tk.TclError) as error:
            messagebox.showerror("Pengingat", f"Pengecekan pengingat gagal: {error}")
        if not self._closing:
            self._reminder_after = self.after(self.CHECK_INTERVAL_MS, self._reminder_tick)
