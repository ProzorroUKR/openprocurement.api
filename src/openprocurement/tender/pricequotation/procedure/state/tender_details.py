from openprocurement.api.auth import ACCR_1, ACCR_2, ACCR_5
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.tender.pricequotation.procedure.state.tender import PriceQuotationTenderState
from openprocurement.tender.pricequotation.constants import DEFAULT_TEMPLATE_KEY
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.api.constants import PQ_NEW_CONTRACTING_FROM, CONTRACT_TEMPLATES_KEYS
from openprocurement.api.context import get_now
from openprocurement.api.utils import raise_operation_error


class TenderDetailsState(TenderDetailsMixing, PriceQuotationTenderState):
    tender_create_accreditations = (ACCR_1, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_2,)

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

        if after == "active.tendering" and after != before:
            self.set_contract_template_name(data)

        if after in self.unsuccessful_statuses:
            self.set_contracts_cancelled(after)

    def set_contract_template_name(self, data):
        EXCLUDED_TEMPLATE_CLASSIFICATION = ("0931",)

        if not tender_created_after(PQ_NEW_CONTRACTING_FROM):
            return

        items = data.get("items")
        if not items or any(i.get("documentType", "") == "contractProforma" for i in data.get("documents", "")):
            return

        classification_id = items[0].get("classification", dict()).get("id")
        template_name = None
        if not classification_id:
            return

        classification_id = classification_id[:4] if classification_id[:3] != "336" else "336"
        if classification_id not in EXCLUDED_TEMPLATE_CLASSIFICATION:
            for key in CONTRACT_TEMPLATES_KEYS:
                if key.startswith(classification_id):
                    template_name = key
                    break
                elif key.startswith(DEFAULT_TEMPLATE_KEY):
                    template_name = key

        if template_name:
            data["contractTemplateName"] = template_name
