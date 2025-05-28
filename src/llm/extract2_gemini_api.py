import os
import time
import nltk
import spacy
from dotenv import load_dotenv
load_dotenv()
# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Load spaCy model
nlp = spacy.load("sl_core_news_sm")

# Import Gemini API client
from google import genai

# Initialize GenAI client using API key from environment
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")
client = genai.Client(api_key=api_key)


def call_gemma(prompt: str) -> str:
    """
    Sends a prompt to the Gemini model and returns the generated text.
    """
    response = client.models.generate_content(
        model="gemma-3-4b-it",
        contents=prompt,
    )
    return response.text.strip()


def grade_question(question: str) -> str:
    """
    Determines if a question is specific enough to be processed further.
    """
    prompt = f"""
Si natančen popravljalec vprašanj.
Tvoja naloga je razložiti zakaj je neko vprašanje slabo zastavljeno oziroma ga popraviti. 
Če je vprašanje preveč splošno to povej.

Odgovore obkroži s #.
Odgovori samo v eni vrstici.

######
Vprašanje: {question}
"""
    answer = call_gemma(prompt)
    try:
        return answer.split("######")[1].split("#")[1].strip()
    except Exception:
        return answer


def determine_ambiguity(question: str) -> str:
    """
    Determines if a question is too ambiguous and needs to be rewritten.
    """
    prompt = f"""
Si sistem za odločanje, ali je neko vprašanje preveč splošno ali ne.
Vhodi so v slovenščini.
Vprašanje je preveč splošno, če:
-je odgovor preveč zapleten
-ne določa teme dovolj natančno
-vsebuje samo ime neke osebe, ne pa priimka
Odgovori naj vsebujejo samo odgovor 'ok' ali 'ne'.
Odgovore obkroži s #.

####
- Vhod: {question}
"""
    answer = call_gemma(prompt)
    try:
        return answer.split("####")[1].split("#")[1].strip()
    except Exception:
        return answer


def extract_keywords(question: str) -> str:
    """
    Converts a question to a searchable query using an LLM.
    """
    prompt = f"""
Si sistem za izluščanje osebka iz vprašanja.
Vhodi so v slovenščini.
Tvoj cilj je iz vhodnega vprašanja izluščiti osebek v imenovalniku ednine.
Odgovori naj vsebujejo samo osebek.
Odgovori obkroži s #.

####
- Vhod: {question}
"""
    answer = call_gemma(prompt)
    try:
        return answer.split("####")[1].split("#")[1].strip()
    except Exception:
        return answer


def extract_ner(text: str) -> list[str]:
    """
    Extracts named entities from the text using spaCy.
    """
    doc = nlp(text)
    return [ent.text for ent in doc.ents]


def extract_keywords_from_text(text: str) -> list[str] | None:
    """
    Extracts keywords from the text. Uses spaCy NER first;
    if no entities found, checks ambiguity, then uses LLM.
    """
    keywords = extract_ner(text)
    if not keywords:
        amb = determine_ambiguity(text)
        if amb == "ok":
            kw = extract_keywords(text)
            return [kw]
        else:
            explanation = grade_question(text)
            print(explanation)
            return None
    return keywords


if __name__ == "__main__":
    start_time = time.time()

    questions = [
        "Kdo je zmagal na prejšnjem turnirju?",
        "Kje poteka prvenstvo?",
        "Kam je šel Janez?",
        "Kaj je glavno mesto moje države?",
        "Kam sem spravil denarnico?",
        "Kaj je glavno mesto slovenije?",
        "Koliko točk je dosegel Luka Dončič na zadnji tekmi?",
        "Kdo je zmagal na zadnjem svetovnem prvenstvu v nogometu?",
        "Kje se nahaja najvišja gora na svetu?",
        "Kdaj je bila ustanovljena Evropska unija?",
        "Kako se imenuje najnovejši film o Jamesu Bondu?",
    ]

    print("Question start time:", time.time() - start_time)
    for q in questions:
        t1 = time.time()
        print("----------------------------------------------------------------------------------------------")
        print("QUESTION:", q)
        keywords = extract_keywords_from_text(q)
        if keywords:
            print("KEYWORDS:", keywords)
        else:
            print("No keywords found or question is too ambiguous.")
        print("Time taken:", time.time() - t1)
