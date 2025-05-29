from __future__ import annotations

import os
from typing import List, Dict, Optional

from dotenv import load_dotenv
import openai
import pinecone
from .base import LLMProvider

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4-turbo")
_PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
_PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT")
_PINECONE_INDEX = os.getenv("PINECONE_INDEX_NAME")

# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = (
    "Si jedrnat asistent za slovenske športne novice. Odgovori v slovenščini, v naslednji obliki:\n"
    "Odgovor: {odgovor}\nNajdeno v: {stavku, kjer je bil odgovor najden}\n"
    "Kontekst je seznam člankov, vsak v naslednji obliki:\n"
    "[DATE: <datum>]\nTITLE: <naslov>\nURL: <url>\nCONTENT: <vsebina>\n"
    "Pri iskanju odgovorov uporabi samo polje 'CONTENT'.\n"
    "Pri navajanju, kje je bil odgovor najden, navedi točen stavek iz 'CONTENT'.\n"
    "Za razvrščanje člankov po datumu vedno uporabi vrednost v polju [DATE:].\n"
    "Če odgovora ni ali ni relevanten, odgovori z \"Ni v podanem kontekstu\" ali \"Ne vem\"."
)

class OpenAIProvider(LLMProvider):
    """Chat‑completion wrapper around OpenAI + Pinecone for RAG in Slovene sports."""

    def __init__(
        self,
        embedding_model: str = _EMBEDDING_MODEL,
        chat_model: str = _CHAT_MODEL,
        pinecone_api_key: Optional[str] = _PINECONE_API_KEY,
        pinecone_env: Optional[str] = _PINECONE_ENV,
        pinecone_index: Optional[str] = _PINECONE_INDEX,
        top_k: int = 5,
    ) -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.embedding_model = embedding_model
        self.chat_model = chat_model
        self.top_k = top_k

        # Initialize Pinecone
        if not pinecone_api_key or not pinecone_env or not pinecone_index:
            raise ValueError("Pinecone API key, environment, and index name must be set in env variables.")
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
        self.index = pinecone.Index(pinecone_index)

    def _retrieve(self, query: str) -> List[Dict[str, str]]:
        # Embed the query
        resp = openai.Embedding.create(input=query, model=self.embedding_model)
        q_vector = resp["data"][0]["embedding"]

        # Query Pinecone
        results = self.index.query(vector=q_vector, top_k=self.top_k, include_metadata=True)
        # Extract metadata for each match
        articles = []
        for match in results["matches"]:
            meta = match["metadata"]
            articles.append({
                "date": meta.get("date", ""),
                "title": meta.get("title", ""),
                "url": meta.get("url", ""),
                "content": meta.get("content", ""),
            })
        return articles

    def generate_answer(
        self,
        query: str,
        context: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.0,
    ) -> str:
        try:
            # 1) Retrieve relevant articles
            articles = self._retrieve(query)

            # 2) Format context string
            rag_context = []
            for art in sorted(articles, key=lambda x: x["date"]):
                rag_context.append(
                    f"[DATE: {art['date']}]
TITLE: {art['title']}
URL: {art['url']}
CONTENT: {art['content']}"
                )
            full_context = "\n---\n".join(rag_context)

            # 3) Build messages
            messages: List[Dict[str, str]] = []
            messages.append({"role": "system", "content": _SYSTEM_PROMPT})
            messages.append({"role": "system", "content": f"Kontekst:\n{full_context}"})
            if context:
                messages.append({"role": "system", "content": f"Dodaten kontekst:\n{context}"})
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": query})

            # 4) Call OpenAI ChatCompletion
            response = openai.ChatCompletion.create(
                model=self.chat_model,
                messages=messages,
                temperature=temperature,
            )

            return response.choices[0].message.content.strip()
        except Exception as exc:
            raise RuntimeError(
                "OpenAI RAG pipeline failed to generate an answer. "
                "Check API keys, Pinecone setup, and parameters."
            ) from exc
