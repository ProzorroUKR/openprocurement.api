import simplejson
from logging import getLogger

from cornice.util import json_error
from pyramid.request import Request
from cornice.resource import resource
from pyramid.security import Allow, Everyone

from openprocurement.api.auth import ACCR_1, ACCR_3, ACCR_5
from openprocurement.api.constants import VERSION
from openprocurement.api.utils import (
    context_unpack,
    json_view,
    update_logging_context,
    request_init_plan,
)
from openprocurement.api.validation import validate_json_data
from openprocurement.api.views.base import MongodbResourceListing
from openprocurement.planning.api.procedure.models.plan import PostPlan, PatchPlan, Plan
from openprocurement.planning.api.procedure.serializers.plan import PlanSerializer
from openprocurement.planning.api.procedure.utils import save_plan
from openprocurement.planning.api.procedure.views.base import PlanBaseResource
from openprocurement.tender.core.procedure.utils import set_ownership
from openprocurement.api.procedure.validation import (
    validate_patch_data_simple,
    validate_input_data,
    validate_data_documents,
    validate_item_owner,
    unless_administrator,
    validate_accreditation_level,
)

LOGGER = getLogger(__name__)


@resource(
    name="Plans Listing",
    path="/plans",
    request_method=("GET",),
)
class PlansListResource(MongodbResourceListing):
    listing_name = "Plans Listing"
    listing_default_fields = {"dateModified"}
    listing_allowed_fields = {
        "dateCreated",
        "dateModified",
        "status",
        "planID",
        "procuringEntity",
        "procurementMethodType",
        "mode",
    }

    def __init__(self, request, context=None):
        super(PlansListResource, self).__init__(request, context)
        self.db_listing_method = request.registry.mongodb.plans.list

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_listing"),
        ]
        return acl


@resource(
    name="Plans",
    collection_path="/plans",
    path="/plans/{plan_id}",
    accept="application/json",
)
class PlansResource(PlanBaseResource):
    serializer_class = PlanSerializer

    @json_view(permission="view_plan")
    def get(self):
        plan = self.request.validated["plan"]
        return {
            "data": self.serializer_class(plan).data,
        }

    @json_view(
        content_type="application/json",
        permission="create_plan",
        validators=(
            validate_input_data(PostPlan),
            validate_accreditation_level(
                levels=(ACCR_1, ACCR_3, ACCR_5), item="plan", operation="creation", source="data"
            ),
            validate_data_documents(route_key="plan_id"),
        ),
    )
    def collection_post(self):
        update_logging_context(self.request, {"plan_id": "__new__"})
        plan = self.request.validated["data"]
        request_init_plan(self.request, plan, plan_src={})
        access = set_ownership(plan, self.request)
        self.state.on_post(plan)
        if save_plan(self.request, modified=True, insert=True):
            LOGGER.info(
                "Created plan {} ({})".format(plan["_id"], plan["planID"]),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "plan_create"},
                    {
                        "plan_id": plan["_id"],
                        "planID": plan["planID"],
                    },
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url("Plans", plan_id=plan["_id"])
            return {
                "data": self.serializer_class(plan).data,
                "access": access,
            }

    @json_view(
        content_type="application/json",
        validators=(
            unless_administrator(validate_item_owner("plan")),
            validate_input_data(PatchPlan, none_means_remove=True),
            validate_patch_data_simple(Plan, item_name="plan"),
        ),
        permission="edit_plan",
    )
    def patch(self):
        updated = self.request.validated["data"]
        plan = self.request.validated["plan"]
        plan_src = self.request.validated["plan_src"]
        if updated:
            plan = self.request.validated["plan"] = updated
            self.state.on_patch(plan_src, plan)
            if save_plan(self.request):
                self.LOGGER.info(
                    f"Updated plan {updated['_id']}", extra=context_unpack(self.request, {"MESSAGE_ID": "plan_patch"})
                )
        return {
            "data": self.serializer_class(plan).data,
        }


@resource(
    name="Plan Tenders",
    path="/plans/{plan_id}/tenders",
)
class PlanTendersResource(PlanBaseResource):
    @json_view()
    def get(self):
        self.request.errors.add("url", "method", "Method not allowed")
        self.request.errors.status = 405
        raise json_error(self.request)

    @json_view(
        content_type="application/json",
        validators=(validate_json_data,),
        permission="create_tender_from_plan",
    )
    def post(self):
        plan = self.request.validated["plan"]
        tender = self.request.validated["json_data"]

        self.state.plan_tender_on_post(plan, tender)

        # create tender POST /tenders
        headers = self.request.headers
        headers["Content-type"] = "application/json; charset=utf-8"
        sub_req = Request.blank(
            f'/api/{VERSION}/tenders',
            environ={"REQUEST_METHOD": "POST"},
            headers=headers,
        )
        sub_req.body = self.request.body
        response = self.request.invoke_subrequest(sub_req, use_tweens=True)
        if "errors" in response.json:
            self.request.response.status = response.status
            return response.json

        tender_id = response.json["data"]["id"]
        tender_location = response.headers["Location"]
        tender_json = response.json

        # update tender
        tender = self.request.registry.mongodb.tenders.get(tender_id)
        plans = [{"id": plan["_id"]}]
        tender["plans"] = plans
        self.request.registry.mongodb.tenders.save(tender)

        # save plan
        plan["tender_id"] = tender_id
        self.state.on_patch(self.request.validated["plan_src"], plan)
        save_plan(self.request)

        self.request.response.status = 201
        self.request.response.headers["Location"] = tender_location
        tender_json["data"]["plans"] = plans
        return tender_json
