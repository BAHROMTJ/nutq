"""Run the examples in docstrings, so the documentation stays correct."""

import doctest
import importlib

MODULES = [
    "nutq", "nutq.api", "nutq.scripts",
    "nutq.lang.tg.numbers", "nutq.lang.tg.translit", "nutq.lang.tg.arabic",
    "nutq.lang.fa.numbers", "nutq.lang.fa.clean",
    "nutq.lang.uz.numbers", "nutq.lang.uz.translit",
]


def load_tests(loader, tests, ignore):
    for name in MODULES:
        tests.addTests(doctest.DocTestSuite(importlib.import_module(name)))
    return tests
