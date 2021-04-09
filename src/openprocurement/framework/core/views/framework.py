# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    APIResourceListing,
    APIResourcePaginatedListing,
    json_view,
    generate_id,
    get_now,
    set_ownership,
    context_unpack,
    upload_objects_documents,
)
from openprocurement.framework.core.design import (
    FRAMEWORK_FIELDS,
    SUBMISSION_CHANGES_FIELDS,
    QUALIFICATION_CHANGES_FIELDS,
    frameworks_by_dateModified_view,
    frameworks_test_by_dateModified_view,
    frameworks_by_local_seq_view,
    frameworks_test_by_local_seq_view,
    frameworks_real_by_local_seq_view,
    frameworks_real_by_dateModified_view,
    # submission
    submissions_by_framework_id_view,
    submissions_by_framework_id_total_view,
    # qualification
    qualifications_by_framework_id_view,
    qualifications_by_framework_id_total_view,
)
from openprocurement.framework.core.utils import (
    frameworksresource,
    generate_framework_pretty_id,
    save_framework,
    obj_serialize,
)
from openprocurement.framework.core.validation import validate_framework_data

VIEW_MAP = {
    "": frameworks_real_by_dateModified_view,
    "test": frameworks_test_by_dateModified_view,
    "_all_": frameworks_by_dateModified_view,

}
CHANGES_VIEW_MAP = {
    "": frameworks_real_by_local_seq_view,
    "test": frameworks_test_by_local_seq_view,
    "_all_": frameworks_by_local_seq_view,
}
FEED = {"dateModified": VIEW_MAP, "changes": CHANGES_VIEW_MAP}


@frameworksresource(
    name="Frameworks",
    path="/frameworks",
    description="See https://standard.open-contracting.org/latest/en/guidance/map/related_processes/",
)
class FrameworkResource(APIResourceListing):
    def __init__(self, request, context):
        super(FrameworkResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = FRAMEWORK_FIELDS
        self.serialize_func = obj_serialize
        self.object_name_for_listing = "Frameworks"
        self.log_message_id = "framework_list_custom"
        self.db = request.registry.databases.frameworks

    @json_view(
        content_type="application/json",
        permission="create_framework",
        validators=(
                validate_framework_data,
        )
    )
    def post(self):
        """This API request is targeted to creating new Frameworks by procuring organizations.

        Creating new Framework
        -------------------

        Example request to create framework:

        .. sourcecode:: http

            POST /frameworks HTTP/1.1
            Host: example.com
            Accept: application/json

            {
              "data": {
                "description": "Назва предмета закупівлі",
                "classification": {
                  "scheme": "ДК021",
                  "description": "Mustard seeds",
                  "id": "03111600-8"
                },
                "title": "Узагальнена назва закупівлі",
                "qualificationPeriod": {
                  "endDate": "2021-02-07T14:33:22.129267+02:00"
                },
                "additionalClassifications": [
                  {
                    "scheme": "ДК003",
                    "id": "17.21.1",
                    "description": "папір і картон гофровані, паперова й картонна тара"
                  }
                ],
                "procuringEntity": {
                  "contactPoint": {
                    "telephone": "0440000000",
                    "email": "aa@aa.com",
                    "name": "Назва організації(ЦЗО)"
                  },
                  "identifier": {
                    "scheme": "UA-EDR",
                    "id": "40996564",
                    "legalName": "Назва організації(ЦЗО)"
                  },
                  "kind": "central",
                  "name": "Повна назва юридичної організації.",
                  "address": {
                    "countryName": "Україна",
                    "postalCode": "01220",
                    "region": "м. Київ",
                    "streetAddress": "вул. Банкова, 11, корпус 1",
                    "locality": "м. Київ"
                  }
                }
              }
            }

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 201 Created
            Location: http://localhost/api/0.1/frameworks/40b48e4878534db1bf228d5928f8f1d9
            Content-Type: application/json

            {
                "data": {
                    "status": "draft",
                    "description": "Назва предмета закупівлі",
                    "classification": {
                      "scheme": "ДК021",
                      "description": "Mustard seeds",
                      "id": "03111600-8"
                    },
                    "prettyID": "UA-F-2020-09-08-000001",
                    "qualificationPeriod": {
                      "endDate": "2021-02-07T14:33:22.129267+02:00"
                    },
                    "frameworkType": "electronicCatalogue",
                    "dateModified": "2020-09-08T01:00:00+03:00",
                    "date": "2020-09-08T01:00:00+03:00",
                    "additionalClassifications": [
                      {
                        "scheme": "ДК003",
                        "id": "17.21.1",
                        "description": "папір і картон гофровані, паперова й картонна тара"
                      }
                    ],
                    "procuringEntity": {
                      "contactPoint": {
                        "email": "aa@aa.com",
                        "telephone": "0440000000",
                        "name": "Назва організації(ЦЗО)"
                      },
                      "identifier": {
                        "scheme": "UA-EDR",
                        "id": "40996564",
                        "legalName": "Назва організації(ЦЗО)"
                      },
                      "name": "Повна назва юридичної організації.",
                      "kind": "central",
                      "address": {
                        "countryName": "Україна",
                        "postalCode": "01220",
                        "streetAddress": "вул. Банкова, 11, корпус 1",
                        "region": "м. Київ",
                        "locality": "м. Київ"
                      }
                    },
                    "owner": "broker",
                    "title": "Узагальнена назва закупівлі",
                    "id": "40b48e4878534db1bf228d5928f8f1d9"
                }
            }
        """
        framework_id = generate_id()
        framework = self.request.validated["framework"]
        framework.id = framework_id
        if not framework.get("prettyID"):
            framework.prettyID = generate_framework_pretty_id(get_now(), self.db, self.server_id)
        access = set_ownership(framework, self.request)
        upload_objects_documents(
            self.request, framework,
            route_kwargs={"framework_id": framework.id},
            route_prefix=framework["frameworkType"]
        )
        self.request.validated["framework"] = framework
        self.request.validated["framework_src"] = {}
        if save_framework(self.request):
            self.LOGGER.info(
                "Created framework {} ({})".format(framework_id, framework.prettyID),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "framework_create"},
                    {"framework_id": framework_id, "prettyID": framework.prettyID,
                     "framework_mode": framework.mode},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Frameworks".format(framework.frameworkType), framework_id=framework_id
            )
            return {"data": framework.serialize(framework.status), "access": access}


@frameworksresource(
    name='Framework Submissions',
    path='/frameworks/{framework_id}/submissions',
    description="",
)
class FrameworkSubmissionRequestResource(APIResourcePaginatedListing):
    obj_id_key = "framework_id"
    serialize_method = obj_serialize
    default_fields = set(SUBMISSION_CHANGES_FIELDS) | {"id", "dateModified"}
    views = {
        "": submissions_by_framework_id_view,
    }
    views_total = {
        "": submissions_by_framework_id_total_view,
    }

    def __init__(self, request, context):
        super(FrameworkSubmissionRequestResource, self).__init__(request, context)
        # params for listing
        self.db = request.registry.databases.submissions


@frameworksresource(
    name='Framework Qualifications',
    path='/frameworks/{framework_id}/qualifications',
    description="",
)
class FrameworkQualificationRequestResource(APIResourcePaginatedListing):
    obj_id_key = "framework_id"
    serialize_method = obj_serialize
    default_fields = set(QUALIFICATION_CHANGES_FIELDS) | {"id", "dateModified"}
    views = {
        "": qualifications_by_framework_id_view,
    }
    views_total = {
        "": qualifications_by_framework_id_total_view,
    }

    def __init__(self, request, context):
        super(FrameworkQualificationRequestResource, self).__init__(request, context)
        # params for listing
        self.db = request.registry.databases.qualifications
