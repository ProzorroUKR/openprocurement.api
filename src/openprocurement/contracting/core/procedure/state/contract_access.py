from hashlib import sha512

from openprocurement.api.auth import extract_access_token
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
        self.validate_access_claimed(contract, role)

    def set_token(self, contract, role, token):
        if role_access := get_access_fields_by_role(contract, role):
            role_access["token"] = token
        else:
            contract.setdefault("access", []).append(
                {
                    "token": token,
                    "role": role,
                }
            )

    def set_owner(self, contract, role):
        # set new owner
        role_access = get_access_fields_by_role(contract, role)
        role_access["owner"] = self.request.authenticated_userid
        new_access = []
        # delete previous tokens
        if role == AccessRole.BUYER:
            contract["owner"] = self.request.authenticated_userid
            overwritten_roles = (AccessRole.TENDER, AccessRole.CONTRACT)
            # deprecated logic fields
            contract.pop("tender_token", None)
            contract.pop("owner_token", None)
        else:
            overwritten_roles = (AccessRole.BID,)
            # deprecated logic fields
            contract.pop("bid_token", None)
            contract.pop("bid_owner", None)
        for access in contract.get("access", []):
            if access["role"] not in overwritten_roles:
                new_access.append(access)
        contract["access"] = new_access

    def validate_access_claimed(self, contract, role):
        if role_access := get_access_fields_by_role(contract, role):
            if role_access.get("owner"):
                raise_operation_error(
                    self.request,
                    "Access already claimed",
                )

    def validate_token(self, contract, role):
        acc_token = extract_access_token(self.request)
        if role_access := get_access_fields_by_role(contract, role):
            obj_token = role_access.get("token")
            if acc_token and obj_token and len(obj_token) != len(acc_token):
                acc_token = sha512(acc_token.encode("utf-8")).hexdigest()
            if acc_token != obj_token:
                raise_operation_error(
                    self.request,
                    "Token mismatch",
                )

    def validate_on_patch(self, contract, role):
        self.validate_role(role)
        self.validate_token(contract, role)
        self.validate_access_claimed(contract, role)
