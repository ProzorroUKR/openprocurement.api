# -*- coding: utf-8 -*-
from re import compile
from barbecue import chef
from jsonpointer import resolve_pointer
from functools import partial
from datetime import datetime, time, timedelta
from pkg_resources import get_distribution
from logging import getLogger
from schematics.exceptions import ModelValidationError
from time import sleep
from pyramid.exceptions import URLDecodeError
from pyramid.compat import decode_path_info
from cornice.resource import resource
from couchdb.http import ResourceConflict
from openprocurement.api.constants import WORKING_DAYS, SANDBOX_MODE, TZ
from openprocurement.api.utils import error_handler
from openprocurement.api.utils import (
    get_now, context_unpack, get_revision_changes, apply_data_patch,
    update_logging_context, set_modetest_titles
)
from openprocurement.tender.core.constants import (
    BIDDER_TIME, SERVICE_TIME, AUCTION_STAND_STILL_TIME
)
from openprocurement.tender.core.traversal import factory
PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)

ACCELERATOR_RE = compile(r'.accelerator=(?P<accelerator>\d+)')


optendersresource = partial(resource, error_handler=error_handler,
                            factory=factory)

def rounding_shouldStartAfter(start_after, tender, use_from=datetime(2016, 7, 16, tzinfo=TZ)):
    if (tender.enquiryPeriod and tender.enquiryPeriod.startDate or get_now()) > use_from and not (SANDBOX_MODE and tender.submissionMethodDetails and u'quick' in tender.submissionMethodDetails):
        midnigth = datetime.combine(start_after.date(), time(0, tzinfo=start_after.tzinfo))
        if start_after > midnigth:
            start_after = midnigth + timedelta(1)
    return start_after


def calc_auction_end_time(bids, start):
    return start + bids * BIDDER_TIME + SERVICE_TIME + AUCTION_STAND_STILL_TIME


def generate_tender_id(ctime, db, server_id=''):
    key = ctime.date().isoformat()
    tenderIDdoc = 'tenderID_' + server_id if server_id else 'tenderID'
    while True:
        try:
            tenderID = db.get(tenderIDdoc, {'_id': tenderIDdoc})
            index = tenderID.get(key, 1)
            tenderID[key] = index + 1
            db.save(tenderID)
        except ResourceConflict:  # pragma: no cover
            pass
        except Exception:  # pragma: no cover
            sleep(1)
        else:
            break
    return 'UA-{:04}-{:02}-{:02}-{:06}{}'.format(ctime.year,
                                                 ctime.month,
                                                 ctime.day,
                                                 index,
                                                 server_id and '-' + server_id)


def tender_serialize(request, tender_data, fields):
    tender = request.tender_from_data(tender_data, raise_error=False)
    if tender is None:
        return dict([(i, tender_data.get(i, '')) for i in ['procurementMethodType', 'dateModified', 'id']])
    return dict([(i, j) for i, j in tender.serialize(tender.status).items() if i in fields])


def save_tender(request):
    tender = request.validated['tender']
    if tender.mode == u'test':
        set_modetest_titles(tender)
    patch = get_revision_changes(tender.serialize("plain"), request.validated['tender_src'])
    if patch:
        now = get_now()
        status_changes = [
            p
            for p in patch
            if not p['path'].startswith('/bids/') and p['path'].endswith("/status") and p['op'] == "replace"
        ]
        for change in status_changes:
            obj = resolve_pointer(tender, change['path'].replace('/status', ''))
            if obj and hasattr(obj, "date"):
                date_path = change['path'].replace('/status', '/date')
                if obj.date and not any([p for p in patch if date_path == p['path']]):
                    patch.append({"op": "replace",
                                  "path": date_path,
                                  "value": obj.date.isoformat()})
                elif not obj.date:
                    patch.append({"op": "remove", "path": date_path})
                obj.date = now
        tender.revisions.append(type(tender).revisions.model_class({
            'author': request.authenticated_userid,
            'changes': patch,
            'rev': tender.rev
        }))
        old_dateModified = tender.dateModified
        if getattr(tender, 'modified', True):
            tender.dateModified = now
        try:
            tender.store(request.registry.db)
        except ModelValidationError, e:
            for i in e.message:
                request.errors.add('body', i, e.message[i])
            request.errors.status = 422
        except ResourceConflict, e:  # pragma: no cover
            request.errors.add('body', 'data', str(e))
            request.errors.status = 409
        except Exception, e:  # pragma: no cover
            request.errors.add('body', 'data', str(e))
        else:
            LOGGER.info('Saved tender {}: dateModified {} -> {}'.format(tender.id, old_dateModified and old_dateModified.isoformat(), tender.dateModified.isoformat()),
                        extra=context_unpack(request, {'MESSAGE_ID': 'save_tender'}, {'RESULT': tender.rev}))
            return True


def apply_patch(request, data=None, save=True, src=None):
    data = request.validated['data'] if data is None else data
    patch = data and apply_data_patch(src or request.context.serialize(), data)
    if patch:
        request.context.import_data(patch)
        if save:
            return save_tender(request)


def remove_draft_bids(request):
    tender = request.validated['tender']
    if [bid for bid in tender.bids if getattr(bid, "status", "active") == "draft"]:
        LOGGER.info('Remove draft bids',
                    extra=context_unpack(request, {'MESSAGE_ID': 'remove_draft_bids'}))
        tender.bids = [bid for bid in tender.bids if getattr(bid, "status", "active") != "draft"]


def cleanup_bids_for_cancelled_lots(tender):
    cancelled_lots = [i.id for i in tender.lots if i.status == 'cancelled']
    if cancelled_lots:
        return
    cancelled_items = [i.id for i in tender.items if i.relatedLot in cancelled_lots]
    cancelled_features = [
        i.code
        for i in (tender.features or [])
        if i.featureOf == 'lot' and i.relatedItem in cancelled_lots or i.featureOf == 'item' and i.relatedItem in cancelled_items
    ]
    for bid in tender.bids:
        bid.documents = [i for i in bid.documents if i.documentOf != 'lot' or i.relatedItem not in cancelled_lots]
        bid.parameters = [i for i in bid.parameters if i.code not in cancelled_features]
        bid.lotValues = [i for i in bid.lotValues if i.relatedLot not in cancelled_lots]
        if not bid.lotValues:
            tender.bids.remove(bid)


def has_unanswered_questions(tender, filter_cancelled_lots=True):
    if filter_cancelled_lots and tender.lots:
        active_lots = [l.id for l in tender.lots if l.status == 'active']
        active_items = [i.id for i in tender.items if not i.relatedLot or i.relatedLot in active_lots]
        return any([
            not i.answer
            for i in tender.questions
            if i.questionOf == 'tender' or i.questionOf == 'lot' and i.relatedItem in active_lots or i.questionOf == 'item' and i.relatedItem in active_items
        ])
    return any([not i.answer for i in tender.questions])


def has_unanswered_complaints(tender, filter_cancelled_lots=True):
    if filter_cancelled_lots and tender.lots:
        active_lots = [l.id for l in tender.lots if l.status == 'active']
        return any([i.status in tender.block_tender_complaint_status for i in tender.complaints if not i.relatedLot \
                    or (i.relatedLot and i.relatedLot in active_lots)])
    return any([i.status in tender.block_tender_complaint_status for i in tender.complaints])


def extract_tender_adapter(request, tender_id):
    db = request.registry.db
    doc = db.get(tender_id)
    if doc is None or doc.get('doc_type') != 'Tender':
        request.errors.add('url', 'tender_id', 'Not Found')
        request.errors.status = 404
        raise error_handler(request.errors)

    return request.tender_from_data(doc)


def extract_tender(request):
    try:
        # empty if mounted under a path in mod_wsgi, for example
        path = decode_path_info(request.environ['PATH_INFO'] or '/')
    except KeyError:
        path = '/'
    except UnicodeDecodeError as e:
        raise URLDecodeError(e.encoding, e.object, e.start, e.end, e.reason)

    tender_id = ""
    # extract tender id
    parts = path.split('/')
    if len(parts) < 4 or parts[3] != 'tenders':
        return

    tender_id = parts[4]
    return extract_tender_adapter(request, tender_id)


class isTender(object):
    """ Route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'procurementMethodType = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.tender is not None:
            return getattr(request.tender, 'procurementMethodType', None) == self.val
        return False


class SubscribersPicker(isTender):
    """ Subscriber predicate. """

    def __call__(self, event):
        if event.tender is not None:
            return getattr(event.tender, 'procurementMethodType', None) == self.val
        return False


def register_tender_procurementMethodType(config, model):
    """Register a tender procurementMethodType.
    :param config:
        The pyramid configuration object that will be populated.
    :param model:
        The tender model class
    """
    config.registry.tender_procurementMethodTypes[model.procurementMethodType.default] = model


def tender_from_data(request, data, raise_error=True, create=True):
    procurementMethodType = data.get('procurementMethodType', 'belowThreshold')
    model = request.registry.tender_procurementMethodTypes.get(procurementMethodType)
    if model is None and raise_error:
        request.errors.add('data', 'procurementMethodType', 'Not implemented')
        request.errors.status = 415
        raise error_handler(request.errors)
    update_logging_context(request, {'tender_type': procurementMethodType})
    if model is not None and create:
        model = model(data)
    return model


def calculate_business_date(date_obj, timedelta_obj, context=None,
                            working_days=False):
    if context and 'procurementMethodDetails' in context and context['procurementMethodDetails']:
        re_obj = ACCELERATOR_RE.search(context['procurementMethodDetails'])
        if re_obj and 'accelerator' in re_obj.groupdict():
            return date_obj + (timedelta_obj / int(re_obj.groupdict()['accelerator']))
    if working_days:
        if timedelta_obj > timedelta():
            if date_obj.weekday() in [5, 6] and WORKING_DAYS.get(date_obj.date().isoformat(), True) or WORKING_DAYS.get(date_obj.date().isoformat(), False):
                date_obj = datetime.combine(date_obj.date(), time(0, tzinfo=date_obj.tzinfo)) + timedelta(1)
                while date_obj.weekday() in [5, 6] and WORKING_DAYS.get(date_obj.date().isoformat(), True) or WORKING_DAYS.get(date_obj.date().isoformat(), False):
                    date_obj += timedelta(1)
        else:
            if date_obj.weekday() in [5, 6] and WORKING_DAYS.get(date_obj.date().isoformat(), True) or WORKING_DAYS.get(date_obj.date().isoformat(), False):
                date_obj = datetime.combine(date_obj.date(), time(0, tzinfo=date_obj.tzinfo))
                while date_obj.weekday() in [5, 6] and WORKING_DAYS.get(date_obj.date().isoformat(), True) or WORKING_DAYS.get(date_obj.date().isoformat(), False):
                    date_obj -= timedelta(1)
                date_obj += timedelta(1)
        for _ in xrange(abs(timedelta_obj.days)):
            date_obj += timedelta(1) if timedelta_obj > timedelta() else -timedelta(1)
            while date_obj.weekday() in [5, 6] and WORKING_DAYS.get(date_obj.date().isoformat(), True) or WORKING_DAYS.get(date_obj.date().isoformat(), False):
                date_obj += timedelta(1) if timedelta_obj > timedelta() else -timedelta(1)
        return date_obj
    return date_obj + timedelta_obj
