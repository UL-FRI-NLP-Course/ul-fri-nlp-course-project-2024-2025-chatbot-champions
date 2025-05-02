from .base import LLMProvider


class LocalProvider(LLMProvider):
    """
    LLM Provider implementation using a local model.
    """

    def generate_answer(self, query: str, context: str) -> str:
        """
        Generates an answer using a local model (currently mocked).

        Args:
            query: The user's original query.
            context: The context retrieved from relevant document chunks.

        Returns:
            A string containing the generated answer.
        """

        prompt = f"""Based on the following context:

{context}

---
Answer the question: {query}
"""

        # print("--- Local Provider PROMPT ---")
        # print(prompt)
        # print("--- END Local Provider PROMPT ---")

        # --- Mock Local LLM Call ---
        # Replace this section with your actual local LLM call
        mock_llm_response = (
            f"(Mocked Local Response) Based on the context for the query: '{query}'. "
            f"The actual local LLM call would happen here."
        )
        # --- End Mock Local LLM Call ---

        return mock_llm_response
