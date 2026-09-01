"""Utility functions for interacting with the clinic SQLite database.

Exposes functions to check availability and book appointments.
"""

import sqlite3

# Open a persistent connection to the same database used by db_setup.py.
# `check_same_thread=False` allows this connection to be shared across threads
# (useful for simple Flask development servers). In production, use a proper DB.
conn = sqlite3.connect("clinic.db", check_same_thread=False)
cursor = conn.cursor()


def check_availability(doctor_name, date, time):
    """Return the first available slot for the given doctor/date/time.

    Args:
        doctor_name (str): The doctor's name to search for.
        date (str): Date string in YYYY-MM-DD format.
        time (str): Time string, e.g. '10:00'.

    Returns:
        tuple or None: The row from the availability table if available, otherwise None.
    """
    # Execute a join between availability and doctors to match by doctor name
    cursor.execute("""SELECT * FROM availability a
                      JOIN doctors d ON a.doctor_id=d.id
                      WHERE d.name=? AND a.date=? AND a.time=? AND a.status='Available'""",
                   (doctor_name, date, time))
    # Return the first matching row or None if there is no available slot
    return cursor.fetchone()


def book_appointment(doctor_name, patient_name, date, time):
    """Book an appointment by updating availability and inserting an appointment row.

    Args:
        doctor_name (str): The doctor's name.
        patient_name (str): The patient's full name.
        date (str): Appointment date.
        time (str): Appointment time.

    Returns:
        str: Confirmation message describing the booked appointment.
    """
    # Look up the doctor's numeric id from the doctors table
    cursor.execute("SELECT id FROM doctors WHERE name=?", (doctor_name,))
    doctor_id = cursor.fetchone()[0]
    # Mark the matched availability slot as 'Booked'
    cursor.execute("""UPDATE availability SET status='Booked'
                      WHERE doctor_id=? AND date=? AND time=?""",
                   (doctor_id, date, time))
    # Insert a record into the appointments table to persist the booking
    cursor.execute("""INSERT INTO appointments (doctor_id, patient_name, date, time, status)
                      VALUES (?, ?, ?, ?, 'Booked')""",
                   (doctor_id, patient_name, date, time))
    # Commit the transaction so changes are saved to disk
    conn.commit()
    # Return a user-friendly confirmation string
    return f"Appointment booked with {doctor_name} for {patient_name} on {date} at {time}"
