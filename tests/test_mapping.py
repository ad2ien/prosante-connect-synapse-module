from psc_mapping_provider import jinja_finalize

def test_things():
    assert jinja_finalize("this") == "this"

def test_none():
    assert jinja_finalize(None) == ""