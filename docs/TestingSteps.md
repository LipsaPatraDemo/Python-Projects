# Testing the Doctor's Assistant

## 1. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

## 2. Configure the OpenAI API key

Create a `.env` file in the project folder:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1
```

## 3. Initialize the database

```powershell
python db_setup.py
```

## 4. Start the Flask application

```powershell
python app.py
```

Keep this terminal running.

## 5. Test the API

Open a second PowerShell terminal:

```powershell
python test.py
```

Or test directly:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/chat `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Is Dr. Alice available tomorrow at 10 AM?"}'
```

## 6. Test a booking conversation

```powershell
$response = Invoke-RestMethod -Uri http://127.0.0.1:5000/chat `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"I want an appointment with Dr. Alice tomorrow"}'

$response
```

Continue using the returned `conversation_id`:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/chat `
  -Method Post `
  -ContentType "application/json" `
  -Body (@{
    conversation_id = $response.conversation_id
    message = "My name is John and I confirm the available time"
  } | ConvertTo-Json)
```

## 7. Check the database

```powershell
python show_db.py
```

A successful booking appears in the `appointments` table, and the selected availability slot changes to `Booked`.
