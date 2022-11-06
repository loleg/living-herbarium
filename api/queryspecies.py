# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """#Gatti, con immagini
#defaultView:ImageGrid
SELECT ?item ?itemLabel ?pic ?gbifid
WHERE
{
VALUES (?gbifid) { ( "%s" ) }
?item wdt:P846 ?gbifid .
?item wdt:P18 ?pic
SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }
}
LIMIT 50"""


def get_results(species_numbers):
    if not species_numbers:
        return {}
    species_query = []
    for n in species_numbers.split(','):
        if n.isnumeric():
            species_query.append(str(n))
    species_text = '" ) ( "'.join(species_query)
    print(species_text)
    user_agent = "WDQS-example Python/%s.%s" % (
        sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query % species_text)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def get_result(species_number):
    if not species_number or not species_number.isnumeric():
        return {}
    user_agent = "WDQS-example Python/%s.%s" % (
        sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query % str(species_number))
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

# results = get_results(endpoint_url, query)
#
# for result in results["results"]["bindings"]:
#     print(result)
