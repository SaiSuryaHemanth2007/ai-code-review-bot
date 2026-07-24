from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

print("API Key:", os.getenv("GROQ_API_KEY"))
print("Model:", os.getenv("GROQ_MODEL"))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model=os.getenv("GROQ_MODEL"),
    messages=[
        {"role": "user", "content": "Say hello!"}
    ]
)

print(response.choices[0].message.content)