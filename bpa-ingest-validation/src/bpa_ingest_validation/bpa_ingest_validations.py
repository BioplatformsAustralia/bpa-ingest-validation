
import datetime
import math
import re

from .bpa_constants import BPA_PREFIX

ands_id_re = re.compile(r"^102\.100\.100[/\.](\d+)$")
ands_id_abbrev_re = re.compile(r"^(\d+)$")
# this format of BPA ID has been used in older projects (e.g. BASE)
ands_id_abbrev_2_re = re.compile(r"^102\.100\.\.100[/\.](\d+)$")
# <sample_id>_<extraction>
#sample_extraction_id_re = re.compile(r"^\d{4,6}_\d")

# generic validation, returning errors or None as second parameter
# These coerce functions are used by BaseSampleMetadata - the only one converted so far
"""
date_or_int_or_comment,
extract_ands_id,
int_or_comment
get_int
get_date_isoformat
"""

#Second return value in ALL cases is the error that was reported.
# Makes logging the responsibility of the caller.
# If no error, return None.

def extract_ands_id(s, silent=False):
    "parse a BPA ID, with or without the prefix, returning with the prefix"
    if isinstance(s, float):
        s = int(s)
    if isinstance(s, int):
        s = str(s)
    if s is None:
        return None, None
    # if someone has appended extraction number, remove it
    s = s.strip()
    if s == "":
        return None, None
    # header row left in
    if s.startswith("e.g. "):
        return None, None
    # remove junk
    if s.startswith("don't use"):
        return None, None
    if s.startswith("missing"):
        return None, None
    if s.startswith("NA"):
        return None, None

    # duplicated 102.100.100: e.g. 102.100.100.102.100.100.25977
    s = s.replace("102.100.100.102.100.100.", "102.100.100/")
    # handle a sample extraction id tacked on the end with an underscore
    if "_" in s:
        s = s.rsplit("_", 1)[0]
    m = ands_id_re.match(s)
    if m:
        return BPA_PREFIX + m.groups()[0], None
    m = ands_id_abbrev_re.match(s)
    if m:
        return BPA_PREFIX + m.groups()[0], None
    m = ands_id_abbrev_2_re.match(s)
    if m:
        return BPA_PREFIX + m.groups()[0], None
    if not silent:
        return None, "unable to parse BPA ID: {}".format(str(s))
    return None, None


def extract_ands_id_silent(s):
    return extract_ands_id(s, silent=True)


def short_ands_id(s):
    val, error = extract_ands_id(s)
    return val.split("/")[-1]


def get_int(val, default=None):
    """
    get a int from a string containing other alpha characters
    """

    if isinstance(val, int):
        return val, None

    try:
        possible_int_value, error = get_clean_number(val, default)
        return int(possible_int_value), error
    except TypeError:
        return default, None


def get_percentage( val, default=None):
    return_val = default
    try:
        return_val = get_clean_number( val, default)
        error = None
        if (return_val > 100 or return_val < 0) and return_val != -9999.0:
            error = "Potential invalid number - Percentage Range error: {}".format(str(val))
        return return_val, error
    except TypeError:
        return default, None


def int_or_comment(val):
    # fix up '14.0' type values coming through from Excel; if not an integer,
    # it's a note or a text code, which we just pass back unaltered
    if val is None:
        return None, None
    try:
        return str(int(float(val))), None
    except ValueError:
        val = str(val).strip()
        if not val:
            return None, None
        return val, None


def date_or_int_or_comment( val):
    if isinstance(val, datetime.date):
        return get_date_isoformat(val), None
    return int_or_comment(val)


number_find_re = re.compile(r"(-?\d+\.?\d*)")


def get_clean_number( val, default=None):
    error = None
    if isinstance(val, float):
        return val, error

    if val is None:
        return default, error

    try:
        return float(val), error
    except TypeError:
        error = "Invalid number - Type error: {} ".format(str(val))
        return default, error
    except ValueError:
        if val not in [
            "unknown",
            "N/A",
            "NA",
            "",
            " ",
        ]:
            error = "Potential invalid number - Value error: {}".format(str(val))
        pass

    matches = number_find_re.findall(str(val))
    if len(matches) == 0:
        return default, error
    return float(matches[0]), error


def get_date_isoformat(s, silent=False):
    "try to parse the date, if we can, return the date as an ISO format string"
    dt = _get_date(s, silent)
    if dt is None:
        return None, None
    return dt.strftime("%Y-%m-%d")


def get_date_isoformat_as_datetime(s, silent=False):
    "try to parse the date, if we can, return the date as an ISO format string"
    dt = _get_date_time( s, silent)
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%S")
    # return dt.strftime("%Y-%m-%dT%H:%M:%SZ")   -- remove the Z for now as CKAN has an issue with it.. ut it back when this is fixed


def get_time(s):
    return str(s)


def _get_date_time(dt, silent=False):
    if dt is None:
        return None

    if (
        dt == "unknown"
        or dt == "Unknown"
        or dt == "UnkNown"
        or dt == "unkNown"
        or dt == "event date not recorded"
        or dt == "Not yet assigned"
        or dt == "Not applicable"
        or dt == "not applicable"
        or dt == "no information"
        or dt == "Not submitted"
        or dt == "not determined"
        or dt == "To be filled in"
        or dt == "(null)"
        or dt == "NA"
        or dt == "n/a"
        or dt == "TBA"
        or dt == "No record"
    ):
        return None

    if isinstance(dt, datetime.date):
        return dt

    if not isinstance(dt, str):
        return None

    if dt.strip() == "":
        return None

    try:
        return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        pass
    try:
        return datetime.datetime.strptime(dt, "%y-%m-%dT%H:%M:%SZ")
    except ValueError:
        pass
    try:
        return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%MZ")
    except ValueError:
        pass
    try:
        retval = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        if not silent:
            logger.warning(
                "DateTime {} does not have a timezone - will force to Z time.".format(
                    retval
                )
            )
        return retval
    except ValueError:
        pass
    try:
        retval = datetime.datetime.strptime(dt, "%y-%m-%d %H:%M:%S")
        if not silent:
            logger.warning(
                "DateTime {} does not have a timezone - will force to Z time.".format(
                    retval
                )
            )
        return retval
    except ValueError:
        pass
    try:
        retval = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M")
        if not silent:
            logger.warning(
                "DateTime {} does not have a timezone - will force to Z time.".format(
                    retval
                )
            )
        return retval
    except ValueError:
        pass
    try:
        retval = datetime.datetime.strptime(dt, "%y-%m-%d %H:%M")
        if not silent:
            logger.warning(
                "DateTime {} does not have a timezone - will force to Z time.".format(
                    retval
                )
            )
        return retval

    except ValueError:
        pass

    return _get_date(logger, dt, silent)


def _get_date(logger, dt, silent=False):
    """
    Convert `dt` into a datetime.date, returning `dt` if it is already an
    instance of datetime.date.

    The following date formats are supported:
       YYYY-mm-dd
       dd/mm/YYYY
       dd-mm-YYYY
       dd.mm.YYYY
       dd.mm.YY

       YYYY-mm (convert to first date of month)
       mm/YYYY (convert to first date of month)

    If conversion fails, returns None.
    """

    if dt is None:
        return None

    if (
        dt == "unknown"
        or dt == "Unknown"
        or dt == "UnkNown"
        or dt == "unkNown"
        or dt == "event date not recorded"
        or dt == "Not yet assigned"
        or dt == "Not applicable"
        or dt == "not applicable"
        or dt == "no information"
        or dt == "Not submitted"
        or dt == "not determined"
        or dt == "To be filled in"
        or dt == "(null)"
        or dt == "NA"
        or dt == "n/a"
        or dt == "TBA"
        or dt == "No record"
    ):
        return None

    if isinstance(dt, datetime.date):
        return dt

    if not isinstance(dt, str):
        return None

    if dt.strip() == "":
        return None

    try:
        return datetime.datetime.strptime(dt, "%Y-%m-%d").date()
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(dt, "%Y-%m").date()
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(dt, "%Y-%b-%d").date()
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(dt, "%d/%m/%Y").date()
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(dt, "%d-%m-%Y").date()
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(dt, "%d.%m.%Y").date()
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(dt, "%d.%m.%y").date()
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(dt, "%m/%Y").date()
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(dt, "%d/%m/%y").date()
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").date()
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(dt, "%y-%m-%d %H:%M:%S").date()
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ").date()
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%MZ").date()
    except ValueError:
        pass

    if not silent:
        logger.error("Date `{}` is not in a supported format".format(dt))
    return None


def get_year(logger, s):
    if re.search(r"\d{4}\.\d*", s):
        # remove decimal and convert back to string
        return str(math.trunc(float(s)))
    else:
        return get_date_isoformat(logger, s)


def date_or_str(logger, v):
    d = get_date_isoformat(logger, v, silent=True)
    if d is not None:
        return d
    as_string = str(v)
    # only round to integer if decimal places are 0
    as_string_groups = re.search(r"(\d{4})(\.0|)", as_string)
    return as_string_groups.group(1) if as_string_groups else as_string


def from_comma_or_space_separated_to_list(logger, raw):
    separators = [",", " ", "\n"]
    if re.search(" ", raw) and re.search(",", raw) and re.search("\n", raw):
        raise Exception(
            "There are spaces and commas and newlines in this string. Only commas OR spaces OR newlines can be used as data separators."
        )
    for next_separator in separators:
        result = raw.split(next_separator)
        if len(result) > 1:
            return result
    raise Exception("Raw input must be separated by one of {}".format(separators))


def get_clean_doi(val):
    if not val:
        return val, None

    try:
        val.index("doi")
    except ValueError:
        return None, "DOI not found in: {}".format(val)

    # change any weblinks back to doi:
    regex = r"^https?:\/\/(dx\.)?doi.org\/"
    subst = "doi:"

    val = re.sub(regex, subst, val, 0)

    # check if DOI looks valid
    # regex is not exhaustive
    # See: https://www.crossref.org/blog/dois-and-matching-regular-expressions/

    if not re.match(r"^doi:10.\d{4,9}\/[-._;()\/:A-Z0-9]+$", val, re.IGNORECASE):
        return None, "DOI does not look valid: {}".format(val)

    return val, None
