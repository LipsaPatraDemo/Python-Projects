# Import Flask application class and helper objects for handling requests and JSON
from flask import Flask, request, jsonify
# Import the function that sends a user's message to the chatbot and returns a reply
from chatbot import interpret_message
# Import helper utilities for checking availability and booking appointments
from tools import check_availability, book_appointment

# Create a Flask application instance using the current module's name
app = Flask(__name__)


# Define an HTTP POST endpoint at /chat that accepts JSON payloads
@app.route("/chat", methods=["POST"])
def chat():
    # Read the incoming JSON and extract the 'message' field sent by the client
    user_message = request.json["message"]
    # Send the user's message to the chatbot interpreter and capture its reply
    reply = interpret_message(user_message)
    # Return the chatbot reply as a JSON object with key 'reply'
    return jsonify({"reply": reply})


# If this module is executed directly (not imported), start the Flask dev server
if __name__ == "__main__":
    # Run with debug=True for auto-reload and better error messages during development
    app.run(debug=True)
