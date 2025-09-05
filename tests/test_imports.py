# tests/test_imports.py
import importlib
import pytest

# What CI must have to build & test your pipeline
REQUIRED = ["duckdb", "pandas", "altair", "nfl_data_py", "pyarrow", "dotenv"]

# Things you might use locally, but are not required in CI
OPTIONAL = ["streamlit"]

@pytest.mark.parametrize("pkg", REQUIRED)
def test_required_imports(pkg):
    importlib.import_module(pkg)

@pytest.mark.parametrize("pkg", OPTIONAL)
def test_optional_imports(pkg):
    pytest.importorskip(pkg, reason="optional for CI (not required)")
