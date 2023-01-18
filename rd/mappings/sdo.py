"""
This is a Python script that converts IDN Catalogue Profile metadata to schema.org metadata

Dependencies:
    * rdflib - https://pypi.org/project/rdflib/
"""
import argparse
from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import DCAT, DCTERMS, GEO, PROV, RDF, SDO, TIME


def _create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input",
        help="The path of an RDF file in IDN CP form to convert.",
    )

    parser.add_argument(
        "-f",
        "--format",
        help="An RDF format for the output",
        choices=["json-ld", "turtle", "xml", "n-triples"],
        default="json-ld",
    )

    return parser


def convert(g: Graph) -> Graph:
    """Reads an IDN CP graph and produces a schema.org graph.

    Uses mapping logic from https://w3id.org/idn/def/cp/sdo.ttl"""
    g2 = Graph(bind_namespaces="rdflib")

    # classes
    for s in g.subjects(RDF.type, DCAT.Resource):
        g2.add((s, RDF.type, SDO.CreativeWork))

    for s in g.subjects(RDF.type, DCAT.Dataset):
        g2.add((s, RDF.type, SDO.Dataset))

    for s, o in g.subject_objects(DCTERMS.type):
        g2.add((s, SDO.additionalType, o))

    # basic
    for s, o in g.subject_objects(DCTERMS.title):
        g2.add((s, SDO.name, o))

    for s, o in g.subject_objects(DCTERMS.description):
        g2.add((s, SDO.description, o))

    # dates
    for s, o in g.subject_objects(DCTERMS.created):
        g2.add((s, SDO.dateCreated, o))

    for s, o in g.subject_objects(DCTERMS.modified):
        g2.add((s, SDO.dateModified, o))

    for s, o in g.subject_objects(DCTERMS.issued):
        g2.add((s, SDO.dateIssued, o))

    # rights
    for s, o in g.subject_objects(DCTERMS.license):
        g2.add((s, SDO.license, o))

    for s, o in g.subject_objects(DCTERMS.rights):
        g2.add((s, SDO.copyrightNotice, o))

    for s, o in g.subject_objects(DCTERMS.accessRights):
        g2.add((s, SDO.conditionsOfAccess, o))

    # provenance
    for s, o in g.subject_objects(DCTERMS.source):
        g2.add((s, SDO.isBasedOn, o))

    for s, o in g.subject_objects(PROV.wasDerivedFrom):
        g2.add((s, SDO.isBasedOn, o))

    # spatial
    for s, o in g.subject_objects(DCTERMS.spatial):
        if isinstance(o, URIRef):  # a Feature
            g2.add((s, SDO.spatialCoverage, o))
        elif isinstance(o, BNode):  # likely a Geometry
            for o2 in g.objects(o, GEO.asWKT):
                bn = BNode()
                g2.add((s, SDO.spatialCoverage, bn))
                g2.add((bn, RDF.type, SDO.Place))
                prop = BNode()
                g2.add((bn, SDO.additionalProperty, prop))
                g2.add((prop, RDF.type, SDO.PropertyValue))
                g2.add((prop, SDO.name, Literal("well-known text (WKT) representation of geometry")))
                g2.add((prop, SDO.propertyID, Literal("http://www.wikidata.org/entity/Q4018860")))
                g2.add((prop, SDO.value, Literal(str(o2))))

    # temporal
    for s, o in g.subject_objects(DCTERMS.temporal):
        for p2, o2 in g.predicate_objects(o):
            if p2 == TIME.hasBeginning:
                for p3, o3 in g.predicate_objects(o2):
                    if p3 in [TIME.inXSDDateTime, TIME.inDateTime, TIME.inXSDDate, TIME.inXSDDateTimeStamp, TIME.inXSDgYear, TIME.inXSDgYearMonth]:
                        g2.add((s, SDO.coverageStartTime, o3))
            if p2 == TIME.hasEnd:
                for p3, o3 in g.predicate_objects(o2):
                    if p3 in [TIME.inXSDDateTime, TIME.inDateTime, TIME.inXSDDate, TIME.inXSDDateTimeStamp, TIME.inXSDgYear, TIME.inXSDgYearMonth]:
                        g2.add((s, SDO.coverageEndTime, o3))

    # access
    for s, o in g.subject_objects(DCAT.accessURL):
        # if the value is a BN, then this accessURL must be on a Distribution of a Resource, not the Resource directly
        if isinstance(s, BNode):
            for s2 in g.subjects(DCAT.distribution, s):
                g2.add((s2, SDO.url, o))
        else:
            g2.add((s, SDO.url, o))

    # classification
    for s, o in g.subject_objects(DCAT.theme):
        bn = BNode()
        g2.add((s, SDO.keywords, bn))
        g2.add((bn, RDF.type, SDO.DefinedTerm))
        g2.add((bn, SDO.url, o))

    # Catalogues
    for s in g.subjects(RDF.type, DCAT.Catalog):
        g2.add((s, RDF.type, SDO.DataCatalog))

    # catalogue membership
    # handle inverse
    for s, o in g.subject_objects(DCTERMS.hasPart):
        g.add((o, DCTERMS.isPartOf, s))

    for s, o in g.subject_objects(DCTERMS.isPartOf):
        # unqualified catalogue membership
        if type(o) == URIRef:
            # check domain, don't bother with range as unlikely to have class info
            if (s, RDF.type, DCAT.Resource) in g or (s, RDF.type, DCAT.Dataset) in g:
                g2.add((s, SDO.includedInDataCatalog, o))
        # qualified catalogue membership
        # following schema.org Role modelling with double properties:
        # http://blog.schema.org/2014/06/introducing-role.html
        elif type(o) == BNode:
            for o2 in g.objects(o, PROV.entity):
                g2.add((s, SDO.includedInDataCatalog, o))
                g2.add((o, RDF.type, SDO.Role))
                g2.add((o, SDO.includedInDataCatalog, o2))
                for o3 in g.objects(o, DCAT.hadRole):
                    g2.add((o, SDO.roleName, o3))

    return g2


if __name__ == "__main__":
    # get access to command line args
    args = _create_parser().parse_args()

    # load the supplied IDN CP RDF file
    g = Graph().parse(args.input)

    if args.format == "turtle":
        f = "longturtle"
    elif args.format == "xml":
        f = "pretty-xml"
    else:
        f = args.format

    print(convert(g).serialize(format=f))
