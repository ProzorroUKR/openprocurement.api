import re
from datetime import timedelta
from functools import wraps
from logging import getLogger

from dateorro import calc_datetime

from openprocurement.api.constants import TENDER_CRITERIA_RULES, WORKING_DAYS
from openprocurement.api.context import get_request_now
from openprocurement.api.mask import mask_object_data
from openprocurement.api.utils import (
    calculate_date,
    calculate_full_date,
    get_first_revision_date,
    is_boolean,
)
from openprocurement.api.validation import validate_json_data

LOGGER = getLogger("openprocurement.tender.core")

ACCELERATOR_RE = re.compile(r".accelerator=(?P<accelerator>\d+)")


QUICK = "quick"
QUICK_NO_AUCTION = "quick(mode:no-auction)"
QUICK_FAST_FORWARD = "quick(mode:fast-forward)"
QUICK_FAST_AUCTION = "quick(mode:fast-auction)"


class ProcurementMethodTypePredicate:
    """Route predicate factory for procurementMethodType route predicate."""

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "procurementMethodType = {}".format(self.val)

    phash = text

    def __call__(self, context, request):
        procurement_method_type = self.procurement_method_type(request)
        if isinstance(self.val, list):
            return procurement_method_type in self.val
        return procurement_method_type == self.val

    @staticmethod
    def tender_data(request):
        if request.tender_doc is not None:
            return request.tender_doc
        elif request.method == "POST" and request.path.endswith("/tenders"):
            # that's how we can have a "POST /tender" view for every tender type
            return validate_json_data(request)
        else:
            return None

    @classmethod
    def procurement_method_type(cls, request):
        data = cls.tender_data(request)
        if data is None:
            return None
        return data.get("procurementMethodType", "belowThreshold")

    @classmethod
    def route_prefix(cls, request):
        return cls.procurement_method_type(request)


class ComplaintTypePredicate:
    """Route predicate factory for complaintType route predicate."""

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "complaintType = {}".format(self.val)

    phash = text

    def __call__(self, context, request):
        return request.complaint_type == self.val


def get_tender_accelerator(context):
    if context and "procurementMethodDetails" in context and context["procurementMethodDetails"]:
        re_obj = ACCELERATOR_RE.search(context["procurementMethodDetails"])
        if re_obj and "accelerator" in re_obj.groupdict():
            return int(re_obj.groupdict()["accelerator"])
    return None


def accelerated_tender(wrapped):
    @wraps(wrapped)
    def wrapper(date_obj, timedelta_obj, tender=None, **kwargs):
        accelerator = get_tender_accelerator(tender)
        if accelerator:
            return calc_datetime(date_obj, timedelta_obj, accelerator=accelerator)
        return wrapped(date_obj, timedelta_obj, **kwargs)

    return wrapper


@accelerated_tender
def calculate_tender_date(date_obj, timedelta_obj, working_days=False, calendar=WORKING_DAYS):
    return calculate_date(date_obj, timedelta_obj, working_days=working_days, calendar=calendar)


@accelerated_tender
def calculate_tender_full_date(date_obj, timedelta_obj, working_days=False, calendar=WORKING_DAYS):
    ceil = timedelta_obj > timedelta()
    return calculate_full_date(date_obj, timedelta_obj, working_days=working_days, calendar=calendar, ceil=ceil)


def context_view(objs):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            response = func(self, *args, **kwargs)
            if is_boolean(self.request.params.get("opt_context")):
                context = {}
                for parent_name, parent_params in objs.items():
                    parent_serializer_class, mask_mapping = parent_params
                    if parent_obj := self.request.validated.get(parent_name):
                        mask_object_data(self.request, parent_obj, mask_mapping)
                        context[parent_name] = parent_serializer_class(parent_obj).data
                response.update({"context": context})
            return response

        return wrapper

    return decorator


def get_criteria_rules(tender):
    periods = TENDER_CRITERIA_RULES.get(tender.get("procurementMethodType", ""), [])

    tender_created = get_first_revision_date(tender, default=get_request_now())

    for period in periods:
        start_date = period["period"].get("start_date")
        end_date = period["period"].get("end_date")

        if start_date is not None and tender_created < start_date:
            continue

        if end_date is not None and tender_created > end_date:
            continue

        return period["criteria"]

    return {}
