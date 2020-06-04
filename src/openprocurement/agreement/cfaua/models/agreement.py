from openprocurement.agreement.cfaua.models.change import (
    ChangeTaxRate,
    ChangeItemPriceVariation,
    ChangeThirdParty,
    ChangePartyWithdrawal,
)
from zope.interface import implementer, provider
from schematics.types import StringType
from schematics.types.compound import ModelType, PolyModelType
from schematics.transforms import whitelist
from pyramid.security import Allow

from openprocurement.api.auth import ACCR_3, ACCR_5
from openprocurement.api.models import Period, IsoDateTimeType, ListType
from openprocurement.planning.api.models import BaseOrganization
from openprocurement.agreement.core.models.agreement import Agreement as BaseAgreement
from openprocurement.agreement.cfaua.models.document import Document
from openprocurement.agreement.cfaua.models.feature import Feature
from openprocurement.agreement.cfaua.models.contract import Contract
from openprocurement.agreement.cfaua.models.item import Item
from openprocurement.agreement.cfaua.models.procuringentity import ProcuringEntity
from openprocurement.agreement.cfaua.interfaces import IClosedFrameworkAgreementUA
from openprocurement.agreement.cfaua.validation import validate_features_uniq
from openprocurement.agreement.cfaua.utils import get_change_class


@implementer(IClosedFrameworkAgreementUA)
@provider(IClosedFrameworkAgreementUA)
class Agreement(BaseAgreement):
    class Options:
        _data_fields = whitelist(
            "agreementID", "agreementNumber", "changes", "contracts", "dateSigned", "description",
            "description_en", "description_ru", "documents", "features", "id", "items", "mode",
            "numberOfContracts", "owner", "period", "procuringEntity", "status", "tender_id",
            "terminationDetails", "title", "title_en", "title_ru"
        )
        _create = _data_fields + whitelist("tender_token")
        _embedded = _create + whitelist(
            "dateModified", "agreementType", "revisions",
            "owner_token", "date", "transfer_token", "doc_id",
        )
        roles = {
            "view": _data_fields + whitelist("dateModified"),
            "create": _create,
            "edit_terminated": whitelist(),
            "edit_active": whitelist("documents", "status", "terminationDetails"),
            "Administrator": whitelist("documents", "mode", "procuringEntity", "status", "terminationDetails"),
            "embedded": _embedded,
            "default": _embedded - whitelist("doc_id") + whitelist("_id", "_rev", "doc_type"),
            "plain": _embedded - whitelist("revisions", "dateModified"),
        }

    agreementNumber = StringType()
    agreementType = StringType(default="cfaua")
    period = ModelType(Period)
    dateSigned = IsoDateTimeType()
    title_en = StringType()
    title_ru = StringType()
    description_en = StringType()
    description_ru = StringType()
    changes = ListType(
        PolyModelType(
            (ChangeTaxRate, ChangeItemPriceVariation, ChangePartyWithdrawal, ChangeThirdParty),
            claim_function=get_change_class,
        ),
        default=list(),
    )
    documents = ListType(ModelType(Document, required=True), default=list())
    contracts = ListType(ModelType(Contract, required=True), default=list())
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    items = ListType(ModelType(Item, required=True))
    procuringEntity = ModelType(ProcuringEntity, required=True)
    terminationDetails = StringType()

    create_accreditations = (ACCR_3, ACCR_5)  # TODO

    def __acl__(self):
        acl = super(Agreement, self).__acl__()
        acl.append((Allow, "{}_{}".format(self.owner, self.owner_token), "upload_agreement_documents"))
        return acl

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == "Administrator":
            role = "Administrator"
        else:
            role = "edit_{}".format(request.context.status)
        return role

    def get_active_contracts_count(self):
        return len([c.id for c in self.contracts if c.status == "active"])
