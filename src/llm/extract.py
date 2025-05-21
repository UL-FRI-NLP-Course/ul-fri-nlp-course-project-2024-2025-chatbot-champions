import nltk
# nltk.download()
nltk.download('punkt')
nltk.download('stopwords')
# !python -m spacy download sl_core_news_sm
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import spacy
nlp = spacy.load("sl_core_news_sm")

def extract_keywords(question):
  tokens = word_tokenize(question.lower())
  stop_words = set(stopwords.words('slovene'))
  keywords = [word for word in tokens if word.isalnum() and word not in stop_words]

  return keywords

def extract_pos(text):
  doc = nlp(text)
  keywords = []
  for token in doc:
    if token.pos_ in ["PROPN", "ADJ", "NOUN"]:
      keywords.append(token.text)
  return keywords

def extract_ner(text):
  doc = nlp(text)
  keywords = []
  for ent in doc.ents:
    keywords.append(ent.text)
  return keywords

def get_signals(q: str) -> list[str]:
    ner   = {e.text for e in nlp(q).ents}
    pos   = {t.text for t in nlp(q) if t.pos_ in {"PROPN", "NOUN", "ADJ"}}
    bare  = {w for w in word_tokenize(q.lower())
                 if w.isalnum() and w not in stopwords.words('slovene')}
    # Preserve original order while deduplicating
    seen, ordered = set(), []
    for tok in word_tokenize(q):
        if tok in ner|pos|bare and tok not in seen:
            ordered.append(tok); seen.add(tok)
    return ordered

if __name__ == "__main__":
    text = "Koliko točk je Luka Dončič zadel na zadnji tekmi?"
    keywords = extract_keywords(text)
    print("KW: ",keywords)
    pos = extract_pos(text)
    print("POS: ",pos)
    ner = extract_ner(text)
    print("NER: ",ner)