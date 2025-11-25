

from bpa_ingest_validations  import (
    extract_ands_id,
    get_int,
    int_or_comment,
    get_date_isoformat,
    date_or_int_or_comment,
    get_clean_number
)

def test_extract_and_id():
    assert True

def test_get_int():
    assert True

def test_get_clean_number():
    floats = (12131.5345, 22.444, 33.0)
    strings = (
        ("3.1415926535", (3.1415926535, None)),
        ("-2.71828", (-2.71828, None)),
        ("37.1 degrees", (37.1, 'Potential invalid number - Value error: 37.1 degrees')),
    )
    for f in floats:
        assert (f, None) == get_clean_number( f)
    for s, f in strings:
        assert get_clean_number( s) == (f)
    assert get_clean_number("") == (None, None)
    assert get_clean_number(123) == (123, None)
    assert get_clean_number( None) == (None, None)
    assert get_clean_number( 'Boo') == (None, 'Potential invalid number - Value error: Boo')

"""
the get_clean_doi method is not used at this time, and has not been converted.
def test_get_clean_doi():
    strings = (
        ("https://dx.doi.org/10.100/1234", None),
        ("http://dx.doi.org/10.100/1234", None),
        ("https://doi.org/10.100/1234", None),
        ("http://doi.org/10.100/1234", None),
        ("doi:10.1038/nphys1170", "doi:10.1038/nphys1170"),
        ("doi:10.1002/0470841559.ch1", "doi:10.1002/0470841559.ch1"),
        ("doi:10.1594/PANGAEA.726855", "doi:10.1594/PANGAEA.726855"),
        ("doi:10.1594/GFZ.GEOFON.gfz2009kciu", "doi:10.1594/GFZ.GEOFON.gfz2009kciu"),
        ("doi:10.1594/PANGAEA.667386", "doi:10.1594/PANGAEA.667386"),
        ("https://doi.org/10.25953/4rpw-z", "doi:10.25953/4rpw-z"),
        ("http://dx.doi.org/10.25953/4rpw-z", "doi:10.25953/4rpw-z"),
    )
    for s, f in strings:
        assert get_clean_doi( s) == (f, None)
    assert get_clean_doi("") == ("", None)
    assert get_clean_doi(None) == (None, None)
"""