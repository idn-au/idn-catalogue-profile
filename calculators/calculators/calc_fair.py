"""
Calculates the FAIR score of a resource.

usage: calc_fair.py [-h] [-o OUTPUT] [-v VALIDATE] input

positional arguments:
  input                 The path of an RDF file or URL of RDF data online.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        A path for an output file or an output format. If set to a file
                        path, the output will be written to the file, rather than returned
                        to standard out. If a format is given, that format will be returned
                        to. standard out. For a given output file path, the file extension
                        determines the format and must be one of .ttl, .rdf, .json-ld, .nt
                        for Turtle, RDF/XML, JSON-LD or N-Ttripes. If a format is given, it
                        must be one of text/turtle, application/rdf+xml,
                        application/ld+json, text/nt
  -v VALIDATE, --validate VALIDATE
                        Validate the input with the IDN CP's validator before trying to
                        score it
"""
import argparse
import os
from pathlib import Path
from typing import Optional, Union, Tuple

import httpx
from pyshacl import validate as val
from rdflib import Graph, URIRef, BNode, Namespace, Literal
from rdflib.namespace import DCAT, DCTERMS, PROV, RDF, TIME
from rdflib.term import Node

from _SCORES import SCORES

QB = Namespace("http://purl.org/linked-data/cube#")


RDF_FILE_SUFFIXES = {
    ".ttl": "text/turtle",
    ".rdf": "application/rdf+xml",
    ".json-ld": "application/ld+json",
    ".nt": "text/nt",
}


EXTRA_PREFIXES = {
    "scores": SCORES,
    "qb": QB,
}


def _create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input",
        help="The path of an RDF file or URL of RDF data online.",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="A path for an output file or an output format. If set to a file path, the output will be written to "
        "the file, rather than returned to standard out. If a format is given, that format will be returned to. "
        "standard out. For a given output file path, the file extension determines the format and must be one "
        f"of {', '.join(RDF_FILE_SUFFIXES.keys())} for Turtle, RDF/XML, JSON-LD or N-Ttripes. "
        f"If a format is given, it must be one of {', '.join(RDF_FILE_SUFFIXES.values())}",
        default="text/turtle",
    )

    parser.add_argument(
        "-v",
        "--validate",
        help="Validate the input with the IDN CP's validator before trying to score it",
        default=False,
    )

    return parser


def _output_is_format(s: str):
    """Checks to see if a string is a known format or a graph"""

    if s in RDF_FILE_SUFFIXES.keys() or s == "graph":
        return True
    else:
        return False


def _get_valid_output_dir(path: Path):
    """Checks that a specified output directory is an existing directory and returns the directory if valid"""

    if not os.path.isdir(path.parent):
        raise argparse.ArgumentTypeError(
            f"The output path you specified, {path}, does not indicate a valid directory"
        )

    return path.parent


def _get_valid_output_file_and_type(path: Path):
    """Checks that a specified output file has a known file type extension and returns it and the corresponding
    RDF Media Type if it is"""

    known_file_types = [".ttl", ".rdf", ".json-ld", ".nt"]
    if path.suffix not in known_file_types:
        raise argparse.ArgumentTypeError(
            f"The output path you specified, {path}, does not specify a known file type. "
            f"It must be one of {', '.join(known_file_types)}"
        )

    return path.name, RDF_FILE_SUFFIXES[path.suffix]


def _input_is_a_file(s: str):
    """Checks if a string is a path to an existing file"""

    if Path(s).is_file():
        return True
    else:
        return False


def _load_input_graph(path_or_url: Union[Path, str]) -> Graph:
    """Parses a file at the path location or download the data from a given URL and returns an RDFLib Graph"""

    g = Graph()
    if _input_is_a_file(path_or_url):
        g.parse(path_or_url)
    else:
        d = httpx.get(path_or_url, follow_redirects=True)
        g.parse(data=d.text, format=d.headers["Content-Type"].split(";")[0])

    return g


def _forward_chain_dcat(g: Graph):
    """Builds out a DCAT graph with RDFS & OWL rules.

    Only builds as necessary for scoring, i.e. not a complete RDFS or OWL inference"""
    for s in g.subjects(RDF.type, DCAT.Dataset):
        g.add((s, RDF.type, DCAT.Resource))

    for s, o in g.subject_objects(DCTERMS.isPartOf):
        g.add((o, DCTERMS.hasPart, s))

    for s, o in g.subject_objects(DCTERMS.hasPart):
        g.add((o, DCTERMS.isPartOf, s))


def _bind_extra_prefixes(g: Graph, prefixes: dict):
    for k, v in prefixes.items():
        g.bind(k, v)


def _create_observation_group(
    resource: URIRef,
    score_class: URIRef,
    beginning: Optional[Literal] = None,
    end: Optional[Literal] = None,
) -> Tuple[Node, Graph]:
    """Creates a Score (ObservationGroup) object to hold multiple Score Dimension measured values (Observations)

    :param resource: The catalogued Resource being scored
    :param score_class: The class of the Score, e.g. scores:FairScore
    :param beginning: A date from which this Score is relevant
    :param end: A date until which this score was relevant
    :return: The ID of the Score and the Score total Graph
    """
    g = Graph()

    g.add((resource, RDF.type, DCAT.Resource))
    score = BNode()
    g.add((resource, SCORES.hasScore, score))
    g.add((score, RDF.type, score_class))
    g.add((score, RDF.type, QB.ObservationGroup))
    g.add((score, SCORES.refResource, resource))

    if beginning is not None or end is not None:
        t = BNode()
        # TODO: decide on the type of Temporal Entity here
        g.add((t, RDF.type, TIME.ProperInterval))
        g.add((score, SCORES.refTime, t))

        if beginning is not None:
            b = BNode()
            g.add((b, RDF.type, TIME.Instant))
            g.add((b, TIME.inXSDDate, beginning))
            g.add((t, TIME.hasBeginning, b))
        if end is not None:
            e = BNode()
            g.add((e, RDF.type, TIME.Instant))
            g.add((e, TIME.inXSDDate, end))
            g.add((t, TIME.hasEnd, e))

    return score, g


def _create_observation(
    score_container: Node, score_property: URIRef, score_value: Union[URIRef, Literal]
) -> Graph:
    """Creates the Observation RDF container for a Score's value for a Resource

    :param resource: the catalogued resource being scored
    :param score_container: the overall Score object (e.g. FAIR for F dimension)
    :param score_property: the Scores Ontology qb:MeasureProperty that defines this score dimension, e.g. scores:fairFScore
    :param score_value: the value of this dimension of the score, e.g. 12 for "F" in FAIR
    :return: a graph of the Observation
    """
    g = Graph()
    obs = BNode()
    g.add((obs, RDF.type, QB.Observation))
    g.add((score_container, QB.observation, obs))

    g.add((obs, score_property, score_value))

    return g


def calculate_f(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    """
    F1. (meta)data are assigned a globally unique and eternally persistent identifier.
    F2. data are described with rich metadata.
    F3. (meta)data are registered or indexed in a searchable resource.
    F4. metadata specify the data identifier.
    """
    f_value = 0
    # from https://ardc.edu.au/resource/fair-data-self-assessment-tool/

    # Does the dataset have any identifiers assigned?
    # 0 No identifier
    # 1 Local identifier
    # 3 Web address (URL)
    # 8 Globally Unique, citable and persistent (e.g. DOI, PURL, ARK or Handle)

    # score will always be 3 or 8 for catalogued resources in RDF
    f_value += 3

    # if the URL is a DOI etc, +1:
    pid_indicators = [
        "doi:",
        "doi.org",
        "ark:",
        "purl.org",
        "linked.data.gov.au",
        "handle.net",
        "w3id.org",
    ]
    for pi in pid_indicators:
        if pi in str(resource):
            f_value += 5
            break

    # TODO: should we test the URL/PID to see if it resolves?

    # Is the dataset identifier included in all metadata records/files describing the data?
    # 0 No
    # 1 Yes

    # always yes for now
    f_value += 1

    # How is the data described with metadata?
    # 0 The data is not described
    # 1 Brief title and description
    # 3 Comprehensively, but in a text-based, non-standard format
    # 4 Comprehensively (see suggestion) using a recognised formal machine-readable metadata schema

    # IDN CP data will always be at least +1 here, +3 if more DCTERMS elements are present other than title & desc,
    # and +4 if all the following are present: title, description, created, modified, type qualifiedAttribution (1+)
    f_value += 1
    c = 0
    for p in metadata.predicates(resource, None):
        if p == DCTERMS.created:
            c += 1
        elif p == DCTERMS.modified:
            c += 1
        elif p == DCTERMS.type:
            c += 1
        elif p == PROV.qualifiedAttribution:
            c += 1
    if c == 1:
        f_value += 1
    elif c == 2:
        f_value += 2
    elif c > 2:
        f_value += 3

    # What type of repository or registry is the metadata record in?
    # 0 The data is not described in any repository
    # 2 Local institutional repository
    # 2 Domain-specific repository
    # 2 Generalist public repository
    # 4 Data is in one place but discoverable through several registries

    # If a catalogue is indicated, +2. If the catalogue responds to a ping for RDF, +4
    catalogue = None
    for o in metadata.objects(resource, DCTERMS.isPartOf):
        catalogue = str(o)
    if catalogue is not None:
        f_value += 2
        RDF_MEDIA_TYPES = [
            "text/turtle",
            "text/n3",
            "application/ld+json",
            "application/n-triples",
            "application/n-quads",
            "application/rdf+xml",
        ]
        x = httpx.get(
            catalogue,
            headers={"Accept": ", ".join(RDF_MEDIA_TYPES)},
            follow_redirects=True,
        )
        if x.is_success:
            f_value += 4

    return _create_observation(score_container, SCORES.fairFScore, Literal(f_value))


def calculate_a(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    a_value = 0

    # How accessible is the data?
    # 0. No access to data or metadata
    # 1. Access to metadata only
    # 2. Unspecified conditional access e.g. contact the data custodian for access
    # 3. Embargoed access after a specified date
    # 4. A de-identified / modified subset of the data is publicly accessible
    # 5. Fully accessible to persons who meet explicitly stated conditions, e.g. ethics approval for sensitive data

    # look for a declared availability classification
    declared = False
    DAR = Namespace("https://linked.data.gov.au/def/data-access-rights/")
    for o in metadata.objects(resource, DCAT.theme):
        declared = True

        if o in [DAR.protected, DAR.restricted]:
            a_value += 0
        elif o == DAR["metadata-only"]:
            a_value += 1
        elif o == DAR.conditional:
            a_value += 2
        elif o == DAR.embargoed:
            a_value += 3
        # 4
        elif o == DAR.open:
            a_value += 5

    if not declared:
        # TODO: try some other method
        pass

    # Is the data available online without requiring specialised protocols or tools once access has been approved?
    # 0. No access to data
    # 1. By individual arrangement
    # 2. File download from online location
    # 3. Non-standard web service (e.g. OpenAPI/Swagger/informal API)
    # 4. Standard web service API (e.g. OGC)

    return _create_observation(score_container, SCORES.fairAScore, Literal(a_value))


def calculate_i(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    i = Graph()
    return i


def calculate_r(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    r = Graph()
    return r


def calculate_fair(g: Graph, resource: URIRef) -> Graph:
    s = Graph(bind_namespaces="rdflib")
    _bind_extra_prefixes(s, EXTRA_PREFIXES)

    og_node, og_graph = _create_observation_group(resource, SCORES.FairScore)
    s += og_graph

    s += calculate_f(g, resource, og_node)
    s += calculate_a(g, resource, og_node)
    s += calculate_i(g, resource, og_node)
    s += calculate_r(g, resource, og_node)

    return s


def calculate_fair_per_resource(g: Graph) -> Graph:
    scores = Graph(bind_namespaces="rdflib")
    _bind_extra_prefixes(scores, EXTRA_PREFIXES)

    for r in g.subjects(RDF.type, DCAT.Resource):
        scores += calculate_fair(g, r)  # type: ignore

    return scores


def main(
    input: Union[Path, str, Graph],
    output: Optional[str] = "text/turtle",
    validate: bool = False,
):
    """The main function of this module. Accepts a path to an RDF file, a URL leading to RDF or an RDFLib graph
    as input and returns either an RDFLib Graph object, an RDF stream in the given format or writes RDF to a file with
    format specified by file ending"""

    # load input
    if isinstance(input, Graph):
        g = input
    else:
        g = _load_input_graph(input)

    # build out input
    _forward_chain_dcat(g)

    # validate
    if validate:
        validator = Path(__file__).parent.parent.absolute().parent / "validator.ttl"
        conforms, report_graph, report_text = val(g, shacl_graph=str(validator))
        if not conforms:
            raise ValueError(
                f"Input is not valid IDN CP. Validation errors are:\n{report_text}"
            )

    # calculate
    scores = calculate_fair_per_resource(g)

    # generate output
    # std out
    if output in RDF_FILE_SUFFIXES.values():
        if output == "application/ld+json":
            jsonld_context = {
                "@vocab": "https://linked.data.gov.au/def/scores/",
                "dcat": "http://www.w3.org/ns/dcat#",
                "qb": "http://purl.org/linked-data/cube#",
                "time": "http://www.w3.org/2006/time#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            }

            # adding all prefixes bound to the graph to the JSON-LD context seems not to work
            # for prefix, namespace in scores.namespace_manager.namespaces():
            #     jsonld_context[prefix] = namespace

            print(
                scores.serialize(
                    format=output, indent=4, context=jsonld_context, auto_compact=True
                )
            )
        else:
            print(
                scores.serialize(
                    format="longturtle" if output == "text/turtle" else output
                )
            )
    # write to file
    elif output.endswith(tuple(RDF_FILE_SUFFIXES.keys())):
        p = Path(output)
        output_dir = _get_valid_output_dir(p)
        output_file, output_format = _get_valid_output_file_and_type(p)
        return scores.serialize(
            destination=p,
            format="longturtle" if output_format == "text/turtle" else output_format,
        )
    # return Graph object
    else:
        return scores


if __name__ == "__main__":
    args = _create_parser().parse_args()

    main(args.input, args.output, args.validate)
