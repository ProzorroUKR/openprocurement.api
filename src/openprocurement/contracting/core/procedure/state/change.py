from openprocurement.api.deprecated.rationale_types import CAUSE_TO_FROZEN_RATIONALE_TYPES_MAPPING
from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.core.procedure.serializers.rationale_types import (
    get_change_rationale_types_reference,
)


class ContractChangeStateMixin:
    def validate_change_rationale_types(self, data, tender):
        contract = self.request.validated["contract"]
        rationale_types = get_change_rationale_types_reference(tender, CAUSE_TO_FROZEN_RATIONALE_TYPES_MAPPING)
        allowed_rationale_types = tuple(contract.get("contractChangeRationaleTypes", rationale_types).keys())
        for rationale in data.get("rationaleTypes", []):
            if rationale not in allowed_rationale_types:
                raise_operation_error(
                    self.request,
                    [f"Value must be one of {allowed_rationale_types}."],
                    name="rationaleTypes",
                    status=422,
                )
