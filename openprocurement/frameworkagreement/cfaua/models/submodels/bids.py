from openprocurement.api.models import ListType
from openprocurement.api.utils import get_now
from openprocurement.frameworkagreement.cfaua.constants import BID_UNSUCCESSFUL_FROM
from openprocurement.frameworkagreement.cfaua.models.submodels.documents import BidderEUDocument
from openprocurement.frameworkagreement.cfaua.models.submodels.lotvalue import LotValue
from openprocurement.tender.core.models import Bid as BaseBid, Administrator_bid_role, view_bid_role, \
    validate_parameters_uniq, bids_validation_wrapper
from openprocurement.tender.openua.models import Parameter
from schematics.transforms import export_loop, whitelist
from schematics.types import BooleanType, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable


class BidModelType(ModelType):
    def export_loop(self, model_instance, field_converter,
                    role=None, print_none=False):
        """
        Calls the main `export_loop` implementation because they are both
        supposed to operate on models.
        """
        if isinstance(model_instance, self.model_class):
            model_class = model_instance.__class__
        else:
            model_class = self.model_class

        tender = model_instance.__parent__
        if (tender.revisions[0].date if tender.revisions else get_now()) > BID_UNSUCCESSFUL_FROM \
                    and role not in [None, 'plain'] and getattr(model_instance, 'status') == 'unsuccessful':
            role = 'bid.unsuccessful'

        shaped = export_loop(model_class, model_instance,
                             field_converter,
                             role=role, print_none=print_none)

        if shaped and len(shaped) == 0 and self.allow_none():
            return shaped
        elif shaped:
            return shaped
        elif print_none:
            return shaped


class Bid(BaseBid):
    class Options:
        roles = {
            'Administrator': Administrator_bid_role,
            'embedded': view_bid_role,
            'view': view_bid_role,
            'create': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'selfQualified',
                                'selfEligible', 'subcontractingDetails', 'documents', 'financialDocuments',
                                'eligibilityDocuments', 'qualificationDocuments'),
            'edit': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'subcontractingDetails'),
            'auction_view': whitelist('value', 'lotValues', 'id', 'date', 'parameters', 'participationUrl', 'status'),
            'auction_post': whitelist('value', 'lotValues', 'id', 'date'),
            'auction_patch': whitelist('id', 'lotValues', 'participationUrl'),
            'active.enquiries': whitelist(),
            'active.tendering': whitelist(),
            'active.pre-qualification': whitelist('id', 'status', 'documents', 'eligibilityDocuments', 'tenderers'),
            'active.pre-qualification.stand-still': whitelist('id', 'status', 'documents', 'eligibilityDocuments',
                                                              'tenderers'),
            'active.auction': whitelist('id', 'status', 'documents', 'eligibilityDocuments', 'tenderers'),
            'active.qualification': view_bid_role,
            'active.awarded': view_bid_role,
            'complete': view_bid_role,
            'unsuccessful': view_bid_role,
            'bid.unsuccessful': whitelist('id', 'status', 'tenderers', 'documents', 'eligibilityDocuments',
                                          'parameters', 'selfQualified', 'selfEligible', 'subcontractingDetails'),
            'cancelled': view_bid_role,
            'invalid': whitelist('id', 'status'),
            'invalid.pre-qualification': whitelist('id', 'status', 'documents', 'eligibilityDocuments', 'tenderers'),
            'deleted': whitelist('id', 'status'),
        }

    documents = ListType(ModelType(BidderEUDocument), default=list())
    financialDocuments = ListType(ModelType(BidderEUDocument), default=list())
    eligibilityDocuments = ListType(ModelType(BidderEUDocument), default=list())
    qualificationDocuments = ListType(ModelType(BidderEUDocument), default=list())
    lotValues = ListType(ModelType(LotValue), default=list())
    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(required=True, choices=[True])
    subcontractingDetails = StringType()
    parameters = ListType(ModelType(Parameter), default=list(), validators=[validate_parameters_uniq])
    status = StringType(
        choices=['draft', 'pending', 'active', 'invalid', 'invalid.pre-qualification', 'unsuccessful', 'deleted'],
        default='pending')

    def serialize(self, role=None):
        if role and role != 'create' and self.status in ['invalid', 'invalid.pre-qualification', 'deleted']:
            role = self.status
        elif role and role != 'create' and self.status == 'unsuccessful':
            role = 'bid.unsuccessful'
        return super(Bid, self).serialize(role)

    @serializable(serialized_name="status")
    def serialize_status(self):
        if self.status in ['draft', 'invalid', 'invalid.pre-qualification', 'unsuccessful',
                           'deleted'] or self.__parent__.status in ['active.tendering', 'cancelled']:
            return self.status
        if self.__parent__.lots:
            active_lots = [lot.id for lot in self.__parent__.lots if lot.status in ('active', 'complete',)]
            if not self.lotValues:
                return 'invalid'
            elif [i.relatedLot for i in self.lotValues if i.status == 'pending' and i.relatedLot in active_lots]:
                return 'pending'
            elif [i.relatedLot for i in self.lotValues if i.status == 'active' and i.relatedLot in active_lots]:
                return 'active'
            else:
                return 'unsuccessful'
        return self.status

    @bids_validation_wrapper
    def validate_value(self, data, value):
        BaseBid._validator_functions['value'](self, data, value)

    @bids_validation_wrapper
    def validate_lotValues(self, data, lotValues):
        BaseBid._validator_functions['lotValues'](self, data, lotValues)

    @bids_validation_wrapper
    def validate_participationUrl(self, data, participationUrl):
        BaseBid._validator_functions['participationUrl'](self, data, participationUrl)

    @bids_validation_wrapper
    def validate_parameters(self, data, parameters):
        BaseBid._validator_functions['parameters'](self, data, parameters)


