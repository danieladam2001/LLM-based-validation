import codecs
import sys
import json
import re
import replicate
import os
import random


os.environ["REPLICATE_API_TOKEN"] = ""
sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)


def llama_request(message):
    if message:
        input = {
            "seed": 42,
            "prompt": message,
            "top_p": 0.9,
            "temperature": 0.1,
            "system_prompt": "You are a helpful assistant. Work only with the text given to you.",
            "max_new_tokens": 500,
            "min_new_tokens": -1
        }

        response = ""
        valid = 0

        while not valid:
            response = ""
            valid = 1
            try:
                for event in replicate.stream(
                        "meta/meta-llama-3-70b-instruct",
                        input=input
                ):
                    response = response + str(event).replace('\n', "")
            except Exception as e:
                print("Error: {}".format(str(e)))
                valid = 0

            if not response or len(response) <= 10:
                valid = 0


        return response


def get_prompt_default(subjectRDF, predicateRDF, objectRDF, textGroup):
    intro1 = "Can the given RDF be inferred from the given snippet?\n\n"
    statement = "RDF for verification: [\"{}\" - \"{}\" - \"{}\"].\n".format(subjectRDF, predicateRDF, objectRDF)
    snippet = "Snippet to verify from: \"{}\n".format(textGroup)

    request = "\n\nPlease, choose the correct option based on your answer!\n"
    option1 = "a) The RDF statement can be directly verified from the snippet. The snippet contains direct proof.\n"
    option2 = "b) The snippet contains some indications of the truthfulness of the RDF."
    option3 = "c) The RDF statement definitely cannot be inferred from the snippet.\n"
    return intro1 + statement + snippet + request + option1 + option2 + option3


def list_to_string(list_array):
    string = " "
    return string.join(list_array)


def sort_data(p_dataset, p_entity1, p_entity2, p_relation, p_case):

    filtered_data = []
    for data_record in p_dataset:
        type1type1 = True if p_entity1 == data_record["entity1"]["type"] else False
        type2type2 = True if p_entity2 == data_record["entity2"]["type"] else False
        type2type1 = True if p_entity2 == data_record["entity1"]["type"] else False
        type1type2 = True if p_entity1 == data_record["entity2"]["type"] else False
        relation_type = True if p_relation == data_record["relation"] else False

        if (type1type1 and type2type2 and relation_type) or (type2type1 and type1type2 and relation_type):
            filtered_data.append(data_record)

    selected_data = []

    if p_case == "Positive_Case":
        selected_data = filtered_data
    else:
        for filtered_data_record in filtered_data:

            all_potential_tails = []

            for data_record in p_dataset:

                filtered_head_id = filtered_data_record["entity1"]["id"]
                filtered_tail_type = filtered_data_record["entity2"]["type"]
                filtered_tail_id = filtered_data_record["entity2"]["id"]
                potential_head_type = data_record["entity1"]["type"]
                potential_head_id = data_record["entity1"]["id"]
                potential_tail_type = data_record["entity2"]["type"]
                potential_tail_id = data_record["entity2"]["id"]

                filtered_tail_name = filtered_data_record["entity2"]["name"]
                potential_head_name = data_record["entity1"]["name"]
                potential_tail_name = data_record["entity2"]["name"]


                if filtered_data_record["document_id"] != data_record["document_id"]:

                    if (filtered_tail_type == potential_head_type) and (filtered_tail_id != potential_head_id) and (filtered_tail_name != potential_head_name):
                        if unique_corrupted_triple(filtered_data_record["document_id"], filtered_head_id, potential_head_id, p_relation, p_dataset):
                            all_potential_tails.append([data_record["entity1"]["id"], data_record["entity1"]["name"], data_record["entity1"]["type"]])

                    if (filtered_tail_type == potential_tail_type) and (filtered_tail_id != potential_tail_id) and (filtered_tail_name != potential_tail_name):
                        if unique_corrupted_triple(filtered_data_record["document_id"], filtered_head_id, potential_tail_id, p_relation, p_dataset):
                            all_potential_tails.append([data_record["entity2"]["id"], data_record["entity2"]["name"], data_record["entity2"]["type"]])


            random.seed(0)
            index = random.randint(0, len(all_potential_tails)) - 1

            new_data_record = filtered_data_record
            new_data_record["entity2"]["id"] = all_potential_tails[index][0]
            new_data_record["entity2"]["name"] = all_potential_tails[index][1]
            new_data_record["entity2"]["type"] = all_potential_tails[index][2]

            selected_data.append(new_data_record)

    return selected_data


def unique_corrupted_triple(p_id, p_head_id, p_tail_id, p_relation, p_dataset):
    for data_record in p_dataset:
        if (data_record["document_id"] == p_id) and (data_record["relation"] == p_relation):
            if (data_record["entity1"]["id"] == p_head_id) and (data_record["entity2"]["id"] == p_tail_id):
                return False
            if (data_record["entity1"]["id"] == p_tail_id) and (data_record["entity2"]["id"] == p_head_id):
                return False
    return True


def clean(string):
    return string.replace('<', ' ').replace('>', ' ').replace(':', ' ').replace('“', ' ').replace('/', ' ').replace('\\', ' ').replace('|', ' ').replace('?', ' ').replace('*', ' ')


def test(p_data, p_case, p_entity1, p_entity2, p_rel):
    deducible = True if p_case == "Positive_Case" else False

    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0

    i = 0
    for task in p_data:

        text = ""
        for passage in task["text_passages"]:
            text = text + passage

        prompt = get_prompt_default(task["entity1"]["name"], task["relation"], task["entity2"]["name"], text)
        response_text = llama_request(prompt)
        regExA = re.search("a\)", response_text[:50])
        response_bool = True if regExA else False

        true_positives += 1 if (response_bool is True) and (deducible is True) else 0
        true_negatives += 1 if (response_bool is False) and (deducible is False) else 0
        false_positives += 1 if (response_bool is True) and (deducible is False) else 0
        false_negatives += 1 if (response_bool is False) and (deducible is True) else 0


        print("{}. {} / {} / {}".format(i, deducible, response_bool, response_text.replace('\n', " ")))

        json_result = {
            "subject": task["entity1"]["name"],
            "predicate": task["relation"],
            "object": task["entity2"]["name"],
            "prompt": prompt,
            "text": text,
            "expected_answer": deducible,
            "LLM_anwser_parsed": response_bool,
            "LLM_answer_raw": response_text,
            "answered_correctly": True if response_bool == deducible else False,
            "LLM": {
                "model": "meta/meta-llama-3-70b-instruct",
                "seed": 42,
                "top_p": 0.9,
                "temperature": 0.1,
                "system_prompt": "You are a helpful assistant. Work only with the text given to you.",
                "max_new_tokens": 500,
                "min_new_tokens": -1
            }
        }

        json_object = json.dumps(json_result, indent=2)
        with open("biored-tests/{}-{}-{}-{}/{}. {}-{}-{}.json".format(p_entity1, p_entity2, p_rel, p_case, i, clean(task["entity1"]["name"]), task["relation"], clean(task["entity2"]["name"])), "w") as outfile:
            outfile.write(json_object)
        i = i + 1

    print("\nTrue Positive: {}\nTrue Negative: {}\nFalse Positive: {}\nFalse Negative: {}".format(true_positives, true_negatives, false_positives, false_negatives))


if __name__ == '__main__':

    if os.environ["REPLICATE_API_TOKEN"] == "":
        print("Replicate API token missing.")
        exit()

    dataset = json.loads(open("biored-adjusted.json", "r").read())

    concepts = [
        ["ChemicalEntity", "DiseaseOrPhenotypicFeature", "Positive_Correlation", "Positive_Case"],
        ["ChemicalEntity", "DiseaseOrPhenotypicFeature", "Positive_Correlation", "Negative_Case"],
        ["ChemicalEntity", "DiseaseOrPhenotypicFeature", "Negative_Correlation", "Positive_Case"],
        ["ChemicalEntity", "DiseaseOrPhenotypicFeature", "Negative_Correlation", "Negative_Case"],

        ["ChemicalEntity", "GeneOrGeneProduct", "Positive_Correlation", "Positive_Case"],
        ["ChemicalEntity", "GeneOrGeneProduct", "Positive_Correlation", "Negative_Case"],
        ["ChemicalEntity", "GeneOrGeneProduct", "Negative_Correlation", "Positive_Case"],
        ["ChemicalEntity", "GeneOrGeneProduct", "Negative_Correlation", "Negative_Case"],

        ["SequenceVariant", "DiseaseOrPhenotypicFeature", "Positive_Correlation", "Positive_Case"],
        ["SequenceVariant", "DiseaseOrPhenotypicFeature", "Positive_Correlation", "Negative_Case"],
        ["SequenceVariant", "DiseaseOrPhenotypicFeature", "Negative_Correlation", "Positive_Case"],
        ["SequenceVariant", "DiseaseOrPhenotypicFeature", "Negative_Correlation", "Negative_Case"],

        ["ChemicalEntity", "ChemicalEntity", "Positive_Correlation", "Positive_Case"],
        ["ChemicalEntity", "ChemicalEntity", "Positive_Correlation", "Negative_Case"],
        ["ChemicalEntity", "ChemicalEntity", "Negative_Correlation", "Positive_Case"],
        ["ChemicalEntity", "ChemicalEntity", "Negative_Correlation", "Negative_Case"],

        ["GeneOrGeneProduct", "GeneOrGeneProduct", "Positive_Correlation", "Positive_Case"],
        ["GeneOrGeneProduct", "GeneOrGeneProduct", "Positive_Correlation", "Negative_Case"],
        ["GeneOrGeneProduct", "GeneOrGeneProduct", "Negative_Correlation", "Positive_Case"],
        ["GeneOrGeneProduct", "GeneOrGeneProduct", "Negative_Correlation", "Negative_Case"],

        ["GeneOrGeneProduct", "DiseaseOrPhenotypicFeature", "Positive_Correlation", "Positive_Case"],
        ["GeneOrGeneProduct", "DiseaseOrPhenotypicFeature", "Positive_Correlation", "Negative_Case"],
        ["GeneOrGeneProduct", "DiseaseOrPhenotypicFeature", "Negative_Correlation", "Positive_Case"],
        ["GeneOrGeneProduct", "DiseaseOrPhenotypicFeature", "Negative_Correlation", "Negative_Case"],

        ["ChemicalEntity", "SequenceVariant", "Positive_Correlation", "Positive_Case"],
        ["ChemicalEntity", "SequenceVariant", "Positive_Correlation", "Negative_Case"],
        ["ChemicalEntity", "SequenceVariant", "Negative_Correlation", "Positive_Case"],
        ["ChemicalEntity", "SequenceVariant", "Negative_Correlation", "Negative_Case"],
    ]

    for concept in concepts:

        entity1, entity2, relation, case = concept[0], concept[1], concept[2], concept[3]
        data = sort_data(dataset, entity1, entity2, relation, case)
        test(data, case, entity1, entity2, relation)

