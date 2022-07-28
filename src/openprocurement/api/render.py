from jinja2 import FileSystemLoader, Environment


loader = FileSystemLoader([
    '/app/src/openprocurement/api/templates',
    '/app/src/openprocurement/tender/core/templates',
])
env = Environment(loader=loader)


# filters
HUMAN_FILTERS = {}


def to_human(value, field):
    return HUMAN_FILTERS[field](value)


env.filters["human"] = to_human
