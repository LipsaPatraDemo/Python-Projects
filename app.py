# Import Flask application class and helper objects for handling requests and JSON
from flask import Flask, request, jsonify
from uuid import uuid4
# Import the function that sends a user's message to the chatbot and returns a reply
from chatbot import interpret_message
# Import helper utilities for checking availability and booking appointments


# Create a Flask application instance using the current module's name
app = Flask(__name__)
conversations = {}


# Define an HTTP POST endpoint at /chat that accepts JSON payloads
@app.route("/chat", methods=["POST"])
def chat():
    # Read the incoming JSON and extract the 'message' field sent by the client
    payload = request.get_json(silent=True) or {}
    user_message = payload.get("message")
    if not user_message:
        return jsonify({"error": "The 'message' field is required."}), 400
    conversation_id = payload.get("conversation_id") or str(uuid4())
    conversation = conversations.setdefault(conversation_id, [])
    
    # Send the user's message to the chatbot interpreter and capture its reply
    reply = interpret_message(user_message, conversation)
    # Return the chatbot reply as a JSON object with key 'reply'
    return jsonify({"conversation_id": conversation_id, "reply": reply})


# If this module is executed directly (not imported), start the Flask dev server
if __name__ == "__main__":
    # Run with debug=True for auto-reload and better error messages during development
    app.run(debug=True)
