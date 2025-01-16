import codecs
import pathlib
import sys
import json
import re
import replicate
import os
import random

#meta/meta-llama-3-70b-instruct
#meta/meta-llama-3.1-405b-instruct
#meta/meta-llama-3-8b-instruct

model = "meta/meta-llama-3.1-405b-instruct"
seed = 42
top_p = 0.9
temperature = 0.1
system_prompt = "You are a helpful assistant. Work only with the text given to you."
max_new_tokens = 500
min_new_tokens = -1

os.environ["REPLICATE_API_TOKEN"] = ""
sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)


def llama_request(message):
    if message:
        input = {
            "seed": seed,
            "prompt": message,
            "top_p": top_p,
            "temperature": temperature,
            "system_prompt": system_prompt,
            "max_new_tokens": max_new_tokens,
            "min_new_tokens": min_new_tokens
        }

        response = ""
        valid = 0

        while not valid:
            response = ""
            valid = 1
            try:
                for event in replicate.stream(
                        model,
                        input=input
                ):
                    response = response + str(event).replace('\n', "")
            except Exception as e:
                print("Error: {}".format(str(e)))
                valid = 0

            if not response or len(response) <= 10:
                valid = 0


        return response


def get_prompt_default(premise, hypothesis):
    intro1 = "Can you determine the inference relation between these two texts that describe the same situation?\n\n"
    text1 = "Text (premise): '{}'\n".format(premise)
    text2 = "Sentece (hypothesis): '{}'\n\n".format(hypothesis)

    entailment = "Entailment = The hypothesis is directly supported by the premise. All information in the hypothesis must align with the premise.\n"
    neutral = "Neutral = The relation between the hypothesis and the premise is neutral (neither entailment nor contradiction).\n"
    contradiction = "Contradiction = If at least one piece of information in one text even slightly differs from the other text, or if the hypothesis mentions something that would not be possible in the premise.\n"

    example_e_1 = "\n###EXAMPLE OF AN ENTAILMENT###" \
        "\nPremise: 'A person on a horse jumps over a broken down airplane.'" \
        "\nHypothesis: 'A person is outdoors, on a horse.'" \
        "\nThe correct label is 'entailment' because all claims in the hypothesis correspond to the premise.'\n"

    example_n_1 = "\n###EXAMPLE OF A NEUTRAL RELATION###" \
        "\nPremise: 'A person on a horse jumps over a broken down airplane.'" \
        "\nHypothesis: 'A person is training his horse for a competition.'" \
        "\nThe correct label is 'neutral' because some claims in the hypothesis are not entirely stated in the premise.'\n"

    example_c_1 = "\n###EXAMPLE OF A CONTRADICTION###" \
        "\nPremise: 'A person on a horse jumps over a broken down airplane.'" \
        "\nHypothesis: 'A person is at a diner, ordering an omelete.'" \
        "\nThe correct label is 'contradiction' because some claims in the hypothesis contradict the premise.'\n"

    request = "\nPlease, choose the correct option based on your answer!\n"
    option1 = "a) entailment\n"
    option2 = "b) neutral\n"
    option3 = "c) contradiction\n"
    return intro1 + text1 + text2 + entailment + neutral + contradiction + example_e_1 + example_n_1 + example_c_1 + request + option1 + option2 + option3


def test(pair_id, premise, hypothesis, label):

    prompt = get_prompt_default(premise=premise, hypothesis=hypothesis)
    response_text = llama_request(prompt)
    a_answer = re.search("a\)", response_text)
    b_answer = re.search("b\)", response_text)
    c_answer = re.search("c\)", response_text)

    response = 'could not be parsed'
    if a_answer: response = 'entailment'
    elif b_answer: response = 'neutral'
    elif c_answer: response = 'contradiction'


    json_result = {
        "premise": premise,
        "hypothesis": hypothesis,
        "prompt": prompt,
        "expected_answer": label,
        "LLM_anwser_parsed": response,
        "LLM_answer_raw": response_text,
        "answered_correctly": True if response == label else False,
        "LLM": {
            "model": model,
            "seed": seed,
            "top_p": top_p,
            "temperature": temperature,
            "system_prompt": system_prompt,
            "max_new_tokens": max_new_tokens,
            "min_new_tokens": min_new_tokens
        }
    }

    json_object = json.dumps(json_result, indent=2)
    with open("snli-results/{}/{}_{}.json".format(model.replace('/', '_'), pair_id, True if response == label else False), "w") as outfile:
        outfile.write(json_object)

    return True if response == label else False


if __name__ == '__main__':

    snli_dataset_test = []
    with open("snli_1.0/snli_1.0/snli_1.0_test.jsonl", 'r', encoding='utf-8') as file:
        for line in file:
            snli_dataset_test.append(json.loads(line.strip()))

    if os.environ["REPLICATE_API_TOKEN"] == "":
        print("Replicate API token missing.")
        exit()

    pathlib.Path("snli-results").mkdir(parents=False, exist_ok=True)
    pathlib.Path("snli-results/{}".format(model.replace('/', '_'))).mkdir(parents=False, exist_ok=True)

    files = os.listdir('snli-results/{}'.format(model.replace('/', '_')))
    random.seed(42)
    random.shuffle(snli_dataset_test)
    count = 0
    for entry in snli_dataset_test:
        if f"{entry['pairID']}_True.json" in files or f"{entry['pairID']}_False.json" in files:
            count += 1
            continue
        if entry['gold_label'] != "-":
            test(entry['pairID'], entry['sentence1'], entry['sentence2'], entry['gold_label'])
            count += 1
        if count == 1000: break
    print(count)


