from openprocurement.api.validation import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.openeu.procedure.state.tender_details import OpenEUTenderDetailsMixing
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import Stage1TenderState


class TenderDetailsState(OpenEUTenderDetailsMixing, Stage1TenderState):

    def on_patch(self, before, after):
        if get_request().authenticated_role != "competitive_dialogue":
            if before["status"] == "active.stage2.waiting":
                raise_operation_error(get_request(), "Can't update tender in (active.stage2.waiting) status")

            if after["status"] == "complete":
                raise_operation_error(get_request(), "Can't update tender to (complete) status")

        super().on_patch(before, after)

