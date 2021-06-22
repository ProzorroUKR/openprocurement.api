from openprocurement.api.utils import APIResource, json_view, context_unpack, get_now
from openprocurement.framework.core.utils import agreementsresource, apply_patch
from openprocurement.framework.core.validation import validate_patch_agreement_data
from openprocurement.framework.electroniccatalogue.utils import check_contract_statuses, check_agreement_status
from openprocurement.framework.electroniccatalogue.validation import validate_agreement_operation_not_in_allowed_status
from openprocurement.framework.core.design import agreements_filter_by_classification_id


@agreementsresource(
    name="electronicCatalogue:Agreements",
    path="/agreements/{agreement_id}",
    agreementType="electronicCatalogue",
    description="Agreements resource"
)
class AgreementResource(APIResource):
    @json_view(permission="view_agreement")
    def get(self):
        return {"data": self.context.serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
                validate_patch_agreement_data,
                validate_agreement_operation_not_in_allowed_status,
        ),
        permission="edit_agreement"
    )
    def patch(self):
        if self.request.authenticated_role == "chronograph":
            now = get_now()
            if not check_agreement_status(self.request, now):
                check_contract_statuses(self.request, now)
        if apply_patch(
                self.request,
                obj_name="agreement",
                data=self.request.validated["agreement"].to_primitive(),
                src=self.request.validated["agreement_src"]
        ):
            self.LOGGER.info(f"Updated agreement {self.request.validated['agreement'].id}",
                             extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_patch"}))
        return {"data": self.request.context.serialize("view")}


@agreementsresource(
    name="Agreements by classificationID",
    path="/agreements_by_classification/{classification_id}",
    description="Agreements filter classification"
)
class AgreementFilterByClassificationResource(APIResource):
    @json_view(permission="view_listing")
    def get(self):

        classification_id = self.request.matchdict.get("classification_id")
        if "-" in classification_id:
            classification_id = classification_id[:classification_id.find("-")]
        additional_classifications = self.request.params.get("additional_classifications", "")

        if additional_classifications.lower() == "none":
            additional_classifications = set()
        elif additional_classifications:
            additional_classifications = set(additional_classifications.split(","))

        key = [classification_id]
        res = agreements_filter_by_classification_id(self.request.registry.databases.agreements, key=key)

        if isinstance(additional_classifications, set):
            results = [
                x.value
                for x in res
                if {i['id'] for i in x.value.get("additionalClassifications", "")} == additional_classifications
            ]
        else:
            results = [
                x.value
                for x in res
            ]

        data = {
            "data": results,
        }
        return data
