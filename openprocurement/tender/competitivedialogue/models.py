# -*- coding: utf-8 -*-
from schematics.types import StringType
from zope.interface import implementer
from openprocurement.api.models import ITender
from openprocurement.tender.openua.models import Tender as TenderUA
from openprocurement.tender.openeu.models import Tender as TenderEU


@implementer(ITender)
class Tender(TenderUA):
    procurementMethodType = StringType(default="competitiveDialogue.aboveThresholdUA")


CompetitiveDialogUA = Tender


@implementer(ITender)
class Tender(TenderEU):
    procurementMethodType = StringType(default="competitiveDialogue.aboveThresholdEU")


CompetitiveDialogEU = Tender
