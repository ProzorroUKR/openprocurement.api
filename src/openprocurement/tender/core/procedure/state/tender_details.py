from openprocurement.tender.core.procedure.context import get_request, get_now
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.api.utils import raise_operation_error
from datetime import timedelta


class TenderDetailsMixing:
    """
    describes business logic rules for tender owners
    when they prepare tender for tendering stage
    """
    def on_post(self, tender):
        self.watch_value_meta_changes(tender)
        self.update_date(tender)
        super().on_post(tender)

    def on_patch(self, before, after):
        if before["status"] not in ("draft", "draft.stage2"):
            if before["procuringEntity"]["kind"] != after["procuringEntity"]["kind"]:
                raise_operation_error(
                    get_request(),
                    "Can't change procuringEntity.kind in a public tender",
                    status=422,
                    location="body",
                    name="procuringEntity"
                )

            tendering_start = before.get("tenderPeriod", {}).get("startDate")
            if tendering_start != after.get("tenderPeriod", {}).get("startDate"):
                raise_operation_error(
                    get_request(),
                    "Can't change tenderPeriod.startDate",
                    status=422,
                    location="body",
                    name="tenderPeriod.startDate"
                )

        self.watch_value_meta_changes(after)
        super().on_patch(before, after)

    def status_up(self, before, after, data):
        if after == "draft" and before != "draft":
            raise_operation_error(
                get_request(),
                "Can't change status to draft",
                status=422,
                location="body",
                name="status"
            )
        elif after == "active.tendering" and before != "active.tendering":
            tendering_start = data["tenderPeriod"]["startDate"]
            if dt_from_iso(tendering_start) <= get_now() - timedelta(minutes=10):
                raise_operation_error(
                    get_request(),
                    "tenderPeriod.startDate should be in greater than current date",
                    status=422,
                    location="body",
                    name="tenderPeriod.startDate"
                )
        super().status_up(before, after, data)

    @staticmethod
    def update_date(tender):
        now = get_now().isoformat()
        tender["date"] = now

        for lot in tender.get("lots", ""):
            lot["date"] = now

    @staticmethod
    def watch_value_meta_changes(tender):
        # tender currency and valueAddedTaxIncluded must be specified only ONCE
        # instead it's specified in many places but we need keep them the same
        currency = tender["value"]["currency"]
        tax_inc = tender["value"]["valueAddedTaxIncluded"]
        for item in tender["items"]:
            if "unit" in item and "value" in item["unit"]:
                item["unit"]["value"]["currency"] = currency
                item["unit"]["value"]["valueAddedTaxIncluded"] = tax_inc
