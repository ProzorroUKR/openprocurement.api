from pyramid.events import ContextFound
from openprocurement.planning.api.design import add_design
from openprocurement.planning.api.utils import plan_from_data, extract_plan, set_logging_context
from logging import getLogger
from pkg_resources import get_distribution

PKG = get_distribution(__package__)

LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('init planing plugin')
    add_design()
    config.add_subscriber(set_logging_context, ContextFound)
    config.add_request_method(extract_plan, 'plan', reify=True)
    config.add_request_method(plan_from_data)
    config.scan("openprocurement.planning.api.views")
