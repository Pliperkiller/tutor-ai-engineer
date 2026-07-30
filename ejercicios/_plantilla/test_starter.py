"""The tutor runs: pytest test_starter.py -q"""
from starter import target_function


def test_base_case():
    assert target_function("<input>") == "<expected output>"
