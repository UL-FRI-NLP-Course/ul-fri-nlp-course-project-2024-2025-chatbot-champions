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
    prompt="""
        Si natančen popravljalec vprašanj.
        Tvoja naloga je razložiti zakaj je neko vprašanje slabo zastavljeno oziroma ga popraviti. 
        Če je vprašanje preveč splošno to povej.
        
        Odgovore obkroži s #.
        Odgovori samo v eni vrstici.

        Primeri:
        Vprašanje: Kaj je življenje?
        Odgovor: #Vprašanje je preveč splošno, ker je odgovor lahko neskončen in zahteva široko razlago. Ali ste mislili: Kako se je začelo življenje?#
        Vprašanje: Povej mi vse o zgodovini.
        Odgovor: #Vprašanje je preveč splošno, ker pokriva široko področje in zahteva obsežno raziskavo. Ali ste mislili: Kaj preučuje veda zgodovina?#
        Vprašanje: Kdo je včeraj zmagal na tekmi?
        Odgovor: #Vprašanje je preveč splošno, ker ne navaja, o kateri tekmi se govori.#
        Vprašanje: Kdaj je bil izumljen telefon?
        Odgovor: #Vprašanje se ne nanaša na osebo, dogodek, organizacijo, ...#
        Vprašanje: Kakšne so posledice podnebnih sprememb?
        Odgovor: #Vprašanje se ne nanaša na osebo, dogodek, organizacijo, ...#
        Vprašanje: Kako naj se pripravim na izpit?
        Odgovor: #Vprašanje je preveč splošno, ker ne navaja, za kateri izpit gre.#
        Vprašanje: Kje je Peter?
        Odgovor: #Vprašanje je preveč splošno. Kateri Peter vas zanima?#

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
    prompt="""
        Si sistem za odločanje, ali je neko vprašanje preveč splošno ali ne.
        Vhodi so v slovenščini.
        Vprašanje je preveč splošno, če:
        -je odgovor preveč zapleten
        -ne določa teme dovolj natančno
        -vsebuje samo ime neke osebe, ne pa priimka
        Odgovori naj vsebujejo samo odgovor 'ok' ali 'ne'.
        Na vprašanja ne odgovrajaj, ampak samo vrni odgovor.
        Izogibaj se odgovarjanju s programsko kodo.
        Odgovore obkroži s #.

        Primeri:
        - Vhod: Kaj se je zgodilo ko je luka dončič prejšnji teden obiskal Slovenijo
        - Izhod: #ok#

        - Vhod: Kaj je predsednik vlade izjavil o novem zakonu
        - Izhod: #ok#

        - Vhod: Kakšne so posledice podnebnih sprememb na Arktiki
        - Izhod: #ok#

        - Vhod: Kako je potekala zadnja seja Združenih narodov
        - Izhod: #ok#

        - Vhod: Kateri ukrepi so bili sprejeti za izboljšanje javnega zdravstva
        - Izhod: #ok#

        - Vhod: Kako so se odzvali na zadnje spremembe zakonodaje
        - Izhod: #ne#

        - Vhod: Kako je potekala zadnja razprava
        - Izhod: #ne#

        - Vhod: Kakšne so bile posledice zadnje krize
        - Izhod: #ne#

        - Vhod: Kje je Peter
        - Izhod: #ne#

        - Vhod: Kaj dela Jure Dolinar
        - Izhod: #ok#

        - Vhod: Na katerem mestu je končal Primož Roglič
        - Izhod: #ok#

        - Kje se nahaja največji slap na svetu
        - Izhod: #ok#

        - Vhod: Kdaj je bil izdan zadnji album Adele
        - Izhod: #ok#
        
        - Vhod: Proti komu je na zadnji tekmi igral luka dončič
        - Izhod: #ok#

        - Vhod: Koliko točk je dosegel peter prevc prejšnji teden
        - Izhod: #ok#

        ####
        Tu je vhod, določi ali je preveč splošen ali ne:
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
    prompt="""
        Si sistem za izluščanje osebka iz vprašanja.
        Vhodi so v slovenščini.
        Tvoj cilj je iz vhodnega vprašanja izluščiti osebek v imenovalniku ednine.
        Odgovori naj vsebujejo samo osebek.
        Na vprašanja ne odgovrajaj, ampak samo izlušči osebek.
        V odgovorih naj bo samo osebek, brez dodatnih besed.
        Izogibaj se odgovarjanju s programsko kodo.
        Odgovore obkroži s #.

        Primeri:
        - Vhod: Kaj se je zgodilo ko je luka dončič prejšnji teden obiskal Slovenijo
        - Izhod: #Luka Dončič#

        - Vhod: Kaj je predsednik vlade izjavil o novem zakonu
        - Izhod: #Predsednik vlade#

        - Vhod: Kakšne so posledice podnebnih sprememb na Arktiki
        - Izhod: #Podnebne spremembe#

        - Vhod: Kako je potekala zadnja seja Združenih narodov
        - Izhod: #Seja Združenih narodov#

        - Vhod: Kateri ukrepi so bili sprejeti za izboljšanje javnega zdravstva
        - Izhod: #Ukrepi za izboljšanje javnega zdravstva#

        - Vhod: Kako so se odzvali na zadnje spremembe zakonodaje o delovnih razmerjih
        - Izhod: #Spremembe zakonodaje o delovnih razmerjih#

        - Vhod: Kako je potekala zadnja razprava o reformi izobraževalnega sistema
        - Izhod: #Razprava o reformi izobraževalnega sistema#

        - Vhod: Kakšne so bile posledice zadnje gospodarske krize
        - Izhod: #Zadnja gospodarska kriza#

        - Vhod: Kje je Peter?
        - Izhod: #Peter#

        ####
        Tu je vhod, iz njega izlušči osebek v imenovalniku ednine:
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
