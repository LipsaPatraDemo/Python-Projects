import requests

url = "http://127.0.0.1:8000/chat"
data = {"message": "I want to book Dr. Alice tomorrow at 10 AM"}

response = requests.post(url, json=data)
print(response.json())
