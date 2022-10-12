import sys
from pathlib import Path

from rdflib import Graph

calc_module_path = Path(Path(__file__).parent.parent / "calculators").absolute()
sys.path.insert(0, str(calc_module_path))
import pytest
from calculators import fair, SCORES


CALC_MODULE_PATH = Path(__file__).parent.parent / "calculators"
sys.path.append(str(CALC_MODULE_PATH))
FAIR_CALCULATOR = CALC_MODULE_PATH / "calc_fair.py"
TEST_DATA_DIR = Path(__file__).parent / "data"


def test_invalid_input():
    with pytest.raises(ValueError):
        g = fair.main(TEST_DATA_DIR / "test_input_invalid_01.ttl", "graph", True)


def test_valid_input():
    g = fair.main(TEST_DATA_DIR / "AGIL.ttl", "graph", True)
    assert isinstance(g, Graph)


def test_agil_f_score():
    g = fair.main(TEST_DATA_DIR / "AGIL.ttl", "graph", True)
    f = None
    for o in g.objects(None, SCORES.fairFScore):
        f = int(o)

    assert f == 14
