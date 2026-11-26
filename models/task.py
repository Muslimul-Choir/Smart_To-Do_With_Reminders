    """Model data: BaseTask (induk) dan Task (turunan)."""
from datetime import datetime, timedelta

PRIORITIES = ("High", "Medium", "Low")
STATUSES = ("Pending", "Completed")
PRIORITY_RANK = {"High": 0, "Medium": 1, "Low": 2}  # makin kecil makin penting
DATETIME_FORMAT = "%Y-%m-%d %H:%M"


class BaseTask:
    """Class induk: menyimpan id, judul, dan deskripsi tugas."""

    def __init__(self, task_id, title, description=""):
        self._task_id = task_id
        self._title = title
        self._description = description

    @property
    def task_id(self):
        return self._task_id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        value = (value or "").strip()
        if not value:
            raise ValueError("Judul tugas tidak boleh kosong.")
        self._title = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = (value or "").strip()

    def describe(self):
        return f"#{self._task_id} {self._title}"

    def __str__(self):
        return self.describe()