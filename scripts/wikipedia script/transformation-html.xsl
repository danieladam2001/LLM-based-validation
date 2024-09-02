<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">

    <xsl:output method="html" version="5"/>
    <xsl:output method="html" version="5" name="htmlResults"/>

    <xsl:template match="/">
        <html lang="cs">
            <head>
                <link rel="stylesheet" href="verification.css" type="text/css"/>
                <title>Wikidata Verification Results</title>
                <link rel="icon" type="image/x-icon" href="./verified.png"/>
            </head>
            <body>
                <div class="wrapper">
                    <table class="nav">
                        <tr>
                            <td class="navCell">
                                <a class="menuHref selected" href="index.html">General
                                    information</a>
                            </td>
                            <td class="navCell">
                                <a class="menuHref"
                                    href="./tasks/{generate-id(/wikidataVerification/tasks/task[1])}.html"
                                    >Detailed results</a>
                            </td>
                        </tr>
                    </table>
                    <h1>General information about the whole process</h1>
                    <div class="general-info">
                        <xsl:apply-templates select="wikidataVerification/generalInformation"/>
                    </div>
                    <xsl:apply-templates select="wikidataVerification/tasks"/>
                </div>
            </body>
            <footer>
                <a class="icon" href="https://www.flaticon.com/free-icons/verified"
                    title="verified icon">Verified icon created by sonnycandra - Flaticon</a>
            </footer>
        </html>
    </xsl:template>

    <xsl:template match="task">
        <xsl:result-document href="./tasks/{generate-id()}.html" format="htmlResults">
            <html lang="cs">
                <head>
                    <link rel="stylesheet" href="../verification.css" type="text/css"/>
                    <title>
                        <xsl:value-of select="subject"/>
                    </title>
                    <link rel="icon" type="image/x-icon" href="../verified.png"/>
                </head>
                <body>
                    <div class="wrapper">
                        <xsl:choose>
                            <xsl:when test="generate-id(preceding-sibling::task[1]) = ''">
                                <table class="nav">
                                    <tr>
                                        <td class="navCell">
                                            <a class="menuHref" href="../index.html">General
                                                information</a>
                                        </td>
                                        <td class="navCell navCellButton" style="color: #dbdbdb"
                                            >←</td>
                                        <td class="navCell navCellDetailed">
                                            <a class="menuHref selected"
                                                href="{generate-id(/wikidataVerification/tasks/task[1])}.html"
                                                >Detailed results</a>
                                        </td>
                                        <td class="navCell navCellButton">
                                            <a class="menuHref"
                                                href="{generate-id(following-sibling::task[1])}.html"
                                                >→</a>
                                        </td>
                                    </tr>
                                </table>
                            </xsl:when>
                            <xsl:when test="generate-id(following-sibling::task[1]) = ''">
                                <table class="nav">
                                    <tr>
                                        <td class="navCell">
                                            <a class="menuHref" href="../index.html">General
                                                information</a>
                                        </td>
                                        <td class="navCell navCellButton">
                                            <a class="menuHref"
                                                href="{generate-id(preceding-sibling::task[1])}.html"
                                                >←</a>
                                        </td>
                                        <td class="navCell navCellDetailed">
                                            <a class="menuHref selected"
                                                href="{generate-id(/wikidataVerification/tasks/task[1])}.html"
                                                >Detailed results</a>
                                        </td>
                                        <td class="navCell navCellButton" style="color: #dbdbdb"
                                            >→</td>
                                    </tr>
                                </table>
                            </xsl:when>
                            <xsl:otherwise>
                                <table class="nav">
                                    <tr>
                                        <td class="navCell">
                                            <a class="menuHref" href="../index.html">General
                                                information</a>
                                        </td>
                                        <td class="navCell navCellButton">
                                            <a class="menuHref"
                                                href="{generate-id(preceding-sibling::task[1])}.html"
                                                >←</a>
                                        </td>
                                        <td class="navCell navCellDetailed">
                                            <a class="menuHref selected"
                                                href="{generate-id(/wikidataVerification/tasks/task[1])}.html"
                                                >Detailed results</a>
                                        </td>
                                        <td class="navCell navCellButton">
                                            <a class="menuHref"
                                                href="{generate-id(following-sibling::task[1])}.html"
                                                >→</a>
                                        </td>
                                    </tr>
                                </table>
                            </xsl:otherwise>
                        </xsl:choose>
                        <xsl:apply-templates select="." mode="detail"/>
                    </div>
                </body>
                <footer>
                    <a class="icon" href="https://www.flaticon.com/free-icons/verified"
                        title="verified icon">Verified icon created by sonnycandra - Flaticon</a>
                </footer>
            </html>
        </xsl:result-document>
    </xsl:template>

    <xsl:template match="task" mode="detail">
        <h1>[<xsl:value-of select="subject"/> - <xsl:value-of select="predicate"/> - <xsl:value-of
                select="object"/>] + Text group <xsl:value-of select="textGroupID"/></h1>
        <hr class="first"/>
        <h3>Information about the selected task</h3>
        <div class="bg">
            <table>
                <tr class="infoRow">
                    <td class="generalInfoCellTitle">Attribute</td>
                    <td class="generalInfoCell">Value</td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Subject</td>
                    <td class="generalInfoCell">
                        <xsl:value-of select="subject"/>
                    </td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Predicate</td>
                    <td class="generalInfoCell">
                        <xsl:value-of select="predicate"/>
                    </td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Predicate URL</td>
                    <td class="generalInfoCell">
                        <a href="{predicateURL}" target="_blank">
                            <xsl:value-of select="predicateURL"/>
                        </a>
                    </td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Object</td>
                    <td class="generalInfoCell">
                        <xsl:value-of select="object"/>
                    </td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Object URL</td>
                    <xsl:choose>
                        <xsl:when test="matches(objectURL, 'www')">
                            <td class="generalInfoCell">
                                <a href="{objectURL/text()}" target="_blank">
                                    <xsl:value-of select="objectURL"/>
                                </a>
                            </td>
                        </xsl:when>
                        <xsl:otherwise>
                            <td class="generalInfoCell">
                                <xsl:value-of select="objectURL"/>
                            </td>
                        </xsl:otherwise>
                    </xsl:choose>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Text group ID</td>
                    <td class="generalInfoCell">
                        <xsl:value-of select="textGroupID"/>
                    </td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">ID of the prompt used</td>
                    <td class="generalInfoCell">
                        <xsl:value-of select="promptID"/>
                    </td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Answer of the LLM</td>
                    <td class="generalInfoCell">
                        <xsl:value-of select="modelAnswer"/>
                    </td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Does the text group support given RDF?</td>
                    <xsl:choose>
                        <xsl:when test="matches(doesTextSupportRDF, 'YES')">
                            <td class="generalInfoCell">
                                <a class="true-answer"><xsl:value-of select="doesTextSupportRDF"/>
                                    (if the answer is positive, detailed examination was
                                    executed)</a>
                            </td>
                        </xsl:when>
                        <xsl:otherwise>
                            <td class="generalInfoCell">
                                <a class="false-answer"><xsl:value-of select="doesTextSupportRDF"/>
                                    (if the answer is positive, detailed examination was
                                    executed)</a>
                            </td>
                        </xsl:otherwise>
                    </xsl:choose>
                </tr>
            </table>
        </div>
        <xsl:apply-templates select="detailedResearch"/>
    </xsl:template>

    <xsl:template match="detailedResearch">
        <hr/>
        <h3>Detailed examination (each paragraph checked separately)</h3>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="paragraph">
        <div class="bg">
            <table class="paragraph">
                <tr class="infoRow">
                    <td class="generalInfoCellTitle">Attribute</td>
                    <td class="generalInfoCell">Value</td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Paragraph content</td>
                    <td class="generalInfoCell">
                        <xsl:value-of select="paragraphText"/>
                    </td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Structure of the prompt</td>
                    <td class="generalInfoCell">Can the given RDF statement be inferred from the
                        given snippet? RDF: ["<a class="rdf"><xsl:value-of select="../../subject"
                            /></a>" - "<a class="rdf"><xsl:value-of select="../../predicate"/></a>"
                        - "<a class="rdf"><xsl:value-of select="../../object"/></a>"], snippet: "<a
                            class="snippet"><xsl:value-of select="paragraphText"/></a>". Please,
                        give an answer and also the reasoning behind it!</td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Answer of the LLM</td>
                    <td class="generalInfoCell">
                        <xsl:value-of select="modelAnswer"/>
                    </td>
                </tr>
                <xsl:choose>
                    <xsl:when test="doesTextSupportRDF = 'YES'">
                        <tr>
                            <td class="generalInfoCellTitle">Parsed LLM answer</td>
                            <td class="generalInfoCell">
                                <a class="true-answer">Yes, according to the LLM the given paragraph
                                    supports the RDF and following reference numbers were
                                        extracted:<a class="rdf numbers"><xsl:value-of
                                            select="referenceNumbers"/></a></a>
                            </td>
                        </tr>

                        <!--                    
                    <xsl:apply-templates select="paragraphs" mode="detailedExam"></xsl:apply-templates>-->
                    </xsl:when>
                    <xsl:otherwise>
                        <tr>
                            <td class="generalInfoCellTitle">Parsed LLM answer</td>
                            <td class="generalInfoCell">
                                <a class="false-answer">No, the LLM did not find any supporting text
                                    in the given text and therefore moved on to the next
                                    paragraph</a>
                            </td>
                        </tr>
                    </xsl:otherwise>
                </xsl:choose>
            </table>
        </div>
        <xsl:apply-templates select="references"/>
    </xsl:template>

    <xsl:template match="references/reference">
        <div class="bg narrow1">
            <table class="paragraph">
                <tr>
                    <td class="generalInfoCellTitle">Reference number (Wikipedia) found?</td>
                    <td class="generalInfoCell"><a class="rdf"><b><xsl:value-of select="referenceNumber"/></b></a> (if a
                        number was extracted, the wikipedia page contains a reference for the
                        previously examined paragraph)</td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Reference title (Wikipedia) found?</td>
                    <td class="generalInfoCell">
                        <xsl:value-of select="referenceTitle"/>
                    </td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Reference URL (Wikipedia) found?</td>
                    <td class="generalInfoCell"><xsl:value-of select="referenceURL"/> (if the URL
                        returns no results, the script attempts to send request to an alternative at
                        web.archive.org)</td>
                </tr>
                <tr>
                    <td class="generalInfoCellTitle">Valid reference content received?</td>
                    <td class="generalInfoCell">
                        <xsl:choose>
                            <xsl:when test="websiteContent = 'FOUND'">
                                <a class="true-answer"><xsl:value-of select="websiteContent"/></a>
                            </xsl:when>
                            <xsl:otherwise>
                                <a class="false-answer"><xsl:value-of select="websiteContent"/></a>
                            </xsl:otherwise>
                        </xsl:choose> (if the answer is positive, paragraphs from the primary source
                        were downloaded and compared seperately)</td>
                </tr>
            </table>
        </div>
        <xsl:if test="websiteContent = 'FOUND'">
            <xsl:apply-templates select="paragraphs" mode="detailedExam"/>
        </xsl:if>
    </xsl:template>

    <xsl:template match="paragraphs/paragraph" mode="detailedExam">
        <div class="bg narrow">
            <xsl:if test="doesTextSupportRDF = 'YES'">
                <table class="primaryParagraph" style="background-color:#90adab;">
                    <xsl:apply-templates select="." mode="color"/>
                </table>
            </xsl:if>
            <xsl:if test="doesTextSupportRDF = 'NO'">
                <table class="primaryParagraph">
                    <xsl:apply-templates select="." mode="color"/>
                </table>
            </xsl:if>
        </div>
    </xsl:template>

    <xsl:template match="paragraphs/paragraph" mode="color">
        <tr class="infoRow">
            <td class="generalInfoCellTitle">Attribute</td>
            <td class="generalInfoCell">Value</td>
        </tr>
        <tr>
            <td class="generalInfoCellTitle">Content of paragraph received from the primary
                source</td>
            <td class="generalInfoCell">
                <xsl:value-of select="paragraphText"/>
            </td>
        </tr>
        <tr>
            <td class="generalInfoCellTitle">Answer of the LLM</td>
            <td class="generalInfoCell">
                <xsl:value-of select="modelAnswer"/>
            </td>
        </tr>
        <tr>
            <td class="generalInfoCellTitle">Match found in primary source?</td>
            <xsl:choose>
                <xsl:when test="doesTextSupportRDF = 'YES'">
                    <td class="generalInfoCell">
                        <a class="true-answer">Yes, according to the LLM the given paragraph from the primary source
                            supports the RDF! </a>
                    </td>
                </xsl:when>
                <xsl:otherwise>
                    <td class="generalInfoCell">
                        <a class="false-answer">No, the LLM did not find any supporting text in the given text and therefore moved on to the next paragraph</a>
                    </td>
                </xsl:otherwise>
            </xsl:choose>

        </tr>
    </xsl:template>

    <xsl:template match="generalInformation">
        <hr class="first"/>
        <h3>Task characteristics</h3>
        <div class="bg">
        <table class="generalInfoTable">
            <tr class="infoRow">
                <td class="generalInfoCellTitle">Attribute</td>
                <td class="generalInfoCell">Value</td>
            </tr>
            <tr>
                <td class="generalInfoCellTitle">LLM used: </td>
                <td class="generalInfoCell">
                    <xsl:value-of select="largeLanguageModel"/>
                </td>
            </tr>
            <tr>
                <td class="generalInfoCellTitle">Date of testing:</td>
                <td class="generalInfoCell">
                    <xsl:value-of select="date"/>
                </td>
            </tr>
            <tr>
                <td class="generalInfoCellTitle">Time of testing:</td>
                <td class="generalInfoCell">
                    <xsl:value-of select="time"/>
                </td>
            </tr>
            <xsl:apply-templates select="duration"/>
            <tr>
                <td class="generalInfoCellTitle">Subject ID:</td>
                <td class="generalInfoCell">
                    <xsl:value-of select="subjectID"/>
                </td>
            </tr>
            <tr>
                <td class="generalInfoCellTitle">Subject name:</td>
                <td class="generalInfoCell">
                    <xsl:value-of select="subject"/>
                </td>
            </tr>
            <tr>
                <td class="generalInfoCellTitle">Subject URL:</td>
                <td class="generalInfoCell">
                    <a href="{wikidataURL/text()}">
                        <xsl:value-of select="wikidataURL"/>
                    </a>
                </td>
            </tr>
            <tr>
                <td class="generalInfoCellTitle">Subject Permalink:</td>
                <td class="generalInfoCell">
                    <a href="{wikidataPermalink/text()}">
                        <xsl:value-of select="wikidataPermalink"/>
                    </a>
                </td>
            </tr>
            <tr>
                <td class="generalInfoCellTitle">Wikipedia URL:</td>
                <td class="generalInfoCell">
                    <a href="{wikipediaURL/text()}">
                        <xsl:value-of select="wikipediaURL"/>
                    </a>
                </td>
            </tr>
            <tr>
                <td class="generalInfoCellTitle">Wikipedia Permalink:</td>
                <td class="generalInfoCell">
                    <a href="{wikipediaPermalink/text()}">
                        <xsl:value-of select="wikipediaPermalink"/>
                    </a>
                </td>
            </tr>
            <tr>
                <td class="generalInfoCellTitle">Wikidata Endpoint:</td>
                <td class="generalInfoCell">
                    <a href="{wikidataEndpointURL/text()}">
                        <xsl:value-of select="wikidataEndpointURL"/>
                    </a>
                </td>
            </tr>
        </table>
        </div>
        <xsl:apply-templates select="statements"/>
        <xsl:apply-templates select="textGroups"/>
        <xsl:apply-templates select="prompts"/>
    </xsl:template>

    <xsl:template match="duration">
        <tr>
            <td class="generalInfoCellTitle">Duration (<xsl:value-of select="./@unit"/>):</td>
            <td class="generalInfoCell">
                <div class="">
                    <xsl:value-of select="."/>
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="./@unit"/>
                </div>
            </td>
        </tr>

    </xsl:template>

    <xsl:template match="statements">
        <hr/>
        <h3>List of uncited statements received from Wikidata</h3>
        <div class="bg">
        <table class="statements">
            <tr class="infoRow">
                <td class="statementCellSubject">Subject</td>
                <td class="statementCellPredicate">Predicate URL adress</td>
                <td class="statementCellPredicateURL">Predicate</td>
                <td class="statementCellobject">Object URL adress</td>
                <td class="statementCellobjectURL">Object</td>
            </tr>
            <xsl:apply-templates/>
        </table>
        </div>
    </xsl:template>

    <xsl:template match="statement">
        <tr>
            <td class="statementCellSubject">
                <xsl:value-of select="subject"/>
            </td>
            <td class="statementCellPredicate">
                <a href="{predicate/text()}" target="_blank">
                    <xsl:value-of select="predicate"/>
                </a>
            </td>
            <td class="statementCellPredicateURL">
                <xsl:value-of select="predicateURL"/>
            </td>
            <xsl:choose>
                <xsl:when test="matches(object, 'www')">
                    <td class="statementCellobject">
                        <a href="{object/text()}" target="_blank">
                            <xsl:value-of select="object"/>
                        </a>
                    </td>
                </xsl:when>
                <xsl:otherwise>
                    <td class="statementCellobject">
                        <xsl:value-of select="object"/>
                    </td>
                </xsl:otherwise>
            </xsl:choose>
            <td class="statementCellobjectURL">
                <xsl:value-of select="objectURL"/>
            </td>
        </tr>
    </xsl:template>

    <xsl:template match="textGroups">
        <hr/>
        <h3>Text groups received from corresponding Wikipedia page</h3>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="group">
        <div class="bg">
        <table class="group">
            <tr class="infoRow">
                <td>Group <xsl:value-of select="groupNumber"/></td>
            </tr>
            <tr>
                <td>Number of characters: <xsl:value-of select="characters"/></td>
            </tr>
            <tr>
                <td class="groupText">
                    <xsl:value-of select="groupText"/>
                </td>
            </tr>
        </table>
        </div>
    </xsl:template>

    <xsl:template match="prompts">
        <hr/>
        <h3>Prompt structures used during the verification task</h3>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="prompt">
        <div class="bg">
        <table class="prompt">
            <tr class="infoRow">
                <td>Prompt <xsl:value-of select="promptNumber"/></td>
            </tr>
            <tr>
                <td>
                    <xsl:value-of select="intro"/>
                </td>
            </tr>
            <tr>
                <td>
                    <xsl:value-of select="rdf"/>
                </td>
            </tr>
            <tr>
                <td>
                    <xsl:value-of select="snippet"/>
                </td>
            </tr>
            <tr>
                <td>
                    <xsl:value-of select="request"/>
                </td>
            </tr>
        </table>
        </div>
    </xsl:template>

























</xsl:stylesheet>
