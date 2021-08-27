# -*- coding: utf-8 -*-
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.api.constants import GUARANTEE_ALLOWED_TENDER_TYPES
from openprocurement.tender.core.procedure.context import get_now
from openprocurement.tender.core.procedure.documents import check_document, update_document_url


# BID DOCUMENTS
def validate_bid_document_operation_in_not_allowed_tender_status(request, **kwargs):
    tender = request.validated["tender"]
    if tender["status"] == "active.awarded" and tender["procurementMethodType"] in GUARANTEE_ALLOWED_TENDER_TYPES:
        bid_id = request.validated["bid"]["id"]
        if (
            any(
                award["status"] == "active" and award["bid_id"] == bid_id
                for award in tender.get("awards", "")
            )
            and any(
                criterion["classification"]["id"] == "CRITERION.OTHER.CONTRACT.GUARANTEE"
                for criterion in tender.get("criteria", "")
            )
        ):
            pass  # documents are allowed if award for this bid is active
        else:
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} document "
                f"in current ({tender['status']}) tender status"
            )
    elif tender["status"] not in ("active.tendering", "active.qualification"):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document "
            f"in current ({tender['status']}) tender status"
        )


def validate_bid_document_operation_with_not_pending_award(request, **kwargs):
    tender = request.validated["tender"]
    bid = request.validated["bid"]
    if tender["status"] == "active.qualification" and not any(
        award["bid_id"] == bid["id"] and award["status"] == "pending"
        for award in tender.get("awards", "")
    ):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document because award of bid is not in pending state",
        )


def validate_upload_documents_not_allowed_for_simple_pmr(request, **kwargs):
    tender = request.validated["tender"]
    statuses = ("active.qualification",)
    if tender["status"] in statuses and tender.get("procurementMethodRationale") == "simple":
        bid_id = request.validated["bid"]["id"]
        criteria = tender["criteria"]
        awards = tender["awards"]
        bid_with_active_award = any([award["status"] == "active" and award["bid_id"] == bid_id for award in awards])
        needed_criterion = any(
            [criterion["classification"]["id"] == "CRITERION.OTHER.CONTRACT.GUARANTEE" for criterion in criteria]
        )
        if not all([needed_criterion, bid_with_active_award]):
            raise_operation_error(
                request,
                "Can't upload document with {} tender status and procurementMethodRationale simple".format(
                    statuses
                ),
            )
