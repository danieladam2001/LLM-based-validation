# Script for verifying statements through Web Search
We designed a way to obtain Web sources for Wikidata statements based on a Wikidata subject identifier.
The identifier is pasted into a SPARQL query which returns a list of all Wikidata statements of the identifier that are missing a reference even though they should have one (they violate the reference constraint).
Each statement is searched on the Web and top five results are returned for examination. We attempt to download content of each URL and if the content is available, we split the text into paragraphs by extracting value from the \<p\> tags.
For each paragraph, we use a LLM (Llama 3 70B) to assess whether it is possible to use the text as a support for the statement. If the response is positive, we use the source as an evidence of the truthfulness of the statement.
The results are saved into /wikidata-references folder which is created automatically at the start of the script.
Each identifier is then saved into a separate folder named by the identifier.
Each statement with its findings is saved as a single .txt file in the JSON format.
