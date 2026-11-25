

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

print("Testing Groq API...")

try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": "Return the word SUCCESS."
            }
        ],
        temperature=0
    )

    print("GROQ API CONNECTION SUCCESSFUL!")
    print(response.choices[0].message.content)

except Exception as error:
    print("GROQ API CONNECTION FAILED!")
    print("Exact error:", repr(error))
