import codecs
import sys
import json
import random
from sentence_transformers import CrossEncoder

model = CrossEncoder('cross-encoder/nli-deberta-base')
sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)

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


def test(p_data, p_case, p_entity1, p_entity2, p_rel, tp, tn, fp, fn):
    deducible = True if p_case == "Positive_Case" else False

    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0

    i = 0
    for task in p_data:

        entity_1 = task['entity1']['name']
        entity_2 = task['entity2']['name']
        relation = task['relation']
        sentences = ' '.join(task['text_passages']).split('. ')

        data_task = []
        for sentence in sentences:
            data_task.append((sentence, f"{entity_1} is in {' '.join(relation.split('_'))} with {entity_2}"))
        print(data_task)
        scores = model.predict(data_task)
        label_mapping = ['contradiction', 'entailment', 'neutral']
        labels = [label_mapping[score_max] for score_max in scores.argmax(axis=1)]

        response_bool = False

        "STRICT APPROACH"
        """
        if 'entailment' in labels and 'contradiction' not in labels:
            response_bool = True
        """


        "LOOSE APPROACH"
        #"""
        if 'entailment' in labels:
            response_bool = True
        #"""

        print(response_bool)

        true_positives += 1 if (response_bool is True) and (deducible is True) else 0
        true_negatives += 1 if (response_bool is False) and (deducible is False) else 0
        false_positives += 1 if (response_bool is True) and (deducible is False) else 0
        false_negatives += 1 if (response_bool is False) and (deducible is True) else 0

        tp += 1 if (response_bool is True) and (deducible is True) else 0
        tn += 1 if (response_bool is False) and (deducible is False) else 0
        fp += 1 if (response_bool is True) and (deducible is False) else 0
        fn += 1 if (response_bool is False) and (deducible is True) else 0

        i = i + 1
        #if i == 4:
            #break

    print("{} {} {} TP: {} TN: {} FP: {} FN: {}".format(relation, task['entity1']['type'], task['entity2']['type'], true_positives, true_negatives, false_positives, false_negatives))
    #print("\nAccuracy: {}".format((true_positives + true_negatives)/(true_positives + true_negatives + false_positives + false_negatives)))
    return tp, tn, fp, fn




if __name__ == '__main__':

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

    tp = 0
    tn = 0
    fp = 0
    fn = 0

    for concept in concepts:
        entity1, entity2, relation, case = concept[0], concept[1], concept[2], concept[3]
        data = sort_data(dataset, entity1, entity2, relation, case)
        tp, tn, fp, fn = test(data, case, entity1, entity2, relation, tp, tn, fp, fn)

    print("\nTrue Positive: {}\nTrue Negative: {}\nFalse Positive: {}\nFalse Negative: {}".format(tp, tn, fp, fn))
    print("\nAccuracy: {}".format((tp + tn) / (tp + tn + fp + fn)))

