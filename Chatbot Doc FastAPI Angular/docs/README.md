# Doctor Appointment Chatbot

This project is a FastAPI-based Doctor's Assistant. It uses the OpenAI Responses API with Python tools backed by SQLite to find doctors, check availability, and book confirmed appointments.

The project requires Python 3.10 or newer and is intended to run from the `Chatbot Doc FastAPI Angular` project folder.

## Quick start

From PowerShell, open the project folder:

```powershell
cd "C:\GenAI People\GITProject\Python-Projects\Chatbot Doc FastAPI Angular"
```

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install fastapi uvicorn openai python-dotenv requests
python db_setup.py
```

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1
```

Start the API:

```powershell
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

The health endpoint is `GET http://127.0.0.1:8000/` and the chatbot endpoint is `POST http://127.0.0.1:8000/chat`.
Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

In a second terminal, run:

```powershell
python test.py
```

For complete health, Swagger, validation, conversation, database, and troubleshooting steps, read [TestingSteps.md](TestingSteps.md).

If port `8000` is unavailable, start the API on port `8001` and use that port for all requests:

```powershell
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8001
```

Do not commit `.env` or expose `OPENAI_API_KEY`.

## Documentation

- [FromScratchGuide.md](FromScratchGuide.md) - complete setup and implementation guide
- [TestingSteps.md](TestingSteps.md) - focused API and booking tests
- [ApplicationExplanation.md](ApplicationExplanation.md) - architecture and code behavior
- [SequenceDiagram.md](SequenceDiagram.md) - request sequence diagram
