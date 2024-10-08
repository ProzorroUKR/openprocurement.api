from jinja2 import Environment, FileSystemLoader

from openprocurement.api.constants import BASE_DIR

loader = FileSystemLoader(
    [
        BASE_DIR + "/src/openprocurement/api/templates",
        BASE_DIR + "/src/openprocurement/tender/core/templates",
    ]
)
env = Environment(loader=loader)


# filters
HUMAN_FILTERS = {}


def to_human(value, field):
    return HUMAN_FILTERS[field](value)


env.filters["human"] = to_human
