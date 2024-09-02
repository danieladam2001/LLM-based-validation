# Script for verifying statements through corresponding Wikipedia search
We designed a method of obtaining primary sources for manually selected statements via corresponding Wikipedia article.
The required inputs for the script are a Wikidata identifier for a selected topic and a list of specific statements contained on corresponding Wikidata page.
The output of this script is a text file saved in /xml folder which is automatically created at the start of the process.
The file contains an XML format which can be later transformed into a user-friendly HTML page.
To make this transformation:
* Copy the whole XML content from the desired .txt file
* Paste the copied XML to subject.xml and save it
* Open Oxygen editor and apply a transformation using the transformation-html.xsl file
* Open index.html using your web browser to view the content




By default, the HTML is generated for data/wikipedia-results/Bioluminescence-gpt4.txt

