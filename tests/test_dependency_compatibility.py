"""Project interpreter claims must not exceed its pinned dependencies."""
import importlib.metadata as metadata
from pathlib import Path
import tomllib
from packaging.specifiers import SpecifierSet

def test_declared_python_range_respects_pinned_numpy_and_scipy():
    declared=SpecifierSet(tomllib.loads((Path(__file__).parents[1]/'pyproject.toml').read_text())['project']['requires-python'])
    requirements={p:SpecifierSet(metadata.metadata(p)['Requires-Python']) for p in ['numpy','scipy']}
    for minor in range(10,16):
        candidate=f'3.{minor}'
        if candidate in declared:
            assert all(candidate in requirement for requirement in requirements.values()),(candidate,requirements)
