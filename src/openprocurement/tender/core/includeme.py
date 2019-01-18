from pkg_resources import iter_entry_points
from pyramid.interfaces import IRequest
from openprocurement.tender.core.utils import (
    extract_tender, isTender, register_tender_procurementMethodType,
    tender_from_data, SubscribersPicker
)
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.core.models import ITender
from openprocurement.tender.core.adapters import TenderConfigurator


def includeme(config):
    from openprocurement.tender.core.design import add_design
    add_design()
    config.add_request_method(extract_tender, 'tender', reify=True)

    # tender procurementMethodType plugins support
    config.registry.tender_procurementMethodTypes = {}
    config.add_route_predicate('procurementMethodType', isTender)
    config.add_subscriber_predicate('procurementMethodType', SubscribersPicker)
    config.add_request_method(tender_from_data)
    config.add_directive('add_tender_procurementMethodType',
                         register_tender_procurementMethodType)
    config.scan("openprocurement.tender.core.views")
    config.scan("openprocurement.tender.core.subscribers")
    config.registry.registerAdapter(TenderConfigurator, (ITender, IRequest),
                                    IContentConfigurator)

    # search for plugins
    settings = config.get_settings()
    plugins = settings.get('plugins') and settings['plugins'].split(',')
    for entry_point in iter_entry_points('openprocurement.tender.core.plugins'):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)
