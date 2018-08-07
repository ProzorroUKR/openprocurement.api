from zope.interface import implementer, provider
from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.transforms import whitelist
from pyramid.security import Allow
from openprocurement.api.models import (
    plain_role,
    schematics_embedded_role,
    schematics_default_role
    )
from openprocurement.api.models import (
    Period,
    IsoDateTimeType,
    ListType
    )
from openprocurement.agreement.core.models.agreement\
    import Agreement as BaseAgreement
from openprocurement.agreement.cfaua.models.document\
    import Document
from openprocurement.agreement.cfaua.models.contract\
    import Contract
from openprocurement.agreement.cfaua.models.item\
    import Item
from openprocurement.agreement.cfaua.models.procuringentity\
    import ProcuringEntity

from openprocurement.agreement.cfaua.interfaces import IClosedFrameworkAgreementUA


@implementer(IClosedFrameworkAgreementUA)
@provider(IClosedFrameworkAgreementUA)
class Agreement(BaseAgreement):

    class Options:
        roles = {
            'plain': plain_role,
            'create': (
                whitelist(
                    'id', 'agreementNumber', 'agreementID', 'title', 'title_en',
                    'title_ru', 'description', 'description_en',
                    'description_ru', 'status', 'period',
                    'dateSigned', 'items', 'owner', 'tender_token',
                    'tender_id', 'mode', 'procuringEntity', 'terminationDetails',
                    'documents', 'contracts'
                )
            ),
            'edit_terminated': whitelist(),
            'edit_active': whitelist('status', 'terminationDetails', 'documents'),
            'default': schematics_default_role,
            'embedded': schematics_embedded_role,
            'view':  (
                whitelist(
                    'id', 'agreementID', 'dateModified',
                    'agreementNumber', 'title', 'title_en', 'title_ru',
                    'description', 'description_en', 'description_ru',
                    'status', 'period', 'dateSigned', 'documents', 'items',
                    'owner', 'mode', 'tender_id', 'procuringEntity',
                    'terminationDetails', 'contracts'
                )
            ),
        }
    agreementNumber = StringType()
    agreementType = StringType(default='cfaua')
    period = ModelType(Period)
    dateSigned = IsoDateTimeType()
    title_en = StringType()
    title_ru = StringType()
    description_en = StringType()
    description_ru = StringType()
    documents = ListType(ModelType(Document), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    items = ListType(ModelType(Item))
    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )
    terminationDetails = StringType()
    create_accreditation = 3  # TODO

    def __acl__(self):
        acl = super(Agreement, self).__acl__()
        acl.append(
            (
                Allow,
                '{}_{}'.format(self.owner, self.owner_token),
                'upload_agreement_documents'
            ),
        )
        return acl

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == 'Administrator':
            role = 'Administrator'
        else:
            role = 'edit_{}'.format(request.context.status)
        return role
