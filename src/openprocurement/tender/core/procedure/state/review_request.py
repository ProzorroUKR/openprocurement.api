from uuid import uuid4

from openprocurement.api.context import get_now, get_request
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.tender import TenderState


class ReviewRequestStateMixin:
    def review_request_on_post(self, data: dict) -> None:
        tender = self.request.validated["tender"]

        self.validate_lot_id(data, tender)
        self.validate_post_review_request_without_inspector(tender)
        self.validate_post_in_tender_status(tender)
        self.validate_post_without_active_award(data, tender)
        self.validate_exist_unanswered_review_request(data, tender)

        data.update(
            {
                "id": uuid4().hex,
                "dateCreated": get_now().isoformat(),
                "tenderStatus": tender["status"],
            }
        )

    def review_request_on_patch(self, before: dict, after: dict) -> None:
        self.validate_patch_review_request_once(before)
        after["date"] = get_now().isoformat()
        if after["approved"]:
            after["is_valid"] = True

    @staticmethod
    def validate_lot_id(data: dict, tender: dict) -> None:
        lots = tender.get("lots", "")
        lot_id = data.get("lotID")
        available_statuses = ("active.qualification", "active.awarded")
        request = get_request()

        if lot_id:
            if tender["status"] not in available_statuses:
                raise_operation_error(
                    get_request(),
                    f"lotID could be set only in {available_statuses} tender statuses",
                    status=422,
                    name="lotID",
                )

            if not lots:
                raise_operation_error(request, "Rogue field", status=422, name="lotID")

            if lot_id and lot_id not in tuple(lot["id"] for lot in lots if lot.get("status", "") == "active"):
                raise_operation_error(
                    get_request(),
                    "lotID should be one of lots",
                    status=422,
                    name="lotID",
                )
        else:
            if tender["status"] in available_statuses and lots:
                raise_operation_error(request, "Required field.", status=422, name="lotID")

    @staticmethod
    def validate_post_review_request_without_inspector(tender: dict) -> None:
        if not tender.get("inspector"):
            raise_operation_error(get_request(), "Can't create reviewRequest without inspector")

    @staticmethod
    def validate_post_in_tender_status(tender: dict) -> None:
        allowed_post_statuses = ("active.enquiries", "active.qualification", "active.awarded")
        if tender["status"] not in allowed_post_statuses:
            raise_operation_error(
                get_request(),
                f"Review request can be created only in {allowed_post_statuses} tender statuses",
            )

    @staticmethod
    def validate_post_without_active_award(data: dict, tender: dict) -> None:
        if tender["status"] not in ("active.qualification", "active.awarded"):
            return

        lot_id = data.get("lotID", "")
        active_awards = [
            i for i in tender.get("awards", "") if i.get("status", "") == "active" and i.get("lotID", "") == lot_id
        ]

        if not active_awards:
            obj_name = "lot" if lot_id else "tender"
            raise_operation_error(
                get_request(),
                f"Review request can be created only for {obj_name} with active award",
            )

    @staticmethod
    def validate_exist_unanswered_review_request(data: dict, tender: dict) -> None:
        if not tender.get("reviewRequests"):
            return

        review_requests = tender.get("reviewRequests")
        lot_id = data.get("lotID", "")
        review_requests = [i for i in review_requests if lot_id == i.get("lotID", "")]

        if review_requests and "approved" not in review_requests[-1]:
            raise_operation_error(
                get_request(),
                "Disallowed create review request while existing another unanswered review request",
            )

    @staticmethod
    def validate_patch_review_request_once(before: dict) -> None:
        if "approved" in before:
            raise_operation_error(get_request(), "Disallowed re-patching review request")


class ReviewRequestState(ReviewRequestStateMixin, TenderState):
    pass
