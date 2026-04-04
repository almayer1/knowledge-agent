from openai import OpenAI
import openai

from config import Settings
from exceptions import OllamaConnectionError
from models import Answer
from retriever import retrieve, format_context

settings = Settings()

client = OpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key
)

SYSTEM_PROMPT = """You are a study assistant helping a student understand their lecture notes.

IMPORTANT RULES:
- Use ONLY the provided context. Never use outside knowledge.
- Cite sources after each sentence using [Source 1], [Source 2] etc.
- If the answer is not in the context say: "I don't have that in my notes."
- Do not include a preamble like 'Here's a clear answer'

Write a clear 3-4 sentence answer, then list 3 key points as bullets."""



def generate(question: str) -> Answer:
    sources = retrieve(question)
    context = format_context(sources)

    user_prompt = f"Context:\n{context}\nQuestion: {question}"

    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )
    except openai.APIConnectionError:
        raise OllamaConnectionError("Could not connect to Ollama.\nMake sure it is running with: ollama serve")
    
    answer = response.choices[0].message.content
    return Answer(
        question=question,
        answer=answer,
        sources=sources
    )