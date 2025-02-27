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
            config.readfp(fp)
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


def get_constant(config, constant, section=DEFAULTSECT, parse_func=parse_date):
    return parse_func(os.environ.get("{}_{}".format(section, constant)) or config.get(section, constant))
