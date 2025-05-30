from typing import List, Tuple
from main import get_answer
import sacrebleu
from rouge_score import rouge_scorer
import statistics
# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

# Placeholder Q&A pairs – update the answers to the correct statistics before use.
QA_PAIRS: List[Tuple[str, List[str]]] = [
    (
        "Koliko točk je Luka Dončić zadel na zadnji tekmi?",
        [
            "Luka Dončić je dosegel 28 točk v zadnji tekmi proti Minnesota Timberwolves.",
            "Na zadnji tekmi proti Minnesota Timberwolves je Luka Dončić dosegel 28 točk.",
            "Luka Dončić je na zadnji tekmi dosegel 28 točk.",
            "Na zadnji tekmi je Luka Dončić dosegel 28 točk proti Minnesota Timberwolves.",
            "Dončić je na zadnji tekmi dosegel 28 točk.",
            "Luka Dončić je dosegel 28 točk.",
        ],
    ),
    (
        "Koliko golov je Anže Kopitar dosegel na zadnji tekmi Los Angeles Kings?",
        [
            "Anže Kopitar je dosegel 1 gol na zadnji tekmi proti Edmonton Oilers.",
            "Na zadnji tekmi proti Edmonton Oilers je Anže Kopitar dosegel 1 gol.",
            "Kopitar je na zadnji tekmi dosegel 1 gol.",
            "Anže Kopitar je dosegel 1 gol.",
        ],
    ),
    (
        "Kateri slovenski kolesar je zmagal zadnjo etapo Dirke po Franciji?",
        [
            "Tadej Pogačar je zmagal zadnjo etapo Dirke po Franciji.",
            "Zadnjo etapo Dirke po Franciji je zmagal Tadej Pogačar.",
            "Zadnjo etapo je zmagal slovenski kolesar Tadej Pogačar.",
            "Slovenski kolesar Tadej Pogačar je bil zmagovalec zadnje etape.",
            "Ni v kontekstu.",
            "Ni dovolj konteksta.",
            "Ni v podanem kontekstu."
        ],
    ),
    (
        "Katero mesto je Ilka Štuhec osvojila na zadnjem smuku?",
        [
            "Osvojila je 11. mesto.",
            "Na zadnjem smuku je Ilka Štuhec osvojila 11. mesto.",
            "Ilka Štuhec je na zadnjem smuku zasedla 11. mesto.",
        ],
    ),
    (
        "Koliko obramb je zbral Jan Oblak na zadnji tekmi Atletico Madrida?",
        [
            "Jan Oblak je zbral 6 obramb v zadnji tekmi Atlético Madrid–Real Betis.",
            "Na zadnji tekmi Atlético Madrid–Real Betis je Jan Oblak zbral 6 obramb.",
            "Oblak je na zadnji tekmi zbral 6 obramb.",
            "Jan Oblak je zbral 6 obramb.",
        ],
    ),
    (
        "Koliko točk je Žiga Jelar osvojil na zadnji tekmi svetovnega pokala v smučarskih skokih?",
        [
            "Žiga Jelar na zadnji tekmi svetovnega pokala ni osvojil nobene točke – ostal je brez uvrstitvenih mest.",
            "Na zadnji tekmi svetovnega pokala v smučarskih skokih Žiga Jelar ni osvojil točk.",
            "Žiga Jelar na zadnji tekmi svetovnega pokala ni dosegel točk.",
        ],
    ),
    (
        "Koliko golov je Benjamin Šeško dosegel na zadnji tekmi RB Leipziga?",
        [
            "Benjamin Šeško na zadnji tekmi RB Leipziga ni dosegel nobenega gola.",
            "Na zadnji tekmi RB Leipziga Benjamin Šeško ni dosegel nobenega gola.",
            "Benjamin Šeško ni dosegel nobenega gola na zadnji tekmi.",
        ],
    ),
    (
        "Koliko točk je Dončić dosegel na predzadnji tekmi?",
        [
            "Dončič je dosegel 38 točk na predzadnji tekmi.",
            "Na predzadnji tekmi je Luka Dončić dosegel 38 točk.",
            "Luka Dončić je na predzadnji tekmi dosegel 38 točk.",
            "Na predzadnji tekmi je Luka Dončić dosegel 38 točk proti Minnesota Timberwolves.",
            "Luka Dončić je dosegel 38 točk.",
        ],
    ),
    (
        "Proti kateri ekipi je Luka Dončić nazadnje igral?",
        [
            "Luka Dončić je nazadnje igral proti Minnesota Timberwolves.",
            "Nazadnje je Luka Dončić igral proti Minnesota Timberwolves.",
            "Dončić je zadnjo tekmo igral proti Minnesota Timberwolves.",
            "Luka Dončić je igral proti Minnesota Timberwolves.",
        ],
    ),
    (
        "Proti kateri ekipi je Benjamin Šeško nazadnje igral?",
        [
            "Igral je proti Stuttgartu.",
            "Benjamin Šeško je nazadnje igral proti Stuttgartu.",
            "Nazadnje je Benjamin Šeško igral proti Stuttgartu.",
            "Šeško je zadnjo tekmo igral proti Stuttgartu.",
        ],
    ),
    (
        "Proti kateri ekipi je Anže Kopitar nazadnje igral?",
        [
            "Anže Kopitar je nazadnje igral proti Edmonton Oilers.",
            "Nazadnje je Anže Kopitar igral proti Edmonton Oilers.",
            "Kopitar je zadnjo tekmo igral proti Edmonton Oilers.",
            "Anže Kopitar je igral proti Edmonton Oilers.",
        ],
    ),
]

BLEU_THRESHOLD = 10.0
ROUGE_L_THRESHOLD = 0.5

def evaluate_metrics(
    model_answer: str,
    expected_refs: List[str]
) -> Tuple[float, float, float, float]:
    # 1) BLEU with multiple refs
    # sacrebleu expects List[List[str]] for corpus_bleu, but for sentence_bleu it takes List[str]
    bleu = sacrebleu.sentence_bleu(model_answer, expected_refs).score

    # 2) ROUGE: score each ref, then take the max F1 across them
    scorer = rouge_scorer.RougeScorer(
        ['rouge1','rouge2','rougeL'], use_stemmer=True
    )
    best_r1, best_r2, best_rl = 0.0, 0.0, 0.0

    for ref in expected_refs:
        scores = scorer.score(ref, model_answer)
        best_r1 = max(best_r1, scores['rouge1'].fmeasure)
        best_r2 = max(best_r2, scores['rouge2'].fmeasure)
        best_rl = max(best_rl, scores['rougeL'].fmeasure)

    return bleu, best_r1, best_r2, best_rl

def is_correct_flag(bleu: float, rougel: float,
                    bleu_thr: float = BLEU_THRESHOLD,
                    rougel_thr: float = ROUGE_L_THRESHOLD) -> bool:
    """
    Returns True if both BLEU and ROUGE-L scores meet thresholds.
    """
    return bleu >= bleu_thr and rougel >= rougel_thr


def run_evaluation():
    total = len(QA_PAIRS)
    bleu_scores, rouge1_scores, rouge2_scores, rougel_scores = [], [], [], []
    correct_count = 0

    print("\nRunning evaluation with BLEU, ROUGE & correctness flag…\n")
    for idx, (question, expected) in enumerate(QA_PAIRS, start=1):
        hypothesis = get_answer(question, [], scrape_k=50)
        bleu, r1, r2, rl = evaluate_metrics(hypothesis, expected)
        is_correct = is_correct_flag(bleu, rl)

        bleu_scores.append(bleu)
        rouge1_scores.append(r1)
        rouge2_scores.append(r2)
        rougel_scores.append(rl)
        correct_count += int(is_correct)

        status = "✅" if is_correct else "❌"
        print(f"{idx:2}. {status} Q: {question}")
        print(f"   → Model Answer: {hypothesis}")
        print(f"   → Expected    : {expected}")
        print(f"   ↳ BLEU    : {bleu:.2f}")
        print(f"   ↳ ROUGE-1: {r1:.3f}, ROUGE-2: {r2:.3f}, ROUGE-L: {rl:.3f}\n")

    print("─" * 60)
    # Overall metrics
    avg_bleu = statistics.mean(bleu_scores) if bleu_scores else 0
    avg_r1 = statistics.mean(rouge1_scores) if rouge1_scores else 0
    avg_r2 = statistics.mean(rouge2_scores) if rouge2_scores else 0
    avg_rl = statistics.mean(rougel_scores) if rougel_scores else 0

    print("Aggregate scores:")
    print(f"  * Average BLEU    : {avg_bleu:.2f}")
    print(f"  * Avg ROUGE-1 F1  : {avg_r1:.3f}")
    print(f"  * Avg ROUGE-2 F1  : {avg_r2:.3f}")
    print(f"  * Avg ROUGE-L F1  : {avg_rl:.3f}\n")
    
    accuracy = correct_count / total * 100
    print(f"Correct/Total: {correct_count}/{total} => Accuracy: {accuracy:.1f}%\n")


if __name__ == "__main__":
    run_evaluation()
