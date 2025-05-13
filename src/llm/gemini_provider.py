# llm/gemini_provider.py
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from .base import LLMProvider
from typing import List, Dict, Optional

load_dotenv()

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        # self.model = client.get_model(model_name)
#         self.model = genai.mod (
#         model_name="gemini-2.0-pro-001",
#         system_instruction=(
#             "You are a real-time sports/politics news assistant. "
#             "Cite sources in square brackets like [1]. Keep answers concise."
#         )
# )

    def generate_answer(
        self, query: str, context: str, history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    # 1️⃣ system prompt – sets the tone
                    "You are a concise assistant. Reply in Slovenian with a single sentence that directly answers the question. "
                    "Do NOT add explanations, reasoning, citations, or extra text.",
                    
                    # 2️⃣ knowledge the model can use
                    f"Context:\n{context}",
                    
                    # 3️⃣ the actual user question
                    f"Question:\n{query}"
                ]
            )
            # response = self.client.models.generate_content(
            #     [
            #         {"role": "system", "parts": [self.system_prompt]},
            #         {"role": "user",   "parts": [f"Context:\n\n{context}"]},
            #         {"role": "user",   "parts": [query]},
            #     ],
            #     generation_config=genai.GenerationConfig(
            #         temperature=0.25,
            #         max_output_tokens=250,
            #     ),
            # )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating answer: {e}")
            raise RuntimeError(
                "Gemini client failed to initialize. Check API key and connectivity."
            )
