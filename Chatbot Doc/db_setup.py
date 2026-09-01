"""Database initialization script for the clinic application.

Creates the necessary SQLite tables and seeds minimal sample data.
"""

import sqlite3


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

    # Seed sample doctors for development/testing purposes
    cursor.execute("INSERT INTO doctors (name, specialty) VALUES ('Dr. X', 'Orthopedic')")
    cursor.execute("INSERT INTO doctors (name, specialty) VALUES ('Dr. Y', 'Dermatologist')")
    # Seed sample availability slots tied to the seeded doctors
    cursor.execute("INSERT INTO availability (doctor_id, date, time, status) VALUES (1, '2026-09-01', '10:00', 'Available')")
    cursor.execute("INSERT INTO availability (doctor_id, date, time, status) VALUES (2, '2026-09-01', '11:00', 'Available')")

    # Commit changes and close the DB connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Initialize the database when the script is run directly
    init_db()
