import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
url = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": "Bearer " + str(api_key)}

response = requests.get(url, headers=headers)
print("Status code:", response.status_code)
print(response.json())
