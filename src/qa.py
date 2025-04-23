from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def answer(question, context, model=None, tokenizer=None, temperature=0.0, max_tokens=1000):
    """
    Function to answer a question based on the provided context using a language model.
    
    Parameters:
        question: The question to be answered.
        context: The context in which the question is asked.
        model: The language model to be used for answering the question.
        temperature: The temperature for the language model's response.
        max_tokens: The maximum number of tokens for the language model's response.
    
    Returns:
        str: The answer to the question based on the context.
    """

    if model is None or tokenizer is None:
        return "This is a placeholder answer, model or tokenizer not provided."
    
    prompt="""
        Si natančen pomočnik za odgovarjanje na vprašanja. Odgovori na vprašanja se nahajajo znotraj
        konteksta, ki ga obkrožajo štiri znaki lojtra. Če ne moreš najti odgovora, reci "Ne vem".
        Ne izmišljuj si odgovorov na katera ni odgovora v kontekstu.

        Primer:
        ####
        Danes je petek.
        ####
        - Q: Kateri dan je danes?
        - A: Danes je petek.

        ####
        Kruh stane 5 evrov.
        ####
        - Q: Koliko je ura?
        - A: Ne vem.

        Tu je kontekst in vprašanje:

        ####
        {context}
        ####
        - Q: {question}
        - A:"""
    prompt = prompt.format(context=context, question=question)
    input_ids = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    outputs = model.generate(**input_ids, max_new_tokens=max_tokens, temperature=temperature)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(answer)
    return answer.split("A: ")[-1].strip()

if __name__ == "__main__":
    
    model_name = "google/gemma-2-2b-it"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )

    answer(
        "Kdo je predsednik vlade?",
        "Slovenija je dobila novega predsednika. Predsednik vlade je ravnokar postal Robert Golob, član stranke Gibanje Svoboda.",
        model=model,
        tokenizer=tokenizer
    )