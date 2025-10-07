from SPARQLWrapper import SPARQLWrapper, XML

wdEndPoint = 'https://query.wikidata.org/sparql'
sparql = SPARQLWrapper(wdEndPoint)
sparql.setQuery("""
    PREFIX eurio: <http://data.europa.eu/s66#>
    CONSTRUCT {
      ?uas a eurio:Organisation .
        ?uas rdfs:label ?name .
          ?uas skos:altLabel ?altName .
            ?uas eurio:hasSite ?webSite .
            }
            WHERE {
            #{?uas wdt:P31 wd:Q38723 .} # is a higher education institution
            #UNION
            #{?uas wdt:P31 wd:Q17028020.} # is a vocational university
              
              ?uas wdt:P463 wd:Q2688654 . # member of Vereniging Hogescholen
              ?uas rdfs:label ?name .
              ?uas skos:altLabel ?altName .
              OPTIONAL { ?uas wdt:P856 ?webSite . } # Official website
              FILTER ( lang(?name) in ("en","nl") )
              FILTER ( lang(?altName) in ("en","nl") )
              }
""")
sparql.setReturnFormat(XML)
results = sparql.query().convert()
results.serialize(destination="uasWikidata.ttl")
