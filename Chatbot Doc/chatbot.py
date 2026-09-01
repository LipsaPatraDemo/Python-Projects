import os
from dotenv import load_dotenv
# Import the OpenAI client class from the official OpenAI package
from openai import OpenAI

# Load environment variables from a .env file
load_dotenv()  # loads .env file

"""Simple chatbot wrapper that sends user messages to an OpenAI chat model."""


# Instantiate a client that will be used for all requests in this module
# it will read the open AI key from the environment variable OPENAI_API_KEY

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 

def interpret_message(user_message):
    """Send `user_message` to the chat completion API and return the assistant reply.

    Args:
        user_message (str): The text sent by the user.

    Returns:
        str: The assistant's textual reply extracted from the API response.
    """
    # Build and send a chat completion request to the model
    response = client.chat.completions.create(
        # The model identifier to use for the chat completion
        model="gpt-4.1",
        # A sequence of messages defining the conversation context
        messages=[
            # System message defines assistant role and behavior
            {"role": "system", "content": "You are Doctor’s Assistant for Super Clinic."},
            # User message contains the actual input to be interpreted
            {"role": "user", "content": user_message}
        ]
    )
    # The API returns a list of choices; take the first choice's message content
    return response.choices[0].message.content
