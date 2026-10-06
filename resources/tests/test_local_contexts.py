from pathlib import Path

from kurra.shacl import validate
from rdflib.namespace import RDF, SH


HERE = Path(__file__).parent
SHAPES = HERE.parent / "validators" / "local-contexts.ttl"


def _results(name: str):
    conforms, report, _ = validate(HERE / "local-contexts" / name, SHAPES)
    results = list(report.subjects(RDF.type, SH.ValidationResult))
    severities = [report.value(result, SH.resultSeverity) for result in results]
    return conforms, results, severities


def test_preferred_direct_pattern_has_no_results():
    conforms, results, _ = _results("direct.ttl")
    assert conforms
    assert results == []


def test_qualified_pattern_is_informational():
    conforms, results, severities = _results("qualified.ttl")
    assert conforms
    assert len(results) == 1
    assert severities == [SH.Info]


def test_questionable_patterns_are_warnings_not_violations():
    conforms, results, severities = _results("warnings.ttl")
    assert conforms
    assert len(results) == 10
    assert severities.count(SH.Warning) == 9
    assert severities.count(SH.Info) == 1
    assert SH.Violation not in severities
