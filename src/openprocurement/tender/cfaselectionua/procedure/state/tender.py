from openprocurement.tender.core.procedure.state.tender import TenderState


class CFASelectionTenderState(TenderState):
    generate_award_milestones = False
    tender_lots_awarding_events = False
    tender_value_from_lots_without_tender_value = True
