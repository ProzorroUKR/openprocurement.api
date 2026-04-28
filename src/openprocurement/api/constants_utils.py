import os
from configparser import DEFAULTSECT, ConfigParser

import standards
from ciso8601 import parse_datetime


def parse_criteria_rules_date(value, constants):
    try:
        return parse_datetime(value)
    except ValueError:
        return getattr(constants, value)


def load_criteria_rules(procurement_method_type, constants):
    periods_data = standards.load(f"criteria/rules/{procurement_method_type}.json")

    periods = []
    for period_data in periods_data:
        data = {"criteria": period_data["criteria"], "period": {}}

        period = period_data.get("period") or {}

        # Get start_date from constants if specified
        if start_date := period.get("start_date"):
            data["period"]["start_date"] = parse_criteria_rules_date(start_date, constants)

        # Get end_date from constants if specified
        if end_date := period.get("end_date"):
            data["period"]["end_date"] = parse_criteria_rules_date(end_date, constants)

        periods.append(data)

    # TODO: Check for overlapping periods

    return periods


def get_default_constants_file_path():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "constants.ini")


def load_constants(file_path):
    config = ConfigParser()
    try:
        with open(file_path) as fp:
            config.read_file(fp)
    except Exception as e:
        raise type(e)(
            "Can't read file '{}': use current path or override using CONSTANTS_FILE_PATH env variable".format(
                file_path
            )
        )
    return config


def parse_date(value):
    date = parse_datetime(value)
    if not date.tzinfo:
        # We're using this only on project initialization,
        # so it's fine to import outside toplevel
        # pylint: disable-next=import-outside-toplevel
        from openprocurement.api.constants import TZ

        date = TZ.localize(date)
    return date


def parse_bool(value):
    if str(value).lower() in ("yes", "y", "true", "t", "1"):
        return True
    if str(value).lower() in (
        "no",
        "n",
        "false",
        "f",
        "0",
        "0.0",
        "",
        "none",
        "[]",
        "{}",
    ):
        return False
    raise ValueError("Invalid value for boolean conversion: " + str(value))


def parse_str_list(value):
    return [x.strip() for x in value.split(",") if x.strip()]


def parse_key_date_pairs(value):
    """Pairs: key, ISO-8601 datetime, key, datetime, ...

    Example: key1,2026-02-23T11:08:17+02:00,key2,2026-02-24T11:08:17+02:00
    Returns: {key1: datetime(2026, 2, 23, 11, 8, 17), key2: datetime(2026, 2, 24, 11, 8, 17)}
    """
    if not value or not str(value).strip():
        return {}
    parts = [x.strip() for x in str(value).split(",")]
    parts = [p for p in parts if p]
    result = {}
    i = 0
    while i + 1 < len(parts):
        edrpou, date_str = parts[i], parts[i + 1]
        result[edrpou] = parse_date(date_str)
        i += 2
    return result


def get_constant(config, constant, section=DEFAULTSECT, parse_func=parse_date):
    env_value = os.environ.get("{}_{}".format(section, constant))
    if env_value is None and section == DEFAULTSECT:
        env_value = os.environ.get(constant)
    return parse_func(env_value or config.get(section, constant))


# classifiers
def split_classifier_by_year(data, scheme_name):
    result = {}
    for item in data:
        for year in item.get("years", []):
            result.setdefault(f"{scheme_name}-{year}", {})[item["code"]] = item
    return result
