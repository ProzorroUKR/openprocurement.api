from copy import deepcopy

import requests

from openprocurement.api.constants_env import SIGNATURE_VERIFICATION_ENABLED
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.serializers.document import download_url_serialize
from openprocurement.api.utils import raise_operation_error, verify_signature
from openprocurement.contracting.core.procedure.state.document import (
    ContractDocumentState as BaseContractDocumentState,
)


class EContractDocumentState(BaseContractDocumentState):
    def validate_document_post(self, data):
        super().validate_document_post(data)
        if data.get("documentType") == "contractSignature":
            self.validate_contract_cancellations()
            self.validate_contract_is_ready_for_signing()
            self.set_author_of_object(data)
            self.validate_contract_signature_duplicate(data)
            self.validate_contract_signature(data)
        else:
            raise_operation_error(
                self.request,
                "Only contractSignature documentType is allowed",
            )

    def document_on_post(self, data):
        super().document_on_post(data)
        self.activate_contract_if_signed(data)

    def validate_contract_cancellations(self):
        contract = self.request.validated["contract"]
        if contract.get("cancellations", []):
            raise_operation_error(
                self.request,
                "Forbidden to sign contract with cancellation",
            )

    def validate_contract_is_ready_for_signing(self):
        tender = self.request.validated["tender"]
        contract = self.request.validated["contract"]
        contract["id"] = contract["_id"]
        contract_after = deepcopy(contract)
        self.set_object_status(contract_after, "active")

        self.validate_required_signed_info(contract)
        self.validate_contract_pending_patch(self.request, contract, contract_after)
        self.validate_contract_active_patch(self.request, contract, contract_after)
        self.validate_activate_contract(contract)
        self.validate_activate_contract_with_review_request(
            self.request,
            tender,
            contract_after,
            self.request.validated["award"].get("lotID"),
        )

    def activate_contract_if_signed(self, doc):
        contract = self.request.validated["contract"]

        docs = deepcopy(contract.get("documents", []))
        docs.append(doc)

        suppliers_count = len(contract.get("suppliers", []))
        participants_count = suppliers_count + 1  # all suppliers + buyer signature
        signs_count = len([doc for doc in docs if doc.get("documentType") == "contractSignature"])
        if signs_count == participants_count:
            self.set_object_status(contract, "active")
            contract_changed = self.synchronize_contracts_data(contract)
            if contract.get("dateSigned", None) is None:
                contract["dateSigned"] = get_request_now().isoformat()
            self.check_tender_status_method()
            self.request.validated["contract_was_changed"] = contract_changed

    def validate_contract_signature_duplicate(self, doc_data):
        contract_docs = deepcopy(self.request.validated["contract"].get("documents", []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            contract_docs.extend(new_documents)
        else:  # PATCH/PUT
            contract_docs.append(doc_data)
        for prev_doc in contract_docs:
            if (
                prev_doc.get("documentType") == "contractSignature"
                and prev_doc["author"] == doc_data["author"]
                and prev_doc["id"] != doc_data["id"]
            ):
                raise_operation_error(
                    self.request,
                    f"Contract signature for {doc_data['author']} already exists",
                    location="body",
                    name="documentType",
                )

    def validate_contract_signature(self, doc_data):
        if not SIGNATURE_VERIFICATION_ENABLED:
            return
        # Get signature file from ds
        doc_url = download_url_serialize(doc_data.get("url"), doc_data)
        response = requests.get(doc_url)
        response.raise_for_status()
        signature = response.content
        # Get pdf file from ds
        pdf = None
        contract = self.request.validated["contract"]
        for doc in contract.get("documents", []):
            if doc.get("documentType") == "contractNotice":
                pdf_url = download_url_serialize(doc.get("url"), doc)
                response = requests.get(pdf_url)
                response.raise_for_status()
                pdf = response.content
                break
        if not pdf:
            raise_operation_error(
                self.request,
                "Contract pdf not found",
                location="body",
                name="documents",
            )
        # Verify signature
        verify_data = verify_signature(self.request, pdf, signature)
        self.validate_contract_signature_type(verify_data)
        self.validate_contract_signature_cert(verify_data)

    def validate_contract_signature_type(self, verify_data):
        sign_info = verify_data.get("sign_info", {})
        sign_type = sign_info.get("pdwSignType")

        if sign_type is None:
            raise_operation_error(
                self.request,
                "Can't validate signature type",
            )

        # It seams each signature type is a bitmask of the following types:
        #
        # 1   == 0b00000001  # CAdES-BES
        # 4   == 0b00000100  # CAdES-T
        # 8   == 0b00001000  # CAdES-C
        # 16  == 0b00010000  # CAdES-X Long
        # 128 == 0b10000000  # CAdES-X Long Trusted
        #
        # We need
        #  - CAdES-X Long
        #  - CAdES-X Long + CAdES-X Long Trusted
        #
        # But CAdES-X Long Trusted is modifier and signature will still be CAdES-X Long
        # So to check if the signature type is CAdES-X Long or CAdES-X Long + CAdES-X Long Trusted
        # we need to check if the signature type has CAdES-X Long bit set

        EU_SIGN_TYPE_CADES_X_LONG = 16

        if not bool(sign_type & EU_SIGN_TYPE_CADES_X_LONG):
            raise_operation_error(
                self.request,
                f"Invalid signature type {sign_type}, expected CAdES-X Long",
            )

    def validate_contract_signature_cert(self, verify_data):
        certs_info = verify_data.get("cert_info", {})
        cert_key_type = certs_info.get("dwPublicKeyType")
        if not cert_key_type:
            raise_operation_error(
                self.request,
                "Can't validate certificate",
            )

        EU_CERT_KEY_TYPE_DSTU4145 = 1

        if cert_key_type != EU_CERT_KEY_TYPE_DSTU4145:
            raise_operation_error(
                self.request,
                "Invalid certificate key type, expected ДСТУ-4145",
            )
