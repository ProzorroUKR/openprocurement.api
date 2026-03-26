from openprocurement.tender.core.procedure.state.qualification_milestone import QualificationMilestoneState


class RequestForProposalQualificationMilestoneState(QualificationMilestoneState):
    def get_24h_milestone_dueDate(self, milestone):
        # if user selected dueDate > 24h, then accept it. Else set dueDate at 24h
        min_dueDate = super().get_24h_milestone_dueDate(milestone)
        milestone_dueDate = milestone.get("dueDate", min_dueDate)
        return max(min_dueDate, milestone_dueDate)
