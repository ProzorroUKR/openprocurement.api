from openprocurement.tender.openuadefense.procedure.state.tender import (
    OpenUADefenseTenderState,
)


class SimpleDefenseTenderState(OpenUADefenseTenderState):
    generate_award_milestones = False
