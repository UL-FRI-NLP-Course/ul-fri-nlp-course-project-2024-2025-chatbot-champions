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
    "You are a concise assistant. Reply in Slovenian with a single sentence "
    "that directly answers the question. Do NOT add explanations, reasoning, "
    "citations, or extra text."
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
        use_rag: bool = False,
        temperature: float = 0.0,
    ) -> str:
        """Generate a single‑sentence Slovenian answer.

        Parameters
        ----------
        query : str
            The user question.
        context : str
            Retrieved text to ground the answer when ``use_rag`` is True.
        history : list[dict[str,str]] | None, optional
            Previous turns with keys ``role`` and ``content``—will be sent as‑is
            to the model to preserve conversation memory.
        use_rag : bool, default False
            If True, the ``context`` is prepended to the prompt instructing the
            model to ground its answer.
        temperature : float, default 0.0
            Sampling temperature.
        """
        try:
            messages: List[Dict[str, str]] = []

            # 1) system instruction
            messages.append({"role": "system", "content": _SYSTEM_PROMPT})

            # 2) optional RAG context as a system message to guide the model
            if use_rag and context.strip():
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
