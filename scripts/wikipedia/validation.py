import codecs
import pathlib
import re
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import openai
import wikipedia
import requests
from bs4 import BeautifulSoup
import math
import datetime

openai.api_key = ''
messages = [{"role": "system", "content": "You will be given some information extraction tasks."}, ]
sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)

if __name__ == '__main__':


    model = "gpt-4-1106-preview"
    # bioluminescence: 179924
    subjectQ = "179924"
    wikipediaURL = requests.get(
        "https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids=Q" + subjectQ + "&props=sitelinks/urls&formatversion=2&sitefilter=enwiki").json()[
        "entities"]["Q" + subjectQ]["sitelinks"]["enwiki"]["url"]

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

    ########################################################################################################################
    """ DEFINITIONS OF FUNCTIONS """


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


    def clean_chat_messages():
        messages.clear()
        messages.append({"role": "system", "content": "You will be given some information extraction tasks."}, )


    def chatgpt_request(message):
        if message:
            try:
                messages.append({"role": "user", "content": message}, )
                chat = openai.ChatCompletion.create(model=model, messages=messages)
                clean_chat_messages()
                return chat.choices[0].message.content + "\n"
            except ValueError:
                return "ChatGPT did not return any message"

    def get_prompt_default(subjectRDF, predicateRDF, objectRDF, textGroup):
        intro = "Can the given RDF statement be inferred from the given snippet?\n"
        statement = "RDF: [\"" + subjectRDF + "\" - \"" + predicateRDF + "\" - \"" + objectRDF + "\"]"
        snippet = "\nSnippet: \"" + textGroup + "\""
        request = "\nPlease, give an answer and also the reasoning behind it!"
        prompt = intro + statement + snippet + request
        return prompt

    def get_prompt_default_xml(subjectRDF, predicateRDF, objectRDF, textGroup):
        intro = "Can the given RDF statement be inferred from the given snippet?\n"
        statement = "RDF: [\"" + subjectRDF + "\" - \"" + predicateRDF + "\" - \"" + objectRDF + "\"]"
        snippet = "\nSnippet: \"" + textGroup + "\""
        request = "\nPlease, give an answer and also the reasoning behind it!"
        return [intro, statement, snippet, request]


    def get_prompt_citation(subjectRDF, predicateRDF, objectRDF, textGroup):
        intro = "The given RDF statement can be inferred from the given snippet!\n"
        statement = "RDF: [\"" + subjectRDF + "\" - \"" + predicateRDF + "\" - \"" + objectRDF + "\"]"
        snippet = "\nSnippet: \"" + textGroup + "\""
        request = "\nPlease, cite one sentence that best supports the given RDF statement [\"" + subjectRDF + "\" - \"" + predicateRDF + "\" - \"" + objectRDF + "\"] in the given snippet. Your answer should only consist of the citation!"
        prompt = intro + statement + snippet + request
        return prompt

    def get_prompt_citation_xml(subjectRDF, predicateRDF, objectRDF, textGroup):
        intro = "The given RDF statement can be inferred from the given snippet!\n"
        statement = "RDF: [\"" + subjectRDF + "\" - \"" + predicateRDF + "\" - \"" + objectRDF + "\"]"
        snippet = "\nSnippet: \"" + textGroup + "\""
        request = "\nPlease, cite one sentence that best supports the given RDF statement [\"" + subjectRDF + "\" - \"" + predicateRDF + "\" - \"" + objectRDF + "\"] in the given snippet. Your answer should only consist of the citation!"
        return [intro, statement, snippet, request]


    def parse_answer(previousAnswer):
        intro = "Choose the correct answer if you hear this answer: " + previousAnswer + "\n"
        option1 = "a) The RDF statement can be inferred from the snippet.\n"
        option2 = "b) The RDF statement can not be inferred from the snippet."
        message = intro + option1 + option2
        reply = chatgpt_request(message)
        regExA = re.search("a\)", reply)
        if regExA:
            return True
        else:
            return False


    def test_statements(listOfStatements, wordGroups):
        defaultInterrogation = []
        iteration = 0
        for i in range(len(listOfStatements)):
            subjectRDF = listOfStatements[i][0]
            predicateRDF = listOfStatements[i][2]
            predicateRDFurl = listOfStatements[i][1]
            objectRDF = listOfStatements[i][4]
            objectRDFurl = listOfStatements[i][3]
            groupNumber = 1
            for group in wordGroups:
                answer = "NO"
                detailedInterrogation = []
                defaultInterrogation.append([])
                defaultInterrogation[iteration].append(subjectRDF)
                defaultInterrogation[iteration].append(predicateRDF)
                defaultInterrogation[iteration].append(predicateRDFurl)
                defaultInterrogation[iteration].append(objectRDF)
                defaultInterrogation[iteration].append(objectRDFurl)
                defaultInterrogation[iteration].append(groupNumber)
                print(f"{subjectRDF} + {predicateRDF} + {objectRDF}")
                prompt = get_prompt_default(subjectRDF, predicateRDF, objectRDF, group)
                defaultInterrogation[iteration].append(1)
                reply = chatgpt_request(prompt)
                defaultInterrogation[iteration].append(reply)
                print(group.replace('\n', ''))
                print(reply.replace('\n', ''))
                isSupportive = parse_answer(reply)
                if isSupportive:
                    answer = "YES"
                    defaultInterrogation[iteration].append(answer)
                    paragraphs = group.splitlines()
                    detailedInterrogation = []
                    paragraphIndex = 0
                    for paragraph in paragraphs:
                        if len(paragraph) >= 10:
                            detailedInterrogation.append([])
                            detailedInterrogation[paragraphIndex].append(paragraph)
                            prompt = get_prompt_default(subjectRDF, predicateRDF, objectRDF, paragraph)
                            detailedInterrogation[paragraphIndex].append(1)
                            reply = chatgpt_request(prompt)
                            print(f"{subjectRDF} + {predicateRDF} + {objectRDF}")
                            print(paragraph.replace('\n', ''))
                            print(reply.replace('\n', ''))
                            detailedInterrogation[paragraphIndex].append(reply)
                            isSupportive = parse_answer(reply)
                            if isSupportive:
                                detailedInterrogation[paragraphIndex].append("YES")
                                wikiNumbers = re.findall("\[([0-9]+)\]", paragraph)
                                detailedInterrogation[paragraphIndex].append(wikiNumbers)
                            else:
                                detailedInterrogation[paragraphIndex].append("NO")
                            paragraphIndex += 1
                else:
                    defaultInterrogation[iteration].append(answer)
                defaultInterrogation[iteration].append(detailedInterrogation)
                iteration += 1
                groupNumber += 1
        return defaultInterrogation


    def show_statements(listOfStatements):
        for statement in listOfStatements:
            print(statement)
        print("In total, there are " + str(len(listOfStatements)) + " statements about " + listOfStatements[0][
            0] + " that require a reference but do not have one!\n")


    def show_word_groups(groups, sections):
        print("There are " + str(len(sections)) + " sections, for example: " + str(sections[:5]) + " and more..")
        print("Because of the input length limits of chatGPT, the text was automatically sepereated into " + str(
            len(groups)) + " groups. The groups were limited to 9999 characters.")
        for i in range(len(groups)):
            print("Group " + str(i + 1) + " has " + str(len(groups[i])) + " characters.")
        print("")


    def get_wiki_sections():
        wikipediaTitle = re.search("wiki/(.*)", wikipediaURL).group(1)
        wikipediaSections = "https://en.wikipedia.org/w/api.php?action=parse&format=json&page=" + wikipediaTitle + "&prop=sections&formatversion=2"
        data = requests.get(wikipediaSections)
        sections = []
        for section in data.json()["parse"]["sections"]:
            wikipedia.set_lang("en")
            title = section["line"]
            sections.append(title)
        paragraphs = get_paragraphs_from_url(wikipediaURL)
        textGroup = ""
        groups = []
        for paraghraph in paragraphs:
            text = paraghraph
            if len(text) + len(textGroup) > 10000:
                groups.append(textGroup)
                textGroup = ""

            textGroup = textGroup + text + "\n"
        groups.append(textGroup)
        return groups, sections


    def get_paragraphs_from_url(url):
        r = requests.get(url).text
        soup = BeautifulSoup(r, 'html.parser')
        listOfParagraphs = []
        for data in soup.find_all("p"):
            if data.getText():
                listOfParagraphs.append(data.getText())
                #print(len(data.getText()))
        return listOfParagraphs


    def get_reference_number(snippet):
        paragraphs = get_paragraphs_from_url(wikipediaURL)
        for p in paragraphs:
            match = re.search(
                snippet.replace("(", "\(").replace(")", "\)")[0:math.floor(len(snippet) / 2)] + ".*?\[(\d*)]", p)
            if match:
                return int(match.group(1))
        return 0


    def get_reference_url(refNumber):
        print(refNumber)
        selectWikiPage = wikipediaURL
        if "wikipedia" in selectWikiPage:
            html = requests.get(wikipediaURL)
            soup = BeautifulSoup(html.content, "html.parser")
            findReferences = soup.select('.reflist>.mw-references-columns>ol>li')
            if not findReferences:
                findReferences = soup.select('.reflist>ol>li')
                if not findReferences:
                    return 0, 0
            resource = findReferences[int(refNumber) - 1].text
            desiredRef = findReferences[int(refNumber) - 1].select_one('.reference-text>cite>.external.text')
            if resource and desiredRef and desiredRef['href']:
                return desiredRef['href'], resource
            else:
                return 0, 0
        else:
            return 0, 0


    def get_xml_output(data):
        xmlFormatOutput = "<xml><statements>"
        for statement in data:
            xml = "<statement>"
            xml += "<subject>" + statement[0] + "</subject>"
            xml += "<predicate>" + statement[1] + "</predicate>"
            xml += "<object>" + statement[2] + "</object>"
            xml += "<timeDuration>" + str(math.floor(statement[3])) + " seconds</timeDuration>"
            xml += "<wikipediaSupport>" + statement[4] + "</wikipediaSupport>"
            if statement[4] == "YES":
                xml += "<findings>"
                for citation in statement[5]:
                    xml += "<finding>"
                    xml += "<citation>" + citation[0] + "</citation>"
                    xml += "<reasoning>" + citation[1].replace("\n", "") + "</reasoning>"
                    xml += "<referenceNumber>" + str(citation[2]) + "</referenceNumber>"
                    xml += "<referenceTitle>" + citation[3] + "</referenceTitle>"
                    xml += "<referenceUrl>" + citation[4] + "</referenceUrl>"
                    xml += "<contentFromURL>" + citation[5] + "</contentFromURL>"
                    xml += "<supportiveTextFound>" + citation[6] + "</supportiveTextFound>"
                    if citation[6] == "FOUND":
                        xml += "<supportiveTexts>"
                        for prove in citation[7]:
                            xml += "<supportiveText>"
                            xml += "<paragraph>" + prove[0] + "</paragraph>"
                            xml += "<reasoning>" + prove[1].replace("\n", "") + "</reasoning>"
                            xml += "</supportiveText>"
                        xml += "</supportiveTexts>"
                    xml += "<timeDuration>" + str(math.floor(citation[8])) + " seconds</timeDuration>"
                    xml += "</finding>"
                xml += "</findings>"
            xml += "</statement>"
            xmlFormatOutput += xml
        xmlFormatOutput += "</statements></xml>"
        return xmlFormatOutput


    def get_xml_output_test(data, generalInfoXML):
        xmlFormatOutput = "<wikidataVerification>"
        xmlFormatOutput += generalInfoXML + "<tasks>"
        for statement in data:
            xml = "<task>"
            xml += "<subject>" + statement[0] + "</subject>"
            xml += "<predicate>" + statement[1] + "</predicate>"
            xml += "<predicateURL>" + statement[2] + "</predicateURL>"
            xml += "<object>" + statement[3] + "</object>"
            xml += "<objectURL>" + statement[4] + "</objectURL>"
            xml += "<textGroupID>" + str(statement[5]) + "</textGroupID>"
            xml += "<promptID>" + str(statement[6]) + "</promptID>"
            xml += "<modelAnswer>" + statement[7].replace("\n", "") + "</modelAnswer>"
            xml += "<doesTextSupportRDF>" + statement[8] + "</doesTextSupportRDF>"
            if statement[8] == "YES":
                xml += "<detailedResearch>"
                for citation in statement[9]:
                    xml += "<paragraph>"
                    xml += "<paragraphText>" + citation[0] + "</paragraphText>"
                    xml += "<promptID>" + str(citation[1]) + "</promptID>"
                    xml += "<modelAnswer>" + citation[2].replace("\n", "") + "</modelAnswer>"
                    xml += "<doesTextSupportRDF>" + citation[3] + "</doesTextSupportRDF>"
                    if citation[3] == "YES":

                        xml += "<referenceNumbers>" + str(citation[4])[
                                                      1:len(str(citation[4])) - 1] + "</referenceNumbers>"
                        xml += "<references>"
                        for ref in citation[5]:
                            xml += "<reference>"
                            xml += "<referenceNumber>" + str(ref[0]) + "</referenceNumber>"
                            xml += "<referenceTitle>" + ref[1] + "</referenceTitle>"
                            xml += "<referenceURL>" + ref[2] + "</referenceURL>"
                            xml += "<websiteContent>" + ref[3] + "</websiteContent>"

                            xml += "<paragraphs>"
                            for task in ref[4]:
                                xml += "<paragraph>"
                                xml += "<paragraphText>" + task[0] + "</paragraphText>"
                                xml += "<modelAnswer>" + task[1] + "</modelAnswer>"
                                xml += "<doesTextSupportRDF>" + task[2] + "</doesTextSupportRDF>"
                                xml += "</paragraph>"
                            xml += "</paragraphs>"
                            xml += "</reference>"
                        xml += "</references>"
                    xml += "</paragraph>"
                xml += "</detailedResearch>"
            xml += "</task>"
            xmlFormatOutput += xml
        xmlFormatOutput += "</tasks></wikidataVerification>"
        return xmlFormatOutput


    def check_primary_resources(data):
        for statement in data:
            if statement[8] == "YES":
                for paragraph in statement[9]:

                    if paragraph[3] == "YES":

                        wikipediaReferenceNumbers = paragraph[4]
                        tasks = []
                        for wikipediaReferenceNumber in wikipediaReferenceNumbers:

                            primarySourceParagraphsTasks = []
                            referenceTitle = "NOT FOUND"
                            referenceUrl = "NOT FOUND"
                            contentFromURL = "NOT FOUND"

                            if int(wikipediaReferenceNumber) > 0:
                                refUrl, refResource = get_reference_url(wikipediaReferenceNumber)
                                if refUrl:
                                    referenceUrl = refUrl
                                    referenceTitle = refResource[2:len(refResource) - 1]
                                    paragraphs = get_paragraphs_from_url(refUrl)
                                    if len(paragraphs) >= 3:
                                        for p in paragraphs:
                                            if len(p) >= 200:
                                                contentFromURL = "FOUND"
                                                supportiveTextFound = "NO"
                                                prompt = get_prompt_default(statement[0], statement[1], statement[3], p)
                                                reply = chatgpt_request(prompt)
                                                isSupportive = parse_answer(reply)
                                                if isSupportive:
                                                    supportiveTextFound = "YES"
                                                primarySourceParagraphsTasks.append([p, reply, supportiveTextFound])

                                    if contentFromURL == "NOT FOUND":
                                        paragraphs = get_paragraphs_from_url("https://web.archive.org/web/" + refUrl)
                                        if len(paragraphs) >= 3:
                                            for p in paragraphs:
                                                if len(p) >= 200:
                                                    contentFromURL = "FOUND"
                                                    supportiveTextFound = "NO"
                                                    prompt = get_prompt_default(statement[0], statement[1],
                                                                                statement[3], p)
                                                    reply = chatgpt_request(prompt)
                                                    isSupportive = parse_answer(reply)
                                                    if isSupportive:
                                                        supportiveTextFound = "YES"
                                                    primarySourceParagraphsTasks.append([p, reply, supportiveTextFound])

                            tasks.append([wikipediaReferenceNumber, referenceTitle, referenceUrl, contentFromURL, primarySourceParagraphsTasks])

                        paragraph.append(tasks)

        return data

    def get_xml_general_info(wordGroups, sections, predparedStatements, duration):
        xmlFormatOutput = "<generalInformation>"
        xmlFormatOutput += "<largeLanguageModel>" + model + "</largeLanguageModel>"
        now = datetime.datetime.now()
        xmlFormatOutput += "<date>" + now.strftime("%Y-%m-%d") + "</date>"
        xmlFormatOutput += "<time>" + now.strftime("%H:%M:%S") + "</time>"
        xmlFormatOutput += "<duration unit='minutes'>" + str(math.floor(duration/60)) + "</duration>"
        xmlFormatOutput += "<duration unit='seconds'>" + str(math.floor(duration % 60)) + "</duration>"
        xmlFormatOutput += "<subjectID>" + subjectQ + "</subjectID>"
        xmlFormatOutput += "<subject>" + predparedStatements[0][0] + "</subject>"
        xmlFormatOutput += "<wikidataURL>http://www.wikidata.org/entity/Q" + subjectQ + "</wikidataURL>"
        html = requests.get("http://www.wikidata.org/wiki/Q" + subjectQ)
        soup = BeautifulSoup(html.content, "html.parser")
        permalink = soup.find(attrs={'id':'t-permalink'}).select("a")[0]["href"]
        xmlFormatOutput += "<wikidataPermalink>https://wikidata.org" + permalink + "</wikidataPermalink>"
        xmlFormatOutput += "<wikipediaURL>" + wikipediaURL + "</wikipediaURL>"
        html = requests.get(wikipediaURL)
        soup = BeautifulSoup(html.content, "html.parser")
        permalink = soup.find(attrs={'id':'t-permalink'}).select("a")[0]["href"]
        xmlFormatOutput += "<wikipediaPermalink>https://en.wikipedia.org" + permalink + "</wikipediaPermalink>"
        xmlFormatOutput += "<wikidataEndpointURL>" + endpoint_url + "</wikidataEndpointURL>"
        xmlFormatOutput += "<statements>"
        for statement in predparedStatements:
            xmlFormatOutput += "<statement>"
            xmlFormatOutput += "<subject>" + statement[0] + "</subject>"
            xmlFormatOutput += "<predicate>" + statement[1] + "</predicate>"
            xmlFormatOutput += "<predicateURL>" + statement[2] + "</predicateURL>"
            xmlFormatOutput += "<object>" + statement[3] + "</object>"
            xmlFormatOutput += "<objectURL>" + statement[4] + "</objectURL>"
            xmlFormatOutput += "</statement>"
        xmlFormatOutput += "</statements>"
        xmlFormatOutput += "<wikipediaSections>"
        for section in sections:
            xmlFormatOutput += "<section>" + section + "</section>"
        xmlFormatOutput += "</wikipediaSections>"
        xmlFormatOutput += "<textGroups>"
        groupNumber = 0
        for group in wordGroups:
            xmlFormatOutput += "<group>"
            xmlFormatOutput += "<groupNumber>" + str((groupNumber + 1)) + "</groupNumber>"
            xmlFormatOutput += "<characters>" + str(len(group)) + "</characters>"
            xmlFormatOutput += "<groupText>" + group + "</groupText>"
            xmlFormatOutput += "</group>"
            groupNumber += 1
        xmlFormatOutput += "</textGroups>"
        xmlFormatOutput += "<prompts>"
        xmlFormatOutput += "<prompt>"
        xmlFormatOutput += "<promptNumber>1</promptNumber>"
        xmlFormatOutput += "<intro>" + get_prompt_default_xml("subject","predicate","object","text")[0] + "</intro>"
        xmlFormatOutput += "<rdf>" + get_prompt_default_xml("subject","predicate","object","text")[1] + "</rdf>"
        xmlFormatOutput += "<snippet>" + get_prompt_default_xml("subject","predicate","object","text")[2] + "</snippet>"
        xmlFormatOutput += "<request>" + get_prompt_default_xml("subject","predicate","object","text")[3] + "</request>"
        xmlFormatOutput += "</prompt>"
        xmlFormatOutput += "</prompts>"
        xmlFormatOutput += "</generalInformation>"
        return xmlFormatOutput


    def default_run(custom_data):
        pathlib.Path("xml").mkdir(parents=False, exist_ok=True)
        time0 = datetime.datetime.now()
        targetStatements = get_target_statements()
        constrainedProperties = get_constrained_properties()
        if custom_data:
            preparedStatements = custom_data
        else:
            preparedStatements = get_statements(targetStatements, constrainedProperties)
        print(len(preparedStatements))
        if len(preparedStatements) == 0:
            print("No RDF for validation.")
        else:
            wordGroups, sections = get_wiki_sections()
            show_statements(preparedStatements)
            show_word_groups(wordGroups, sections)
            result = test_statements(preparedStatements, wordGroups)
            result1 = check_primary_resources(result)
            print(result1)
            time1 = datetime.datetime.now()
            timeDiff = time1 - time0
            timeSeconds = timeDiff.total_seconds()
            general = get_xml_general_info(wordGroups, sections, preparedStatements, timeSeconds)
            with open(f'xml/{time1.strftime("%Y-%m-%d(%Hh%Mm%Ss)")}.txt', 'w', encoding="utf-8") as f:
                f.write(get_xml_output_test(result1, general).replace("&", "&amp;"))


    ########################################################################################################################
    """ CODE """

    if openai.api_key == "":
        print("OpenAI API key missing")
        exit()
    default_run(
        [['Bioluminescence', 'http://www.wikidata.org/prop/direct/P1889', 'different from',
          'http://www.wikidata.org/entity/Q957208', 'iridescence'],
         ['Bioluminescence', 'http://www.wikidata.org/prop/direct/P1889', 'different from',
          'http://www.wikidata.org/entity/Q101248333', 'biofluorescence'],
         ['Bioluminescence', 'http://www.wikidata.org/prop/direct/P1889', 'different from',
          'http://www.wikidata.org/entity/Q192275', 'phosphorescence'],
         ['Bioluminescence', 'http://www.wikidata.org/prop/direct/P1889', 'different from',
          'http://www.wikidata.org/entity/Q191807', 'fluorescence'],
         ['Bioluminescence', 'http://www.wikidata.org/prop/direct/P279', 'subclass of',
          'http://www.wikidata.org/entity/Q13416689', 'cell metabolism']]
    )