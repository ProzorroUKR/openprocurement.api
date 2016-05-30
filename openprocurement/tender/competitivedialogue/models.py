# -*- coding: utf-8 -*-
from datetime import timedelta
from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from zope.interface import implementer
from openprocurement.api.models import ITender, Period
from openprocurement.tender.openua.models import Tender as BaseTender, EnquiryPeriod
from openprocurement.tender.openua.utils import calculate_business_date

STAND_STILL_TIME = timedelta(days=4)
ENQUIRY_STAND_STILL_TIME = timedelta(days=2)
CLAIM_SUBMIT_TIME = timedelta(days=2)
COMPLAINT_SUBMIT_TIME = timedelta(days=3)
TENDER_PERIOD = timedelta(days=6)
ENQUIRY_PERIOD_TIME = timedelta(days=3)
TENDERING_EXTRA_PERIOD = timedelta(days=2)


@implementer(ITender)
class Tender(BaseTender):
    procurementMethodType = StringType(default="aboveThresholdUA.competitiveDialogue")
