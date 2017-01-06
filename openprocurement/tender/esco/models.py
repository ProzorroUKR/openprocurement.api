# -*- coding: utf-8 -*-
from zope.interface import implementer
from schematics.types import StringType, FloatType
from schematics.types.compound import ModelType
from schematics.transforms import whitelist

from openprocurement.api.models import ITender
from openprocurement.api.models import Value

from openprocurement.tender.openua.models import (
    Tender as BaseTenderUA, Bid as BaseUABid,
    PeriodStartEndRequired, SifterListType,
)

from openprocurement.tender.openeu.models import (
    Tender as BaseTenderEU, Bid as BaseEUBid,
)

from openprocurement.tender.limited.models import (
    ReportingTender as BaseReportingTender,
)


class ESCOBid():
    yearlyPayments = FloatType(min_value=0, max_value=1, required=True)  # The percentage of annual payments in favor of Bidder
    annualCostsReduction = ModelType(Value, required=True)  # Buyer's annual costs reduction
    contractDuration = ModelType(PeriodStartEndRequired, required=True)


class Bid(ESCOBid, BaseUABid):
    """ ESCO UA bid model """

    class Options:
        roles = {
            'create': whitelist('value', 'yearlyPayments', 'annualCostsReduction', 'contractDuration', 'tenderers', 'parameters', 'lotValues', 'status', 'selfQualified', 'selfEligible', 'subcontractingDetails', 'documents'),
            'edit': whitelist('value', 'yearlyPayments', 'annualCostsReduction', 'contractDuration', 'tenderers', 'parameters', 'lotValues', 'status', 'subcontractingDetails'),
            'auction_view': whitelist('value', 'yearlyPayments', 'annualCostsReduction', 'contractDuration', 'lotValues', 'id', 'date', 'parameters', 'participationUrl', 'status'),
            'auction_post': whitelist('value', 'yearlyPayments', 'annualCostsReduction', 'contractDuration', 'lotValues', 'id', 'date'),
        }


@implementer(ITender)
class Tender(BaseTenderUA):
    """ ESCO UA Tender model """
    procurementMethodType = StringType(default="esco.UA")
    bids = SifterListType(ModelType(Bid), default=list(), filter_by='status', filter_in_values=['invalid', 'deleted'])  # A list of all the companies who entered submissions for the tender.


TenderESCOUA = Tender


class Bid(ESCOBid, BaseEUBid):
    """ ESCO EU bid model """

    class Options:
        roles = {
            'create': whitelist('value', 'yearlyPayments', 'annualCostsReduction', 'contractDuration', 'tenderers', 'parameters', 'lotValues', 'status', 'selfQualified', 'selfEligible', 'subcontractingDetails', 'documents', 'financialDocuments', 'eligibilityDocuments', 'qualificationDocuments'),
            'edit': whitelist('value', 'yearlyPayments', 'annualCostsReduction', 'contractDuration', 'tenderers', 'parameters', 'lotValues', 'status', 'subcontractingDetails'),
            'auction_view': whitelist('value', 'yearlyPayments', 'annualCostsReduction', 'contractDuration', 'lotValues', 'id', 'date', 'parameters', 'participationUrl', 'status'),
            'auction_post': whitelist('value', 'yearlyPayments', 'annualCostsReduction', 'contractDuration', 'lotValues', 'id', 'date'),
        }


@implementer(ITender)
class Tender(BaseTenderEU):
    """ ESCO EU Tender model """
    procurementMethodType = StringType(default="esco.EU")
    bids = SifterListType(ModelType(Bid), default=list(), filter_by='status', filter_in_values=['invalid', 'deleted'])  # A list of all the companies who entered submissions for the tender.


TenderESCOEU = Tender


@implementer(ITender)
class Tender(BaseReportingTender):
    """ ESCO Reporting Tender model """
    procurementMethodType = StringType(default="esco.reporting")


TenderESCOReporting = Tender
