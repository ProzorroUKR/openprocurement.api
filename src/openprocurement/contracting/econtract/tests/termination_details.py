from openprocurement.api.tests.base import snitch
from openprocurement.contracting.econtract.tests.base import BaseEContractContentWebTest
from openprocurement.contracting.econtract.tests.termination_details_blanks import (
    activate_termination_details_completed,
    activate_termination_details_disrupted_amount_exceeds_value,
    activate_termination_details_signature_invalid_cert,
    activate_termination_details_signature_invalid_type,
    activate_termination_details_signature_verified,
    activate_termination_details_without_required_fields,
    delete_termination_details_after_active_forbidden,
    delete_termination_details_buyer_only,
    delete_termination_details_draft,
    delete_termination_details_not_found,
    get_termination_details,
    get_termination_details_context,
    patch_termination_details_buyer_only,
    patch_termination_details_draft,
    patch_termination_details_pending_change_forbidden,
    upload_termination_signature_requires_buyer,
    upload_termination_signature_wrong_document_type,
)


class ContractTerminationDetailsTest(BaseEContractContentWebTest):
    initial_contract_status = "active"

    test_patch_termination_details_buyer_only = snitch(patch_termination_details_buyer_only)
    test_patch_termination_details_draft = snitch(patch_termination_details_draft)
    test_patch_termination_details_pending_change_forbidden = snitch(patch_termination_details_pending_change_forbidden)
    test_activate_termination_details_without_required_fields = snitch(
        activate_termination_details_without_required_fields
    )
    test_upload_termination_signature_requires_buyer = snitch(upload_termination_signature_requires_buyer)
    test_upload_termination_signature_wrong_document_type = snitch(upload_termination_signature_wrong_document_type)
    test_activate_termination_details_completed = snitch(activate_termination_details_completed)
    test_activate_termination_details_disrupted_amount_exceeds_value = snitch(
        activate_termination_details_disrupted_amount_exceeds_value
    )
    test_get_termination_details = snitch(get_termination_details)
    test_get_termination_details_context = snitch(get_termination_details_context)
    test_activate_termination_details_signature_verified = snitch(activate_termination_details_signature_verified)
    test_activate_termination_details_signature_invalid_type = snitch(
        activate_termination_details_signature_invalid_type
    )
    test_activate_termination_details_signature_invalid_cert = snitch(
        activate_termination_details_signature_invalid_cert
    )
    test_delete_termination_details_not_found = snitch(delete_termination_details_not_found)
    test_delete_termination_details_buyer_only = snitch(delete_termination_details_buyer_only)
    test_delete_termination_details_draft = snitch(delete_termination_details_draft)
    test_delete_termination_details_after_active_forbidden = snitch(delete_termination_details_after_active_forbidden)
