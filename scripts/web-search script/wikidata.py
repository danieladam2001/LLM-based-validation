import codecs
import re
import sys
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import replicate
import os
import pathlib

subjectQ = "36233"
endpoint_url = "https://query.wikidata.org/sparql"
queryTarget = """SELECT DISTINCT ?subjectLabel ?property ?object ?objectLabel
WHERE {
  {
    SELECT ?subject ?p ?stmt ?object (URI(REPLACE(STR(?p),STR(p:),STR(wdt:))) as ?property)
    WHERE {
      ?subject ?p ?stmt.
      ?stmt ?ps ?object .
      BIND (URI(REPLACE(STR(?p),STR(p:),STR(ps:))) as ?ps)
      FILTER (?subject = wd:Q""" + subjectQ + """)
      FILTER (REGEX(STR(?p), STR(p:)))
      hint:SubQuery hint:runOnce true .
    }
  }
  hint:Prior hint:runFirst true .
  FILTER NOT EXISTS { ?stmt prov:wasDerivedFrom ?ref . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}"""

queryProperties = """SELECT ?property ?propertyLabel
WHERE {
  ?property wdt:P2302 wd:Q54554025.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}"""

os.environ["REPLICATE_API_TOKEN"] = ""
sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)


def get_statements(targetStatements, constrainedProperties):
    result = []
    for target in targetStatements:
        for prop in constrainedProperties:
            regExQ = re.search("P\d*", target[1])
            regExP = re.search("P\d*", prop[0])
            if regExQ and regExP:
                if regExQ.group() == regExP.group():
                    result.append([target[0], target[1], prop[1], target[2], target[3]])
    return result


def get_results(endpoint, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def get_target_statements():
    listResult = []
    results = get_results(endpoint_url, queryTarget)
    for i in range(len(results["results"]["bindings"])):
        listResult.append([results["results"]["bindings"][i]["subjectLabel"]["value"],
                           results["results"]["bindings"][i]["property"]["value"],
                           results["results"]["bindings"][i]["object"]["value"],
                           results["results"]["bindings"][i]["objectLabel"]["value"]])
    return listResult


def get_constrained_properties():
    listResult = []
    results = get_results(endpoint_url, queryProperties)
    for i in range(len(results["results"]["bindings"])):
        listResult.append([results["results"]["bindings"][i]["property"]["value"],
                           results["results"]["bindings"][i]["propertyLabel"]["value"]])
    return listResult


def fetch_top_search_results(query):
    search_results = search(query, tld="com", num=5, stop=5, pause=2)
    return search_results


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


def get_paragraphs_from_url(url):
    try:
        r = requests.get(url).text
    except Exception as e:
        print("Error: {}".format(str(e)))
        return []

    soup = BeautifulSoup(r, 'html.parser')
    listOfParagraphs = []
    for data in soup.find_all("p"):
        if data.getText():
            trimmed = ' '.join(data.getText().replace("\n", "").split())
            if len(trimmed) >= 100:
                listOfParagraphs.append(trimmed)
    return listOfParagraphs



if __name__ == '__main__':

    if os.environ["REPLICATE_API_TOKEN"] == "":
        print("Replicate API key missing")
        exit()
    pathlib.Path("wikidata-references/Q{}".format(subjectQ)).mkdir(parents=False, exist_ok=True)
    targetStatements = get_target_statements()
    constrainedProperties = get_constrained_properties()
    preparedStatements = get_statements(targetStatements, constrainedProperties)

    for statement in preparedStatements:
        print(statement)

    for statement in preparedStatements:

        file_exists = os.path.isfile("wikidata-references/Q{}/{}-{}-{}.json".format(subjectQ, statement[0], statement[2], statement[4]))
        if file_exists:
            continue

        json_result = {
            "LLM": {
                "model": "meta/meta-llama-3-70b-instruct",
                "seed": 42,
                "top_p": 0.9,
                "temperature": 0.1,
                "system_prompt": "You are a helpful assistant. Work only with the text given to you.",
                "max_new_tokens": 500,
                "min_new_tokens": -1
            },
            "task": {
                "subject": statement[0],
                "predicate": statement[2],
                "object": statement[4]
            },
            "sources": []
        }

        print(statement)
        sources = fetch_top_search_results("{} {} {} -wikipedia".format(statement[0], statement[2], statement[4]))
        for source in sources:
            json_source = {
                "url": source,
                "rdf_proof": False
            }
            print(source)
            paragraphs = get_paragraphs_from_url(source)
            for paragraph in paragraphs:
                prompt = get_prompt_default(statement[0], statement[2], statement[4], paragraph)
                response_text = llama_request(prompt)
                regExA = re.search("a\)", response_text[:50])
                response_bool = True if regExA else False
                if response_bool:
                    print("{} {} {} verified at {} in paragraph {}".format(statement[0], statement[2], statement[4], source, paragraph))
                    json_source["rdf_proof"] = True
                    json_source["paragraph"] = paragraph
                    json_source["raw_LLM"] = response_text
                    break

            json_result["sources"].append(json_source)

        print(json_result)
        with open("wikidata-references/Q{}/{}-{}-{}.json".format(subjectQ, statement[0], statement[2], statement[4]), "w", encoding='utf-8') as outfile:
            json.dump(json_result, outfile, ensure_ascii=False, indent=2)