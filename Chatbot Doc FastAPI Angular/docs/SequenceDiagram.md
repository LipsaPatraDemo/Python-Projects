# Doctor's Assistant Sequence Diagram

This diagram shows how a user request travels through the Flask API, OpenAI Responses API, database tools, and SQLite database.

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Postman
    participant Flask as Flask API (app.py)
    participant Chatbot as Chatbot (chatbot.py)
    participant OpenAI as OpenAI Responses API
    participant Tools as Database Tools (tools.py)
    participant DB as SQLite (clinic.db)

    User->>Flask: POST /chat with message
    Flask->>Flask: Get or create conversation_id
    Flask->>Chatbot: interpret_message(message, conversation)
    Chatbot->>Chatbot: Add user message to conversation history
    Chatbot->>OpenAI: responses.create(input, instructions, tools)

    alt User describes a symptom or asks about a specialty
        Note over OpenAI: Interpret symptoms using instructions<br/>e.g. ankle swelling -> Orthopedics
        OpenAI-->>Chatbot: function_call: find_doctors
        Chatbot->>Tools: find_doctors(name or specialty)
        Tools->>DB: SELECT doctors
        DB-->>Tools: Doctor records
        Tools-->>Chatbot: Doctor data
        Chatbot->>OpenAI: function_call_output
        OpenAI-->>Chatbot: Final response
    else User asks about availability
        OpenAI-->>Chatbot: function_call: check_availability
        Chatbot->>Tools: check_availability(doctor, date, time)
        Tools->>DB: SELECT available slot
        DB-->>Tools: Slot status
        Tools-->>Chatbot: Availability result
        Chatbot->>OpenAI: function_call_output
        OpenAI-->>Chatbot: Final response
    else User asks to book an appointment
        OpenAI-->>Chatbot: function_call: check_availability
        Chatbot->>Tools: check_availability(doctor, date, time)
        Tools->>DB: SELECT available slot
        DB-->>Tools: Slot status
        Tools-->>Chatbot: Availability result
        alt Requested slot unavailable
            Chatbot->>OpenAI: function_call_output
            OpenAI-->>Chatbot: function_call: list_available_slots
            Chatbot->>Tools: list_available_slots(doctor, date)
            Tools->>DB: SELECT available slots
            DB-->>Tools: Available slots
            Tools-->>Chatbot: Alternative slots
            Chatbot->>OpenAI: function_call_output
            OpenAI-->>Chatbot: Offer alternative slot
        else Requested slot available
            Chatbot->>OpenAI: function_call_output
            OpenAI-->>Chatbot: Ask for patient name or confirmation
        end

        User->>Flask: POST /chat with same conversation_id
        Flask->>Chatbot: interpret_message(confirmation, conversation)
        Chatbot->>OpenAI: responses.create with conversation history
        OpenAI-->>Chatbot: function_call: book_appointment
        Chatbot->>Tools: book_appointment(doctor, patient, date, time)
        Tools->>DB: UPDATE availability status to Booked
        Tools->>DB: INSERT appointment
        DB-->>Tools: Booking saved
        Tools-->>Chatbot: Booking confirmation
        Chatbot->>OpenAI: function_call_output
        OpenAI-->>Chatbot: Final booking confirmation
    end

    Chatbot-->>Flask: Assistant reply
    Flask-->>User: JSON reply and conversation_id
```

## Main Components

- **User / Postman** sends messages to the `/chat` endpoint.
- **Flask API** manages requests and conversation IDs.
- **Chatbot** runs the Responses API tool-calling loop.
- **OpenAI Responses API** decides whether a database tool is needed.
- **Database tools** execute doctor, availability, and booking operations.
- **SQLite** stores doctors, availability slots, and appointments.
