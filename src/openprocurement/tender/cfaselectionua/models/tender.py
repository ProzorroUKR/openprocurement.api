# -*- coding: utf-8 -*-
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.cfaselectionua.interfaces import ICFASelectionUATender
from openprocurement.tender.cfaselectionua.models.submodels.agreement import Agreement
from openprocurement.tender.cfaselectionua.models.submodels.award import Award
from openprocurement.tender.cfaselectionua.models.submodels.bid import Bid
from openprocurement.tender.cfaselectionua.models.submodels.contract import Contract
from openprocurement.tender.cfaselectionua.models.submodels.feature import Feature
from openprocurement.tender.cfaselectionua.models.submodels.item import Item
from openprocurement.tender.cfaselectionua.models.submodels.lot import Lot
from openprocurement.tender.cfaselectionua.models.submodels.organizationAndPocuringEntity import ProcuringEntity
from schematics.types import StringType, IntType, URLType, BooleanType
from schematics.types.compound import ModelType
from zope.interface import implementer, provider
from pyramid.security import Allow
from openprocurement.api.models import ListType, Period, Value
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.models import (
    validate_lots_uniq,
    Guarantee, TenderAuctionPeriod,
    PeriodEndRequired, Tender as BaseTender,
    Cancellation,
    validate_features_uniq
)


@implementer(ICFASelectionUATender)
@provider(ICFASelectionUATender)
class CFASelectionUATender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors
    to submit bids for evaluation and selecting a winner or winners.
    """
    class Options:
        namespace = 'Tender'
        roles = RolesFromCsv('Tender.csv', relative_to=__file__)

    items = ListType(ModelType(Item), min_size=1, validators=[validate_items_uniq])  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    value = ModelType(Value)  # The total estimated value of the procurement.
    enquiryPeriod = ModelType(PeriodEndRequired, required=False)  # The period during which enquiries may be made and will be answered.
    tenderPeriod = ModelType(PeriodEndRequired, required=False)  # The period when the tender is open for submissions. The end date is the closing date for tender submissions.
    hasEnquiries = BooleanType()  # A Yes/No field as to whether enquiries were part of tender process.
    awardPeriod = ModelType(Period)  # The date or period on which an award is anticipated to be made.
    numberOfBidders = IntType()  # The number of unique tenderers who participated in the tender
    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the tender.
    procuringEntity = ModelType(ProcuringEntity, required=True)  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    awards = ListType(ModelType(Award), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    auctionPeriod = ModelType(TenderAuctionPeriod, default={})
    minimalStep = ModelType(Value, required=False)
    auctionUrl = URLType()
    cancellations = ListType(ModelType(Cancellation), default=list())
    features = ListType(ModelType(Feature), validators=[validate_features_uniq])
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq], min_size=1, max_size=1)
    guarantee = ModelType(Guarantee)
    status = StringType(choices=['draft', 'draft.pending', 'draft.unsuccessful', 'active.enquiries', 'active.tendering',
                                 'active.auction', 'active.qualification', 'active.awarded', 'complete',
                                 'cancelled', 'unsuccessful'], default='draft')  # TODO Refactoring status
    agreements = ListType(ModelType(Agreement), default=list(), min_size=1, max_size=1)

    procurementMethod = StringType(choices=['open', 'selective', 'limited'], default='selective')
    procurementMethodType = StringType(default="closeFrameworkAgreementSelectionUA")
    unsuccessfulReason = ListType(StringType, serialize_when_none=False)
    procuring_entity_kinds = ['general', 'special', 'defense', 'other']

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == 'Administrator':
            role = 'Administrator'
        elif request.authenticated_role == 'chronograph':
            role = 'chronograph'
        elif request.authenticated_role == 'auction':
            role = 'auction_{}'.format(request.method.lower())
        elif request.authenticated_role == 'contracting':
            role = 'contracting'
        elif request.authenticated_role == 'agreement_selection':
            role = 'edit_{}'.format(request.authenticated_role)
        else:
            role = 'edit_{}'.format(request.context.status)
        return role

    def __acl__(self):
        acl = [
            (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_award_complaint')
            for i in self.bids
        ]
        acl.extend([
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_tender'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_tender_documents'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_complaint'),
            (Allow, 'g:agreement_selection', 'edit_agreement_selection'),
            (Allow, 'g:agreement_selection', 'edit_tender'),
        ])
        return acl

    def __local_roles__(self):
        roles = dict([('{}_{}'.format(self.owner, self.owner_token), 'tender_owner')])
        for i in self.bids:
            roles['{}_{}'.format(i.owner, i.owner_token)] = 'bid_owner'
        return roles
