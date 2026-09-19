# Doctor's Assistant Application

## 1. What This Application Does

This project is a chatbot for a medical clinic. A user can communicate with it in English and ask it to:

- Find doctors by name or specialty
- Check whether a doctor is available at a specific date and time
- List available appointment slots
- Book an appointment

The user does not need to know SQL or Python. The user sends a normal English message, and the application handles the database work.

## 2. Technologies Used

- **Python**: The programming language used for the application
- **Flask**: Provides the web API that receives user requests
- **OpenAI Responses API**: Understands the user's English and selects the correct operation
- **SQLite**: Stores doctor and appointment data
- **SQL**: Used by Python to read and update the SQLite database

## 3. Project Files

### `app.py`

This is the web application entry point. It creates a Flask API endpoint:

```text
POST /chat
```

It receives a request such as:

```json
{
  "message": "Find a cardiologist"
}
```

It sends the message to `interpret_message()` in `chatbot.py` and returns the assistant's answer.

It also creates or reuses a `conversation_id`. This ID allows the application to remember earlier messages during a conversation.

### `chatbot.py`

This file controls the conversation with the LLM. It contains:

- OpenAI client setup
- Instructions for the assistant
- Descriptions of the available tools
- Conversation history handling
- Logic for running tools selected by the LLM

The available tools are:

```text
find_doctors
check_availability
list_available_slots
find_appointments
book_appointment
```

The LLM chooses a tool based on the user's message and the tool descriptions.

### `tools.py`

This file contains the Python functions that communicate with SQLite.

#### `find_doctors()`

Searches the `doctors` table by doctor name or specialty.

```python
find_doctors(doctor_name=None, specialty=None)
```

It returns doctor records such as:

```python
[
    {
        "id": 1,
        "name": "Dr. Alice",
        "specialty": "Cardiology"
    }
]
```

#### `check_availability()`

Checks one exact doctor, date, and time.

```python
check_availability(doctor_name, date, time)
```

It returns whether the requested slot is available.

#### `list_available_slots()`

Returns all available slots for one doctor on one date.

```python
list_available_slots(doctor_name, date)
```

This is useful when the requested time is unavailable and the assistant needs to offer alternatives.

#### `find_appointments()`

Finds existing booked appointments for a patient. It can optionally filter the results by doctor or date.

```python
find_appointments(patient_name, doctor_name=None, date=None)
```

For example, when the user says:

```text
I am Lipsa. Check my appointment details with Dr. Bob.
```

the LLM selects `find_appointments` and Python searches the `appointments` table by patient name and doctor name. The result includes the doctor, specialty, patient name, date, time, and booking status.

#### `book_appointment()`

Books an available slot.

```python
book_appointment(doctor_name, patient_name, date, time)
```

It changes the slot status from `Available` to `Booked` and inserts a new record into the `appointments` table.

### `db_setup.py`

Creates and prepares the SQLite database. It creates tables such as:

- `doctors`
- `availability`
- `appointments`

It can also add sample doctors and appointment slots.

### `show_db.py`

Displays database contents. It is useful for checking doctors, availability, and booked appointments.

### `test.py`

Sends test requests to the Flask API.

### `clinic.db`

The SQLite database file. It stores the application's data.

### `docs/`

Contains reference documents, setup instructions, testing steps, diagrams, and this explanation.

## 4. How a User Request Works

Suppose the user sends:

```text
Is Dr. Alice available tomorrow at 10 AM?
```

### Step 1: The User Sends a Request

The user sends an HTTP request to:

```text
POST /chat
```

The request contains:

```json
{
  "message": "Is Dr. Alice available tomorrow at 10 AM?"
}
```

### Step 2: Flask Receives the Request

`app.py` reads the message and gets or creates a `conversation_id`.

Then it calls:

```python
interpret_message(user_message, conversation)
```

### Step 3: The Message Goes to the LLM

`chatbot.py` sends the following information to the OpenAI Responses API:

- The user's message
- Previous messages in the conversation
- Instructions for the assistant
- Descriptions of the available tools

### How the Chatbot Understands Natural Language

The chatbot understands natural language because the OpenAI language model has been trained to understand how words and sentences are used. The application sends the user's message to the model together with instructions and descriptions of the available tools.

The model does not search the database by itself. Instead, it performs these steps:

1. **Reads the meaning of the message**. It identifies what the user wants, even when the user does not use technical words.
2. **Finds important details**. It extracts information such as the doctor's name, specialty, date, time, and patient's name.
3. **Chooses the correct tool**. It compares the request with the tool descriptions and selects the operation that can answer it.
4. **Creates structured arguments**. It converts the information from the sentence into named values that Python can use.

For example, the user may say:

```text
Can I see a heart specialist tomorrow morning?
```

The model can understand that:

- `heart specialist` probably means the `Cardiology` specialty
- `tomorrow morning` refers to a future date and a time period
- the user wants to find a doctor or available appointment

It may select `find_doctors` and create:

```json
{
  "specialty": "Cardiology"
}
```

If the user says:

```text
Is Dr. Alice available tomorrow at 10 AM?
```

the model identifies the request as an availability question and creates:

```json
{
  "doctor_name": "Dr. Alice",
  "date": "2026-09-08",
  "time": "10:00"
}
```

The tool descriptions help the model choose correctly. For example, the description of `check_availability` says that it checks whether a doctor's exact date and time is available. The description of `book_appointment` says that it books an available appointment after confirmation.

The model also uses the previous conversation. If the user first says:

```text
I want an appointment with Dr. Alice tomorrow.
```

and then says:

```text
10 AM works for me. My name is John.
```

the second message can be understood using the first message and the same `conversation_id`. The model combines the information before selecting the booking operation.

The model's output is a structured function call, not a direct database query:

```json
{
  "name": "check_availability",
  "arguments": {
    "doctor_name": "Dr. Alice",
    "date": "2026-09-08",
    "time": "10:00"
  }
}
```

Python then receives this function call, finds the matching function in `TOOL_FUNCTIONS`, and executes it. This separation is important:

- The **LLM understands the user's language and chooses an operation**.
- **Python validates the tool name and runs the function**.
- The **database returns the real clinic data**.
- The **LLM turns the database result into a natural-language answer**.

### Step 4: The LLM Understands the English

The LLM identifies:

- Doctor: Dr. Alice
- Operation: Check availability
- Date: Tomorrow
- Time: 10 AM

It selects the tool:

```text
check_availability
```

It creates structured arguments similar to:

```json
{
  "doctor_name": "Dr. Alice",
  "date": "2026-09-08",
  "time": "10:00"
}
```

The exact date depends on the current date used by the application.

### Step 5: Python Runs the Selected Tool

`chatbot.py` maps the tool name to the Python function:

```python
TOOL_FUNCTIONS = {
    "find_doctors": find_doctors,
    "check_availability": check_availability,
    "list_available_slots": list_available_slots,
  "find_appointments": find_appointments,
    "book_appointment": book_appointment,
}
```

Then Python calls:

```python
check_availability(
    doctor_name="Dr. Alice",
    date="2026-09-08",
    time="10:00"
)
```

### Step 6: The Database Is Queried

`tools.py` sends an SQL query to SQLite. The query checks whether the requested doctor has an available slot at the requested date and time.

The database may return:

```json
{
  "available": true,
  "doctor_name": "Dr. Alice",
  "date": "2026-09-08",
  "time": "10:00",
  "status": "Available"
}
```

### Step 7: The Result Goes Back to the LLM

Python sends the database result back to the OpenAI Responses API as a tool result.

The LLM reads the result and prepares a human-friendly answer.

### Step 8: The User Receives the Answer

The answer may be:

```text
Yes, Dr. Alice is available on September 8 at 10:00.
```

Flask returns it as JSON:

```json
{
  "conversation_id": "some-id",
  "reply": "Yes, Dr. Alice is available on September 8 at 10:00."
}
```

## 5. How Different Requests Select Different Tools

The LLM uses the user's meaning and the tool descriptions to select an operation.

| User request | Selected tool |
|---|---|
| `Find a cardiologist` | `find_doctors` |
| `Is Dr. Alice free tomorrow at 10 AM?` | `check_availability` |
| `What times are available for Dr. Alice tomorrow?` | `list_available_slots` |
| `I am Lipsa. Check my appointment with Dr. Bob.` | `find_appointments` |
| `Book the 10 AM slot for John` | `book_appointment` |

The application does not use a large hardcoded `if/else` block to understand every English sentence. The LLM interprets the request, and Python executes only the matching registered function.

## 6. How Doctor Search Works

If a user asks:

```text
Do you have a heart specialist?
```

The LLM may understand that `heart specialist` means `Cardiology` and call:

```python
find_doctors(specialty="Cardiology")
```

If a user says:

```text
My ankle is swollen.
```

The assistant instructions guide the LLM to treat ankle, bone, joint, fracture, or swelling requests as an orthopedic request and call:

```python
find_doctors(specialty="Orthopedics")
```

The LLM does not directly read the database. The Python function reads the database and sends the result back to the LLM.

## 7. How Existing Appointment Details Are Checked

The application can also find an appointment that was already booked. This is different from checking whether a future slot is available:

- `check_availability` checks an open slot before booking.
- `find_appointments` reads the `appointments` table to find an existing booking.

For this request:

```text
I am Lipsa. Check the appointment details with Dr. Bob.
```

the LLM extracts:

```json
{
  "patient_name": "Lipsa",
  "doctor_name": "Dr. Bob"
}
```

It calls:

```python
find_appointments(
    patient_name="Lipsa",
    doctor_name="Dr. Bob"
)
```

`tools.py` joins the `appointments` and `doctors` tables. It matches the patient and doctor without being affected by capitalization, so `Lipsa` and `lipsa` are treated as the same name. The LLM then explains the returned appointment details in normal English.

## 8. How Booking Works

Booking normally happens over multiple messages.

### First Message

```text
I want an appointment with Dr. Alice tomorrow.
```

The assistant checks or asks for the exact time and the patient's name.

### Confirmation Message

```text
My name is John. I confirm 10 AM.
```

The same `conversation_id` is sent with the follow-up request, so the application can use the earlier conversation history.

The LLM then selects:

```text
book_appointment
```

Python calls:

```python
book_appointment(
    doctor_name="Dr. Alice",
    patient_name="John",
    date="2026-09-08",
    time="10:00"
)
```

The database performs two important actions:

1. Changes the availability status from `Available` to `Booked`
2. Inserts the booking into the `appointments` table

The assistant then returns a booking confirmation.

## 9. Complete Application Flow

```text
User
  |
  | English message
  v
Flask API in app.py
  |
  | Calls interpret_message()
  v
OpenAI Responses API
  |
  | Understands the request and selects a tool
  v
Python function in tools.py
  |
  | Executes SQL
  v
SQLite database in clinic.db
  |
  | Returns doctor or appointment data
  v
OpenAI Responses API
  |
  | Creates a natural-language answer
  v
Flask API
  |
  v
User receives JSON response
```

## 10. Important Separation of Responsibilities

Each part has a different responsibility:

- **User**: Sends a request in normal English
- **Flask**: Receives the request and returns the response
- **LLM**: Understands the request and selects a tool
- **Python tools**: Perform the actual database operations
- **SQLite**: Stores and returns the data

The LLM decides **what operation is needed**. Python performs the operation. SQLite stores the actual clinic data.

## 11. Detailed Code Flow of All Tools

All five tools follow the same general path:

```text
User sends an English request
  ↓
LLM understands the request and selects a tool
  ↓
chatbot.py finds the matching Python function
  ↓
tools.py reads or updates SQLite
  ↓
The result is sent back to the LLM
  ↓
The LLM creates the final response
```

The mapping in `chatbot.py` connects each tool name to its Python function:

```python
TOOL_FUNCTIONS = {
    "find_doctors": find_doctors,
    "check_availability": check_availability,
    "list_available_slots": list_available_slots,
    "find_appointments": find_appointments,
    "book_appointment": book_appointment,
}
```

### 11.1 `find_doctors`

**Purpose:** Find doctors by name or specialty.

```python
find_doctors(doctor_name=None, specialty=None)
```

**Code flow:**

1. The LLM identifies a doctor-search request, such as `Find a dermatologist`.
2. It calls `find_doctors` with a doctor name, specialty, or both.
3. Common specialty words are normalized. For example, `dermatologist` becomes `Dermatology` and `orthopedic` becomes `Orthopedics`.
4. The function builds a SQL query for the `doctors` table.
5. The query searches by name and/or specialty, ignoring capitalization.
6. The results are sorted by doctor name and converted into dictionaries.
7. The results are returned to the LLM, which explains them to the user.

Example query:

```sql
SELECT DISTINCT id, name, specialty
FROM doctors
WHERE LOWER(specialty) LIKE LOWER(?)
ORDER BY name
```

### 11.2 `check_availability`

**Purpose:** Check one exact appointment slot.

```python
check_availability(doctor_name, date, time)
```

**Code flow:**

1. The LLM extracts the doctor name, date, and exact time.
2. The function joins the `availability` and `doctors` tables.
3. It searches for the exact doctor, date, and time.
4. It only accepts a slot whose status is `Available`.
5. If a matching row exists, the function returns `available: true` with the slot details.
6. If no row exists, it returns `available: false` with the requested details.
7. The LLM turns the result into a natural-language answer.

### 11.3 `list_available_slots`

**Purpose:** List every available slot for one doctor on a date.

```python
list_available_slots(doctor_name, date)
```

**Code flow:**

1. The LLM calls this tool when the user asks for available times or when an exact requested time is unavailable.
2. The function joins `availability` with `doctors`.
3. It searches for the selected doctor and date.
4. It filters the records to status `Available`.
5. It sorts the results by time.
6. It returns a list of available slots as dictionaries.
7. The LLM offers those times to the user.

### 11.4 `find_appointments`

**Purpose:** Find existing booked appointments for a patient.

```python
find_appointments(patient_name, doctor_name=None, date=None)
```

**Code flow:**

1. The LLM identifies a request about an existing appointment.
2. It extracts the patient's name and optional doctor name or date.
3. The function starts by matching the patient name and status `Booked`.
4. If a doctor was provided, it adds a doctor-name filter.
5. If a date was provided, it adds a date filter.
6. The function joins `appointments` with `doctors` to include the doctor's name and specialty.
7. Results are ordered by date and time and converted into dictionaries.
8. The LLM explains the appointment details to the user.

Example:

```python
find_appointments(
    patient_name="Lipsa",
    doctor_name="Dr. Bob"
)
```

### 11.5 `book_appointment`

**Purpose:** Book an available appointment.

```python
book_appointment(doctor_name, patient_name, date, time)
```

**Code flow:**

1. The LLM calls this tool only after the patient confirms the exact appointment.
2. The function first checks whether the doctor exists.
3. It updates the matching available slot from `Available` to `Booked`.
4. If the slot was already booked or does not exist, the function returns an error and does not create an appointment.
5. If the update succeeds, it inserts a new row into the `appointments` table.
6. The database transaction is committed when the connection closes successfully.
7. A booking confirmation is returned to the LLM.
8. The LLM sends the confirmation to the user.

Database operations:

```sql
UPDATE availability
SET status = 'Booked'
```

```sql
INSERT INTO appointments
    (doctor_id, patient_name, date, time, status)
VALUES
    (?, ?, ?, ?, 'Booked')
```
