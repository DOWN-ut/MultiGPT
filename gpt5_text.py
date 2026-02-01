import os
from openai import OpenAI

keyFile = open("key.txt", "r")

client = OpenAI(
    # This is the default and can be omitted
    api_key=keyFile.read(),
)

response = client.responses.create(
    model="gpt-5.2",
    reasoning={"effort": "low"},
    input=[
        {
            "role": "developer",
            "content": "Talk like a pirate."
        },
        {
            "role": "user",
            "content": "Are semicolons optional in JavaScript?"
        }
    ]
)

print(response.output_text)