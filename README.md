[![Serialize AMP to PFP-CIDOC](https://github.com/Auden-Musulin-Papers/amp2pfp/actions/workflows/amp2pfp.yml/badge.svg)](https://github.com/Auden-Musulin-Papers/amp2pfp/actions/workflows/amp2pfp.yml)
# amp2pfp
repo to serialize amp-entity-data into pfp-cidoc rdf

This repo fetches data from the [amp-entities repo](https://github.com/Auden-Musulin-Papers/amp-entities) and converts it into a CIDOC CRM RDF Graph (hopefully) validating against the (in)famous [PFP-Shacl](https://pfp-schema.acdh.oeaw.ac.at/shacl/shacl.ttl).

## pfp
If you don't know what PFP stands for: [PFP](https://www.oeaw.ac.at/acdh/research/dh-research-infrastructure/activities/modelling-humanities-data/pfp-prosopographical-research-platform-austria) means **Prosopographical Research Platform Austria** and yes, it only makes sense in the German translation **Prosopographische Forschungsplattform Österreich**.


## develop


```bash
git clone https://github.com/Auden-Musulin-Papers/amp2pfp.git
cd amp2pfp
[python -m venv venv]
[source venv/bin/activate]
pip install -r requirements.txt
cp .env .secret [and add your ownloud credentials]
```



## build and validate the graph
```bash
./scripts/build_amp_graph.sh
```

the graph is uploaded to [owncloud](https://cloud.oeaw.ac.at/index.php/s/K58kj4kGyGCYmai)
