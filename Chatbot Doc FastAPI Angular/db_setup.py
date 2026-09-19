"""Database initialization script for the clinic application.

Creates the necessary SQLite tables and seeds minimal sample data.
"""

import sqlite3
from datetime import date, timedelta


def init_db():
    # Connect to (or create) the SQLite database file named clinic.db
    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()

    # Create a table to store doctor records (id, name, specialty)
    cursor.execute("""CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, specialty TEXT)""")

    # Create a table to store availability slots for doctors
    cursor.execute("""CREATE TABLE IF NOT EXISTS availability (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER, date TEXT, time TEXT, status TEXT)""")

    # Create a table to store booked appointments
    cursor.execute("""CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER, patient_name TEXT, date TEXT, time TEXT, status TEXT)""")

    # Consolidate the original duplicate sample doctors before seeding the new names.
    legacy_doctors = [("Dr. X", "Dr. Alice"), ("Dr. Y", "Dr. Bob")]
    for old_name, new_name in legacy_doctors:
        cursor.execute("SELECT id FROM doctors WHERE name=? ORDER BY id", (old_name,))
        old_ids = [row[0] for row in cursor.fetchall()]
        if old_ids:
            primary_id = old_ids[0]
            cursor.execute("UPDATE doctors SET name=? WHERE id=?", (new_name, primary_id))
            for duplicate_id in old_ids[1:]:
                cursor.execute("UPDATE availability SET doctor_id=? WHERE doctor_id=?", (primary_id, duplicate_id))
                cursor.execute("UPDATE appointments SET doctor_id=? WHERE doctor_id=?", (primary_id, duplicate_id))
                cursor.execute("DELETE FROM doctors WHERE id=?", (duplicate_id,))

    # Keep specialty names consistent with the values used by the assistant.
    cursor.execute("UPDATE doctors SET specialty='Orthopedics' WHERE specialty='Orthopedic'")
    cursor.execute("UPDATE doctors SET specialty='Dermatology' WHERE specialty='Dermatologist'")

    # Seed sample doctors and slots only when they are not already configured.
    doctors = [("Dr. Alice", "Orthopedics"), ("Dr. Bob", "Dermatology")]
    for name, specialty in doctors:
        cursor.execute("SELECT id FROM doctors WHERE name=? AND specialty=?", (name, specialty))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO doctors (name, specialty) VALUES (?, ?)", (name, specialty))

    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    for name, time in (("Dr. Alice", "10:00"), ("Dr. Alice", "11:00"), ("Dr. Bob", "11:00")):
        cursor.execute("SELECT id FROM doctors WHERE name=?", (name,))
        doctor_id = cursor.fetchone()[0]
        cursor.execute(
            "SELECT 1 FROM availability WHERE doctor_id=? AND date=? AND time=?",
            (doctor_id, tomorrow, time),
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO availability (doctor_id, date, time, status) VALUES (?, ?, ?, 'Available')",
                (doctor_id, tomorrow, time),
            )

    # Commit changes and close the DB connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Initialize the database when the script is run directly
    init_db()
