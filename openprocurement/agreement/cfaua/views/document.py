from openprocurement.api.utils import (
    json_view,
    )
from openprocurement.agreement.core.resource import (
    agreements_resource
    )
from openprocurement.agreement.cfaua.views.agreement import (
    AgreementResource
    )


@agreements_resource(
    name='cfaua.Agreement.Document',
    collection_path='/agreements/{agreement_id}/documents',
    path='/agreements/{agreement_id}/documents/{document_id}',
    agreementType='cfaua',
    description='Agreements resource'
)
class AgreementContractsResource(AgreementResource):

    @json_view(permission='view_agreement')
    def collection_get(self):
        agreement = self.context
        return {'data': [
            contract.serialize('view')
            for contract in agreement.contracts
        ]}

    @json_view(permission='view_agreement')
    def get(self):
        return {
            "data": self.request.validated['contract'].serialize('view')
        }