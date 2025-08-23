def test_imports_successful():
    try:
        import duckdb
        import streamlit
    except ImportError:
        assert False, "One or more imports failed"
    assert True
