import os
import json
from datetime import date

from dotenv import load_dotenv
from openai import OpenAI

from tools import (book_appointment, check_availability, find_appointments,
                   find_doctors, list_available_slots)

# Load environment variables from a .env file
load_dotenv()  # loads .env file

"""Doctor's Assistant using the OpenAI Responses API and database tools."""


# Instantiate a client that will be used for all requests in this module
# it will read the open AI key from the environment variable OPENAI_API_KEY

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
INSTRUCTIONS = f"""You are Doctor's Assistant for Super Clinic.
Today is {date.today().isoformat()}.
Help callers find doctors and book appointments using the clinic tools.
Use tools for every doctor, specialty, availability, or booking question; never invent data.
Use find_appointments when a patient asks about an existing or previously booked appointment.
Use the patient's name and doctor name from the current conversation when available.
When a symptom is used to find a doctor, map ankle, bone, joint, fracture, or swelling
to Orthopedics unless the caller provides a different specialty.
Map skin, rash, acne, itching, or hair problems to Dermatology.
Treat the returned tool data as authoritative: if check_availability returns available=true,
say the slot is available; if it returns available=false, say it is unavailable.
Use ISO dates (YYYY-MM-DD) and 24-hour times (HH:MM) when calling tools.
If a requested slot is unavailable, check the nearest available slots and offer them.
Before booking, collect the patient's name and confirm the exact doctor, date, and time.
Only book after the caller clearly agrees to the proposed slot.
Be concise, warm, and do not provide medical diagnosis. If no matching specialty exists,
explain that clearly and ask whether you can help with anything else.
"""

TOOLS = [
    {"type": "function", "name": "find_doctors",
     "description": "Find clinic doctors by name or specialty.",
     "parameters": {"type": "object", "properties": {
         "doctor_name": {"type": "string"}, "specialty": {"type": "string"}},
         "additionalProperties": False}},
   
    {"type": "function", "name": "check_availability",
     "description": "Check whether a doctor's exact date and time is available.",
     "parameters": {"type": "object", "properties": {
         "doctor_name": {"type": "string"}, "date": {"type": "string", "description": "YYYY-MM-DD"},
         "time": {"type": "string", "description": "HH:MM"}},
         "required": ["doctor_name", "date", "time"], "additionalProperties": False}},
    
    
    {"type": "function", "name": "list_available_slots",
     "description": "List available appointment slots for a doctor on a date.",
     "parameters": {"type": "object", "properties": {
         "doctor_name": {"type": "string"}, "date": {"type": "string", "description": "YYYY-MM-DD"}},
         "required": ["doctor_name", "date"], "additionalProperties": False}},

    {"type": "function", "name": "find_appointments",
     "description": "Find booked appointments for a patient, optionally filtered by doctor or date.",
     "parameters": {"type": "object", "properties": {
         "patient_name": {"type": "string"}, "doctor_name": {"type": "string"},
         "date": {"type": "string", "description": "YYYY-MM-DD"}},
         "required": ["patient_name"], "additionalProperties": False}},
    
    {"type": "function", "name": "book_appointment",
     "description": "Book an available appointment after the patient confirms it.",
     "parameters": {"type": "object", "properties": {
         "doctor_name": {"type": "string"}, "patient_name": {"type": "string"},
         "date": {"type": "string", "description": "YYYY-MM-DD"},
         "time": {"type": "string", "description": "HH:MM"}},
         "required": ["doctor_name", "patient_name", "date", "time"], "additionalProperties": False}},
]

TOOL_FUNCTIONS = {"find_doctors": find_doctors, "check_availability": check_availability,
                  "list_available_slots": list_available_slots,
                  "find_appointments": find_appointments, "book_appointment": book_appointment}

# Execute the Python function selected by the LLM.
def _run_tool(name, arguments):
    # Find the function registered under the tool name.
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        # Return a controlled error when the tool name is not registered.
        return {"error": f"Unknown tool: {name}"}
    try:
        # Pass the LLM's JSON arguments to the selected Python function.
        return function(**arguments)
    except (KeyError, TypeError, ValueError) as error:
        # Return invalid or missing argument errors to the LLM.
        return {"error": str(error)}

# Send a user message to the LLM and process any requested tools.
def interpret_message(user_message, conversation=None):
    """Send a message through the Responses API tool-calling loop."""
    # Reuse the existing conversation or create a new history list.
    history = conversation if conversation is not None else []
    # Add the latest user message to the conversation history.
    history.append({"role": "user", "content": user_message})
    if client is None:
        # Stop early when the API key is not configured.
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    # Repeat until the LLM returns a final text response.
    while True:
        # Send the conversation, instructions, and tool definitions to OpenAI.
        response = client.responses.create(model=MODEL, instructions=INSTRUCTIONS,
                                           input=history, tools=TOOLS)
        # Preserve the LLM response for the next step of the conversation.
        history.extend(response.output)
        # Collect any tool calls requested by the LLM.
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            # No tool call means the LLM has produced the final answer.
            return response.output_text
        for call in calls:
            # Convert the tool arguments from JSON text into a Python dictionary.
            result = _run_tool(call.name, json.loads(call.arguments))
            # Send the tool result back to the LLM so it can continue or answer.
            history.append({"type": "function_call_output", "call_id": call.call_id,
                            "output": json.dumps(result, default=str)})
