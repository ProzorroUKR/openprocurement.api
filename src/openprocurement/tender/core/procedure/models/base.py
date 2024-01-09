from openprocurement.api.procedure.models.base import Model
from logging import getLogger

LOGGER = getLogger(__name__)


class BaseBid(Model):
    pass


class BaseAward(Model):
    pass


class BaseQualification(Model):
    pass
