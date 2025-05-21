from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

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

if __name__ == "__main__":
    
    model_name = "google/gemma-2-2b-it"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )

    questions=[
        "Kdo je zmagal na prejšnjem turnirju?",                 # Vprašanje je preveč splošno, ker ne navaja, o katerem turnirju gre.
        "Kje poteka prvenstvo?",                                # Vprašanje je preveč splošno, ker ne navaja, o katerem prvenstvu gre. Ali ste mislili: Kje poteka prvenstvo v košarki?
        "Kam je šel janez?",                                    # Vprašanje je preveč splošno. Kateri Janez vas zanima?
        "Kaj je glavno mesto moje države?",                     # Vprašanje je preveč splošno, ker ne navaja, katero državo se govori. Ali ste mislili: Kaj je glavno mesto Slovenije?
        "Kam sem spravil denarnico?"                            # Vprašanje je preveč splošno. Kateri denarnico?
    ]

    for q in questions:
        print("----------------------------------------------------------------------------------------------")
        a=grade_question(
            question=q,
            model=model,
            tokenizer=tokenizer,
            temperature=0.0
        )

        print("\n\nFINAL ANSWER: ",a)
        print("\n----------------------------------------------------------------------------------------------")
