"""ReminderManager: memeriksa deadline & mencegah popup yang sama berulang."""
from datetime import datetime


class ReminderManager:
    def __init__(self, task_manager, soon_hours=24):
        self._manager = task_manager
        self._soon_hours = soon_hours
        self._notified = set()  # simpan (task_id, jenis, deadline) yang sudah muncul

    @property
    def soon_hours(self):
        return self._soon_hours

    def get_overdue(self, now=None):
        return self._manager.overdue_tasks(now)

    def get_due_soon(self, now=None):
        return self._manager.due_soon(now, self._soon_hours)

    def collect_new_alerts(self, now=None):
        """Kembalikan (overdue_baru, soon_baru) yang belum pernah ditampilkan."""
        now = now or datetime.now()
        return (
            self._filter_new(self.get_overdue(now), "overdue"),
            self._filter_new(self.get_due_soon(now), "soon"),
        )

    def _filter_new(self, tasks, alert_type):
        result = []
        for t in tasks:
            key = (t.task_id, alert_type, t.deadline)
            if key not in self._notified:
                self._notified.add(key)
                result.append(t)
        return result

    def reset(self):
        self._notified.clear()

    @staticmethod
    def build_message(overdue_tasks, soon_tasks, now=None):
        now = now or datetime.now()
        lines = []
        if overdue_tasks:
            lines.append("TUGAS TERLAMBAT:")
            for t in overdue_tasks:
                lines.append(f"  - {t.title} ({t.subject}) - {t.time_left_text(now)}")
        if soon_tasks:
            if lines:
                lines.append("")
            lines.append("TENGGAT WAKTU MENDEKAT:")
            for t in soon_tasks:
                lines.append(f"  - {t.title} ({t.subject}) - {t.deadline_text()} ({t.time_left_text(now)})")
        return "\n".join(lines)
