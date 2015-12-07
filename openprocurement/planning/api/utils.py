# -*- coding: utf-8 -*-
from functools import partial
from json import dumps
from logging import getLogger
from time import sleep

from pkg_resources import get_distribution

from cornice.resource import resource
from cornice.util import json_error
from couchdb.http import ResourceConflict
from openprocurement.api.models import Revision, get_now
from openprocurement.api.utils import update_logging_context, context_unpack, get_revision_changes, \
    apply_data_patch
from openprocurement.planning.api.models import Plan
from openprocurement.planning.api.traversal import factory
from schematics.exceptions import ModelValidationError

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def generate_plan_id(ctime, db, server_id=''):
    key = ctime.date().isoformat()
    plan_id_doc = 'planID_' + server_id if server_id else 'planID'
    while True:
        try:
            plan_id = db.get(plan_id_doc, {'_id': plan_id_doc})
            index = plan_id.get(key, 1)
            plan_id[key] = index + 1
            db.save(plan_id)
        except ResourceConflict:  # pragma: no cover
            pass
        except Exception:  # pragma: no cover
            sleep(1)
        else:
            break
    return 'UA-P-{:04}-{:02}-{:02}-{:06}{}'.format(ctime.year, ctime.month, ctime.day, index,
                                                   server_id and '-' + server_id)


def plan_serialize(request, plan_data, fields):
    plan = request.plan_from_data(plan_data, raise_error=False)
    return dict([(i, j) for i, j in plan.serialize("view").items() if i in fields])


def save_plan(request):
    plan = request.validated['plan']
    patch = get_revision_changes(plan.serialize("plain"), request.validated['plan_src'])
    if patch:
        plan.revisions.append(Revision({'author': request.authenticated_userid, 'changes': patch, 'rev': plan.rev}))
        old_dateModified = plan.dateModified
        plan.dateModified = get_now()
        try:
            plan.store(request.registry.db)
        except ModelValidationError, e:
            for i in e.message:
                request.errors.add('body', i, e.message[i])
            request.errors.status = 422
        except Exception, e:  # pragma: no cover
            request.errors.add('body', 'data', str(e))
        else:
            LOGGER.info('Saved plan {}: dateModified {} -> {}'.format(plan.id,
                                                                      old_dateModified and old_dateModified.isoformat(),
                                                                      plan.dateModified.isoformat()),
                        extra=context_unpack(request, {'MESSAGE_ID': 'save_plan'}, {'PLAN_REV': plan.rev}))
            return True


def apply_patch(request, data=None, save=True, src=None):
    data = request.validated['data'] if data is None else data
    patch = data and apply_data_patch(src or request.context.serialize(), data)
    if patch:
        request.context.import_data(patch)
        if save:
            return save_plan(request)


def error_handler(errors, request_params=True):
    params = {
        'ERROR_STATUS': errors.status
    }
    if request_params:
        params['ROLE'] = str(errors.request.authenticated_role)
        if errors.request.params:
            params['PARAMS'] = str(dict(errors.request.params))
    if errors.request.matchdict:
        for x, j in errors.request.matchdict.items():
            params[x.upper()] = j
    if 'plan' in errors.request.validated:
        params['PLAN_REV'] = errors.request.validated['plan'].rev
        params['PLANID'] = errors.request.validated['plan'].planID
    LOGGER.info('Error on processing request "{}"'.format(dumps(errors, indent=4)),
                extra=context_unpack(errors.request, {'MESSAGE_ID': 'error_handler'}, params))
    return json_error(errors)


opresource = partial(resource, error_handler=error_handler, factory=factory)


def set_logging_context(event):
    request = event.request
    params = {}
    if 'plan' in request.validated:
        params['PLAN_REV'] = request.validated['plan'].rev
        params['PLANID'] = request.validated['plan'].planID
    update_logging_context(request, params)


def extract_plan_adapter(request, plan_id):
    db = request.registry.db
    doc = db.get(plan_id)
    if doc is None:
        request.errors.add('url', 'plan_id', 'Not Found')
        request.errors.status = 404
        raise error_handler(request.errors)

    return request.plan_from_data(doc)


def extract_plan(request):
    plan_id = request.matchdict['plan_id']
    return extract_plan_adapter(request, plan_id)


def plan_from_data(request, data, raise_error=True, create=True):
    if create:
        return Plan(data)
    return Plan
