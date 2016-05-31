# -*- coding: utf-8 -*-
from datetime import timedelta
from schematics.types import StringType
from schematics.exceptions import ValidationError
from zope.interface import implementer
from openprocurement.api.models import ITender, get_now
from openprocurement.tender.openua.models import Tender as TenderUA
from openprocurement.tender.openeu.models import Tender as TenderEU
from openprocurement.tender.openeu.models import TENDERING_DAYS, TENDERING_DURATION
from openprocurement.tender.openua.utils import calculate_business_date


@implementer(ITender)
class Tender(TenderUA):
    procurementMethodType = StringType(default="competitiveDialogue.aboveThresholdUA")

    def validate_tenderPeriod(self, data, period):
        # if data['_rev'] is None when tender was created just now
        if not data['_rev'] and calculate_business_date(get_now(), -timedelta(minutes=10)) >= period.startDate:
            raise ValidationError(u"tenderPeriod.startDate should be in greater than current date")
        if period and calculate_business_date(period.startDate, TENDERING_DURATION, data) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than {} days".format(TENDERING_DAYS))


CompetitiveDialogUA = Tender


@implementer(ITender)
class Tender(TenderEU):
    procurementMethodType = StringType(default="competitiveDialogue.aboveThresholdEU")


CompetitiveDialogEU = Tender
