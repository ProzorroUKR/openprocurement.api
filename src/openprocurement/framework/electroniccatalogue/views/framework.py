# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    APIResource,
    json_view,
    context_unpack,
    raise_operation_error,
)
from openprocurement.framework.core.utils import (
    frameworksresource,
    apply_patch,
    save_framework,
)
from openprocurement.framework.core.validation import validate_patch_framework_data
from openprocurement.framework.electroniccatalogue.utils import calculate_framework_periods, check_status
from openprocurement.framework.electroniccatalogue.validation import (
    validate_ec_framework_patch_status,
    validate_qualification_period_duration
)

AGREEMENT_DEPENDENT_FIELDS = ("qualificationPeriod", "procuringEntity")


@frameworksresource(
    name="electronicCatalogue:Frameworks",
    path="/frameworks/{framework_id}",
    frameworkType="electronicCatalogue",
    description="See https://standard.open-contracting.org/latest/en/guidance/map/related_processes/",
)
class FrameworkResource(APIResource):
    @json_view(permission="view_framework")
    def get(self):
        """Framework Read

        Get Framework
        ----------

        Example request to get framework:

        .. sourcecode:: http

            GET /frameworks/40b48e4878534db1bf228d5928f8f1d9 HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
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
        if self.request.authenticated_role == "chronograph":
            framework_data = self.context.serialize("chronograph_view")
        else:
            framework_data = self.context.serialize(self.context.status)
        return {"data": framework_data}

    @json_view(
        content_type="application/json",
        validators=(
                validate_patch_framework_data,
                validate_ec_framework_patch_status,
        ),
        permission="edit_framework",
    )
    def patch(self):
        """Framework Edit (partial)


        .. sourcecode:: http

            PATCH /frameworks/40b48e4878534db1bf228d5928f8f1d9?acc_token=7c6a46e300bb41438ef626232028950b HTTP/1.1
            Host: example.com
            Accept: application/json

            {
              "data": {
                "qualificationPeriod": {
                  "endDate": "2021-02-22T14:33:22.129267+02:00"
                },
                "procuringEntity": {
                  "contactPoint": {
                    "email": "ab@aa.com",
                    "name": "зміна",
                    "telephone": "0440000002"
                  }
                },
                "description": "Назва предмета закупівлі1"
              }
            }

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
              "data": {
                "status": "active",
                "description": "Назва предмета закупівлі1",
                "classification": {
                  "scheme": "ДК021",
                  "description": "Mustard seeds",
                  "id": "03111600-8"
                },
                "title": "updated in draft status",
                "enquiryPeriod": {
                  "startDate": "2020-09-08T01:00:00+03:00",
                  "endDate": "2020-09-23T00:00:00+03:00"
                },
                "qualificationPeriod": {
                  "startDate": "2020-09-23T00:00:00+03:00",
                  "endDate": "2021-02-22T14:33:22.129267+02:00"
                },
                "prettyID": "UA-F-2020-09-08-000001",
                "period": {
                  "startDate": "2020-09-08T01:00:00+03:00",
                  "endDate": "2021-01-23T00:00:00+02:00"
                },
                "frameworkType": "electronicCatalogue",
                "date": "2020-09-08T01:00:00+03:00",
                "additionalClassifications": [
                  {
                    "scheme": "ДК003",
                    "id": "17.21.1",
                    "description": "папір і картон гофровані, паперова й картонна тара"
                  }
                ],
                "next_check": "2020-10-07T00:00:00+03:00",
                "procuringEntity": {
                  "contactPoint": {
                    "email": "ab@aa.com",
                    "telephone": "0440000002",
                    "name": "зміна"
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
                "dateModified": "2020-09-08T01:00:00+03:00",
                "id": "40b48e4878534db1bf228d5928f8f1d9"
              }
            }
        """
        framework = self.context
        if self.request.authenticated_role == "chronograph":
            check_status(self.request)
            save_framework(self.request)
        else:
            if self.request.validated["data"].get("status") not in ("draft", "active"):
                raise_operation_error(
                    self.request, "Can't switch to {} status".format(self.request.validated["data"].get("status"))
                )
            if self.request.validated["data"].get("status") == "active":
                model = self.request.context._fields["qualificationPeriod"]
                calculate_framework_periods(self.request, model)
                validate_qualification_period_duration(self.request, model)

            apply_patch(self.request, src=self.request.validated["framework_src"], obj_name="framework")

            if (
                    any([f in self.request.validated["json_data"] for f in AGREEMENT_DEPENDENT_FIELDS])
                    and framework.agreementID
                    and self.request.validated["agreement_src"]["status"] == "active"
            ):
                self.update_agreement()

        self.LOGGER.info("Updated framework {}".format(framework.id),
                         extra=context_unpack(self.request, {"MESSAGE_ID": "framework_patch"}))
        # TODO: Change to chronograph_view for chronograph
        return {"data": framework.serialize(framework.status)}

    def update_agreement(self):
        framework = self.request.validated["framework"]

        updated_agreement_data = {
            "period": {
                "startDate": self.request.validated["agreement_src"]["period"]["startDate"],
                "endDate": framework.qualificationPeriod.endDate.isoformat()
            },
            "procuringEntity": framework.procuringEntity
        }
        apply_patch(
            self.request, src=self.request.validated["agreement_src"], data=updated_agreement_data, obj_name="agreement"
        )
        self.LOGGER.info("Updated agreement {}".format(self.request.validated["agreement_src"]["id"]),
                         extra=context_unpack(self.request, {"MESSAGE_ID": "framework_patch"}))
