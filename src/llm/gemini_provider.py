# llm/gemini_provider.py
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from .base import LLMProvider
from typing import List, Dict, Optional

load_dotenv()

_SYSTEM_PROMPT = (
    "You are a concise assistant. Reply in Slovenian and tailor your answers to the user's specific question, summarizing and synthesizing the most relevant points from the provided context rather than verbatim quoting."
    "You may also expand upon the answer slightly if it helps clarify or provide useful additional information, but always stay relevant to the question and context.\n"
    # "Answer: {answer}\nFound in: {sentence where the answer was found}\n"
    "The context is a list of articles, each formatted as follows:\n"
    "[DATE: <date>]\nTITLE: <title>\nSUBTITLE: <subtitle>\nSUBCATEGORY: <subcategory>\n"
    "URL: <url>\nAUTHOR: <author>\nSECTION: <section>\nRECAP: <recap>\nCONTENT: <content>\n"
    "When searching for answers, the 'CONTENT' field of each article will most likely contain the answer, but other fields (such as DATE, SUBTITLE, AUTHOR, etc.) can also be used if relevant.\n"
    # "When referencing where the answer was found, provide the exact sentence from the 'CONTENT' field.\n"
    "For ordering articles by date, always use the value in the [DATE: ...] field.\n"
    "Do not add explanations, justifications, citations, or any additional text outside the required format.\n"
    "If the answer is not present or relevant in the context, reply with exactly \"Ni v podanem kontekstu\"."
)

class GeminiProvider(LLMProvider):
    def __init__(self):
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            print(f"Error initializing Gemini client: {e}")
            raise RuntimeError(
                "Gemini client failed to initialize. Check API key and connectivity."
            )
        models = self.client.models.list()
        print("Available models:")
        for model in models:
            print(f"- {model.name} ({model.display_name})")
        models_to_test = []
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
                model="gemini-1.5-flash-latest",
                contents=[
                    _SYSTEM_PROMPT,                    
                    f"Context:\n{context}",                    
                    f"Question:\n{query}"
                ]
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating answer: {e}")
