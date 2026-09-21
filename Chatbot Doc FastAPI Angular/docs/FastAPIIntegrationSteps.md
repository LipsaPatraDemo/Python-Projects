# Adding FastAPI to This Project

This project already has the chatbot logic in `app.py` and `chatbot.py`. The easiest way to add FastAPI is to keep the chatbot code as it is and replace only the web server layer.

This guide assumes your project folder is:

```text
C:\GenAI People\GITProject\Python-Projects\Chatbot Doc FastAPI Angular
```

Open that folder in VS Code before starting.

---

## Step 0: Open the correct folder

1. Open VS Code.
2. Open the folder named:
   ```text
   Chatbot Doc FastAPI Angular
   ```
3. In the terminal, make sure the current working directory is the project root:

```powershell
cd "C:\GenAI People\GITProject\Python-Projects\Chatbot Doc FastAPI Angular"
```

If you are using a terminal inside VS Code, it should now be pointed at the project root before you run the commands below.

---

## 1) Create or activate the virtual environment

If the project has a venv already, activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If the environment does not exist yet, create it first:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Run this only after you are inside the project folder.

---

## 2) Install FastAPI and Uvicorn

Run this command in the project root:

```bash
pip install fastapi uvicorn
```

This is the required install for the FastAPI backend in this project.

This command should be run from the project root, not from inside a subfolder like `docs` or `Chatbot Doc`.

---

## 3) Open `app.py` and replace the Flask server code

Open the file:

```text
app.py
```

Your current app uses Flask and the route `POST /chat`. FastAPI can do the same job with a cleaner syntax.

Replace the existing Flask code with this version:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
from chatbot import interpret_message

app = FastAPI(title="Doctor Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conversations = {}

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

@app.post("/chat")
def chat(payload: ChatRequest):
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="The 'message' field is required.")

    conversation_id = payload.conversation_id or str(uuid4())
    conversation = conversations.setdefault(conversation_id, [])

    try:
        reply = interpret_message(payload.message, conversation)
        return {
            "conversation_id": conversation_id,
            "reply": reply
        }
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "Doctor Chatbot API is running"}
```

This keeps your existing chatbot behavior and only swaps the HTTP framework.

Important: do this in the main project root file `app.py`, not in the `docs` folder.

---

## 4) Keep the chatbot logic unchanged

No major change is needed in `chatbot.py`. That file already contains:

- OpenAI client setup
- tool definitions
- conversation flow
- `interpret_message(...)`

FastAPI only handles HTTP requests and passes the user message to that function.

Open `chatbot.py` only to verify that the logic is still intact; do not change it unless you need to fix a chatbot issue unrelated to the API layer.

---

## 5) Add CORS for Angular

If your Angular app runs on port 4200, add CORS like this:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This allows the Angular frontend to call the backend without browser blocking.

If your Angular app is in a separate folder, do not run the backend commands there. Keep the terminal in the Python project root while this server runs.

---

## 6) Run the FastAPI server

From the project root, start the API:

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

You should run this command only after:

1. the virtual environment is activated
2. `fastapi` and `uvicorn` are installed
3. `app.py` has been updated

Then test:

- API root: http://127.0.0.1:8000
- Chat endpoint: http://127.0.0.1:8000/chat

Leave this terminal running while you test the API. Open a second terminal only for curl or Postman requests.

---

## 7) Test the endpoint

Open a second terminal and run:

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"I need a doctor for my ankle pain"}'
```

Expected response:

```json
{
  "conversation_id": "abc123",
  "reply": "..."
}
```

This command should be run from any terminal, but the FastAPI server itself must still be running in the Python project folder.

---

## 8) Recommended project flow

After adding FastAPI:

1. Open the Python project root folder
2. Activate the virtual environment
3. Install dependencies in that root folder
4. Edit `app.py` in the root folder
5. Start the server from that same root folder
6. Test with a second terminal
7. Keep the Angular app in its own folder and call the backend at `http://127.0.0.1:8000`

---

## 9) Remove Flask only from this project (optional cleanup)

Only do this after the FastAPI app is working.

Important: do this inside the project virtual environment, not from your global Python installation.

From the project root, run:

```powershell
cd "C:\GenAI People\GITProject\Python-Projects\Chatbot Doc FastAPI Angular"
.\venv\Scripts\Activate.ps1
pip uninstall flask
```

This removes Flask only from the venv in this project folder.

It does not uninstall Flask from your computer globally.

After that, check that your app still runs with FastAPI:

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

If the server starts successfully, the FastAPI migration is working.

---

## 10) Optional migration strategy

If you are not ready to remove Flask completely, you can do this in two stages:

- Keep the existing Flask app for now
- Create a new FastAPI version in the same root folder
- Run FastAPI in development and test it first
- Remove the Flask version later

This is a safe path if you want to avoid breaking the project immediately.

---

## Summary

The migration is simple:

- Open the project root folder first
- Activate the virtual environment
- Install `fastapi` and `uvicorn` in that folder
- Replace the Flask server in `app.py`
- Keep the chatbot logic in `chatbot.py`
- Add CORS for Angular
- Run `uvicorn app:app --reload` from the project root
- Test the API from a second terminal
- Optionally remove Flask only from the project venv with `pip uninstall flask` after verification

This gives you a modern, fast backend while keeping the existing project behavior.
