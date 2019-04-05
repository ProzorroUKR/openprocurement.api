from schematics.transforms import export_loop
from schematics.types import BooleanType, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from openprocurement.api.models import ListType
from openprocurement.api.utils import get_now, get_document_date
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.core.models import Bid as BaseBid, \
    validate_parameters_uniq, bids_validation_wrapper
from openprocurement.tender.cfaua.constants import BID_UNSUCCESSFUL_FROM
from openprocurement.tender.cfaua.models.submodels.documents import BidderEUDocument
from openprocurement.tender.cfaua.models.submodels.lotvalue import LotValue
from openprocurement.tender.cfaua.models.submodels.parameters import BidParameter
from openprocurement.tender.cfaua.models.submodels.value import Value


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
        tender_date = get_document_date(tender, default=get_now())
        status = getattr(model_instance, 'status')
        if tender_date > BID_UNSUCCESSFUL_FROM and role not in [None, 'plain'] and status == 'unsuccessful':
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
        roles = RolesFromCsv('Bid.csv', relative_to=__file__)

    documents = ListType(ModelType(BidderEUDocument), default=list())
    financialDocuments = ListType(ModelType(BidderEUDocument), default=list())
    eligibilityDocuments = ListType(ModelType(BidderEUDocument), default=list())
    qualificationDocuments = ListType(ModelType(BidderEUDocument), default=list())
    lotValues = ListType(ModelType(LotValue), default=list())
    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(required=True, choices=[True])
    subcontractingDetails = StringType()
    parameters = ListType(ModelType(BidParameter), default=list(), validators=[validate_parameters_uniq])
    status = StringType(
        choices=['draft', 'pending', 'active', 'invalid', 'invalid.pre-qualification', 'unsuccessful', 'deleted'],
        default='pending'
    )
    value = ModelType(Value)

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
