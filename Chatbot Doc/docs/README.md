# Doctor Appointment Chatbot

This project is a Flask-based Doctor's Assistant. It uses the OpenAI Responses API with Python tools backed by SQLite to find doctors, check availability, and book confirmed appointments.

## Quick start

From the project root in PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install flask openai python-dotenv requests
python db_setup.py
```

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1
```

Start the API:

```powershell
python app.py
```

The endpoint is `POST http://127.0.0.1:5000/chat`. In a second terminal, run:

```powershell
python test.py
```

## Documentation

- [FromScratchGuide.md](FromScratchGuide.md) - complete setup and implementation guide
- [TestingSteps.md](TestingSteps.md) - focused API and booking tests
- [ApplicationExplanation.md](ApplicationExplanation.md) - architecture and code behavior
- [SequenceDiagram.md](SequenceDiagram.md) - request sequence diagram
