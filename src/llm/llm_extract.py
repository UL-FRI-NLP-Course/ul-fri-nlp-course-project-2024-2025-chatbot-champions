from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def extract_keywords(question, model=None, tokenizer=None, temperature=0.0, max_tokens=1000):
    """
    Converts a question to a searchable query using a LLM.
    """
    
    if model is None or tokenizer is None:
        return "This is a placeholder answer, model or tokenizer not provided."
    
    prompt="""
        Si sistem za generiranje povzetkov, ki bodo uporabljeni za iskanje po spletu.
        Vhodi in povzetki so v slovenščini.
        Tvoj cilj je iz vhoda izluščiti ključne informacije in jih povzeti v nekaj besedah.
        Odgovori naj bodo strukturirani kot poizvedba na spletnem brskalniku.

        Primeri:
        - Vhod: Kaj se je zgodilo ko je Luka Dončič prejšnji teden obiskal Slovenijo?
        - Izhod: Luka Dončič obišče Slovenijo

        - Vhod: Kaj je predsednik vlade izjavil o novem zakonu?
        - Izhod: Predsednik vlade izjavi o novem zakonu

        - Vhod: Kakšne so posledice podnebnih sprememb na Arktiki?
        - Izhod: Posledice podnebnih sprememb na Arktiki

        - Vhod: Kako je potekala zadnja seja Združenih narodov?
        - Izhod: Seja Združenih narodov

        - Vhod: Kateri ukrepi so bili sprejeti za izboljšanje javnega zdravstva?
        - Izhod: Ukrepi za izboljšanje javnega zdravstva

        - Vhod: Kako so se odzvali na zadnje spremembe zakonodaje o delovnih razmerjih?
        - Izhod: Odzivi na spremembe zakonodaje o delovnih razmerjih

        - Vhod: Kako je potekala zadnja razprava o reformi izobraževalnega sistema?
        - Izhod: Razprava o reformi izobraževalnega sistema

        - Vhod: Kakšne so bile posledice zadnje gospodarske krize?
        - Izhod: Posledice zadnje gospodarske krize

        ####
        Tu je vhod, iz njega izlušči ključne informacije in jih povzemi v nekaj besedah:
        - Vhod: {question}
        """
    prompt = prompt.format(question=question)
    input_ids = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    outputs = model.generate(**input_ids, max_new_tokens=max_tokens, temperature=temperature)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    #print(answer)
    return answer.split("####")[1].split("- Izhod:")[1].strip()

if __name__ == "__main__":
    
    model_name = "google/gemma-2-2b-it"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )

    questions=[
        "Kakšne so posledice nedavnega potresa v Turčiji?",     # Output: Posledice potresa v Turčiji
        "Kakšna je nova strategija za digitalizacijo?",         # Output: Nova strategija za digitalizacijo
        "Kdo je bil prvi predsednik Slovenije?"                 # Output: Prvi predsednik Slovenije je Milan Kučan.
    ]

    for q in questions:
        a=extract_keywords(
            question=q,
            model=model,
            tokenizer=tokenizer,
            temperature=0.1
        )

        print("\n\nFINAL ANSWER: ",a)
