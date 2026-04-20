import json
from typing import Generator

import ollama

from config import Settings
from exceptions import OllamaConnectionError
from models import Answer
from retriever import retrieve, format_context

settings = Settings()

SYSTEM_PROMPT = """You are a study assistant helping a student understand their lecture notes.

IMPORTANT RULES:
- Use ONLY the provided context. Never use outside knowledge.
- Cite sources after each sentence using [Source 1], [Source 2] etc.
- If the answer is not in the context say: "I don't have that in my notes."
- Do not include a preamble like 'Here's a clear answer'
- If the user asks a follow-up question, use the conversation history to understand what they're referring to.

Write a clear 3-4 sentence answer, then list 3 key points using markdown bullet points starting with "- " (a dash and a space)."""


def generate_stream(question: str, history: list) -> Generator:
    sources = retrieve(question)
    context = format_context(sources)

    user_prompt = f"Context:\n{context}\nQuestion: {question}"

    try:
        response = ollama.chat(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *history,
                {"role": "user", "content": user_prompt}
            ],
            stream=True
        )
    except Exception as e:
        raise OllamaConnectionError("Could not connect to Ollama.\nMake sure it is running with: ollama serve")

    for chunk in response:
        token = chunk.message.content
        if token:
            yield token

    data = []
    for source in sources:
        data.append(source.model_dump())

    yield json.dumps({"sources": data})

def generate(question: str) -> Answer:
    sources = retrieve(question)
    context = format_context(sources)
    user_prompt = f"Context:\n{context}\nQuestion: {question}"

    try:
        response = ollama.chat(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )
    except Exception as e:
        raise OllamaConnectionError("Could not connect to Ollama.\nMake sure it is running with: ollama serve")

    answer = response.message.content
    return Answer(
        question=question,
        answer=answer,
        sources=sources
    )
