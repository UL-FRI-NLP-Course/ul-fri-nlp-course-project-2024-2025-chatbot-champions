import time

start_time = time.time()

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import nltk
# nltk.download()
nltk.download('punkt')
nltk.download('stopwords')
# !python -m spacy download sl_core_news_sm
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import spacy
nlp = spacy.load("sl_core_news_sm")

def grade_question(question, model=None, tokenizer=None, temperature=0.0, max_tokens=1000):
    """
    Determines if a question is specific enough to be processed further.
    """
    
    if model is None or tokenizer is None:
        return "This is a placeholder answer, model or tokenizer not provided."
    
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
    prompt = prompt.format(question=question)
    input_ids = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    outputs = model.generate(**input_ids, max_new_tokens=max_tokens, temperature=temperature)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    #print(answer)

    return answer.split("######")[1].split("#")[1].strip()

def determine_ambiguity(question,model=None,tokenizer=None,temperature=0.0,max_tokens=1000):
    """
    Determines if a question is too ambigous and needs to be rewritten.
    """

    if model is None or tokenizer is None:
        return "This is a placeholder answer, model or tokenizer not provided."
    
    question = question.rstrip("?")

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

        ####
        Tu je vhod, določi ali je preveč splošen ali ne:
        - Vhod: {question}
        """
    prompt = prompt.format(question=question)
    input_ids = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    outputs = model.generate(**input_ids, max_new_tokens=max_tokens, temperature=temperature)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    #print(answer)
    return answer.split("####")[1].split("- Izhod:")[1].split("#")[1].strip()


def extract_keywords(question, model=None, tokenizer=None, temperature=0.0, max_tokens=1000):
    """
    Converts a question to a searchable query using an LLM.
    """
    
    if model is None or tokenizer is None:
        return "This is a placeholder answer, model or tokenizer not provided."
    
    question = question.rstrip("?")

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
    prompt = prompt.format(question=question)
    input_ids = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    outputs = model.generate(**input_ids, max_new_tokens=max_tokens, temperature=temperature)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    #print(answer)
    return answer.split("####")[1].split("- Izhod:")[1].split("#")[1].strip()

def extract_ner(text):
  """
  Extracts named entities from the text using spaCy.
  """
  doc = nlp(text)
  keywords = []
  for ent in doc.ents:
    keywords.append(ent.text)
  return keywords

def extract_keywords_from_text(text, model=None, tokenizer=None):
  """
  Extracts keywords from the text. First it tries to extract named entities using spaCy,
  if no named entities are found, it checks if question is too ambiguous.
  if it is, it explains why it is ambiguous.
  If it is not ambiguous, it extracts keywords using an LLM.
  """
  keywords = extract_ner(text)
  if not keywords:
    # If no named entities are found, check if the question is too ambiguous
    amb = determine_ambiguity(text, model=model, tokenizer=tokenizer)
    if amb == "ok":
      # If the question is not ambiguous, extract keywords using an LLM
      keywords = extract_keywords(text, model=model, tokenizer=tokenizer)
    else:
      explanation = grade_question(text, model=model, tokenizer=tokenizer)
      print(explanation)
      return None
  return keywords

if __name__ == "__main__":
    
    model_name = "google/gemma-2-2b-it"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )

    questions=[
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

    print("Question start time: ",time.time()-start_time)

    for q in questions:
        t1=time.time()
        print("----------------------------------------------------------------------------------------------")
        print("QUESTION: ",q)
        
        keywords = extract_keywords_from_text(q,model=model,tokenizer=tokenizer)
        if keywords:
            print("KEYWORDS: ", keywords)
        else:
            print("No keywords found or question is too ambiguous.")
        print("Time taken: ",time.time()-t1)


# Question start time:  778.6557877063751
# ----------------------------------------------------------------------------------------------
# QUESTION:  Kdo je zmagal na prejšnjem turnirju?
# Vprašanje je preveč splošno, ker ne navaja, o katerem turnirju gre.
# No keywords found or question is too ambiguous.
# Time taken:  325.22353768348694
# ----------------------------------------------------------------------------------------------
# QUESTION:  Kje poteka prvenstvo?
# Vprašanje je preveč splošno, ker ne navaja, o katerem prvenstvu gre. Ali ste mislili: Kje poteka prvenstvo v košarki?
# No keywords found or question is too ambiguous.
# Time taken:  31.472512245178223
# ----------------------------------------------------------------------------------------------
# QUESTION:  Kam je šel Janez?
# KEYWORDS:  ['Janez']
# Time taken:  0.1322321891784668
# ----------------------------------------------------------------------------------------------
# QUESTION:  Kaj je glavno mesto moje države?
# Vprašanje je preveč splošno, ker ne navaja, katero državo se govori. Ali ste mislili: Kaj je glavno mesto Slovenije?
# No keywords found or question is too ambiguous.
# Time taken:  58.897807359695435
# ----------------------------------------------------------------------------------------------
# QUESTION:  Kam sem spravil denarnico?
# Vprašanje je preveč splošno. Kateri denarnico?
# No keywords found or question is too ambiguous.
# Time taken:  74.36941981315613
# ----------------------------------------------------------------------------------------------
# QUESTION:  Kaj je glavno mesto slovenije?
# KEYWORDS:  ['slovenije']
# Time taken:  0.005627632141113281
# ----------------------------------------------------------------------------------------------
# QUESTION:  Koliko točk je dosegel Luka Dončič na zadnji tekmi?
# KEYWORDS:  ['Luka Dončič']
# Time taken:  0.004616498947143555
# ----------------------------------------------------------------------------------------------
# QUESTION:  Kdo je zmagal na zadnjem svetovnem prvenstvu v nogometu?
# KEYWORDS:  Zmagal na zadnjem svetovnem prvenstvu v nogometu
# Time taken:  18.207677125930786
# ----------------------------------------------------------------------------------------------
# QUESTION:  Kje se nahaja najvišja gora na svetu?
# KEYWORDS:  Mount Everest
# Time taken:  44.27122640609741
# ----------------------------------------------------------------------------------------------
# QUESTION:  Kdaj je bila ustanovljena Evropska unija?
# KEYWORDS:  ['Evropska unija']
# Time taken:  0.005578517913818359
# ----------------------------------------------------------------------------------------------
# QUESTION:  Kako se imenuje najnovejši film o Jamesu Bondu?
# KEYWORDS:  ['Jamesu Bondu']
# Time taken:  0.00446319580078125
