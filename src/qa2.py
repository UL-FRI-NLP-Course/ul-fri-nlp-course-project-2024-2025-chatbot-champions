from typing import List, Tuple
from main import get_answer
from difflib import SequenceMatcher
# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

# Placeholder Q&A pairs – update the answers to the correct statistics before use.
QA_PAIRS: List[Tuple[str, str]] = [
    (
        "Koliko točk je Luka Dončić zadel na zadnji tekmi?",
        "Luka Dončić je zadel 28 točk na zadnji tekmi proti Minnesoti.",
    ),
# NER Keywords:  ['Luka Dončić']
# Keyword Keywords:  ['točk', 'luka', 'dončić', 'zadel', 'zadnji', 'tekmi']
# POS Keywords:  ['točk', 'Luka', 'Dončić', 'zadnji', 'tekmi']
    (
        "Koliko golov je Anže Kopitar dosegel na zadnji tekmi Los Angeles Kings?",
        "Anže Kopitar je dosegel dva gola.",
    ),
# NER Keywords:  ['Anže Kopitar', 'Los Angeles Kings']
# Keyword Keywords:  ['golov', 'anže', 'kopitar', 'dosegel', 'zadnji', 'tekmi', 'los', 'angeles', 'kings']
# POS Keywords:  ['golov', 'Anže', 'Kopitar', 'zadnji', 'tekmi', 'Los', 'Angeles', 'Kings']
    (
        "Kateri slovenski kolesar je zmagal zadnjo etapo Dirke po Franciji?",
        "Tadej Pogačar je osvojil zadnjo etapo Toura.",
    ),
# NER Keywords:  ['Dirke po Franciji']
# Keyword Keywords:  ['slovenski', 'kolesar', 'zmagal', 'zadnjo', 'etapo', 'dirke', 'franciji']
# POS Keywords:  ['slovenski', 'kolesar', 'zadnjo', 'etapo', 'Dirke', 'Franciji']
    (
        "Koliko točk je Tadej Pogačar zbral na zadnji dirki Liège-Bastogne-Liège?",
        "Pogačar je zbral 60 točk za lestvico UCI.",
    ),
# NER Keywords:  ['Tadej Pogačar', 'Liège', 'Bastogne']
# Keyword Keywords:  ['točk', 'tadej', 'pogačar', 'zbral', 'zadnji', 'dirki']
# POS Keywords:  ['točk', 'Tadej', 'Pogačar', 'zadnji', 'dirki', 'Liège', 'Bastogne', 'Liège']
    (
        "Katero mesto je Ilka Štuhec osvojila na zadnjem smuku v Kvitfjellu?",
        "Ilka Štuhec je bila tretja.",
    ),
# NER Keywords:  ['Ilka Štuhec', 'Kvitfjellu']
# Keyword Keywords:  ['mesto', 'ilka', 'štuhec', 'osvojila', 'zadnjem', 'smuku', 'kvitfjellu']
# POS Keywords:  ['mesto', 'Ilka', 'Štuhec', 'zadnjem', 'smuku', 'Kvitfjellu']
    (
        "Koliko točk je Rok Možič dosegel na zadnji tekmi italijanskega prvenstva?",
        "Rok Možič je dosegel 21 točk.",
    ),
# NER Keywords:  ['Rok Možič']
# Keyword Keywords:  ['točk', 'rok', 'možič', 'dosegel', 'zadnji', 'tekmi', 'italijanskega', 'prvenstva']
# POS Keywords:  ['točk', 'Rok', 'Možič', 'zadnji', 'tekmi', 'italijanskega', 'prvenstva']
    (
        "Katero mesto je Tim Gajser osvojil na zadnji dirki MXGP v Lommlu?",
        "Tim Gajser je bil prvi.",
    ),
# NER Keywords:  ['Tim Gajser', 'Lommlu']
# Keyword Keywords:  ['mesto', 'tim', 'gajser', 'osvojil', 'zadnji', 'dirki', 'mxgp', 'lommlu']
# POS Keywords:  ['mesto', 'Tim', 'Gajser', 'zadnji', 'dirki', 'MXGP', 'Lommlu']
    (
        "Koliko golov je slovenska ženska rokometna reprezentanca dosegla na zadnji tekmi evropskega prvenstva?",
        "Slovenke so dosegle 27 golov.",
    ),
# NER Keywords:  []
# Keyword Keywords:  ['golov', 'slovenska', 'ženska', 'rokometna', 'reprezentanca', 'dosegla', 'zadnji', 'tekmi', 'evropskega', 'prvenstva']
# POS Keywords:  ['golov', 'slovenska', 'ženska', 'rokometna', 'reprezentanca', 'zadnji', 'tekmi', 'evropskega', 'prvenstva']
    (
        "Koliko obramb je zbral Jan Oblak na zadnji tekmi Atletica Madrida?",
        "Jan Oblak ni imel veliko dela in ni ubranil nobenega strela.",
    ),
# NER Keywords:  ['Jan Oblak', 'Atletica Madrida']
# Keyword Keywords:  ['obramb', 'zbral', 'jan', 'oblak', 'zadnji', 'tekmi', 'atletica', 'madrida']
# POS Keywords:  ['obramb', 'Jan', 'Oblak', 'zadnji', 'tekmi', 'Atletica', 'Madrida']
    (
        "Koliko točk je Žiga Jelar osvojil na zadnji tekmi svetovnega pokala v smučarskih skokih?",
        "Žiga Jelar je osvojil 32 točk.",
    ),
# NER Keywords:  ['Žiga Jelar']
# Keyword Keywords:  ['točk', 'žiga', 'jelar', 'osvojil', 'zadnji', 'tekmi', 'svetovnega', 'pokala', 'smučarskih', 'skokih']
# POS Keywords:  ['točk', 'Žiga', 'Jelar', 'zadnji', 'tekmi', 'svetovnega', 'pokala', 'smučarskih', 'skokih']
    (
        "Katero mesto je Urša Bogataj osvojila na zadnji tekmi svetovnega pokala v smučarskih skokih?",
        "Urša Bogataj je bila druga.",
    ),
# NER Keywords:  ['Urša Bogataj']
# Keyword Keywords:  ['mesto', 'urša', 'bogataj', 'osvojila', 'zadnji', 'tekmi', 'svetovnega', 'pokala', 'smučarskih', 'skokih']
# POS Keywords:  ['mesto', 'Urša', 'Bogataj', 'zadnji', 'tekmi', 'svetovnega', 'pokala', 'smučarskih', 'skokih']
    (
        "Koliko sekund zaostanka je imel Primož Roglič na kronometru zadnjega dne Gira?",
        "Zaostal je za 14 sekund.",
    ),
# NER Keywords:  ['Primož Roglič', 'Gira']
# Keyword Keywords:  ['sekund', 'zaostanka', 'imel', 'primož', 'roglič', 'kronometru', 'zadnjega', 'dne', 'gira']
# POS Keywords:  ['sekund', 'zaostanka', 'Primož', 'Roglič', 'kronometru', 'zadnjega', 'dne', 'Gira']
    (
        "Koliko točk je Cedevita Olimpija dosegla na zadnji tekmi ABA lige?",
        "Cedevita Olimpija je dosegla 89 točk.",
    ),
# NER Keywords:  ['Cedevita Olimpija', 'ABA']
# Keyword Keywords:  ['točk', 'cedevita', 'olimpija', 'dosegla', 'zadnji', 'tekmi', 'aba', 'lige']
# POS Keywords:  ['točk', 'Cedevita', 'Olimpija', 'zadnji', 'tekmi', 'ABA', 'lige']
    (
        "Koliko golov je dosegla slovenska hokejska reprezentanca na zadnji pripravljalni tekmi?",
        "Reprezentanca je dosegla tri gole.",
    ),
# NER Keywords:  []
# Keyword Keywords:  ['golov', 'dosegla', 'slovenska', 'hokejska', 'reprezentanca', 'zadnji', 'pripravljalni', 'tekmi']
# POS Keywords:  ['golov', 'slovenska', 'hokejska', 'reprezentanca', 'zadnji', 'pripravljalni', 'tekmi']
    (
        "Koliko golov je Benjamin Šeško dosegel na zadnji tekmi RB Leipziga?",
        "Benjamin Šeško ni dosegel gola.",
    ),
# NER Keywords:  ['Benjamin Šeško', 'RB Leipziga']
# Keyword Keywords:  ['golov', 'benjamin', 'šeško', 'dosegel', 'zadnji', 'tekmi', 'rb', 'leipziga']
# POS Keywords:  ['golov', 'Benjamin', 'zadnji', 'tekmi', 'RB', 'Leipziga']
]

def is_correct(model_answer: str, expected: str, query: str, threshold: float = 0.55) -> bool:
    """
    Returns True if the model_answer is sufficiently similar to expected.
    Uses a similarity threshold (default 0.8).
    """
    model = model_answer.lower().replace(query.lower(), "").rstrip(".")
    exp = expected.lower().replace(query.lower(), "").rstrip(".")
    similarity = SequenceMatcher(None, model, exp).ratio()
    return similarity >= threshold


def run_evaluation():
    total = len(QA_PAIRS)
    correct = 0

    print("\nRunning evaluation…\n")
    for idx, (question, expected) in enumerate(QA_PAIRS, start=1):
        answer, keyword = get_answer(question, [])
        ok = is_correct(answer, expected, keyword)
        correct += int(ok)

        status = "✅" if ok else "❌"
        print(f"{idx:2}. {status} Q: {question}")
        print(f"   → Model:    {answer}")
        print(f"   → Expected: {expected}\n")

    print("─" * 60)
    print(f"Accuracy: {correct}/{total} = {correct / total:.0%}\n")


if __name__ == "__main__":
    run_evaluation()
