from openprocurement.api.utils import (
    json_view,
    set_ownership,
    generate_id,
    context_unpack,
    get_now
    )
from openprocurement.agreement.core.utils import (
    save_agreement
    )
from openprocurement.agreement.core.validation import (
    validate_agreement_data
    )
from openprocurement.agreement.core.resource import (
    AgreementsResource,
    agreements_resource
    )


@agreements_resource(
    name="Agreements",
    path="/agreements"
)
class APIAgreementsResource(AgreementsResource):
    """ Base agreement containder """
    @json_view(
        content_type="application/json",
        permission='create_agreement',
        validators=(validate_agreement_data,)
    )
    def post(self):
        agreement_id = generate_id()
        agreement = self.request.validated['agreement']
        agreement.id = agreement_id
        if self.request.json_body['data'].get('status') == 'draft':
            agreement.status = 'draft'
        set_ownership(agreement, self.request)  # rewrite as subscriber?
        self.request.validated['agreement'] = agreement
        self.request.validated['agreement_src'] = {}
        if save_agreement(self.request):
            self.LOGGER.info(
                'Created agreement {} ({})'.format(agreement_id, agreement.agreementID),
                extra=context_unpack(
                    self.request,
                    {'MESSAGE_ID': 'agreement_create'},
                    {'agreement_id': agreement_id, 'agreementID': agreement.agreementID}
                )
            )
            self.request.response.status = 201
            self.request.response.headers['Location']\
                = self.request.route_url(
                '{}:Agreement'.format(agreement.agreementType),
                agreement_id=agreement_id
            )
            return {
                'data': agreement.serialize(agreement.status),
                'access': {
                    'token': agreement.owner_token
                }
            }