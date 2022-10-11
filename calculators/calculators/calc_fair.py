"""
~$ python calc_fair.py [-o]

"""
import os
import argparse
from pathlib import Path
import httpx
from rdflib import Graph, URIRef
from typing import Optional, Union
from pyshacl import validate as val
from rdflib.namespace import DCAT, DCTERMS, RDF


RDF_FILE_SUFFIXES = {
    ".ttl": "text/turtle",
    ".rdf": "application/rdf+xml",
    ".json-ld": "application/ld+json",
    ".nt": "text/nt",
}


def create_parser():
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


def output_is_format(s: str):
    if s in RDF_FILE_SUFFIXES.keys() or s == "graph":
        return True
    else:
        return False


def get_valid_output_dir(path: Path):
    """Checks that a specified output directory is an existing directory and returns the directory if valid"""

    if not os.path.isdir(path.parent):
        raise argparse.ArgumentTypeError(
            f"The output path you specified, {path}, does not indicate a valid directory"
        )

    return path.parent


def get_valid_output_file_and_type(path: Path):
    """Checks that a specified output file has a known file type extension and returns it and the corresponding
    RDF Media Type if it is"""

    known_file_types = [".ttl", ".rdf", ".json-ld", ".nt"]
    if path.suffix not in known_file_types:
        raise argparse.ArgumentTypeError(
            f"The output path you specified, {path}, does not specify a known file type. "
            f"It must be one of {', '.join(known_file_types)}"
        )

    return path.name, RDF_FILE_SUFFIXES[path.suffix]


def input_is_a_file(s: str):
    if Path(s).is_file():
        return True
    else:
        return False


def load_input_graph(path_or_url: Union[Path, str]) -> Graph:
    """Parses a file at the path location or download the data from a given URL and returns an RDFLib Graph"""

    g = Graph()
    if input_is_a_file(path_or_url):
        g.parse(path_or_url)
    else:
        d = httpx.get(path_or_url, follow_redirects=True)
        g.parse(data=d.text, format=d.headers["Content-Type"].split(";")[0])

    return g


def forward_chain_dcat(g: Graph):
    for s in g.subjects(RDF.type, DCAT.Dataset):
        g.add((s, RDF.type, DCAT.Resource))

    for s, o in g.subject_objects(DCTERMS.isPartOf):
        g.add((o, DCTERMS.hasPart, s))

    for s, o in g.subject_objects(DCTERMS.hasPart):
        g.add((o, DCTERMS.isPartOf, s))


def calculate_f(g: Graph) -> Graph:
    # Does the dataset have any identifiers assigned?
    ## No identifier
    ## Local identifier
    ## Web address (URL)
    ## Globally Unique, citable and persistent (e.g. DOI, PURL, ARK or Handle)



    # Is the dataset identifier included in all metadata records/files describing the data?

    # How is the data described with metadata?

    # What type of repository or registry is the metadata record in?
    pass


def calculate_a(g: Graph) -> Graph:
    pass


def calculate_i(g: Graph) -> Graph:
    pass


def calculate_r(g: Graph) -> Graph:
    pass


def calculate_fair(g: Graph, resource_iri: URIRef) -> Graph:
    score = Graph()
    score.add((
        resource_iri,
    ))


def calculate_fair_per_resource(g: Graph) -> Graph:
    scores = Graph()
    scores.bind("dcat", DCAT)
    scores.bind("dcterms", DCTERMS)

    for r in g.subjects(RDF.type, DCAT.Resource):
        scores.add((r, RDF.type, DCAT.Resource))

    return scores


def main(input: Union[Path, str, Graph], output: Optional[str] = "text/turtle", validate: bool = False):
    """The main function of this module. Accepts a path to an RDF file, a URL leading to RDF or an RDFLib graph
    as input and returns either an RDFLib Graph object, an RDF stream in the given format or writes RDF to a file with
    format specified by file ending"""

    # load input
    if isinstance(input, Graph):
        g = input
    else:
        g = load_input_graph(input)

    # build out input
    forward_chain_dcat(g)

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
        print(scores.serialize(format="longturtle" if output == "text/turtle" else output))
    # write to file
    elif output.endswith(tuple(RDF_FILE_SUFFIXES.keys())):
        p = Path(output)
        output_dir = get_valid_output_dir(p)
        output_file, output_format = get_valid_output_file_and_type(p)
        return scores.serialize(destination=p, format="longturtle" if output_format == "text/turtle" else output_format)
    # return Graph object
    else:
        return scores


if __name__ == "__main__":
    args = create_parser().parse_args()

    main(args.input, args.output, args.validate)

