from config import GROQ_API
from groq import Groq

models = [
    ["llm_gemma", "Gemma 2 9B", "gemma2-9b-it", 6.1],
    ["llm_llama", "Llama 3.1 405B", "llama-3.1-8b-instant", 0.2],
    ["llm_mixtral", "Mixtral 8x7B", "mixtral-8x7b-32768", 0.3]
]

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {GROQ_API}",
    "Content-Type": "application/json"
}

client = Groq(api_key=GROQ_API)

def generate_response(model, prompt):
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
        ],
        stream=True,
        stop=None,
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content