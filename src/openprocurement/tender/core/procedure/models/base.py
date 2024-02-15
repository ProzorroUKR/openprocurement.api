from logging import getLogger

from openprocurement.api.procedure.models.base import Model

LOGGER = getLogger(__name__)


class BaseBid(Model):
    pass


class BaseAward(Model):
    pass


class BaseQualification(Model):
    pass
