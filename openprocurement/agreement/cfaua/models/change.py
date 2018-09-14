# -*- coding: utf-8 -*-
from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.roles import RolesFromCsv
from openprocurement.api.models import ListType
from openprocurement.agreement.core.models.change import Change as BaseChange
from openprocurement.agreement.cfaua.models.modification import UnitPriceModifiaction, ContractModifiaction
from openprocurement.agreement.cfaua.validation import (
    validate_item_price_variation_modifications,
    validate_third_party_modifications,
    validate_modifications_items_uniq
)


class ClassicChange(BaseChange):
    class Options:
        namespace = 'Change'
        roles = RolesFromCsv('Change.csv', relative_to=__file__)

    agreementNumber = StringType()


class ChangeTaxRate(ClassicChange):
    class Options:
        namespace = 'Change'
        roles = RolesFromCsv('ChangeTaxRate.csv', relative_to=__file__)

    rationaleType = StringType(default='taxRate')
    modifications = ListType(ModelType(UnitPriceModifiaction), validators=[validate_modifications_items_uniq])


class ChangeItemPriceVariation(ClassicChange):
    class Options:
        namespace = 'Change'
        roles = RolesFromCsv('ChangeItemPriceVariation.csv', relative_to=__file__)

    rationaleType = StringType(default='itemPriceVariation')
    modifications = ListType(ModelType(UnitPriceModifiaction),
                             validators=[validate_item_price_variation_modifications,
                                         validate_modifications_items_uniq])


class ChangeThirdParty(ClassicChange):
    class Options:
        namespace = 'Change'
        roles = RolesFromCsv('ChangeThirdParty.csv', relative_to=__file__)

    rationaleType = StringType(default='thirdParty')
    modifications = ListType(ModelType(UnitPriceModifiaction), validators=[validate_third_party_modifications,
                                                                           validate_modifications_items_uniq])


class ChangePartyWithdrawal(ClassicChange):
    class Options:
        namespace = 'Change'
        roles = RolesFromCsv('ChangePartyWithdrawal.csv', relative_to=__file__)

    rationaleType = StringType(default='partyWithdrawal')
    modifications = ListType(ModelType(ContractModifiaction), validators=[validate_modifications_items_uniq])
