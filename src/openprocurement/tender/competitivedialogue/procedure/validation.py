from openprocurement.tender.competitivedialogue.utils import (
    prepare_shortlistedFirms,
    prepare_bid_identifier,
)
from openprocurement.api.utils import raise_operation_error


def validate_firm_to_create_bid(request, **_):
    tender = request.validated["tender"]
    bid = request.validated["data"]
    firm_keys = prepare_shortlistedFirms(tender.get("shortlistedFirms") or "")
    bid_keys = prepare_bid_identifier(bid)
    if not (bid_keys <= firm_keys):
        raise_operation_error(request, "Firm can't create bid")


def unless_cd_bridge(*validations):
    def decorated(request, **_):
        if request.authenticated_role != "competitive_dialogue":
            for validation in validations:
                validation(request)
    return decorated


def validate_cd2_allowed_patch_fields(request, **_):
    changes = request.validated["data"]
    tender = request.validated["tender"]

    status = tender["status"]
    if status in ("draft.stage2", "active.tendering"):
        tender_whitelist = {"tenderPeriod", "complaintPeriod", "items"}
        if status == "draft.stage2":
            tender_whitelist.add("mainProcurementCategory")
            tender_whitelist.add("status")

        for f in changes:
            if f not in tender_whitelist and tender.get(f) != changes[f]:
                return raise_operation_error(
                    request,
                    "Field change's not allowed",
                    location="body",
                    name=f,
                    status=422
                )

        items = changes.get("items")
        if items:
            before_items = tender["items"]
            if len(items) != len(before_items):
                return raise_operation_error(
                    request,
                    "List size change's not allowed",
                    location="body",
                    name="items"
                )

            item_whitelist = {"deliveryDate"}
            for a, b in zip(items, before_items):
                for f in a:
                    if f not in item_whitelist and a[f] != b[f]:
                        return raise_operation_error(
                            request,
                            "Field change's not allowed",
                            location="body",
                            name=f"items.{f}",
                            status=422
                        )
