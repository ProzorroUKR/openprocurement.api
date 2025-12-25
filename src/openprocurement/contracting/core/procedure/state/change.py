from openprocurement.api.constants import RATIONALE_TYPES
from openprocurement.api.utils import raise_operation_error


class ContractChangeStateMixin:
    def validate_change_rationale_types(self, data):
        contract = self.request.validated["contract"]
        allowed_rationale_types = tuple(contract.get("contractChangeRationaleTypes", RATIONALE_TYPES).keys())
        for rationale in data.get("rationaleTypes", []):
            if rationale not in allowed_rationale_types:
                raise_operation_error(
                    self.request,
                    [f"Value must be one of {allowed_rationale_types}."],
                    name="rationaleTypes",
                    status=422,
                )
