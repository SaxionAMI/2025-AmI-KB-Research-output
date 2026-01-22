
from pylode.profiles.ontpub import OntPub

ontology_path = "eurio_v2_5.ttl"   # replace with your file
output_html  = "ontology_doc.html"

od = OntPub(ontology=ontology_path)

html = od.make_html(destination=output_html)

print(f"Done: {output_html}")
