
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


def to_uppercase(logger, s):
    if s is None:
        return
    return str(s).upper()

def extract_ands_id(logger, s, silent=False):
    "parse a BPA ID, with or without the prefix, returning with the prefix"
    if isinstance(s, float):
        s = int(s)
    if isinstance(s, int):
        s = str(s)
    if s is None:
        return None
    # if someone has appended extraction number, remove it
    s = s.strip()
    if s == "":
        return None
    # header row left in
    if s.startswith("e.g. "):
        return None
    # remove junk
    if s.startswith("don't use"):
        return None
    if s.startswith("missing"):
        return None
    if s.startswith("NA"):
        return None

    # duplicated 102.100.100: e.g. 102.100.100.102.100.100.25977
    s = s.replace("102.100.100.102.100.100.", "102.100.100/")
    # handle a sample extraction id tacked on the end with an underscore
    if "_" in s:
        s = s.rsplit("_", 1)[0]
    m = ands_id_re.match(s)
    if m:
        return BPA_PREFIX + m.groups()[0]
    m = ands_id_abbrev_re.match(s)
    if m:
        return BPA_PREFIX + m.groups()[0]
    m = ands_id_abbrev_2_re.match(s)
    if m:
        return BPA_PREFIX + m.groups()[0]
    if not silent:
        logger.warning("unable to parse BPA ID: {}".format(str(s)))
    return None


def extract_ands_id_silent(logger, s):
    return extract_ands_id(logger, s, silent=True)


def short_ands_id(logger, s):
    return extract_ands_id(logger, s).split("/")[-1]


def get_int(logger, val, default=None):
    """
    get a int from a string containing other alpha characters
    """

    if isinstance(val, int):
        return val

    try:
        return int(get_clean_number(logger, val, default))
    except TypeError:
        return default


def get_percentage(logger, val, default=None):
    return_val = default
    try:
        return_val = get_clean_number(logger, val, default)
        if (return_val > 100 or return_val < 0) and return_val != -9999.0:
            logger.warning(
                "Potential invalid number - Percentage Range error: {}".format(str(val))
            )
        return return_val
    except TypeError:
        return default


def int_or_comment(logger, val):
    # fix up '14.0' type values coming through from Excel; if not an integer,
    # it's a note or a text code, which we just pass back unaltered
    if val is None:
        return None
    try:
        return str(int(float(val)))
    except ValueError:
        val = str(val).strip()
        if not val:
            return None
        return val


def date_or_int_or_comment(logger, val):
    if isinstance(val, datetime.date):
        return get_date_isoformat(logger, val)
    return int_or_comment(logger, val)


number_find_re = re.compile(r"(-?\d+\.?\d*)")


def get_clean_number(logger, val, default=None):
    if isinstance(val, float):
        return val

    if val is None:
        return default

    try:
        return float(val)
    except TypeError:
        logger.error("Invalid number - Type error: {} ".format(str(val)))
        return default
    except ValueError:
        if val not in [
            "unknown",
            "N/A",
            "NA",
            "",
            " ",
        ]:
            logger.warning(
                "Potential invalid number - Value error: {}".format(str(val))
            )
        pass

    matches = number_find_re.findall(str(val))
    if len(matches) == 0:
        return default
    return float(matches[0])


def get_date_isoformat(logger, s, silent=False):
    "try to parse the date, if we can, return the date as an ISO format string"
    dt = _get_date(logger, s, silent)
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d")


def get_date_isoformat_as_datetime(logger, s, silent=False):
    "try to parse the date, if we can, return the date as an ISO format string"
    dt = _get_date_time(logger, s, silent)
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%S")
    # return dt.strftime("%Y-%m-%dT%H:%M:%SZ")   -- remove the Z for now as CKAN has an issue with it.. ut it back when this is fixed


def get_time(logger, s):
    return str(s)


def _get_date_time(logger, dt, silent=False):
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


def get_clean_doi(logger, val):
    if not val:
        return val

    try:
        val.index("doi")
    except ValueError:
        logger.error("DOI not found in: {}".format(val))
        return None

    # change any weblinks back to doi:
    regex = r"^https?:\/\/(dx\.)?doi.org\/"
    subst = "doi:"

    val = re.sub(regex, subst, val, 0)

    # check if DOI looks valid
    # regex is not exhaustive
    # See: https://www.crossref.org/blog/dois-and-matching-regular-expressions/

    if not re.match(r"^doi:10.\d{4,9}\/[-._;()\/:A-Z0-9]+$", val, re.IGNORECASE):
        logger.error("DOI does not look valid: {}".format(val))
        return None

    return val
