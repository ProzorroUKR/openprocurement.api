# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta

from dateutil.parser import parse
from tests.base.constants import MOCK_DATETIME

from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.base import BaseCoreWebTest

# CPB that have "active": true in standards https://prozorroukr.github.io/standards/organizations/authorized_cpb.json
valid_identifier_id = "40996564"

now = get_now()
test_electronicCatalogue_data = {
    "procuringEntity": {
        "contactPoint": {
            "telephone": "0440000000",
            "name": "Назва організації(ЦЗО)",
            "email": "aa@aa.com"
        },
        "identifier": {
            "scheme": "UA-EDR",
            "id": valid_identifier_id,
            "legalName": "Назва організації(ЦЗО)"
        },
        "kind": "central",
        "address": {
            "countryName": "Україна",
            "postalCode": "01220",
            "region": "м. Київ",
            "streetAddress": "вул. Банкова, 11, корпус 1",
            "locality": "м. Київ"
        },
        "name": "Повна назва юридичної організації."
    },
    "additionalClassifications": [
        {
            "scheme": "ДК003",
            "id": "17.21.1",
            "description": "папір і картон гофровані, паперова й картонна тара"
        }
    ],
    "classification": {
        "scheme": "ДК021",
        "description": "Mustard seeds",
        "id": "03111600-8"
    },
    "title": "Узагальнена назва закупівлі",
    "description": "Назва предмета закупівлі",
    "qualificationPeriod": {"endDate": (parse(MOCK_DATETIME) + timedelta(days=60)).isoformat()}
}


class BaseElectronicCatalogueTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_auth = ("Basic", ("broker", ""))


class BaseElectronicCatalogueWebTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_electronicCatalogue_data
    docservice = False

    def setUp(self):
        super(BaseElectronicCatalogueWebTest, self).setUp()
        self.create_framework()

    def create_framework(self):
        data = deepcopy(self.initial_data)

        response = self.app.post_json("/frameworks", {"data": data})
        framework = response.json["data"]
        self.framework_token = response.json["access"]["token"]
        self.framework_id = framework["id"]

    def tearDown(self):
        del self.db[self.framework_id]
        super(BaseElectronicCatalogueWebTest, self).tearDown()
