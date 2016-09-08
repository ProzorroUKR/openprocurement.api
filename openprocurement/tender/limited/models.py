from uuid import uuid4
from zope.interface import implementer
from pyramid.security import Allow
from schematics.transforms import whitelist, blacklist
from schematics.types import StringType, BaseType, MD5Type, BooleanType
from schematics.types.compound import ModelType, ListType, DictType
from schematics.types.serializable import serializable
from schematics.exceptions import ValidationError
from openprocurement.api.models import (
    plain_role, view_role, create_role, edit_role, enquiries_role, listing_role,
    Administrator_role, schematics_default_role, schematics_embedded_role,
    chronograph_role, chronograph_view_role, draft_role, SANDBOX_MODE,
    embedded_lot_role, ListType, default_lot_role, validate_lots_uniq,
)
from openprocurement.api.models import (
    Value, IsoDateTimeType, Document, Organization, SchematicsDocument,
    Model, Revision, Period, view_bid_role,
)
from openprocurement.api.models import validate_cpv_group, validate_items_uniq
from openprocurement.api.models import get_now
from openprocurement.api.models import Cancellation as BaseCancellation
from openprocurement.api.models import ITender
from openprocurement.api.models import Contract as BaseContract
from openprocurement.api.models import ProcuringEntity as BaseProcuringEntity
from openprocurement.tender.openua.models import Complaint as BaseComplaint
from openprocurement.tender.openua.models import Item
from openprocurement.tender.openua.models import Tender as OpenUATender


class Complaint(BaseComplaint):
    class Options:
        roles = {
            'active': view_bid_role,
        }


class Contract(BaseContract):
    items = ListType(ModelType(Item))

    def validate_dateSigned(self, data, value):
        if value and value > get_now():
            raise ValidationError(u"Contract signature date can't be in the future")


award_edit_role = blacklist('id', 'date', 'documents', 'complaints', 'complaintPeriod')
award_create_role = blacklist('id', 'status', 'date', 'documents', 'complaints', 'complaintPeriod')
award_create_reporting_role = award_create_role + blacklist('qualified')
award_edit_reporting_role = award_edit_role + blacklist('qualified')


class Award(Model):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """
    class Options:
        roles = {
            'create': award_create_reporting_role,
            'edit': award_edit_reporting_role,
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
            'Administrator': whitelist('complaintPeriod'),
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType()  # Award title
    title_en = StringType()
    title_ru = StringType()
    subcontractingDetails = StringType()
    qualified = BooleanType()
    description = StringType()  # Award description
    description_en = StringType()
    description_ru = StringType()
    status = StringType(required=True, choices=['pending', 'unsuccessful', 'active', 'cancelled'], default='pending')
    date = IsoDateTimeType(default=get_now)
    value = ModelType(Value)
    suppliers = ListType(ModelType(Organization), required=True, min_size=1, max_size=1)
    items = ListType(ModelType(Item))
    documents = ListType(ModelType(Document), default=list())
    complaints = ListType(ModelType(Complaint), default=list())
    complaintPeriod = ModelType(Period)

ReportingAward = Award


class Cancellation(BaseCancellation):
    class Options:
        roles = {
            'create': whitelist('reason', 'status', 'reasonType', 'cancellationOf', 'relatedLot'),
            'edit': whitelist('status', 'reasonType'),
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }

    cancellationOf = StringType(required=True, choices=['tender'], default='tender')
    reasonType = StringType(choices=['cancelled', 'unsuccessful'], default='cancelled')

    def validate_relatedLot(self, data, relatedLot):
        return


class ProcuringEntity(BaseProcuringEntity):
    class Options:
        roles = {
            'edit_active': schematics_default_role + blacklist("kind"),
        }


@implementer(ITender)
class Tender(SchematicsDocument, Model):
    """Data regarding tender process - publicly inviting prospective contractors
       to submit bids for evaluation and selecting a winner or winners.
    """

    class Options:
        roles = {
            'plain': plain_role,
            'create': create_role,
            'edit': edit_role,
            'edit_draft': draft_role,
            'edit_active': edit_role,
            'edit_active.awarded': whitelist(),
            'edit_complete': whitelist(),
            'edit_unsuccessful': whitelist(),
            'edit_cancelled': whitelist(),
            'view': view_role,
            'listing': listing_role,
            'draft': enquiries_role,
            'active': enquiries_role,
            'active.awarded': view_role,
            'complete': view_role,
            'unsuccessful': view_role,
            'cancelled': view_role,
            'Administrator': Administrator_role,
            'chronograph': chronograph_role,  # remove after chronograph fix
            'chronograph_view': chronograph_view_role, # remove after chronograph fix
            'default': schematics_default_role,
            'contracting': whitelist('doc_id', 'owner'),
        }

    title = StringType(required=True)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    date = IsoDateTimeType()
    tenderID = StringType()  # TenderID should always be the same as the OCID. It is included to make the flattened data structure more convenient.
    items = ListType(ModelType(Item), required=True, min_size=1, validators=[validate_cpv_group, validate_items_uniq])  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    value = ModelType(Value, required=True)  # The total estimated value of the procurement.
    procurementMethod = StringType(choices=['open', 'selective', 'limited'], default='limited')  # Specify tendering method as per GPA definitions of Open, Selective, Limited (http://www.wto.org/english/docs_e/legal_e/rev-gpr-94_01_e.htm)
    procurementMethodRationale = StringType()  # Justification of procurement method, especially in the case of Limited tendering.
    procurementMethodRationale_en = StringType()
    procurementMethodRationale_ru = StringType()
    procurementMethodType = StringType(default="reporting")
    procuringEntity = ModelType(ProcuringEntity, required=True)  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    documents = ListType(ModelType(Document), default=list())  # All documents and attachments related to the tender.
    awards = ListType(ModelType(Award), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    revisions = ListType(ModelType(Revision), default=list())
    status = StringType(choices=['draft', 'active', 'complete', 'cancelled', 'unsuccessful'], default='active')
    mode = StringType(choices=['test'])
    cancellations = ListType(ModelType(Cancellation), default=list())
    _attachments = DictType(DictType(BaseType), default=dict())  # couchdb attachments
    dateModified = IsoDateTimeType()
    owner_token = StringType()
    owner = StringType()
    if SANDBOX_MODE:
        procurementMethodDetails = StringType()

    create_accreditation = 1
    edit_accreditation = 2
    procuring_entity_kinds = ['general', 'special', 'defense', 'other']
    block_complaint_status = OpenUATender.block_complaint_status

    __parent__ = None
    __name__ = ''

    def __local_roles__(self):
        return dict([('{}_{}'.format(self.owner, self.owner_token), 'tender_owner')])

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == 'Administrator':
            role = 'Administrator'
        elif request.authenticated_role == 'chronograph':
            role = 'chronograph'
        elif request.authenticated_role == 'contracting':
            role = 'contracting'
        else:
            role = 'edit_{}'.format(request.context.status)
        return role

    def __acl__(self):
        return [
            (Allow, 'g:brokers', 'create_award_complaint'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_tender'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_tender_documents'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_complaint'),
        ]

    def initialize(self):
        self.date = get_now()

    def validate_procurementMethodDetails(self, *args, **kw):
        if self.mode and self.mode == 'test' and self.procurementMethodDetails and self.procurementMethodDetails != '':
            raise ValidationError(u"procurementMethodDetails should be used with mode test")

    def __repr__(self):
        return '<%s:%r@%r>' % (type(self).__name__, self.id, self.rev)

    @serializable(serialized_name='id')
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [k for k in data.keys() if data[k] == self.__class__.fields[k].default or data[k] == getattr(self, k)]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self

ReportingTender = Tender


class Award(ReportingAward):

    lotID = MD5Type()

    def validate_lotID(self, data, lotID):
        if isinstance(data['__parent__'], Model):
            if not lotID and data['__parent__'].lots:
                raise ValidationError(u'This field is required.')
            if lotID and lotID not in [i.id for i in data['__parent__'].lots]:
                raise ValidationError(u"lotID should be one of lots")

    class Options:
        roles = {
            'create': award_create_role,
            'edit': award_edit_role,
        }


class Lot(Model):
    class Options:
        roles = {
            'create': whitelist('id', 'title', 'title_en', 'title_ru', 'description', 'description_en', 'description_ru', 'value'),
            'edit': whitelist('title', 'title_en', 'title_ru', 'description', 'description_en', 'description_ru', 'value'),
            'embedded': embedded_lot_role,
            'view': default_lot_role,
            'default': default_lot_role,
            'auction_view': default_lot_role,
            'auction_patch': whitelist('id', 'auctionUrl'),
            'chronograph': whitelist('id', 'auctionPeriod'),
            'chronograph_view': whitelist('id', 'auctionPeriod', 'numberOfBids', 'status'),
            'Administrator': whitelist('auctionPeriod'),
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    date = IsoDateTimeType()
    value = ModelType(Value, required=True)
    status = StringType(choices=['active', 'cancelled', 'unsuccessful', 'complete'], default='active')

    @serializable(serialized_name="value", type=ModelType(Value))
    def lot_value(self):
        return Value(dict(amount=self.value.amount,
                          currency=self.__parent__.value.currency,
                          valueAddedTaxIncluded=self.__parent__.value.valueAddedTaxIncluded))


class Contract(BaseContract):
    items = ListType(ModelType(Item))


@implementer(ITender)
class Tender(ReportingTender):
    """ Negotiation """
    awards = ListType(ModelType(Award), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    cause = StringType(choices=['artContestIP', 'noCompetition', 'twiceUnsuccessful',
                                'additionalPurchase', 'additionalConstruction', 'stateLegalServices'],
                       required=True)
    causeDescription = StringType(required=True, min_length=1)
    causeDescription_en = StringType(min_length=1)
    causeDescription_ru = StringType(min_length=1)
    procurementMethodType = StringType(default="negotiation")
    create_accreditation = 3
    edit_accreditation = 4
    procuring_entity_kinds = ['general', 'special', 'defense']
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq])

NegotiationTender = Tender


@implementer(ITender)
class Tender(NegotiationTender):
    """ Negotiation """
    cause = StringType(choices=['quick', 'artContestIP', 'noCompetition', 'twiceUnsuccessful',
                                'additionalPurchase', 'additionalConstruction', 'stateLegalServices'], required=False)
    procurementMethodType = StringType(default="negotiation.quick")
    create_accreditation = 3
    edit_accreditation = 4
    procuring_entity_kinds = ['general', 'special', 'defense']

NegotiationQuickTender = Tender
