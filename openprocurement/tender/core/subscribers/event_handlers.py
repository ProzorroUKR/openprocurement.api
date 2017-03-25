# -*- coding: utf-8 -*-
from pyramid.events import subscriber
from openprocurement.api.events import ErrorDesctiptorEvent


@subscriber(ErrorDesctiptorEvent)
def tender_error_handler(event):
    if 'tender' in event.request.validated:
        event.params['TENDER_REV'] = event.request.validated['tender'].rev
        event.params['TENDERID'] = event.request.validated['tender'].tenderID
        event.params['TENDER_STATUS'] = event.request.validated['tender'].status
