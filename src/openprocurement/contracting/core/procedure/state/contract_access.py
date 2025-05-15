from hashlib import sha512

from openprocurement.api.auth import extract_access_token
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import raise_operation_error


class ContractAccessState(BaseState):

    def get_role(self, data, contract):
        def get_identifier(entity):
            try:
                return f"{entity['identifier']['scheme']}-{entity['identifier']['id']}"
            except (TypeError, KeyError):
                return ""

        author = get_identifier(data)
        buyer = get_identifier(contract.get("buyer"))
        supplier = get_identifier(contract.get("suppliers", [{}])[0] if contract.get("suppliers") else {})

        if author == buyer:
            return "buyer"
        elif author == supplier:
            return "supplier"

    def validate_on_post(self, contract, role):
        if not role:
            raise_operation_error(
                self.request,
                "Invalid identifier",
            )
        self.validate_access_claimed(contract, role)

    def set_token(self, contract, role, token):
        contract.setdefault("access", {}).setdefault(role, {})["token"] = token

    def set_owner(self, contract, role):
        contract.setdefault("access", {}).setdefault(role, {})["owner"] = self.request.authenticated_userid
        if role == "buyer":
            contract["owner"] = self.request.authenticated_userid
            contract.pop("tender_token", None)
            contract.pop("owner_token", None)
        else:
            contract.pop("bid_token", None)
            contract.pop("bid_owner", None)

    def validate_access_claimed(self, contract, role):
        if contract.get("access", {}).get(role, {}).get("owner"):
            raise_operation_error(
                self.request,
                "Access already claimed",
            )

    def validate_token(self, contract, role):
        acc_token = extract_access_token(self.request)
        obj_token = contract.get("access", {}).get(role, {}).get("token")
        if acc_token and obj_token and len(obj_token) != len(acc_token):
            acc_token = sha512(acc_token.encode("utf-8")).hexdigest()
        if acc_token != obj_token:
            raise_operation_error(
                self.request,
                "Token mismatch",
            )

    def validate_on_patch(self, contract, role):
        self.validate_token(contract, role)
        self.validate_access_claimed(contract, role)
