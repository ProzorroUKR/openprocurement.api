from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.tender.pricequotation.procedure.state.tender import PriceQuotationTenderState
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.context import get_now
from openprocurement.api.utils import raise_operation_error


class TenderDetailsState(TenderDetailsMixing, PriceQuotationTenderState):

    def on_patch(self, before, after):
        super().on_patch(before, after)

        tendering_start = before.get("tenderPeriod", {}).get("startDate")
        if "draft" not in before["status"]:
            if tendering_start != after.get("tenderPeriod", {}).get("startDate"):
                raise_operation_error(
                    get_request(),
                    "Can't change tenderPeriod.startDate",
                    status=422,
                    location="body",
                    name="tenderPeriod.startDate"
                )

    def status_up(self, before, after, data):
        super().status_up(before, after, data)

        if before == "draft" and after == "draft.publishing":
            if not data.get("noticePublicationDate"):
                data["noticePublicationDate"] = get_now().isoformat()
            data["tenderPeriod"]["startDate"] = get_now().isoformat()

        if before == "draft.unsuccessful" and after != before:
            raise_operation_error(
                get_request(),
                f"Can't change status from {before} to {after}",
            )
