from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.tender.pricequotation.procedure.state.tender import PriceQuotationTenderState
from openprocurement.tender.pricequotation.constants import DEFAULT_TEMPLATE_KEY
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.api.constants import PQ_NEW_CONTRACTING_FROM, CONTRACT_TEMPLATES_KEYS
from openprocurement.api.context import get_now
from openprocurement.api.utils import raise_operation_error


class TenderDetailsState(TenderDetailsMixing, PriceQuotationTenderState):

    def on_post(self, tender):
        EXCLUDED_TEMPLATE_CLASSIFICATION = ("09310000-5",)

        super().on_post(tender)
        if tender_created_after(PQ_NEW_CONTRACTING_FROM):
            classification_id = tender.get("classification", dict()).get("id")
            template_name = None
            if classification_id and classification_id not in EXCLUDED_TEMPLATE_CLASSIFICATION:
                for key in CONTRACT_TEMPLATES_KEYS:
                    if key.startswith(classification_id):
                        template_name = key
                        break
                    elif key.startswith(DEFAULT_TEMPLATE_KEY):
                        template_name = key

            if template_name:
                tender["contractTemplateName"] = template_name

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
