from openprocurement.api.context import get_request_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.contracting.core.procedure.utils import is_owner_by_fields


def validate_termination_details_buyer_only(request, **_):
    contract = request.validated["contract"]
    if not is_owner_by_fields(request, contract, role=AccessRole.BUYER):
        raise_operation_error(request, "Forbidden", location="url", name="permission")


def validate_termination_details_draft_status(request, **_):
    termination_details = request.validated["termination_details"]
    if termination_details.get("status") != "draft":
        raise_operation_error(
            request,
            f"Can't add document to terminationDetails in current ({termination_details.get('status')}) status",
        )


def prepare_termination_details_patch(request, **_):
    """
    terminationDetails is replaced wholesale on PATCH (like amountPaid), but
    status/dateCreated/documents are server-owned and must be carried over
    before the merged payload is validated against the full Contract model.
    status can only move draft -> active as a side effect of a verified
    signature upload (see EContractTerminationDetailsDocumentState), never
    directly via PATCH, so it is always forced back to its previous value.
    """
    if "terminationDetails" not in request.validated["json_data"]:
        return
    patch_td = request.validated["data"].setdefault("terminationDetails", {})
    before_td = request.validated["contract"].get("terminationDetails") or {}
    patch_td["status"] = before_td.get("status", "draft")
    patch_td["documents"] = before_td.get("documents", [])
    patch_td["dateCreated"] = before_td.get("dateCreated") or get_request_now().isoformat()
    if "amountPaid" not in patch_td:
        patch_td["amountPaid"] = {"amount": 0}
