# -*- coding: utf-8 -*-
from logging import getLogger

LOGGER = getLogger('openprocurement.contracting.api')


def includeme(config):
    from openprocurement.contracting.api.utils import contract_from_data, extract_contract
    from openprocurement.contracting.api.design import add_design
    LOGGER.info('Init contracting plugin.')
    add_design()
    config.add_request_method(extract_contract, 'contract', reify=True)
    config.add_request_method(contract_from_data)
    config.scan("openprocurement.contracting.api.views")
