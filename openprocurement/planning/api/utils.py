# -*- coding: utf-8 -*-
from functools import partial
from json import dumps
from logging import getLogger
from time import sleep
from urllib import quote
from rfc6266 import build_header
from urlparse import urlparse, parse_qs
from base64 import b64encode
from cornice.resource import resource
from cornice.util import json_error
from couchdb.http import ResourceConflict
from openprocurement.api.models import Revision, get_now
from openprocurement.api.utils import (update_logging_context, context_unpack, get_revision_changes,
    apply_data_patch, generate_id, DOCUMENT_BLACKLISTED_FIELDS,get_filename )
from openprocurement.planning.api.models import Plan
from openprocurement.planning.api.traversal import factory
from schematics.exceptions import ModelValidationError
from pkg_resources import get_distribution

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def generate_plan_id(ctime, db, server_id=''):
    """ Generate ID for new plan in format "UA-P-YYYY-MM-DD-NNNNNN" + ["-server_id"]
        YYYY - year, MM - month (start with 1), DD - day, NNNNNN - sequence number per 1 day
        and save plans count per day in database document with _id = "planID" as { key, value } = { "2015-12-03": 2 }
    :param ctime: system date-time
    :param db: couchdb database object
    :param server_id: server mark (for claster mode)
    :return: planID in "UA-2015-05-08-000005"
    """
    key = ctime.date().isoformat()  # key (YYYY-MM-DD)
    plan_id_doc = 'planID_' + server_id if server_id else 'planID'  # document _id
    index = 1
    while True:
        try:
            plan_id = db.get(plan_id_doc, {'_id': plan_id_doc})  # find root document
            index = plan_id.get(key, 1)
            plan_id[key] = index + 1  # count of plans in db (+1 ?)
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
    """ Save plan object to database
    :param request:
    :return: True if Ok
    """
    plan = request.validated['plan']
    patch = get_revision_changes(plan.serialize("plain"), request.validated['plan_src'])
    if patch:
        plan.revisions.append(Revision({'author': request.authenticated_userid, 'changes': patch, 'rev': plan.rev}))
        old_date_modified = plan.dateModified
        plan.dateModified = get_now()
        try:
            plan.store(request.registry.db)
        except ModelValidationError, e: # pragma: no cover
            for i in e.message:
                request.errors.add('body', i, e.message[i])
            request.errors.status = 422
        except Exception, e:  # pragma: no cover
            request.errors.add('body', 'data', str(e))
        else:
            LOGGER.info('Saved plan {}: dateModified {} -> {}'.format(plan.id,
                                                                      old_date_modified and old_date_modified.isoformat(),
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
    LOGGER.info('Error on processing request "{}"'.format(dumps(errors, indent=4)),
                extra=context_unpack(errors.request, {'MESSAGE_ID': 'error_handler'}, params))
    return json_error(errors)


opresource = partial(resource, error_handler=error_handler, factory=factory)

class APIResource(object):

    def __init__(self, request, context):
        self.context = context
        self.request = request
        self.db = request.registry.db
        self.server_id = request.registry.server_id
        self.server = request.registry.couchdb_server
        self.LOGGER = getLogger(type(self).__module__)

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

def upload_file(request, blacklisted_fields=DOCUMENT_BLACKLISTED_FIELDS):
    first_document = request.validated['documents'][0] if 'documents' in request.validated and request.validated['documents'] else None
    if request.content_type == 'multipart/form-data':
        data = request.validated['file']
        filename = get_filename(data)
        content_type = data.type
        in_file = data.file
    else:
        filename = first_document.title
        content_type = request.content_type
        in_file = request.body_file

    if hasattr(request.context, "documents"):
        # upload new document
        model = type(request.context).documents.model_class
    else:
        # update document
        model = type(request.context)
    document = model({'title': filename, 'format': content_type})
    document.__parent__ = request.context
    if 'document_id' in request.validated:
        document.id = request.validated['document_id']
    if first_document:
        for attr_name in type(first_document)._fields:
            if attr_name not in blacklisted_fields:
                setattr(document, attr_name, getattr(first_document, attr_name))
    key = generate_id()
    document_route = request.matched_route.name.replace("collection_", "")
    document_path = request.current_route_path(_route_name=document_route, document_id=document.id, _query={'download': key})
    document.url = '/' + '/'.join(document_path.split('/')[3:])
    conn = getattr(request.registry, 's3_connection', None)
    if conn:
        bucket = conn.get_bucket(request.registry.bucket_name)
        filename = "{}/{}/{}".format(request.validated['plan_id'], document.id, key)
        key = bucket.new_key(filename)
        key.set_metadata('Content-Type', document.format)
        key.set_metadata("Content-Disposition", build_header(document.title, filename_compat=quote(document.title.encode('utf-8'))))
        key.set_contents_from_file(in_file)
        key.set_acl('private')
    else:
        filename = "{}_{}".format(document.id, key)
        request.validated['plan']['_attachments'][filename] = {
            "content_type": document.format,
            "data": b64encode(in_file.read())
        }
    update_logging_context(request, {'file_size': in_file.tell()})
    return document

def update_file_content_type(request):
    conn = getattr(request.registry, 's3_connection', None)
    if conn:
        document = request.validated['document']
        key = parse_qs(urlparse(document.url).query).get('download').pop()
        bucket = conn.get_bucket(request.registry.bucket_name)
        filename = "{}/{}/{}".format(request.validated['plan_id'], document.id, key)
        key = bucket.get_key(filename)
        if key.content_type != document.format:
            key.set_remote_metadata({'Content-Type': document.format}, {}, True)

def get_file(request):
    plan_id = request.validated['plan_id']
    document = request.validated['document']
    key = request.params.get('download')
    conn = getattr(request.registry, 's3_connection', None)
    filename = "{}_{}".format(document.id, key)
    if conn and filename not in request.validated['plan']['_attachments']:
        filename = "{}/{}/{}".format(plan_id, document.id, key)
        url = conn.generate_url(method='GET', bucket=request.registry.bucket_name, key=filename, expires_in=300)
        request.response.content_type = document.format.encode('utf-8')
        request.response.content_disposition = build_header(document.title, filename_compat=quote(document.title.encode('utf-8')))
        request.response.status = '302 Moved Temporarily'
        request.response.location = url
        return url
    else:
        filename = "{}_{}".format(document.id, key)
        data = request.registry.db.get_attachment(plan_id, filename)
        if data:
            request.response.content_type = document.format.encode('utf-8')
            request.response.content_disposition = build_header(document.title, filename_compat=quote(document.title.encode('utf-8')))
            request.response.body_file = data
            return request.response
        request.errors.add('url', 'download', 'Not Found')
        request.errors.status = 404