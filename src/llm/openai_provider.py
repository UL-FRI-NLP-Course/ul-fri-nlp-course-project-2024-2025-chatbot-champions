import os
from openai import OpenAI
from .base import LLMProvider
from typing import List, Dict, Optional
from .prompt import SYSTEM_PROMPT

# Instantiate the OpenAI client
# It will automatically use the OPENAI_API_KEY environment variable
# Ensure this variable is set in your .env file
try:
    client = OpenAI()
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    # Handle initialization error appropriately - maybe raise an exception
    # or fallback to a different provider if configured.
    client = None


class OpenAIProvider(LLMProvider):
    """
    LLM Provider implementation using OpenAI's models.
    """

    def __init__(self, model="gpt-3.5-turbo"):  # Allow model selection
        self.model = model
        if client is None:
            raise RuntimeError(
                "OpenAI client failed to initialize. Check API key and connectivity."
            )

    def generate_answer(
        self, query: str, context: str, history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generates an answer using the specified OpenAI model,
        incorporating chat history and retrieved context.

        Args:
            query: The user's original query.
            context: The context retrieved from relevant document chunks.
            history: A list of previous chat messages (dicts with 'role' and 'content').

        Returns:
            A string containing the generated answer.
        """
        if history is None:
            history = []

        # System prompt explaining the task
        system_prompt = {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }

        # Prepare messages for OpenAI API format
        messages = [system_prompt]
        messages.extend(history)  # Add previous turns

        # Add the current user query combined with context
        # Note: Combining context directly into the user message is one approach.
        # Another is to put context in the system prompt or a separate user message.
        messages.append(
            {
                "role": "user",
                "content": f"Based on the following context:\n\n{context}\n\n---\nAnswer the question: {query}",
            }
        )

        try:
            # print("--- Sending request to OpenAI API ---")
            # print(f"Messages: {messages}") # Be careful logging sensitive data

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # Adjust creativity (0=deterministic, 1=creative)
                max_tokens=250,  # Limit response length
            )

            # print("--- Received response from OpenAI API ---")
            # print(completion)

            response_content = completion.choices[0].message.content
            if response_content is None:
                return "Sorry, I received an empty response from the AI."

            return response_content.strip()

        except Exception as e:
            print(f"Error during OpenAI API call: {e}")
            # Consider more specific error handling (e.g., rate limits, auth errors)
            return f"Sorry, I encountered an error communicating with the AI: {e}"
