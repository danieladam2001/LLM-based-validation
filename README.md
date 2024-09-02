# Traceable LLM-based validation of statements in knowledge graphs
This repository contains scripts and supplementary materials (datasets and results) for the project Traceable LLM-based validation of statements in knowledge graphs.
The purpose of this project is to propose a method for validating RDF statements using LLMs and to suggest two possible applications in knowledge graphs, in our case Wikidata.
## Abstract
This article presents a method for verifying RDF triples using LLMs, with an emphasis
on providing traceable arguments. Because the LLMs cannot currently reliably identify
the origin of the information used to construct the response to the user query, our
approach is to avoid using internal LLM factual knowledge altogether. Instead, verified
RDF statements are compared to chunks of external documents retrieved through a
web search or Wikipedia. To assess the possible application of this workflow on
biosciences content, we evaluated 1,719 positive statements from the BioRED dataset
and the same number of newly generated negative statements. The resulting precision
is 88%, and recall is 44%. This indicates that the method requires human oversight.
We demonstrate the method on Wikidata, where a SPARQL query is used to
automatically retrieve statements needing verification. Overall, the results suggest that
LLMs could be used for large-scale verification of statements in KGs, a task previously
unfeasible due to human annotation costs.
## Experiments
### Results
All data containing the results of the experiments (BioRED evaluation) or exemplary use-cases are located in data folder.
```md
├───data
│   ├───introduction-examples
│   ├───web_search-results
│   │   ├───Q22686
│   │   └───Q36233
│   ├───wikipedia-results
│   └───biored-results
```
### Scripts
All data required for the replicability of the experiments (BioRED evaluation, Web search, Wikipedia search) are located in scripts folder.
```md
├───scripts
    ├───biored evaluation script
    │   ├───biored-adjusted.json
    │   ├───bioRED-test.py
    │   └───biored-tests
    ├───web-search script
    │   ├───wikidata.py
    │   └───wikidata-references
    └───wikipedia script
        ├───index.html
        ├───schema.xsd
        ├───subject.xml
        ├───transformation-html.xsl
        ├───validation.py
        ├───verification.css
        ├───tasks
        └───xml
```
