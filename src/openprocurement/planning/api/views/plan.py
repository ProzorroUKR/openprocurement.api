from logging import getLogger
from cornice.util import json_error
from pyramid.request import Request
from openprocurement.api.constants import VERSION
from openprocurement.api.views.base import BaseResource, MongodbResourceListing
from openprocurement.api.utils import (
    context_unpack, get_now, generate_id, json_view, set_ownership, raise_operation_error,
)
from openprocurement.planning.api.constants import PROCURING_ENTITY_STANDSTILL
from openprocurement.planning.api.models import Milestone
from openprocurement.planning.api.utils import (
    generate_plan_id,
    save_plan,
    apply_patch,
    opresource,
)
from openprocurement.planning.api.validation import (
    validate_patch_plan_data,
    validate_plan_data,
    validate_plan_has_not_tender,
    validate_plan_with_tender,
    validate_plan_not_terminated,
    validate_plan_status_update,
    validate_plan_procurementMethodType_update,
    validate_tender_data,
    validate_plan_scheduled,
)
from openprocurement.tender.core.validation import (
    validate_procurement_type_of_first_stage,
    validate_tender_matches_plan,
    validate_tender_plan_procurement_method_type,
    validate_plan_budget_breakdown,
)
from openprocurement.tender.core.procedure.validation import validate_input_data
from dateorro import calc_working_datetime
import simplejson


LOGGER = getLogger(__name__)


@opresource(
    name="Plans",
    path="/plans",
    description="Planing http://ocds.open-contracting.org/standard/r/1__0__0/en/schema/reference/#planning",
)
class PlansResource(MongodbResourceListing):
    def __init__(self, request, context):
        super(PlansResource, self).__init__(request, context)
        self.listing_name = "Plans"
        self.listing_default_fields = {"dateModified"}
        self.listing_allowed_fields = {"dateCreated", "planID", "dateModified"}
        self.db_listing_method = request.registry.mongodb.plans.list

    @json_view(
        content_type="application/json",
        permission="create_plan",
        validators=(
            validate_plan_data,
        ),
    )
    def post(self):
        plan_id = generate_id()
        plan = self.request.validated["plan"]
        plan.id = plan_id

        plan.planID = generate_plan_id(self.request, self.server_id)
        access = set_ownership(plan, self.request)
        self.request.validated["plan"] = plan
        self.request.validated["plan_src"] = {}
        if save_plan(self.request, insert=True):
            LOGGER.info(
                "Created plan {} ({})".format(plan_id, plan.planID),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "plan_create"}, {"plan_id": plan_id, "planID": plan.planID}
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url("Plan", plan_id=plan_id)
            return {"data": plan.serialize("view"), "access": access}


@opresource(
    name="Plan",
    path="/plans/{plan_id}",
    description="Planing http://ocds.open-contracting.org/standard/r/1__0__0/en/schema/reference/#planning",
)
class PlanResource(BaseResource):
    @json_view(permission="view_plan")
    def get(self):
        plan = self.request.validated["plan"]
        plan_data = plan.serialize("view")
        return {"data": plan_data}

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_plan_data,
            validate_plan_not_terminated,
            validate_plan_procurementMethodType_update,
            validate_plan_status_update,
            validate_plan_with_tender,  # we need this because of the plans created before the statuses release
        ),
        permission="edit_plan",
    )
    def patch(self):
        plan = self.request.validated["plan"]
        src_data = plan.serialize("plain")
        if apply_patch(self.request, src=self.request.validated["plan_src"], save=False):
            self._check_field_change_events(src_data, plan)
            save_plan(self.request)
            LOGGER.info("Updated plan {}".format(plan.id),
                        extra=context_unpack(self.request, {"MESSAGE_ID": "plan_patch"}))
        return {"data": plan.serialize("view")}

    def _check_field_change_events(self, src_data, plan):
        src_identifier = src_data["procuringEntity"]["identifier"]
        identifier = plan["procuringEntity"]["identifier"]
        if src_identifier["scheme"] != identifier["scheme"] or src_identifier["id"] != identifier["id"]:
            if any(m["status"] in Milestone.ACTIVE_STATUSES for m in src_data.get("milestones", "")):
                standstill_end = calc_working_datetime(get_now(), PROCURING_ENTITY_STANDSTILL)
                if standstill_end > plan["tender"]["tenderPeriod"]["startDate"]:
                    raise_operation_error(
                        self.request,
                        "Can't update procuringEntity later than {} "
                        "business days before tenderPeriod.StartDate".format(
                            PROCURING_ENTITY_STANDSTILL.days
                        )
                    )
                # invalidate active milestones and update milestone.dateModified
                plan.dateModified = get_now()
                plan.is_modified = False
                for m in plan.milestones:
                    if m.status in Milestone.ACTIVE_STATUSES:
                        m.status = Milestone.STATUS_INVALID
                        m.dateModified = plan.dateModified
                        

@opresource(name="Plan Tenders", path="/plans/{plan_id}/tenders", description="Tender creation based on a plan")
class PlanTendersResource(BaseResource):
    @json_view()
    def get(self):
        self.request.errors.add("url", "method", "Method not allowed")
        self.request.errors.status = 405
        raise json_error(self.request)

    @json_view(
        content_type="application/json",
        validators=(
            validate_plan_scheduled,
            validate_plan_has_not_tender,  # we need this because of the plans created before the statuses release
            validate_tender_data,
            validate_tender_plan_procurement_method_type,
            validate_tender_matches_plan,
            validate_plan_budget_breakdown,
        ),
        permission="create_tender_from_plan",
    )
    def post(self):
        plan = self.request.validated["plan"]
        plans = [{"id": plan.id}]
        tender = self.request.validated["tender_data"]
        tender_config = self.request.validated["tender_config"]

        # create tender POST /tenders
        headers = self.request.headers
        headers["Content-type"] = "application/json; charset=utf-8"
        sub_req = Request.blank(f'/api/{VERSION}/tenders',
                                environ={"REQUEST_METHOD": "POST"},
                                headers=headers)
        sub_req.body = simplejson.dumps({
            "data": tender,
            "config": tender_config,
        }).encode()
        response = self.request.invoke_subrequest(sub_req, use_tweens=True)
        if "errors" in response.json:
            self.request.response.status = response.status
            return response.json

        tender_id = response.json["data"]["id"]
        tender_location = response.headers["Location"]
        tender_json = response.json

        # update tender
        tender = self.request.registry.mongodb.tenders.get(tender_id)

        tender["plans"] = plans
        self.request.registry.mongodb.tenders.save(tender)

        # save plan
        plan.tender_id = tender_id
        save_plan(self.request)

        self.request.response.status = 201
        self.request.response.headers["Location"] = tender_location
        tender_json["data"]["plans"] = plans
        return tender_json
