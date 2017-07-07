# -*- coding: utf-8 -*-
from functools import partial
from rfc6266 import build_header
from urlparse import urlparse, parse_qs
from urllib import quote
from pkg_resources import get_distribution
from base64 import b64encode
from logging import getLogger
from cornice.resource import resource
from schematics.exceptions import ModelValidationError
from openprocurement.api.utils import (error_handler, get_revision_changes,
                                       context_unpack, update_logging_context,
                                       apply_data_patch, generate_id,
                                       set_modetest_titles,
                                       get_filename, DOCUMENT_BLACKLISTED_FIELDS
                                       )
from openprocurement.api.models import Revision, get_now

from openprocurement.contracting.api.traversal import factory
from openprocurement.contracting.api.models import Contract


contractingresource = partial(resource, error_handler=error_handler,
                              factory=factory)

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def extract_contract(request):
    db = request.registry.db
    contract_id = request.matchdict['contract_id']
    doc = db.get(contract_id)
    if doc is not None and doc.get('doc_type') == 'contract':
        request.errors.add('url', 'contract_id', 'Archived')
        request.errors.status = 410
        raise error_handler(request.errors)
    elif doc is None or doc.get('doc_type') != 'Contract':
        request.errors.add('url', 'contract_id', 'Not Found')
        request.errors.status = 404
        raise error_handler(request.errors)

    return request.contract_from_data(doc)


def contract_from_data(request, data, raise_error=True, create=True):
    if create:
        return Contract(data)
    return Contract


def contract_serialize(request, contract_data, fields):
    contract = request.contract_from_data(contract_data, raise_error=False)
    return dict([(i, j) for i, j in contract.serialize("view").items() if i in fields])


def save_contract(request):
    """ Save contract object to database
    :param request:
    :return: True if Ok
    """
    contract = request.validated['contract']

    if contract.mode == u'test':
        set_modetest_titles(contract)
    patch = get_revision_changes(contract.serialize("plain"),
                                 request.validated['contract_src'])
    if patch:
        contract.revisions.append(
            Revision({'author': request.authenticated_userid,
                      'changes': patch, 'rev': contract.rev}))
        old_date_modified = contract.dateModified
        contract.dateModified = get_now()
        try:
            contract.store(request.registry.db)
        except ModelValidationError, e:  # pragma: no cover
            for i in e.message:
                request.errors.add('body', i, e.message[i])
            request.errors.status = 422
        except Exception, e:  # pragma: no cover
            request.errors.add('body', 'data', str(e))
        else:
            LOGGER.info('Saved contract {}: dateModified {} -> {}'.format(
                contract.id, old_date_modified and old_date_modified.isoformat(),
                contract.dateModified.isoformat()),
                extra=context_unpack(request, {'MESSAGE_ID': 'save_contract'},
                                     {'CONTRACT_REV': contract.rev}))
            return True


def apply_patch(request, data=None, save=True, src=None):
    data = request.validated['data'] if data is None else data
    patch = data and apply_data_patch(src or request.context.serialize(), data)
    if patch:
        request.context.import_data(patch)
        if save:
            return save_contract(request)


def set_ownership(item, request):
    item.owner_token = generate_id()
