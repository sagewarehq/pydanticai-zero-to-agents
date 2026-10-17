"""Building block · Embeddings: retrieval-augmented generation (RAG).

Embeddings turn text into vectors; similar meaning → nearby vectors. Embed
your documents once, embed the question, take the closest documents, and give
them to the agent as a tool. That is RAG in ~40 lines, no vector DB needed.

    uv run building_blocks/embeddings_rag.py
"""

import os

import numpy as np
from pydantic_ai import Agent, Embedder

# A tiny "knowledge base". In real life: your docs, tickets, policies, notes.
DOCS = [
    'Workshop wifi: network "PythonAsia-Sprint", password is on the whiteboard.',
    'Lunch is served at 12:30 in the hallway. Vegetarian options are on the left table.',
    'Demos start at 16:00. Each team gets five minutes, plus two for questions.',
    'API keys: use OpenRouter if you have no provider key. Free models train on your data.',
    'The sprint ends at 17:30. Please return the borrowed power strips to the front desk.',
    'If your agent loops forever, set usage_limits=UsageLimits(request_limit=10).',
]

embedder = Embedder('openai:text-embedding-3-small')
doc_vectors = np.array(embedder.embed_documents_sync(DOCS).embeddings)

agent = Agent(
    os.getenv('MODEL', 'openai:gpt-5-mini'),
    instructions='Answer workshop questions in one or two sentences using search_notes. If the notes do not cover it, say so.',
)


@agent.tool_plain
async def search_notes(query: str, top_k: int = 2) -> list[str]:
    """Search the workshop notes by meaning."""
    q = np.array((await embedder.embed_query(query)).embeddings[0])
    scores = doc_vectors @ q / (np.linalg.norm(doc_vectors, axis=1) * np.linalg.norm(q))
    return [DOCS[i] for i in np.argsort(scores)[::-1][:top_k]]


for question in ['When do I need to present?', 'What do I do if my agent never stops?', 'Is there parking?']:
    print(f'Q: {question}\nA: {agent.run_sync(question).output}\n')
