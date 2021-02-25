# -*- coding: utf-8 -*-
from openprocurement.api.roles import RolesFromCsv
from openprocurement.framework.cfaua.models.agreement import (
    ChangeTaxRate as BaseChangeTaxRate,
    ChangeItemPriceVariation as BaseChangeItemPriceVariation,
    ChangeThirdParty as BaseChangeThirdParty,
    ChangePartyWithdrawal as BaseChangePartyWithdrawal,
)


class ChangeTaxRate(BaseChangeTaxRate):
    class Options:
        namespace = "Change"
        roles = RolesFromCsv("ChangeTaxRate.csv", relative_to=__file__)


class ChangeItemPriceVariation(BaseChangeItemPriceVariation):
    class Options:
        namespace = "Change"
        roles = RolesFromCsv("ChangeItemPriceVariation.csv", relative_to=__file__)


class ChangeThirdParty(BaseChangeThirdParty):
    class Options:
        namespace = "Change"
        roles = RolesFromCsv("ChangeThirdParty.csv", relative_to=__file__)


class ChangePartyWithdrawal(BaseChangePartyWithdrawal):
    class Options:
        namespace = "Change"
        roles = RolesFromCsv("ChangePartyWithdrawal.csv", relative_to=__file__)
