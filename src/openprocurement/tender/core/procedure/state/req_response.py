from schematics.exceptions import ValidationError

from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import error_handler
from openprocurement.tender.core.procedure.models.req_response import (
    MatchResponseValue,
    validate_req_response_evidences_relatedDocument,
    validate_req_response_related_tenderer,
    validate_req_response_requirement,
    validate_response_requirement_uniq,
)
from openprocurement.tender.core.procedure.state.utils import invalidate_pending_bid


class BaseReqResponseState(BaseState):
    parent_obj_name: str

    def always(self, data: dict) -> None:
        self.pre_save_validations(data)

    def pre_save_validations(self, data: dict) -> None:
        parent = self.request.validated[self.parent_obj_name]

        if isinstance(data, dict):
            data = [data]

        for i, req_response in enumerate(data):
            try:
                validate_response_requirement_uniq(parent.get("requirementResponses"))
                self.validate_req_response_data(parent, req_response)
            except ValidationError as e:
                error_name = i
                error_msg = e.messages[0]
                if self.request.method != "POST":
                    # For operation with concrete requirement response
                    error_name = list(e.messages[0].keys())[0]
                    error_msg = e.messages[0][error_name]
                self.request.errors.add("body", error_name, error_msg)

        if self.request.errors:
            self.request.errors.status = 422
            raise error_handler(self.request)

    def validate_req_response_data(self, parent: dict, req_response: dict) -> None:
        validate_req_response_requirement(req_response, self.parent_obj_name)
        MatchResponseValue.match(req_response)
        validate_req_response_related_tenderer(parent, req_response)
        validate_req_response_evidences_relatedDocument(parent, req_response, self.parent_obj_name)


class BidReqResponseState(BaseReqResponseState):
    parent_obj_name = "bid"

    def validate_req_response_data(self, parent: dict, req_response: dict) -> None:
        bid = self.request.validated[self.parent_obj_name]
        if bid["status"] not in ["active", "pending"]:
            return
        super().validate_req_response_data(parent, req_response)

    def always(self, data: dict) -> None:
        super().always(data)
        invalidate_pending_bid()


class AwardReqResponseState(BaseReqResponseState):
    parent_obj_name = "award"


class QualificationReqResponseState(BaseReqResponseState):
    parent_obj_name = "qualification"
