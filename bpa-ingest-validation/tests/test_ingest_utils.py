from io import BytesIO

import bpa_ingest_validation.ingest_utils  #import get_clean_number, get_clean_doi
from ..util import make_logger


logger = make_logger(__name__)

TEST_CHUNK_SIZE = 8 * (1 << 20)


def test_get_clean_number():
    floats = (12131.5345, 22.444, 33.0)
    strings = (
        ("3.1415926535", 3.1415926535),
        ("-2.71828", -2.71828),
        ("37.1 degrees", 37.1),
    )
    for f in floats:
        assert f == ingest_utils.get_clean_number(logger, f)
    for s, f in strings:
        assert get_clean_number(logger, s) == f
    assert get_clean_number(logger, "") is None
    assert get_clean_number(logger, 123) == 123
    assert get_clean_number(logger, None) is None



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
        assert get_clean_doi(logger, s) == f
    assert get_clean_doi(logger, "") == ""
    assert get_clean_doi(logger, None) is None
