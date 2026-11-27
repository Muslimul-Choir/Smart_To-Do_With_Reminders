"""TaskManager: kelola daftar tugas (CRUD, cari, urutkan, statistik, Focus Mode, JSON)."""
import json
import os
from datetime import datetime, timedelta

from models.task import Task, PRIORITY_RANK


class TaskManager:
    def __init__(self):
        self._tasks = []
        self._next_id = 1
        self._listeners = []

    def add_listener(self, callback):
        self._listeners.append(callback)

    def _notify(self):
        for callback in self._listeners:
            callback()

    # ---------- pencarian biner rekursif ----------
    @staticmethod
    def _binary_search(tasks, task_id, low, high):
        """Cari tugas berdasarkan ID secara rekursif (list selalu urut ID)."""
        if low > high:
            return None
        mid = (low + high) // 2
        mid_task = tasks[mid]
        if mid_task.task_id == task_id:
            return mid_task
        if mid_task.task_id < task_id:
            return TaskManager._binary_search(tasks, task_id, mid + 1, high)
        return TaskManager._binary_search(tasks, task_id, low, mid - 1)

    def find_by_id(self, task_id):
        return self._binary_search(self._tasks, task_id, 0, len(self._tasks) - 1)

    # ---------- CRUD ----------
    @property
    def tasks(self):
        return list(self._tasks)

    def add_task(self, title, description, subject, deadline, priority):
        task = Task(self._next_id, title, description, subject, deadline, priority)
        self._next_id += 1
        self._tasks.append(task)
        self._notify()
        return task

    def _get_or_raise(self, task_id):
        task = self.find_by_id(task_id)
        if task is None:
            raise KeyError(f"Tugas dengan ID {task_id} tidak ditemukan.")
        return task

    def edit_task(self, task_id, title, description, subject, deadline, priority):
        task = self._get_or_raise(task_id)
        task.title = title
        task.description = description
        task.subject = subject
        task.deadline = deadline
        task.priority = priority
        self._notify()
        return task

    def delete_task(self, task_id):
        self._tasks.remove(self._get_or_raise(task_id))
        self._notify()

    def complete_task(self, task_id):
        task = self._get_or_raise(task_id)
        task.complete()
        self._notify()
        return task

    # ---------- urutkan, cari, dan filter ----------
    def sorted_by_deadline(self, tasks=None):
        items = self._tasks if tasks is None else tasks
        return sorted(items, key=lambda t: (t.deadline, PRIORITY_RANK[t.priority]))

    def search(self, keyword="", status="All", priority="All"):
        kw = (keyword or "").strip().lower()
        result = []
        for t in self._tasks:
            if status != "All" and t.status != status:
                continue
            if priority != "All" and t.priority != priority:
                continue
            if kw and kw not in t.title.lower() and kw not in t.subject.lower() and kw not in t.description.lower():
                continue
            result.append(t)
        return self.sorted_by_deadline(result)

    # ---------- deteksi deadline ----------
    def overdue_tasks(self, now=None):
        now = now or datetime.now()
        return self.sorted_by_deadline([t for t in self._tasks if t.is_overdue(now)])

    def due_soon(self, now=None, hours=24):
        now = now or datetime.now()
        return self.sorted_by_deadline([t for t in self._tasks if t.is_due_soon(now, hours)])

    def upcoming(self, now=None, limit=5):
        now = now or datetime.now()
        items = [t for t in self._tasks if not t.is_completed() and t.deadline >= now]
        return self.sorted_by_deadline(items)[:limit]

    # ---------- statistik ----------
    def statistics(self, now=None):
        now = now or datetime.now()
        pending = [t for t in self._tasks if not t.is_completed()]
        return {
            "total": len(self._tasks),
            "completed": len(self._tasks) - len(pending),
            "pending": len(pending),
            "overdue": sum(1 for t in pending if t.is_overdue(now)),
            "due_today": sum(1 for t in pending if t.is_due_today(now)),
            "priority": {p: sum(1 for t in pending if t.priority == p) for p in PRIORITY_RANK},
        }

    # ---------- Focus Mode ----------
    def recommend_next(self):
        """Pilih 1 tugas belum selesai dengan tenggat terdekat & prioritas tertinggi."""
        pending = [t for t in self._tasks if not t.is_completed()]
        if not pending:
            return None
        return min(pending, key=lambda t: (t.deadline, PRIORITY_RANK[t.priority]))

    # ---------- simpan & muat JSON ----------
    def save_json(self, path):
        data = {
            "next_id": self._next_id,
            "tasks": [t.to_dict() for t in self._tasks],
        }
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        tasks = sorted((Task.from_dict(d) for d in data["tasks"]), key=lambda t: t.task_id)
        self._tasks = tasks
        last_id = tasks[-1].task_id + 1 if tasks else 1
        self._next_id = max(int(data.get("next_id", 1)), last_id)
        self._notify()

    def load_sample_data(self):
        now = datetime.now().replace(second=0, microsecond=0)
        samples = [
            ("Kirim proposal", "Periksa lampiran sebelum dikirim", "Pekerjaan", now + timedelta(hours=5), "High"),
            ("Belanja kebutuhan", "Beli kebutuhan mingguan", "Pribadi", now + timedelta(days=1), "Medium"),
            ("Periksa kendaraan", "Cek oli dan tekanan ban", "Rumah", now + timedelta(days=2), "Low"),
            ("Bayar tagihan internet", "Jatuh tempo pembayaran bulanan", "Keuangan", now + timedelta(days=3), "Medium"),
            ("Rencanakan akhir pekan", "Tentukan kegiatan dan jadwal", "Pribadi", now + timedelta(days=6), "Low"),
        ]
        for args in samples:
            self.add_task(*args)
