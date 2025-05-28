# llm/ollama_provider.py
from __future__ import annotations

import os
from typing import List, Dict, Optional

from dotenv import load_dotenv
from llama_cpp import Llama
from .base import LLMProvider

load_dotenv()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "Si jedrnat asistent. Odgovori v slovenščini v naslednji obliki:\n"
    "Odgovor: {odgovor}\nNajdeno v: {stavku, kjer je bil odgovor najden}\n"
    "Kontekst je seznam člankov, vsak v naslednji obliki:\n"
    "[DATE: <datum>]\nTITLE: <naslov>\nSUBTITLE: <podnaslov>\nSUBCATEGORY: <podkategorija>\n"
    "URL: <url>\nAUTHOR: <avtor>\nSECTION: <sekcija>\nRECAP: <povzetek>\nCONTENT: <vsebina>\n"
    "Pri iskanju odgovorov uporabi samo polje 'CONTENT' vsakega članka.\n"
    "Pri navajanju, kje je bil odgovor najden, navedi točen stavek iz polja 'CONTENT'.\n"
    "Za razvrščanje člankov po datumu vedno uporabi vrednost v polju [DATE: ...].\n"
    "Ne dodajaj razlag, utemeljitev, citatov ali kakršnegakoli dodatnega besedila zunaj zahtevane oblike.\n"
    "Če odgovora ni ali ni relevanten v kontekstu, odgovori z \"Ni v podanem kontekstu\" ali \"Ne vem\"."
)


_DEFAULT_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", "GaMS-9B-Instruct-Q4_k.gguf")
_DEFAULT_CTX = int(os.getenv("LLAMA_N_CTX", "4096"))
_DEFAULT_GPU_LAYERS = int(os.getenv("LLAMA_N_GPU_LAYERS", "-1"))


class OllamaProvider(LLMProvider):  # name kept for drop‑in compatibility
    """Chat‑completion wrapper around a local GGUF file via llama‑cpp."""

    def __init__(
        self,
        model_path: str = _DEFAULT_MODEL_PATH,
        n_gpu_layers: int = _DEFAULT_GPU_LAYERS,
        n_ctx: int = _DEFAULT_CTX,
    ) -> None:
        self.model = Llama(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,
            n_ctx=n_ctx,
            chat_format="chatml",
        )

    # ---------------------------------------------------------------------
    # Public API (same signature as GeminiProvider)
    # ---------------------------------------------------------------------

    def generate_answer(
        self,
        query: str,
        context: str,
        history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.0,
    ) -> str:
        try:
            messages: List[Dict[str, str]] = []

            # 1) system instruction
            messages.append({"role": "system", "content": _SYSTEM_PROMPT})

            # 2) optional RAG context as a system message to guide the model
            messages.append({"role": "system", "content": f"Kontekst:\n{context}"})

            # 3) prior history, if any
            if history:
                messages.extend(history)

            # 4) current user question
            messages.append({"role": "user", "content": query})

            # 5) run inference
            response = self.model.create_chat_completion(
                messages=messages, temperature=temperature
            )

            return (
                response["choices"][0]["message"]["content"].strip()
                if response and "choices" in response
                else ""
            )
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "Local llama‑cpp model failed to generate an answer. "
                "Check model path, GPU memory, and parameters."
            ) from exc
