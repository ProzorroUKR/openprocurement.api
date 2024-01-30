from typing import Optional
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.context import get_request
from openprocurement.tender.core.procedure.context import get_request


class ReviewRequestBlockMixin:
    @staticmethod
    def validate_action_with_exist_inspector_review_request(allowed_fields: Optional[tuple] = None) -> None:
        request = get_request()
        tender = request.validated["tender"]

        rev_reqs = tender.get("reviewRequests")

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
