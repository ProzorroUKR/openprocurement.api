# -*- coding: utf-8 -*-
from zope.interface import implementer
from schematics.types import StringType, FloatType, IntType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist

from openprocurement.tender.core.models import ITender, get_tender
from openprocurement.api.models import Value, Model

from openprocurement.tender.openua.models import SifterListType

from openprocurement.tender.openeu.models import (
    Tender as BaseTenderEU, Bid as BaseEUBid,
)


from openprocurement.tender.esco.utils import calculate_npv



class ESCOBid(Model):

    yearlyPayments = FloatType(min_value=0, max_value=1, required=True)  # The percentage of annual payments in favor of Bidder
    annualCostsReduction = ModelType(Value, required=True)  # Buyer's annual costs reduction
    contractDuration = IntType(min_value=0, max_value=10, required=True)

    @serializable(serialized_name="value", type=ModelType(Value))
    def bid_value(self):
        tender = get_tender(self.__parent__)
        nbu_rat = tender.NBUdiscountRate
        npv = calculate_npv(nbu_rat, self.annualCostsReduction.amount,
                            self.yearlyPayments, self.contractDuration)
        return Value(dict(amount=npv,
                          currency=tender.value.currency,
                          valueAddedTaxIncluded=tender.value.valueAddedTaxIncluded))


class Bid(BaseEUBid, ESCOBid):
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
    NBUdiscountRate = 0.22  # XXX temporary solution TODO discuss field type, name and location


TenderESCOEU = Tender
