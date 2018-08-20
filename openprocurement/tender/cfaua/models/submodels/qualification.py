from uuid import uuid4

from openprocurement.api.models import Model, IsoDateTimeType, ListType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.cfaua.models.submodels.complaint import Complaint
from openprocurement.tender.cfaua.models.submodels.documents import EUDocument
from schematics.exceptions import ValidationError
from schematics.types import StringType, MD5Type, BooleanType
from schematics.types.compound import ModelType


class Qualification(Model):
    """ Pre-Qualification """

    class Options:
        roles = RolesFromCsv('Qualification.csv', relative_to=__file__)

    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    bidID = StringType(required=True)
    lotID = MD5Type()
    status = StringType(choices=['pending', 'active', 'unsuccessful', 'cancelled'], default='pending')
    date = IsoDateTimeType()
    documents = ListType(ModelType(EUDocument), default=list())
    complaints = ListType(ModelType(Complaint), default=list())
    qualified = BooleanType(default=False)
    eligible = BooleanType(default=False)

    def validate_qualified(self, data, qualified):
        if data['status'] == 'active' and not qualified:
            raise ValidationError(u'This field is required.')

    def validate_eligible(self, data, eligible):
        if data['status'] == 'active' and not eligible:
            raise ValidationError(u'This field is required.')

    def validate_lotID(self, data, lotID):
        if isinstance(data['__parent__'], Model):
            if not lotID and data['__parent__'].lots:
                raise ValidationError(u'This field is required.')
            if lotID and lotID not in [i.id for i in data['__parent__'].lots]:
                raise ValidationError(u"lotID should be one of lots")
