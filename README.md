# Traceable LLM-based validation of statements in knowledge graphs
This repository contains scripts and supplementary materials (datasets and results) for the project Traceable LLM-based validation of statements in knowledge graphs.
The purpose of this project is to propose a method for validating RDF statements using LLMs and to suggest two possible applications in knowledge graphs, in our case Wikidata.
## Experiments
### Results
All data containing the results of the experiments (BioRED evaluation) or exemplary use-cases are located in data folder.
```md
├───data
    ├───introduction-examples
    ├───web_search-results
    │   ├───Q22686
    │   └───Q36233
    ├───wikipedia-results
    └───biored-results
```
### Scripts
All data required for the replicability of the experiments (BioRED evaluation, Web search, Wikipedia search) are located in scripts folder.
```md
├───scripts
    ├───biored_evaluation
    │   ├───biored-adjusted.json
    │   ├───bioRED-test.py
    │   └───biored-tests
    ├───web-search
    │   ├───wikidata.py
    │   └───wikidata-references
    └───wikipedia
        ├───index.html
        ├───schema.xsd
        ├───subject.xml
        ├───transformation-html.xsl
        ├───validation.py
        ├───verification.css
        ├───tasks
        └───xml
```
## Example
This example shows the application on Wikidata, specifically the use-case constisting of obtaining URL adresses from the Web.
We will demonstrate the workflow on Václav Havel (Q36233). By placing the numerical value of the identifier into the 'subjectQ' variable,
we set the task to the corresponding topic. The value is used in a SPARQL query to list out all statements about Václav Havel from Wikidata
that require a reference but are missing it. These statements are marked with a flag symbol when viewed on the Wikidata website. In our case,
53 statements were listed. These are the first ten results:
* ['Václav Havel', 'award received', 'http://www.wikidata.org/entity/Q2537841', 'Gottlieb Duttweiler Prize']
* ['Václav Havel', 'award received', 'http://www.wikidata.org/entity/Q7182737', 'Philadelphia Liberty Medal']
* ['Václav Havel', 'award received', 'http://www.wikidata.org/entity/Q700899', 'Quadriga']
* ['Václav Havel', 'award received', 'http://www.wikidata.org/entity/Q2100712', 'Point Alpha Prize']
* ['Václav Havel', 'award received', 'http://www.wikidata.org/entity/Q1124092', 'Concordia Prize']
* ['Václav Havel', 'award received', 'http://www.wikidata.org/entity/Q2028158', "St. George's Order of Victory"]
* ['Václav Havel', 'award received', 'http://www.wikidata.org/entity/Q2628946', 'Order of Rio Branco']
* ['Václav Havel', 'number of children', '0', '0']
* ['Václav Havel', 'award received', 'http://www.wikidata.org/entity/Q122167901', 'Evelyn F. Burkey Award']
* ['Václav Havel', 'award received', 'http://www.wikidata.org/entity/Q1453512', 'Freedom Award']

For each statement, a web search is performed to gather 5 internet sources covering the topic. We excluded Wikipedia sources by adding the "-wikipedia" parameter to the query.
For the first statement, the query would simply look like this: "Václav Havel award received Gottlieb Duttweiler Prize -wikipedia". The list of retreived articles for this specific query is as follows:
1. https://www.linkedin.com/pulse/gottlieb-duttweiler-prize-2019-goes-watson-matthias-hartmann
2. https://webfoundation.org/2015/04/sir-tim-berners-lee-receives-gottlieb-duttweiler-award-2015/
3. https://www.swissinfo.ch/eng/swiss-politics/joschka-fischer-wins-gottlieb-duttweiler-prize/3887864
4. https://www.vaclavhavel.cz/docs/vyrocni-zprava-2016-en.pdf
5. https://www.vaclavhavel.cz/docs/vyrocni-zprava-2017-en.pdf

The script attempts to download the content of the website. If the content is available, meaning there are values in \<p\> tags of the HTML source code, each paragraph is in combination with the original statement filled into a designated prompt, which is afterwards sent to the LLM API.
The prompt is designed to classify whether the paragraph (snippet of text) supports the statement or not. The model is asked to choose one out of three options, where only the first one (titled "a") is considered positive response. If the LLM replies with a negative answer, the script continues to following paragraph. If the answer is positive, we break the current cycle (we do not need to find multiple evidence in a single URL) and continue to next URL.

In our case supportive statements were found in two out of the five retreived URLs (specifically 1. and 3. address). These are raw responses from the LLM API which clearly choose the option "a", meaning responded positively, and marked the paragraph/source as supportive.
After manual check, we conclude that the source truly containted evidence of the truthfulness of the statement.
* The correct answer is a) The RDF statement can be directly verified from the snippet. The snippet contains direct proof.The snippet explicitly mentions that the award has been given to Václav Havel, and the award is from the Gottlieb Duttweiler Institute, which matches the RDF statement [\"Václav Havel\" - \"award received\" - \"Gottlieb Duttweiler Prize\"].
* The correct answer is: a) The RDF statement can be directly verified from the snippet. The snippet contains direct proof.The snippet explicitly mentions \"Previous winners of the award... include former Czech president, Václav Havel\", which directly verifies the RDF statement [\"Václav Havel\" - \"award received\" - \"Gottlieb Duttweiler Prize\"].

This demonstrates the workflow of the verification process with a successful example. A disadvantage of this method is that also untrustworthy sources can be returned by the Web search. This is mostly evaded in the method where we find sources via corresponding Wikipedia article, for which there is also a script available.
