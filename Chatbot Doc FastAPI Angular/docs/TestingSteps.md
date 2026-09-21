# Testing the Doctor's Assistant

These steps assume Windows PowerShell, Python 3.10 or newer, and a fresh clone of this repository.

## 1. Open the project folder

Run all backend commands from the FastAPI project root:

```powershell
cd "C:\GenAI People\GITProject\Python-Projects\Chatbot Doc FastAPI Angular"
```

Verify Python is available:

```powershell
python --version
```

Python 3.10 or newer is required because the FastAPI request model uses the `str | None` type syntax.

## 2. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

If the virtual environment does not exist, create it first:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 3. Install dependencies

This repository does not currently include a `requirements.txt` file, so install the runtime packages directly:

```powershell
python -m pip install fastapi uvicorn openai python-dotenv requests
```

## 4. Configure the OpenAI API key

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1
```

Never commit `.env` or expose the API key.

## 5. Initialize the database

```powershell
python db_setup.py
```

## 6. Start FastAPI

Open Terminal 1 in the project root and run:

```powershell
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Keep this terminal running.

If port `8000` is unavailable, find the process using it:

```powershell
netstat -ano | findstr :8000
```

Stop the process using its PID:

```powershell
taskkill /PID <PID> /F
```

Alternatively, start the API on port `8001`:

```powershell
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8001
```

Set the base URL in Terminal 2 to match the port used by Uvicorn. Run this with `8000`, or change it to `8001` if you used the alternative port:

```powershell
$BaseUrl = "http://127.0.0.1:8000"
```

Use `$BaseUrl` in all following commands.

## 7. Test the health endpoint

Open Terminal 2 and run:

```powershell
Invoke-RestMethod "$BaseUrl/"
```

Expected response:

```json
{
  "message": "Doctor Chatbot API is running"
}
```

## 8. Open the Swagger documentation

Open this URL in a browser:

```text
http://127.0.0.1:8000/docs
```

If you started Uvicorn on port `8001`, open `http://127.0.0.1:8001/docs` instead.

Select `POST /chat`, choose `Try it out`, and send:

```json
{
  "message": "I need a doctor for my ankle pain"
}
```

## 9. Test the chat endpoint from PowerShell

```powershell
$body = @{
    message = "I need a doctor for my ankle pain"
} | ConvertTo-Json

$response = Invoke-RestMethod `
  -Uri "$BaseUrl/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$response
```

Expected response format:

```json
{
  "conversation_id": "generated-id",
  "reply": "..."
}
```

This test requires a valid `OPENAI_API_KEY`.

## 10. Test conversation continuity

Use the `conversation_id` returned by the previous request:

```powershell
$conversationId = $response.conversation_id

$body = @{
    conversation_id = $conversationId
    message = "Please show me available appointment times"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "$BaseUrl/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

## 11. Test invalid input

```powershell
try {
  Invoke-RestMethod `
    -Uri "$BaseUrl/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{"message":"   "}' `
    -ErrorAction Stop
} catch {
  $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
  Write-Host "Status: $([int]$_.Exception.Response.StatusCode)"
  Write-Host $reader.ReadToEnd()
}
```

Expected result: HTTP `400` with:

```json
{
  "detail": "The 'message' field is required."
}
```

## 12. Check the database

```powershell
python show_db.py
```

A successful booking appears in the `appointments` table, and the selected availability slot changes to `Booked`.

## 13. Stop the server

Return to Terminal 1 and press `Ctrl+C`.

## Troubleshooting

### `WinError 10013` or port 8000 is unavailable

Check whether another process is using port 8000:

```powershell
netstat -ano | findstr :8000
```

Stop that process with `taskkill`, or use port 8001.

### `OPENAI_API_KEY is not configured`

Check that `.env` is in the project root beside `app.py`, then restart Uvicorn.

The health endpoint and Swagger UI can work without an API key, but a normal `/chat` request requires a valid key.

### Chat returns HTTP 500

Check the Uvicorn terminal for the detailed error. Confirm that the API key is valid and that the OpenAI service is reachable.

### `no such table` appears

Run the database setup command again from the project root:

```powershell
python db_setup.py
```

### PowerShell cannot activate the virtual environment

Run this once in the current PowerShell session, then activate the environment again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```
