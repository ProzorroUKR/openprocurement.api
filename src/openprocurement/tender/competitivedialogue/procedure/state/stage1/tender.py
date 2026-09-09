from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState


class CDStage1TenderState(BaseOpenEUTenderState):
    pre_qualification_stand_still_next_status = "active.stage2.pending"
