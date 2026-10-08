from cornice.resource import resource
from pyramid.security import Allow, Everyone

from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.limited.procedure.state.award import (
    NegotiationAwardState,
    NegotiationQuickAwardState,
    ReportingAwardState,
)


@resource(
    name="reporting:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="reporting",
)
class ReportingAwardResource(TenderAwardResource):
    state_class = ReportingAwardState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_award"),
            (Allow, "g:brokers", "edit_award"),
            (Allow, "g:brokers", "upload_award_documents"),
            (Allow, "g:brokers", "edit_award_documents"),
            (Allow, "g:admins", "create_award"),
            (Allow, "g:admins", "edit_award"),
            (Allow, "g:admins", "upload_award_documents"),
            (Allow, "g:admins", "edit_award_documents"),
            (Allow, "g:bots", "upload_award_documents"),
        ]
        return acl


@resource(
    name="negotiation:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="negotiation",
)
class NegotiationAwardResource(TenderAwardResource):
    state_class = NegotiationAwardState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_award"),
            (Allow, "g:brokers", "edit_award"),
            (Allow, "g:brokers", "upload_award_documents"),
            (Allow, "g:brokers", "edit_award_documents"),
            (Allow, "g:admins", "create_award"),
            (Allow, "g:admins", "edit_award"),
            (Allow, "g:admins", "upload_award_documents"),
            (Allow, "g:admins", "edit_award_documents"),
            (Allow, "g:bots", "upload_award_documents"),
        ]
        return acl


@resource(
    name="negotiation.quick:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="negotiation.quick",
)
class NegotiationQuickAwardResource(NegotiationAwardResource):
    state_class = NegotiationQuickAwardState
