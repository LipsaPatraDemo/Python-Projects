# Build the Doctor's Assistant From Scratch

This guide explains how to build and run this project from an empty folder on Windows. The finished application is a Flask API that lets a user ask questions in normal English, uses the OpenAI Responses API to choose database tools, and stores clinic data in SQLite.

## 1. What you will build

The application will support these conversations:

- Find a doctor by name or specialty.
- Check a doctor's exact availability.
- List all available slots on a date.
- Find an existing appointment by patient name.
- Book an available slot after the patient confirms the details.

The request flow is:

```text
Client -> Flask /chat -> OpenAI model -> Python database tool -> SQLite
                                      <- tool result <-
                         final assistant response -> Flask -> Client
```

The model does not access SQLite directly. It asks Python to run one of the functions in `tools.py`, and Python returns the result to the model.

## 2. Prerequisites

Install the following before starting:

1. Python 3.10 or newer from [python.org](https://www.python.org/downloads/).
2. VS Code with the Python extension.
3. An OpenAI API key.
4. PowerShell on Windows.

During Python installation, enable **Add Python to PATH**. Verify the installation:

```powershell
python --version
pip --version
```

## 3. Create the project folder

Create a folder and open it in VS Code:

```powershell
mkdir "Chatbot Doc"
cd "Chatbot Doc"
code .
```

Create these files in the project root:

```text
Chatbot Doc/
  app.py
  chatbot.py
  db_setup.py
  show_db.py
  test.py
  tools.py
  .env
  .gitignore
```

The `clinic.db` file is generated later. The `docs/` folder is optional and contains project documentation.

## 4. Create a virtual environment

A virtual environment keeps this project's packages separate from other Python projects.

From the project root, run:

```powershell
python -m venv venv
\.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, allow it only for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` at the beginning of the terminal prompt. Confirm that the active Python belongs to the environment:

```powershell
where.exe python
```

## 5. Install the packages

Install the packages used by the application:

```powershell
python -m pip install --upgrade pip
pip install flask openai python-dotenv requests
```

SQLite is included with Python, so no separate database server or SQLite installation is needed.

Save the installed dependencies for repeatable setup:

```powershell
pip freeze > requirements.txt
```

On another computer, install them with:

```powershell
pip install -r requirements.txt
```

## 6. Configure the API key

Create a file named `.env` in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1
```

Replace the placeholder with your real key. Do not commit this file or share the key.

Create `.gitignore` so secrets, generated files, and the virtual environment are not committed:

```gitignore
venv/
__pycache__/
*.pyc
.env
```

`chatbot.py` uses `python-dotenv` to load `.env`. If the key is missing, the application starts but a chat request raises `OPENAI_API_KEY is not configured.`

## 7. Create the database initializer

Create `db_setup.py`. Its `init_db()` function should:

1. Open or create `clinic.db`.
2. Create `doctors`, `availability`, and `appointments` tables with `CREATE TABLE IF NOT EXISTS`.
3. Insert sample doctors such as Dr. Alice in Orthopedics and Dr. Bob in Dermatology.
4. Add tomorrow's sample availability.
5. Commit and close the connection.

Use the completed implementation in this repository's [db_setup.py](../db_setup.py). Run it from the project root:

```powershell
python db_setup.py
```

A successful run creates `clinic.db`. It is safe to run the initializer again because it checks for existing doctors and slots before inserting them.

The tables are:

| Table | Purpose |
| --- | --- |
| `doctors` | Doctor name and specialty |
| `availability` | Doctor, date, time, and slot status |
| `appointments` | Patient bookings and their status |

Dates are stored as `YYYY-MM-DD` text and times as `HH:MM` text. Keeping one format makes sorting and exact comparisons predictable.

## 8. Create the database tools

Create `tools.py`. This module is the boundary between the chatbot and SQLite.

Implement these functions:

```python
find_doctors(doctor_name=None, specialty=None)
check_availability(doctor_name, date, time)
list_available_slots(doctor_name, date)
find_appointments(patient_name, doctor_name=None, date=None)
book_appointment(doctor_name, patient_name, date, time)
```

Use parameterized SQL values, for example:

```python
connection.execute(
    "SELECT id, name, specialty FROM doctors WHERE LOWER(name) LIKE LOWER(?)",
    (f"%{doctor_name}%",),
)
```

Never build SQL by concatenating user input. The booking function must update only a slot whose status is still `Available`, then insert the appointment. This prevents a slot that has already been booked from being booked again.

Use the completed implementation in [tools.py](../tools.py).

## 9. Create the chatbot layer

Create `chatbot.py` in this order:

### 9.1 Load configuration

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
```

The actual project makes the client `None` when no key is configured so the error can be reported clearly when a request is made.

### 9.2 Write assistant instructions

Tell the model that it is a clinic assistant and that it must:

- Use tools for doctor, specialty, availability, appointment, and booking questions.
- Never invent doctors or time slots.
- Use `YYYY-MM-DD` and `HH:MM` for tool arguments.
- Ask for the patient's name and confirmation before booking.
- Offer other available slots when the requested slot is unavailable.
- Avoid medical diagnosis.

Include the current date in the instructions so that words such as “tomorrow” can be converted correctly.

### 9.3 Describe the tools to the model

Create one function-tool schema for each Python function. Each schema needs:

- `type: "function"`
- the function `name`
- a clear `description`
- a JSON Schema `parameters` object
- required fields for arguments that cannot be omitted

The tool names and Python functions must match exactly:

```text
find_doctors
check_availability
list_available_slots
find_appointments
book_appointment
```

Register the Python functions in a dictionary so the model's selected function can be executed safely:

```python
TOOL_FUNCTIONS = {
    "find_doctors": find_doctors,
    "check_availability": check_availability,
    "list_available_slots": list_available_slots,
    "find_appointments": find_appointments,
    "book_appointment": book_appointment,
}
```

### 9.4 Implement the tool-calling loop

The `interpret_message()` function should:

1. Append the user's message to the conversation history.
2. Call `client.responses.create()` with the model, instructions, history, and tool schemas.
3. Append the model output to the history.
4. Find any `function_call` items.
5. Decode each call's JSON arguments and execute the matching Python function.
6. Append each result as a `function_call_output`.
7. Call the model again until it returns final text with no tool calls.

Use the completed implementation in [chatbot.py](../chatbot.py). This loop is the central connection between natural-language requests and deterministic database operations.

## 10. Create the Flask API

Create `app.py`:

```python
from flask import Flask, request, jsonify
from uuid import uuid4
from chatbot import interpret_message

app = Flask(__name__)
conversations = {}


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = payload.get("message")
    if not user_message:
        return jsonify({"error": "The 'message' field is required."}), 400

    conversation_id = payload.get("conversation_id") or str(uuid4())
    conversation = conversations.setdefault(conversation_id, [])
    reply = interpret_message(user_message, conversation)
    return jsonify({"conversation_id": conversation_id, "reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
```

The `conversation_id` is important. The first request creates one, and later requests include it so the assistant remembers the doctor, date, time, and patient name from earlier messages. This in-memory history is suitable for learning and local development; a production system should store conversations in a durable store.

## 11. Create database inspection and test scripts

Create `show_db.py` to print table names, columns, and rows. Use the completed [show_db.py](../show_db.py) as the reference implementation.

Create `test.py`:

```python
import requests

response = requests.post(
    "http://127.0.0.1:5000/chat",
    json={"message": "Find doctors who treat bone or joint problems"},
)
print(response.status_code)
print(response.json())
```

## 12. Start and verify the application

Use two PowerShell terminals. Follow the detailed startup instructions in the **Step-by-step chatbot test** section below to start Flask in Terminal 1 and send requests from Terminal 2.

You can also call the endpoint directly:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/chat `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Is Dr. Alice available tomorrow at 10 AM?"}'
```

The response has this shape:

```json
{
  "conversation_id": "generated-id",
  "reply": "...assistant response..."
}
```

### Step-by-step chatbot test

Before running the chatbot tests, start the Flask server and prepare a second terminal for requests.

1. **Open Terminal 1 and start the Flask server.** In VS Code, select **Terminal > New Terminal**, then run:

  ```powershell
  .\venv\Scripts\Activate.ps1
  python db_setup.py
  python app.py
  ```

  Keep this terminal open. When Flask starts successfully, you should see a message similar to:

  ```text
  Running on http://127.0.0.1:5000
  ```

2. **Open Terminal 2 for chatbot requests.** Select **Terminal > New Terminal** again. Move to the project folder and activate the same virtual environment:

  ```powershell
  cd "C:\path\to\Chatbot Doc"
  .\venv\Scripts\Activate.ps1
  ```

3. **Use the chatbot endpoint.** The URL is:

  ```text
  http://127.0.0.1:5000/chat
  ```

  This is a `POST` API endpoint, so do not test it by opening the URL as a normal browser page. Send a JSON request from Terminal 2 using `Invoke-RestMethod`, `python test.py`, Postman, or another API client. The first command below confirms that the URL and chatbot are working.

Follow these steps after the Flask server is running:

1. **Check that the server is reachable.** In the second PowerShell terminal, run:

   ```powershell
   Invoke-RestMethod -Uri http://127.0.0.1:5000/chat `
     -Method Post `
     -ContentType "application/json" `
     -Body '{"message":"Hello"}'
   ```

   You should receive JSON containing a `conversation_id` and a friendly `reply`.

2. **Test doctor search.** Send a question about a specialty:

   ```powershell
   Invoke-RestMethod -Uri http://127.0.0.1:5000/chat `
     -Method Post `
     -ContentType "application/json" `
     -Body '{"message":"Find doctors for skin problems"}'
   ```

   The assistant should use `find_doctors` and mention Dr. Bob or the Dermatology specialty. It should not invent a doctor that is not in the database.

3. **Test exact availability.** Use the date printed by `db_setup.py` or calculate tomorrow's date:

   ```powershell
   $tomorrow = (Get-Date).AddDays(1).ToString("yyyy-MM-dd")
   Invoke-RestMethod -Uri http://127.0.0.1:5000/chat `
     -Method Post `
     -ContentType "application/json" `
     -Body (@{
       message = "Is Dr. Alice available on $tomorrow at 10:00?"
     } | ConvertTo-Json)
   ```

   The assistant should report whether the exact slot is available. The date must be in `YYYY-MM-DD` format when it reaches the database.

4. **Test alternative slots.** Ask for a doctor and date without specifying a time:

   ```powershell
   Invoke-RestMethod -Uri http://127.0.0.1:5000/chat `
     -Method Post `
     -ContentType "application/json" `
     -Body (@{
       message = "What times are available with Dr. Alice on $tomorrow?"
     } | ConvertTo-Json)
   ```

   The assistant should list the available times from the `availability` table.

5. **Test a booking conversation.** Start a new conversation and keep its ID:

   ```powershell
   $booking = Invoke-RestMethod -Uri http://127.0.0.1:5000/chat `
     -Method Post `
     -ContentType "application/json" `
     -Body (@{
       message = "I want to book Dr. Alice on $tomorrow at 10:00"
     } | ConvertTo-Json)
   $booking
   ```

   The assistant should ask for the patient's name and confirmation before booking. It must not book immediately without confirmation.

6. **Continue with the same conversation ID.** Replace the message with the name and clear confirmation:

   ```powershell
   Invoke-RestMethod -Uri http://127.0.0.1:5000/chat `
     -Method Post `
     -ContentType "application/json" `
     -Body (@{
       conversation_id = $booking.conversation_id
       message = "My name is Alex and I confirm the appointment at 10:00."
     } | ConvertTo-Json)
   ```

   A successful response should contain a booking confirmation with the patient name, doctor, date, and time.

7. **Verify the database change.** In the second terminal, run:

   ```powershell
   python show_db.py
   ```

   Confirm both changes:

   - The selected row in `availability` has status `Booked`.
   - A matching row exists in `appointments` with patient `Alex` and status `Booked`.

8. **Test that the same slot cannot be booked twice.** Send another booking request for the same doctor, date, and time. The assistant should say that the slot is unavailable or offer another slot. The database should not contain a second appointment for that exact slot.

9. **Test an invalid request.** Send a request without a message:

   ```powershell
   Invoke-RestMethod -Uri http://127.0.0.1:5000/chat `
     -Method Post `
     -ContentType "application/json" `
     -Body '{}'
   ```

   Flask should return HTTP status `400` and an error stating that the `message` field is required.

If one of these tests fails, look at the terminal running `python app.py`. Flask prints the Python error there. Then check the troubleshooting section below.

## 13. Troubleshooting

### `ModuleNotFoundError`

Activate the virtual environment and install the dependencies again:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### PowerShell will not activate `venv`

Run the process-scoped policy command from step 4, then activate again.

### `OPENAI_API_KEY is not configured`

Check that `.env` is in the same folder as `chatbot.py`, that the variable is spelled exactly `OPENAI_API_KEY`, and that the Flask server was restarted after editing `.env`.

### `no such table`

Run this from the project root:

```powershell
python db_setup.py
```

### The test cannot connect to port 5000

Keep `python app.py` running in another terminal. If port 5000 is already occupied, stop the other process or configure a different Flask port and update the test URL.

### Dates or times do not match

Use ISO formats in tool calls and stored data: `2026-09-10` for dates and `10:00` for times. Natural-language conversion is handled by the model, but the database comparisons are exact.

## 14. Recommended learning order

Follow the project in this order:

1. Learn basic Python functions, dictionaries, imports, and exceptions.
2. Run `db_setup.py` and inspect SQLite output with `show_db.py`.
3. Read and test the functions in `tools.py`.
4. Read the tool schemas and calling loop in `chatbot.py`.
5. Start the Flask server and send a direct `/chat` request.
6. Test a multi-message booking conversation.
7. Add automated tests before changing booking or database behavior.

At that point you have a working local prototype with a clear separation between the HTTP API, AI orchestration, database tools, and SQLite storage.


## In short how to start the project

cd "C:\GenAI People\GITProject\Python-Projects\Chatbot Doc"

python -m venv venv
.\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install flask openai python-dotenv requests

python db_setup.py
python app.py