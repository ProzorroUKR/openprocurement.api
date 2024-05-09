from typing import Optional

from openprocurement.api.context import get_request
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request


class ReviewRequestBlockMixin:
    @staticmethod
    def invalidate_review_requests(lot_id: str = ""):
        request = get_request()
        tender = request.validated["tender"]
        tender_status = tender.get("status")

        if tender_status in ("active.qualification", "active.awarded"):
            tender_status = ("active.qualification", "active.awarded")
        else:
            tender_status = (tender_status,)

        for rev_req in tender.get("reviewRequests", ""):
            if (
                rev_req.get("lotID", "") == lot_id
                and rev_req.get("tenderStatus") in tender_status
                and rev_req.get("approved")
                and rev_req.get("is_valid")
            ):
                rev_req["is_valid"] = False

    @staticmethod
    def validate_action_with_exist_inspector_review_request(
        allowed_fields: Optional[tuple] = None,
        lot_id: str = "",
    ) -> None:

        request = get_request()
        tender = request.validated["tender"]

        rev_reqs = [i for i in tender.get("reviewRequests", "") if i.get("lotID", "") == lot_id]

        if rev_reqs and "approved" not in rev_reqs[-1]:
            if allowed_fields:
                json_data = request.validated["json_data"]
                for i in json_data.keys():
                    if i not in allowed_fields:
                        raise_operation_error(
                            request,
                            f"With unanswered review request can be patched only {allowed_fields} fields",
                            status=422,
                        )
            else:
                raise_operation_error(
                    request,
                    f"Disallowed while exist unanswered review request",
                    status=422,
                )
