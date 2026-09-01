# Doctor Appointment Chatbot

This project is a simple Flask-based chatbot for a clinic that can receive a user message and respond to appointment requests. It stores doctor and appointment data in a SQLite database and uses the OpenAI API for chat responses.

## Project structure

- `app.py` - Flask API server
- `chatbot.py` - OpenAI chat integration
- `db_setup.py` - Creates and seeds the SQLite database
- `tools.py` - Database helper functions for checking availability and booking appointments
- `show_db.py` - Displays the database tables and records
- `test.py` - Sends a sample request to the local API
- `clinic.db` - SQLite database file

## 1) Create and activate a virtual environment

From the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks the script, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## 2) Install packages

Install the required Python packages:

```powershell
pip install flask openai python-dotenv requests
```

Optional: if you have a `requirements.txt` file later, you can also do:

```powershell
pip install -r requirements.txt
```

## 3) Configure environment variables

Create a `.env` file in the root folder and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Example:

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
```

## 4) Set up the database

Initialize SQLite tables and seed sample data:

```powershell
python db_setup.py
```

This creates the `clinic.db` file and inserts sample doctors and availability records.

## 5) Run the app

Start the Flask server:

```powershell
python app.py
```

The app will run on:

```text
http://127.0.0.1:5000
```

The chatbot endpoint is:

```text
POST http://127.0.0.1:5000/chat
```

Example JSON body:

```json
{
  "message": "I want to book Dr. X tomorrow at 10 AM"
}
```

## 6) Test the API

Run the built-in test request:

```powershell
python test.py
```

This sends a sample message to the local API and prints the JSON response.

## 7) View database contents

To inspect tables and rows in the database:

```powershell
python show_db.py
```

This prints all tables and the current contents of `clinic.db`.

## 8) Useful commands summary

```powershell
# create venv
python -m venv venv

# activate venv
.\venv\Scripts\Activate.ps1

# install dependencies
pip install flask openai python-dotenv requests

# set up DB
db_setup.py
python db_setup.py

# run Flask app
python app.py

# test API
python test.py

# show DB contents
python show_db.py
```

## 9) Notes

- The app uses SQLite, so no external database server is required.
- The app expects the OpenAI key in `.env` before using `chatbot.py`.
- If the server does not start, make sure the virtual environment is active and all packages are installed.
- If you get an API error, verify that `OPENAI_API_KEY` is set correctly.
