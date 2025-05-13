import os
import openai
from openai import OpenAI, APIError
from .base import LLMProvider
from typing import List, Dict, Optional
from .prompt import SYSTEM_PROMPT
from dotenv import load_dotenv

# Instantiate the OpenAI client
# It will automatically use the OPENAI_API_KEY environment variable
# Ensure this variable is set in your .env file

# Load environment variables from .env file
load_dotenv()

# Select LLM Provider based on environment variable
openai_api_key = os.getenv("OPENAI_API_KEY").strip()
try:
    client = OpenAI(api_key=openai_api_key)
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
        system_msg = {
            "role": "system",
            "content": (
                "You are a real-time sports/politics news assistant. "
                "Cite sources in square brackets like [1]. Keep answers concise."
            ),
        }
        assistant_context_msg = {
            "role": "assistant",
            "content": f"Context:\n\n{context}",
        }
        user_msg = {"role": "user", "content": query}

        messages = [system_msg, assistant_context_msg, user_msg]

        try:
            # print("--- Sending request to OpenAI API ---")
            # print(f"Messages: {messages}") # Be careful logging sensitive data
            
            completion = client.chat.completions.create(
                model="gpt-4o-mini",      # or whatever you deploy
                messages=messages,
                temperature=0.25,
                max_tokens=250,
                stream=False,             # flip to True if you stream
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
