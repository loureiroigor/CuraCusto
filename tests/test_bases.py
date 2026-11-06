from curacusto.bases.cmed import parse_pmc


def test_parse_pmc():
    assert parse_pmc(12.5) == 12.5
    assert parse_pmc("1.234,56") == 1234.56
    assert parse_pmc("15,21") == 15.21
    assert parse_pmc("    -     ") is None
    assert parse_pmc(None) is None
