# -*- coding: utf-8 -*-
from logging import getLogger
from cornice.util import json_error
from openprocurement.api.utils import (
    context_unpack, get_now, generate_id, json_view, set_ownership,
    APIResourceListing, raise_operation_error,
)
from openprocurement.planning.api.constants import PROCURING_ENTITY_STANDSTILL
from openprocurement.planning.api.models import Milestone
from openprocurement.planning.api.design import (
    FIELDS,
    plans_by_dateModified_view,
    plans_real_by_dateModified_view,
    plans_test_by_dateModified_view,
    plans_by_local_seq_view,
    plans_real_by_local_seq_view,
    plans_test_by_local_seq_view,
)
from openprocurement.planning.api.utils import (
    generate_plan_id,
    save_plan,
    plan_serialize,
    apply_patch,
    opresource,
    APIResource,
)
from openprocurement.planning.api.validation import (
    validate_patch_plan_data,
    validate_plan_data,
    validate_plan_has_not_tender,
    validate_plan_with_tender,
    validate_plan_not_terminated,
    validate_plan_status_update,
    validate_plan_procurementMethodType_update,
    validate_patch_milestone_data,
)
from openprocurement.tender.core.validation import (
    validate_tender_data,
    validate_procurement_type_of_first_stage,
    validate_tender_matches_plan,
    validate_tender_plan_procurement_method_type,
    validate_plan_budget_breakdown,
)
from openprocurement.tender.core.views.tender import TendersResource
from dateorro import calc_working_datetime


LOGGER = getLogger(__name__)
VIEW_MAP = {
    "": plans_real_by_dateModified_view,
    "test": plans_test_by_dateModified_view,
    "_all_": plans_by_dateModified_view,
}
CHANGES_VIEW_MAP = {
    "": plans_real_by_local_seq_view,
    "test": plans_test_by_local_seq_view,
    "_all_": plans_by_local_seq_view,
}
FEED = {"dateModified": VIEW_MAP, "changes": CHANGES_VIEW_MAP}


@opresource(
    name="Plans",
    path="/plans",
    description="Planing http://ocds.open-contracting.org/standard/r/1__0__0/en/schema/reference/#planning",
)
class PlansResource(APIResourceListing):
    def __init__(self, request, context):
        super(PlansResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = FIELDS
        self.serialize_func = plan_serialize
        self.object_name_for_listing = "Plans"
        self.log_message_id = "plan_list_custom"
        self.db = request.registry.databases.plans

    @json_view(
        content_type="application/json",
        permission="create_plan",
        validators=(
            validate_plan_data,
        ),
    )
    def post(self):
        """This API request is targeted to creating new Plan by procuring organizations.

        Creating new Plan

        -------------------

        Example request to create plan:

        .. sourcecode:: http

            POST /plans HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "tender": {
                        "procurementMethod": "допорогові закупівлі",
                        "tenderPeriod": {
                            "startDate": "2015-05-09T23:11:39.720908+03:00"
                        }
                    },
                    "items": [
                        {
                            "deliveryDate": {
                                "endDate": "2015-05-11T23:11:39.721063+03:00"
                            },
                            "additionalClassifications": [
                                {
                                    "scheme": "ДКПП",
                                    "id": "28.29.39-10.00",
                                    "description": "Прилади контролювання маси та прилади контрольні автоматичні з максимальною масою зважування не більше ніж 5000 кг"
                                }
                            ],
                            "unit": {
                                "code": "KGM",
                                "name": "кг"
                            },
                            "classification": {
                                "scheme": "CPV",
                                "description": "Роботи з будування пневматичних будівель",
                                "id": "45217000-1"
                            },
                            "quantity": 760
                        }
                    ],
                    "procuringEntity": {
                        "identifier": {
                            "scheme": "UA-EDR",
                            "id": "111983",
                            "legalName": "ДП Державне Уравління Справами"
                        },
                        "name": "ДУС"
                    },
                    "budget": {
                        "project": {
                            "name": "proj_name",
                            "id": "proj_id"
                        },
                        "amount": 10000,
                        "amountNet": 12222,
                        "id": "budget_id",
                        "description": "budget_description"
                    }
                }
            }

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 201 Created
            Location: http://localhost/api/0.10/plans/84582807b5654bee9e216adb05e57d39
            Content-Type: application/json

            {
                "access": {
                    "token": "e4c75de4320649a4bbbdfa180e7a9ef2"
                },
                "data": {
                    "items": [
                        {
                            "classification": {
                                "scheme": "CPV",
                                "description": "Роботи з будування пневматичних будівель",
                                "id": "45217000-1"
                            },
                            "additionalClassifications": [
                                {
                                    "scheme": "ДКПП",
                                    "id": "28.29.39-10.00",
                                    "description": "Прилади контролювання маси та прилади контрольні"
                                },
                                {
                                    "scheme": "КЕКВ",
                                    "id": "123",
                                    "description": "-"
                                }
                            ],
                            "deliveryDate": {
                                "endDate": "2015-05-11T23:11:39.721063+03:00"
                            },
                            "id": "8cd4abfd0bbb489a83a81dec1393ab8d",
                            "unit": {
                                "code": "KGM",
                                "name": "кг"
                            },
                            "quantity": 760
                        }
                    ],
                    "planID": "UA-2015-11-26-000001",
                    "budget": {
                        "amountNet": 12222,
                        "description": "budget_description",
                        "project": {
                            "id": "proj_id",
                            "name": "proj_name"
                        },
                        "currency": "UAH",
                        "amount": 10000,
                        "id": "budget_id"
                    },
                    "procuringEntity": {
                        "identifier": {
                            "scheme": "UA-EDR",
                            "id": "111983",
                            "legalName": "ДП Державне Уравління Справами"
                        },
                        "name": "ДУС"
                    },
                    "tender": {
                        "procurementMethod": "open",
                        "tenderPeriod": {
                            "startDate": "2015-05-09T23:11:39.720908+03:00"
                        }
                    },
                    "id": "ac658c4ff7ab47dea27e32d15a655ddb"
                }
}
        """
        plan_id = generate_id()
        plan = self.request.validated["plan"]
        plan.id = plan_id

        plan.planID = generate_plan_id(get_now(), self.db, self.server_id)
        access = set_ownership(plan, self.request)
        self.request.validated["plan"] = plan
        self.request.validated["plan_src"] = {}
        if save_plan(self.request):
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
class PlanResource(APIResource):
    @json_view(permission="view_plan")
    def get(self):
        """Plan Read


        Get Plan
        ----------

        Example request to get tender:

        .. sourcecode:: http

            GET /plans/62179f8f94a246239268750a6eb0e53f HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {
                    "items": [
                        {
                            "classification": {
                                "scheme": "CPV",
                                "description": "Роботи з будування пневматичних будівель",
                                "id": "45217000-1"
                            },
                            "additionalClassifications": [
                                {
                                    "scheme": "ДКПП",
                                    "id": "28.29.39-10.00",
                                    "description": "Прилади контролювання маси та прилади контрольні автоматичні з максимальною масою зважування не більше ніж 5000 кг"
                                }
                            ],
                            "deliveryDate": {
                                "endDate": "2015-05-11T23:11:39.721063+03:00"
                            },
                            "id": "62179f8f94a246239268750a6eb0e53f",
                            "unit": {
                                "code": "KGM",
                                "name": "кг"
                            },
                            "quantity": 760
                        }
                    ],
                    "planID": "UA-2015-11-16-000001",
                    "budget": {
                        "project": {
                            "id": "proj_id",
                            "name": "proj_name"
                        },
                        "amount": 10000,
                        "amountNet": 12222,
                        "id": "budget_id",
                        "description": "budget_description"
                    },
                    "id": "9b07a65c921e47e7ab3fb9eafb3f44a5",
                    "procuringEntity": {
                        "identifier": {
                            "scheme": "UA-EDR",
                            "id": "111983",
                            "legalName": "ДП Державне Уравління Справами"
                        },
                        "name": "ДУС"
                    },
                    "tender": {
                        "procurementMethod": "допорогові закупівлі",
                        "tenderPeriod": {
                            "startDate": "2015-05-09T23:11:39.720908+03:00"
                        }
                    },
                    "dateModified": "2015-11-16T16:33:02.915600+02:00"
                }
            }

        """
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
        """Plan Edit (partial)

        For example here is how procuring entity can change name:

        .. sourcecode:: http

            PATCH /plans/62179f8f94a246239268750a6eb0e53f HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "procuringEntity": {
                        "identifier": {
                            "legalName": "ДП Державне Уравління Справами11"
                        },
                        "name": "ДУС"
                    },
                    "budget": {
                        "project": {
                            "name": "proj_name",
                            "id": "proj_id"
                        },
                        "amount": 10020,
                        "amountNet": 22222,
                        "id": "budget_id",
                        "description": "budget_description"
                    }
                }
            }

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

        """
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
                plan.modified = False
                for m in plan.milestones:
                    if m.status in Milestone.ACTIVE_STATUSES:
                        m.status = Milestone.STATUS_INVALID
                        m.dateModified = plan.dateModified
                        

@opresource(name="Plan Tenders", path="/plans/{plan_id}/tenders", description="Tender creation based on a plan")
class PlanTendersResource(TendersResource):
    @json_view()
    def get(self):
        self.request.errors.add("url", "method", "Method not allowed")
        self.request.errors.status = 405
        raise json_error(self.request)

    @json_view(
        content_type="application/json",
        validators=(
            validate_plan_not_terminated,
            validate_plan_has_not_tender,  # we need this because of the plans created before the statuses release
            validate_tender_data,
            validate_procurement_type_of_first_stage,
            validate_tender_plan_procurement_method_type,
            validate_tender_matches_plan,
            validate_plan_budget_breakdown,
        ),
        permission="create_tender_from_plan",
    )
    def post(self):
        plan = self.request.validated["plan"]
        tender = self.request.validated["tender"]
        tender.link_plan(plan.id)
        result = super(PlanTendersResource, self).post()
        if not self.request.errors:
            plan.tender_id = tender.id
            save_plan(self.request)

        return result
