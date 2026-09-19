"""Database tools exposed to the Doctor's Assistant model."""

import os
import sqlite3


DB_PATH = os.path.join(os.path.dirname(__file__), "clinic.db")


def _connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def find_doctors(doctor_name=None, specialty=None):
    """Find doctors by a case-insensitive name and/or specialty."""
    clauses = []
    values = []
    specialty_aliases = {
        "dermatologist": "Dermatology",
        "orthopedic": "Orthopedics",
    }
    if specialty:
        specialty = specialty_aliases.get(specialty.strip().lower(), specialty)
    if doctor_name:
        clauses.append("LOWER(name) LIKE LOWER(?)")
        values.append(f"%{doctor_name}%")
    if specialty:
        clauses.append("LOWER(specialty) LIKE LOWER(?)")
        values.append(f"%{specialty}%")
    query = "SELECT DISTINCT id, name, specialty FROM doctors"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY name"
    with _connect() as connection:
        return [dict(row) for row in connection.execute(query, values).fetchall()]


def check_availability(doctor_name, date, time):
    """Return an exact available slot, or an explanatory result."""
    with _connect() as connection:
        row = connection.execute(
            """SELECT DISTINCT d.name AS doctor_name, d.specialty, a.date, a.time, a.status
               FROM availability a JOIN doctors d ON a.doctor_id = d.id
               WHERE LOWER(d.name) = LOWER(?) AND a.date = ? AND a.time = ?
                 AND a.status = 'Available'""",
            (doctor_name, date, time),
        ).fetchone()
    if not row:
        return {"available": False, "doctor_name": doctor_name, "date": date, "time": time}
    result = dict(row)
    result["available"] = True
    return result


def list_available_slots(doctor_name, date):
    """Return every available slot for a doctor on a date."""
    with _connect() as connection:
        rows = connection.execute(
            """SELECT DISTINCT d.name AS doctor_name, d.specialty, a.date, a.time
               FROM availability a JOIN doctors d ON a.doctor_id = d.id
               WHERE LOWER(d.name) = LOWER(?) AND a.date = ? AND a.status = 'Available'
               ORDER BY a.time""",
            (doctor_name, date),
        ).fetchall()
    return [dict(row) for row in rows]


def find_appointments(patient_name, doctor_name=None, date=None):
    """Find booked appointments for a patient, optionally filtered by doctor or date."""
    clauses = ["LOWER(a.patient_name) = LOWER(?)", "a.status = 'Booked'"]
    values = [patient_name]
    if doctor_name:
        clauses.append("LOWER(d.name) = LOWER(?)")
        values.append(doctor_name)
    if date:
        clauses.append("a.date = ?")
        values.append(date)
    query = """SELECT a.id, d.name AS doctor_name, d.specialty,
                      a.patient_name, a.date, a.time, a.status
               FROM appointments a
               JOIN doctors d ON a.doctor_id = d.id
               WHERE """ + " AND ".join(clauses) + " ORDER BY a.date, a.time"
    with _connect() as connection:
        return [dict(row) for row in connection.execute(query, values).fetchall()]


def book_appointment(doctor_name, patient_name, date, time):
    """Atomically book an available slot and return its confirmation."""
    with _connect() as connection:
        doctor = connection.execute(
            "SELECT id, name FROM doctors WHERE LOWER(name) = LOWER(?)", (doctor_name,)
        ).fetchone()
        if not doctor:
            return {"booked": False, "error": f"Doctor {doctor_name} was not found."}
        cursor = connection.execute(
            """UPDATE availability SET status = 'Booked'
               WHERE id = (SELECT id FROM availability
                           WHERE doctor_id = ? AND date = ? AND time = ?
                             AND status = 'Available' ORDER BY id LIMIT 1)""",
            (doctor["id"], date, time),
        )
        if cursor.rowcount != 1:
            return {"booked": False, "error": "That appointment slot is no longer available."}
        connection.execute(
            """INSERT INTO appointments (doctor_id, patient_name, date, time, status)
               VALUES (?, ?, ?, ?, 'Booked')""",
            (doctor["id"], patient_name, date, time),
        )
    return {"booked": True, "doctor_name": doctor["name"], "patient_name": patient_name,
            "date": date, "time": time}