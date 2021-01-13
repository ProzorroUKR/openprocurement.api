# -*- coding: utf-8 -*-
from pyramid.events import subscriber
from pyramid.events import ContextFound, NewRequest
from openprocurement.api.events import ErrorDesctiptorEvent
from openprocurement.api.utils import update_logging_context


@subscriber(ErrorDesctiptorEvent)
def tender_error_handler(event):
    if "tender" in event.request.validated:
        event.params["TENDER_REV"] = event.request.validated["tender"].rev
        event.params["TENDERID"] = event.request.validated["tender"].tenderID
        event.params["TENDER_STATUS"] = event.request.validated["tender"].status


@subscriber(NewRequest)
def wrap_request(event):
    def add_nosniff_header(request, response):
        """IE has some rather unfortunately content-type-sniffing behaviour
        that can be used to trigger XSS attacks via a JSON API, as described here:
        * http://blog.watchfire.com/wfblog/2011/10/json-based-xss-exploitation.html
        * https://superevr.com/blog/2012/exploiting-xss-in-ajax-web-applications/
        Make cornice safe-by-default against this attack by including the header.
        """
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
    request = event.request
    request.add_response_callback(add_nosniff_header)


@subscriber(ContextFound)
def extend_tender_logging_context(event):
    request = event.request
    if "tender" in request.validated:
        params = {}
        params["TENDER_REV"] = request.validated["tender"].rev
        params["TENDERID"] = request.validated["tender"].tenderID
        params["TENDER_STATUS"] = request.validated["tender"].status
        params["TENDER_MODE"] = request.validated["tender"].mode
        update_logging_context(request, params)
