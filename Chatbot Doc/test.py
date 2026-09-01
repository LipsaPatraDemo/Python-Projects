import requests

url = "http://127.0.0.1:5000/chat"
data = {"message": "I want to book Dr. X tomorrow at 10 AM"}

response = requests.post(url, json=data)
print(response.json())
