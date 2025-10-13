from SPARQLWrapper import SPARQLWrapper, XML

wdEndPoint = 'https://query.wikidata.org/sparql'
sparql = SPARQLWrapper(wdEndPoint)
sparql.setQuery("""
PREFIX eurio: <http://data.europa.eu/s66#>
CONSTRUCT {
  ?uas a eurio:Organisation .
  ?uas eurio:legalName ?name .
  ?uas skos:altLabel ?altName .
  ?uas eurio:hasSite ?webSite .
} WHERE {
  {
    ?uas wdt:P463 wd:Q2688654 . # member of Vereniging Hogescholen
  } UNION {
    ?uas wdt:P31 wd:Q3918 . # is a university
    ?uas wdt:P17 wd:Q55 . # country Netherlands
  }
  OPTIONAL { ?uas wdt:P856 ?webSite . } # Official website
  ?uas rdfs:label ?name .
  ?uas skos:altLabel ?altName .
  # Note: the mul is the default language
  FILTER ( lang(?name) in ("en","nl", "mul") )
  FILTER ( lang(?altName) in ("en","nl", "mul") )
}
""")
sparql.setReturnFormat(XML)
results = sparql.query().convert()
results.serialize(destination="uasWikidata.ttl")
