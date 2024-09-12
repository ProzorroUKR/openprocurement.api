import re
from datetime import timedelta
from functools import wraps
from logging import getLogger

from dateorro import calc_datetime

from openprocurement.api.constants import WORKING_DAYS
from openprocurement.api.utils import calculate_date, calculate_full_date, is_boolean
from openprocurement.api.validation import validate_json_data
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)

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
        procurement_method_type = cls.procurement_method_type(request)
        if procurement_method_type in ABOVE_THRESHOLD_GROUP:
            return ABOVE_THRESHOLD_GROUP_NAME
        return procurement_method_type


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
                for parent_name, parent_serializer_class in objs.items():
                    if parent_obj := self.request.validated.get(parent_name):
                        context[parent_name] = parent_serializer_class(parent_obj).data
                response.update({"context": context})
            return response

        return wrapper

    return decorator
