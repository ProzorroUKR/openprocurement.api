from schematics.exceptions import ValidationError

from openprocurement.api.constants_env import REQ_RESPONSE_VALUES_VALIDATION_FROM
from openprocurement.api.context import get_request_now
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
from openprocurement.tender.core.procedure.validation import (
    validate_req_response_values,
)


class BaseReqResponseState(BaseState):
    parent_obj_name: str

    def always(self, data: dict) -> None:
        self.pre_save_validations(data)

    def pre_save_validations(self, data: dict) -> None:
        parent = self.request.validated[self.parent_obj_name]

        if isinstance(data, dict):
            data = [data]

        def add_error(error_name: str, e: ValidationError) -> None:
            error_msg = e.messages[0]
            if self.request.method != "POST":
                # For operation with concrete requirement response
                if isinstance(e.messages[0], dict):
                    error_name = list(e.messages[0].keys())[0]
                    error_msg = e.messages[0][error_name]
                else:
                    error_name = "data"
                    error_msg = e.messages[0]

            self.request.errors.add("body", error_name, error_msg)

        try:
            validate_response_requirement_uniq(parent.get("requirementResponses"))
        except ValidationError as e:
            add_error("requirementResponses", e)

        for i, req_response in enumerate(data):
            try:
                self.validate_req_response_data(parent, req_response)
            except ValidationError as e:
                add_error(f"requirementResponses.{i}", e)

        if self.request.errors:
            self.request.errors.status = 422
            raise error_handler(self.request)

    def validate_req_response_data(self, parent: dict, req_response: dict) -> None:
        validate_req_response_requirement(req_response, self.parent_obj_name)
        MatchResponseValue.match(req_response)
        validate_req_response_related_tenderer(parent, req_response)
        validate_req_response_evidences_relatedDocument(parent, req_response, self.parent_obj_name)
        if get_request_now() > REQ_RESPONSE_VALUES_VALIDATION_FROM:
            validate_req_response_values(req_response)


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
