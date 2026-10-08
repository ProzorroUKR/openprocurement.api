from hashlib import sha512

from openprocurement.api.auth import extract_access_token
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.tender import TenderState


class CDStage2CredentialsState(TenderState):
    def validate_tender_credentials_patch_request(self):
        self.validate_dialogue_owner()

    def validate_dialogue_owner(self):
        """The stage 1 (dialogue) owner token gives the credentials of the stage 2 tender"""
        tender = get_tender()
        acc_token = extract_access_token(self.request)
        acc_token_hex = sha512(acc_token.encode("utf-8")).hexdigest()
        if self.request.authenticated_userid != tender["owner"] or acc_token_hex != tender["dialogue_token"]:
            raise_operation_error(self.request, "Forbidden", location="url", name="permission")
