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
    ?uas wdt:P31/wdt:P279* wd:Q3918 . # is a university (and the subclasses thereof)
    ?uas wdt:P17 wd:Q55 . # country Netherlands
  } UNION {
    ?uas wdt:P31 wd:Q31855 . # is a research institute
    ?uas wdt:P17 wd:Q55 . # country Netherlands
  } UNION {
    ?uas wdt:P31 wd:Q1059324 . # is a university hospital (de MC's)
    ?uas wdt:P17 wd:Q55 . # country Netherlands
  } UNION {
    VALUES ?uas {wd:Q50037936 } . # SIA
  } UNION {
    VALUES ?uas {wd:Q131428044 } . # TFF
  } UNION {
    VALUES ?uas {wd:Q253439} . # KNAW
  }
  ?uas rdfs:label ?name .
  OPTIONAL { ?uas wdt:P856 ?webSite . } # Official website
  OPTIONAL {
    ?uas skos:altLabel ?altName .
    FILTER ( lang(?altName) in ("en","nl", "mul") )
  }
  # Note: the mul is the default language
  FILTER ( lang(?name) in ("en","nl", "mul") )
}
""")
sparql.setReturnFormat(XML)
results = sparql.query().convert()
results.serialize(destination="seedData.ttl")
