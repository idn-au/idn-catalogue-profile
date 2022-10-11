import os
from pathlib import Path
import subprocess
from rdflib import Graph
import sys
import pytest

CALC_MODULE_PATH = Path(__file__).parent.parent / "calculators"
sys.path.append(str(CALC_MODULE_PATH))
FAIR_CALCULATOR = CALC_MODULE_PATH / "calc_fair.py"
TEST_DATA_DIR = Path(__file__).parent / "data"


def test_invalid_input():
    from calculators import fair
    with pytest.raises(ValueError):
        g = fair.main(TEST_DATA_DIR / "test_input_invalid_01.ttl", "graph", True)


def test_valid_input():
    from calculators import fair
    g = fair.main(TEST_DATA_DIR / "AGIL.ttl", "graph", True)
    assert isinstance(g, Graph)
