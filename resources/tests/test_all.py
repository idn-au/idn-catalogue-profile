from pathlib import Path

from rdflib import Graph
from kurra.shacl import validate


def test_all_profile_turtle_files_parse():
    resources = Path(__file__).parent.parent
    for f in sorted(resources.rglob("*.ttl")):
        if ".venv" not in f.parts:
            Graph().parse(f, format="turtle")


def test_all():
    for f in sorted(Path(__file__).parent.glob("*.ttl")):
        v = validate(f, Path(__file__).parent.parent / "validator.ttl")

        if "invalid" in str(f):
            assert not v[0], f"File {f} should have failed validation but did not"
        else:
            assert v[0], f"File {f} failed validation but should not"
