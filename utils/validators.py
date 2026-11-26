"""Validasi input pengguna menggunakan ValueError."""
import re
from datetime import date, datetime

from models.task import PRIORITIES

ValidationError = ValueError
PRIORITY_MAP = {"Tinggi": "High", "Sedang": "Medium", "Rendah": "Low"}


def validate_title(title):
    title = (title or "").strip()
    if not title:
        raise ValidationError("Judul tugas tidak boleh kosong.")
    if len(title) > 100:
        raise ValidationError("Judul tugas maksimal 100 karakter.")
    return title


def validate_description(description):
    return (description or "").strip()


def validate_subject(subject):
    return (subject or "").strip() or "Umum"


def validate_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = value.strip() if isinstance(value, str) else ""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise ValidationError("Format tanggal harus YYYY-MM-DD, contoh: 2026-11-15.")
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Tanggal tidak valid (cek bulan dan harinya).")


def validate_time(value):
    text = (value or "").strip()
    if not re.fullmatch(r"\d{2}:\d{2}", text):
        raise ValidationError("Format jam harus HH:MM (24 jam), contoh: 23:59.")
    try:
        return datetime.strptime(text, "%H:%M").time()
    except ValueError:
        raise ValidationError("Jam tidak valid (00:00 - 23:59).")


def validate_deadline(date_text, time_text):
    return datetime.combine(validate_date(date_text), validate_time(time_text))


def validate_priority(priority):
    value = (priority or "").strip().capitalize()
    value = PRIORITY_MAP.get(value, value)
    if value not in PRIORITIES:
        raise ValidationError("Prioritas harus Tinggi, Sedang, atau Rendah.")
    return value


def validate_task_id(task_id):
    try:
        num = int(str(task_id).strip())
    except (TypeError, ValueError):
        raise ValidationError("ID tugas harus berupa angka.")
    if num <= 0:
        raise ValidationError("ID tugas harus lebih dari 0.")
    return num


def validate_task_form(title, description, subject, date_text, time_text, priority):
    """Validasi seluruh isi form; mengembalikan dict bersih."""
    return {
        "title": validate_title(title),
        "description": validate_description(description),
        "subject": validate_subject(subject),
        "deadline": validate_deadline(date_text, time_text),
        "priority": validate_priority(priority),
    }
