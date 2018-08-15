from openprocurement.api.utils import (
    json_view,
    APIResource,
    set_ownership
    )
from openprocurement.agreement.core.resource import agreements_resource


from openprocurement.agreement.core.utils import (
    context_unpack,
    save_agreement
    )
from openprocurement.agreement.cfaua.validation\
    import validate_credentials_generate


@agreements_resource(
    name='cfaua.Agreement.credentials',
    path='/agreements/{agreement_id}/credentials',
    description="Agreement credentials"
)
class AgreementCredentialsResource(APIResource):

    @json_view(
        permission='generate_credentials',
        validators=validate_credentials_generate
    )
    def patch(self):
        agreement = self.request.validated['agreement']

        set_ownership(agreement, self.request)
        if save_agreement(self.request):
            self.LOGGER.info(
                'Generate Agreement credentials {}'.format(agreement.id),
                extra=context_unpack(self.request, {'MESSAGE_ID': 'agreement_patch'}))
            return {
                'data': agreement.serialize("view"),
                'access': {
                    'token': agreement.owner_token
                }
            }