from schematics.exceptions import ValidationError
from schematics.transforms import export_loop
from schematics.types.compound import ModelType as BaseModelType,  ListType as BaseListType
from openprocurement.api.models import Model, DecimalType as BaseDecimalType
from decimal import Decimal
from logging import getLogger

LOGGER = getLogger(__name__)


class ListType(BaseListType):  # TODO RM?
    """
    Schematics ListType export_loop returns None instead of the empty list
    if an empty list passed to model.
    So you have to pass serialize_when_none , like
    ListType(ModelType(Parameter, required=True), serialize_when_none=True, ...
    and then converting '[]' to 'None' won't happen.
    1) It's not obvious
    2) If we use model to validate user input data, we do want to know they sending this empty list
    """
    def allow_none(self):
        return True


class ModelType(BaseModelType):  # TODO RM?

    def __init__(self, model_class, **kwargs):
        name = kwargs.pop("name", None)
        if name:
            model_class.__name__ = name
        super().__init__(model_class, **kwargs)


class NoneAllowedModelType(BaseModelType):
    """
    without overwriting export_loop
    the following data provided to model {'auctionPeriod': {'startDate': None}}
    would result with None as output from .serialize()
    """

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

        shaped = export_loop(model_class, model_instance,
                             field_converter,
                             role=role, print_none=True)

        if shaped and len(shaped) == 0 and self.allow_none():
            return shaped
        elif shaped:
            return shaped
        elif print_none:
            return shaped


class DecimalType(BaseDecimalType):
    def to_primitive(self, *args, **kwargs):
        value = super().to_primitive(*args, **kwargs)
        if isinstance(value, Decimal):
            return '{0:f}'.format(value)
        return value


class BaseBid(Model):
    pass


class BaseAward(Model):
    pass


class BaseQualification(Model):
    pass


def validate_object_id_uniq(objs, *_, obj_name=None):

    if objs:
        if not obj_name:
            obj_name = objs[0].__class__.__name__
        obj_name_multiple = obj_name[0].lower() + obj_name[1:]
        ids = [i["id"] for i in objs]
        if ids and len(set(ids)) != len(ids):
            raise ValidationError("{} id should be uniq for all {}s".format(obj_name, obj_name_multiple))
