from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
try:
    r = client.chat.completions.create(model="llama-3.3-70b-versatile", max_tokens=20, messages=[{"role":"user","content":"hi"}])
    print(r.choices[0].message.content)
except Exception as e:
    print(type(e), e)