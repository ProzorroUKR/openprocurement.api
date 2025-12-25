from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.core.procedure.serializers.contract import (
    get_change_rationale_types,
)


class ContractChangeStateMixin:
    def validate_change_rationale_types(self, data, tender):
        contract = self.request.validated["contract"]
        allowed_rationale_types = tuple(
            contract.get("contractChangeRationaleTypes", get_change_rationale_types(tender)).keys()
        )
        for rationale in data.get("rationaleTypes", []):
            if rationale not in allowed_rationale_types:
                raise_operation_error(
                    self.request,
                    [f"Value must be one of {allowed_rationale_types}."],
                    name="rationaleTypes",
                    status=422,
                )
