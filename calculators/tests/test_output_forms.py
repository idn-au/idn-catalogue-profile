import os
import subprocess
import sys
from pathlib import Path

from rdflib import Graph

CALC_MODULE_PATH = Path(__file__).parent.parent / "calculators"
sys.path.append(str(CALC_MODULE_PATH))
FAIR_CALCULATOR = CALC_MODULE_PATH / "calc_fair.py"
TEST_DATA_DIR = Path(__file__).parent / "data"


def test_cli_output_to_stdout():
    proc = subprocess.Popen(
        ["python", FAIR_CALCULATOR, TEST_DATA_DIR / "test_input_invalid_01.ttl"],
        stdout=subprocess.PIPE,
    )
    assert Graph().parse(data=proc.stdout.read().decode())


def test_cli_output_to_stdout_json_ld():
    proc = subprocess.Popen(
        [
            "python",
            FAIR_CALCULATOR,
            TEST_DATA_DIR / "test_input_invalid_01.ttl",
            "-o",
            "application/ld+json",
        ],
        stdout=subprocess.PIPE,
    )
    assert Graph().parse(data=proc.stdout.read().decode(), format="application/ld+json")


def test_cli_output_to_file():
    output_file = TEST_DATA_DIR / "test_input_invalid_01_out.ttl"
    subprocess.Popen(
        [
            "python",
            FAIR_CALCULATOR,
            TEST_DATA_DIR / "test_input_invalid_01.ttl",
            "-o",
            output_file,
        ]
    ).communicate()
    assert Graph().parse(output_file)
    os.unlink(output_file)


def test_cli_output_graph():
    from calculators import fair

    g = fair.main(TEST_DATA_DIR / "test_input_invalid_01.ttl", "graph")
    assert isinstance(g, Graph)
