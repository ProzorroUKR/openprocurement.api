from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.contracting.core.procedure.utils import get_access_fields_by_role


class ContractAccessState(BaseState):
    def get_role(self, data, contract):
        def get_identifier(entity):
            try:
                return f"{entity['identifier']['scheme']}-{entity['identifier']['id']}"
            except (TypeError, KeyError):
                return ""

        author = get_identifier(data)
        buyer = get_identifier(contract.get("buyer"))
        supplier = get_identifier(contract.get("suppliers", [{}])[0])

        if author == buyer:
            return AccessRole.BUYER
        elif author == supplier:
            return AccessRole.SUPPLIER

    def validate_role(self, role):
        if not role:
            raise_operation_error(
                self.request,
                "Invalid identifier",
            )

    def validate_on_post(self, contract, role):
        self.validate_role(role)
        self.validate_access_generation_forbidden(contract, role)
        self.validate_access_claimed(contract, role)
        self.validate_owner(contract, role)

    @staticmethod
    def set_token(contract, role, token):
        if role_access := get_access_fields_by_role(contract, role):
            role_access["token"] = token
        else:
            contract.setdefault("access", []).append(
                {
                    "token": token,
                    "role": role,
                }
            )

    def validate_access_generation_forbidden(self, contract, role):
        if not get_access_fields_by_role(contract, role):
            raise_operation_error(
                self.request,
                "Forbidden to generate access as contract doesn't have owner for this role",
            )

    def validate_owner(self, contract, role):
        role_access = get_access_fields_by_role(contract, role)
        if role_access["owner"] != self.request.authenticated_userid:
            raise_operation_error(
                self.request,
                "Owner mismatch",
            )

    def validate_access_claimed(self, contract, role):
        if role_access := get_access_fields_by_role(contract, role):
            if role_access.get("token"):
                raise_operation_error(
                    self.request,
                    "Access already claimed",
                )
