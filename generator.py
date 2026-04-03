from openai import OpenAI

from config import Settings
from models import Answer
from retriever import retrieve, format_context

settings = Settings()

client = OpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key
)

system_message = "You are a personal knowledge assistant. Answer the user's question using ONLY the context provided below. If the context doesn't contain enough information, say \"I don't have that in my notes.\" Always cite the source number (e.g. [Source 1]) for every claim you make."

def generate(question: str) -> Answer:
    sources = retrieve(question)
    context = format_context(sources)

    user_message = f"Context:\n{context}\nQuestion: {question}"

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )
    answer = response.choices[0].message.content
    return Answer(
        question=question,
        answer=answer,
        sources=sources
    )