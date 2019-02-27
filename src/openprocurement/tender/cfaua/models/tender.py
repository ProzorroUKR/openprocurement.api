
from datetime import timedelta
from iso8601 import parse_date
from openprocurement.api.roles import RolesFromCsv
from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist, whitelist
from schematics.types import IntType, URLType, BooleanType, BaseType
from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from zope.interface import implementer, provider
from openprocurement.api.models import (
    listing_role, Period, ListType, SifterListType, plain_role, IsoDurationType
)
from openprocurement.api.utils import get_now
from openprocurement.api.validation import (
    validate_cpv_group, validate_items_uniq,
    validate_classification_id)
from openprocurement.tender.cfaua.validation import validate_max_awards_number, validate_max_agreement_duration_period
from openprocurement.tender.cfaua.interfaces import (
    ICloseFrameworkAgreementUA
)
from openprocurement.tender.cfaua.models.submodels.agreement import Agreement
from openprocurement.tender.cfaua.models.submodels.award import Award
from openprocurement.tender.cfaua.models.submodels.bids import BidModelType, Bid
from openprocurement.tender.cfaua.models.submodels.cancellation import Cancellation
from openprocurement.tender.cfaua.models.submodels.complaint import ComplaintModelType, Complaint
from openprocurement.tender.cfaua.models.submodels.documents import EUDocument
from openprocurement.tender.cfaua.models.submodels.item import Item
from openprocurement.tender.cfaua.models.submodels.guarantee import Guarantee
from openprocurement.tender.cfaua.models.submodels.feature import Feature
from openprocurement.tender.cfaua.models.submodels.lot import Lot
from openprocurement.tender.cfaua.models.submodels.organization import ProcuringEntity
from openprocurement.tender.cfaua.models.submodels.periods import TenderAuctionPeriod, ContractPeriod
from openprocurement.tender.cfaua.models.submodels.qualification import Qualification
from openprocurement.tender.cfaua.models.submodels.value import Value

from openprocurement.tender.core.models import (
    EnquiryPeriod,
    PeriodStartEndRequired,
    create_role, edit_role, view_role,
    auction_view_role, auction_post_role, auction_patch_role, enquiries_role,
    auction_role, chronograph_role, chronograph_view_role, Administrator_role, schematics_default_role,
    schematics_embedded_role, validate_lots_uniq
)
from openprocurement.tender.core.models import validate_features_uniq, Question, Tender
from openprocurement.tender.core.utils import (
    calculate_business_date,
    calc_auction_end_time,
    has_unanswered_questions,
    has_unanswered_complaints,
)
from openprocurement.tender.openua.constants import AUCTION_PERIOD_TIME


eu_role = blacklist('enquiryPeriod', 'qualifications')
edit_role_eu = edit_role + eu_role
create_role_eu = create_role + eu_role
pre_qualifications_role = (blacklist('owner_token', '_attachments', 'revisions') + schematics_embedded_role)
eu_auction_role = auction_role


@implementer(ICloseFrameworkAgreementUA)
@provider(ICloseFrameworkAgreementUA)
class CloseFrameworkAgreementUA(Tender):
    """ OpenEU tender model """
    class Options:
        namespace = 'Tender'
        roles = RolesFromCsv('CloseFrameworkAgreementUA.csv', relative_to=__file__)

    create_accreditation = 3
    edit_accreditation = 4
    procuring_entity_kinds = ['general', 'special', 'defense']
    block_tender_complaint_status = ['claim', 'pending', 'accepted', 'satisfied', 'stopping']
    block_complaint_status = ['pending', 'accepted', 'satisfied', 'stopping']
    auctionPeriod = ModelType(TenderAuctionPeriod, default={})
    auctionUrl = URLType()
    awards = ListType(ModelType(Award), default=list())
    awardPeriod = ModelType(Period)  # The dat e or period on which an award is anticipated to be made.
    bids = SifterListType(BidModelType(Bid), default=list(), filter_by='status', filter_in_values=['invalid', 'invalid.pre-qualification', 'deleted'])  # A list of all the companies who entered submissions for the tender.
    cancellations = ListType(ModelType(Cancellation), default=list())
    complaints = ListType(ComplaintModelType(Complaint), default=list())
    contractPeriod = ModelType(ContractPeriod, required=False)
    agreements = ListType(ModelType(Agreement), default=list())
    documents = ListType(ModelType(EUDocument), default=list())  # All documents and attachments related to the tender.
    enquiryPeriod = ModelType(EnquiryPeriod, required=False)
    guarantee = ModelType(Guarantee)
    hasEnquiries = BooleanType()  # A Yes/No field as to whether enquiries were part of tender process.
    items = ListType(ModelType(Item), required=True, min_size=1,
                     validators=[validate_cpv_group, validate_items_uniq, validate_classification_id])  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    features = ListType(ModelType(Feature), validators=[validate_features_uniq])
    minimalStep = ModelType(Value, required=True)
    numberOfBidders = IntType()  # The number of unique tenderers who participated in the tender
    maxAwardsCount = IntType(required=True, validators=[validate_max_awards_number])
    lots = ListType(ModelType(Lot), min_size=1, max_size=1, default=list(), validators=[validate_lots_uniq])
    procurementMethodType = StringType(default="closeFrameworkAgreementUA")
    procuringEntity = ModelType(ProcuringEntity, required=True)  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    qualificationPeriod = ModelType(Period)
    qualifications = ListType(ModelType(Qualification), default=list())
    questions = ListType(ModelType(Question), default=list())
    status = StringType(choices=['draft', 'active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still', 'active.auction', 'active.qualification', 'active.qualification.stand-still', 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)
    title_en = StringType(required=True, min_length=1)
    value = ModelType(Value, required=True)  # The total estimated value of the procurement.
    agreementDuration = IsoDurationType(required=True, validators=[validate_max_agreement_duration_period])

    def __local_roles__(self):
        roles = dict([('{}_{}'.format(self.owner, self.owner_token), 'tender_owner')])
        for i in self.bids:
            roles['{}_{}'.format(i.owner, i.owner_token)] = 'bid_owner'
        return roles

    def __acl__(self):
        acl = [
            (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_qualification_complaint')
            for i in self.bids
            if i.status in ['active', 'unsuccessful', 'invalid.pre-qualification']
        ]
        acl.extend([
            (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_award_complaint')
            for i in self.bids
            if i.status == 'active'
        ])
        acl.extend([
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_tender'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_tender_documents'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_complaint'),
        ])
        return acl

    def check_auction_time(self):
        if self.auctionPeriod and self.auctionPeriod.startDate and self.auctionPeriod.shouldStartAfter \
                and self.auctionPeriod.startDate > calculate_business_date(parse_date(self.auctionPeriod.shouldStartAfter), AUCTION_PERIOD_TIME, self, True):
            self.auctionPeriod.startDate = None
        for lot in self.lots:
            if lot.auctionPeriod and lot.auctionPeriod.startDate and lot.auctionPeriod.shouldStartAfter \
                    and lot.auctionPeriod.startDate > calculate_business_date(parse_date(lot.auctionPeriod.shouldStartAfter), AUCTION_PERIOD_TIME, self, True):
                lot.auctionPeriod.startDate = None

    def invalidate_bids_data(self):
        self.check_auction_time()
        self.enquiryPeriod.invalidationDate = get_now()
        for bid in self.bids:
            if bid.status not in ["deleted", "draft"]:
                bid.status = "invalid"


