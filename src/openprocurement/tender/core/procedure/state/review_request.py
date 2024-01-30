from uuid import uuid4

from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.api.utils import get_now, raise_operation_error
from openprocurement.api.context import get_request


class ReviewRequestStateMixin:
    def review_request_on_post(self, data: dict) -> None:
        tender = self.request.validated["tender"]

        self.validate_post_review_request_without_inspector(tender)
        self.validate_post_in_tender_status(tender)
        self.validate_exist_unanswered_review_request(tender)

        data.update({
            "id": uuid4().hex,
            "dateCreated": get_now().isoformat(),
            "tenderStatus": tender["status"]
        })

    def review_request_on_patch(self, before: dict, after: dict) -> None:
        self.validate_patch_review_request_once(before)
        after["date"] = get_now().isoformat()

    @staticmethod
    def validate_post_review_request_without_inspector(tender: dict) -> None:
        if not tender.get("inspector"):
            raise_operation_error(get_request(), "Can't create reviewRequest without inspector")

    @staticmethod
    def validate_post_in_tender_status(tender: dict) -> None:
        allowed_post_statuses = ("active.enquiries", "active.awarded")
        if tender["status"] not in allowed_post_statuses:
            raise_operation_error(
                get_request(),
                f"Review request can be created only in {allowed_post_statuses} tender statuses",
            )

    @staticmethod
    def validate_exist_unanswered_review_request(tender: dict) -> None:
        if tender.get("reviewRequests") and "approved" not in tender["reviewRequests"][-1]:
            raise_operation_error(
                get_request(),
                "Disallowed create review request while existing another unanswered review request"
            )

    @staticmethod
    def validate_patch_review_request_once(before: dict) -> None:
        if "approved" in before:
            raise_operation_error(get_request(), "Disallowed re-patching review request")


class ReviewRequestState(ReviewRequestStateMixin, TenderState):
    pass
