from openai import OpenAI

from config import Settings
from models import Answer
from retriever import retrieve, format_context

settings = Settings()

client = OpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key
)

SYSTEM_PROMPT = """You are a personal study assistant with access to a student's lecture notes.

Your rules:
- Answer ONLY using the context provided. Never use outside knowledge.
- Always cite sources inline using [Source N] after every claim.
- If the context doesn't contain enough information say: "I don't have that in my notes."
- Be concise and clear — you are helping a student understand and study.
- If multiple sources support the same point, cite all of them [Source 1][Source 2].
- Never make up information. Accuracy is more important than a complete answer.

Response format:
Answer:
Your answer here with inline citations [Source N].

Key Points:
- Bullet point summary of the most important facts

Sources Used:
List only the sources you actually cited."""


def generate(question: str) -> Answer:
    sources = retrieve(question)
    context = format_context(sources)

    user_prompt = f"Context:\n{context}\nQuestion: {question}"

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )
    answer = response.choices[0].message.content
    return Answer(
        question=question,
        answer=answer,
        sources=sources
    )