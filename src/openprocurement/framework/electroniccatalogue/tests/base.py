# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta

import standards

from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import get_now
from openprocurement.framework.core.tests.base import BaseCoreWebTest
from openprocurement.framework.electroniccatalogue.models import ElectronicCatalogueFramework
from openprocurement.framework.electroniccatalogue.tests.periods import PERIODS


def get_cpb_ids_by_activity():
    """
    Get first active: True and first active: False cpb from standards
    To test rule that only CPB that have "active": true in standards can create electronicCatalogue framework
    https://prozorroukr.github.io/standards/organizations/authorized_cpb.json

    :return: active cpb id, non active cpb id
    """
    active_cpb = []
    non_active_cpb = []
    authorized_cpb = standards.load("organizations/authorized_cpb.json")
    for cpb in authorized_cpb:
        if not active_cpb or not non_active_cpb:
            id_ = cpb["identifier"]["id"]
            active_cpb.append(id_) if cpb["active"] else non_active_cpb.append(id_)
    return active_cpb[0], non_active_cpb[0]


active_cpb_id, non_active_cpb_id = get_cpb_ids_by_activity()

now = get_now()
test_electronicCatalogue_data = {
    "procuringEntity": {
        "contactPoint": {
            "telephone": u"0440000000",
            "name": u"Назва організації(ЦЗО)",
            "email": u"aa@aa.com"
        },
        "identifier": {
            "scheme": u"UA-EDR",
            "id": active_cpb_id,
            "legalName": u"Назва організації(ЦЗО)"
        },
        "kind": u"central",
        "address": {
            "countryName": u"Україна",
            "postalCode": u"01220",
            "region": u"м. Київ",
            "streetAddress": u"вул. Банкова, 11, корпус 1",
            "locality": u"м. Київ"
        },
        "name": u"Повна назва юридичної організації."
    },
    "additionalClassifications": [
        {
            "scheme": u"ДК003",
            "id": u"17.21.1",
            "description": u"папір і картон гофровані, паперова й картонна тара"
        }
    ],
    "classification": {
        "scheme": u"ДК021",
        "description": u"Mustard seeds",
        "id": u"03111600-8"
    },
    "title": u"Узагальнена назва закупівлі",
    "description": u"Назва предмета закупівлі",
    "qualificationPeriod": {"endDate": (now + timedelta(days=60)).isoformat()}
}

test_electronicCatalogue_documents = [
    {
        "hash": "md5:00000000000000000000000000000000",
        "title": "framework.doc",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/f76fd74118794d3099163fb571f7d374?KeyID=a8968c46&Signature=enQ0CbN82KUq2UF35XE5AoHQp4akyyXL8a18JJhKTwe2gBZouJQV8JxVPA%2FirPrEZoN6LsYF%2FmqpcaFFaHGnAg%253D%253D",
        "format": "application/msword",
        "datePublished": "2020-09-08T01:00:00+03:00",
        "id": "cd52b90af77e4f5b8cb0f210e83987b5",
        "dateModified": "2020-09-08T01:00:00+03:00"
    },
    {
        "hash": "md5:00000000000000000000000000000000",
        "title": "framework_additional_docs.doc",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/abf06db1635b48e0819cb258b3fc1179?KeyID=a8968c46&Signature=%2FsMVClawScZwgZdy%2FXVGRQpaN4KUmLiGNRpyNxh%252BTLvtTMwaKtLdizgNWNevCqZqDTjBmKDHGXnfMG8d2%252BIrBg%253D%253D",
        "format": "application/msword",
        "datePublished": "2020-09-08T01:00:00+03:00",
        "id": "3fe9486c38a1473ca201e42ebbf9b648",
        "dateModified": "2020-09-08T01:00:00+03:00"
    },
    {
        "hash": "md5:00000000000000000000000000000000",
        "title": "framework_additional_docs.doc",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/4cf75d2a81c64711bdccbed55bcb10fc?KeyID=a8968c46&Signature=ijDPle6V3lQQZjOoEIB0hbFXJgsEHcq26VnDeLHfVAUeBoBXUCkV1rGOvL%252BXpX2f4ZeUMwJ5XXqw6SikMBU%2FDQ%253D%253D",
        "format": "application/msword",
        "datePublished": "2020-09-08T01:00:00+03:00",
        "id": "3fe9486c38a1473ca201e42ebbf9b648",
        "dateModified": "2020-09-08T01:00:00+03:00"
    }
]


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    initial_auth = ("Basic", ("broker", ""))


class BaseElectronicCatalogueWebTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_electronicCatalogue_data
    framework_class = ElectronicCatalogueFramework
    docservice = False
    periods = PERIODS

    def create_framework(self):
        data = deepcopy(self.initial_data)

        response = self.app.post_json("/frameworks", {"data": data})
        self.framework_document = response.json["data"]
        self.framework_token = response.json["access"]["token"]
        self.framework_id = response.json["data"]["id"]


class ElectronicCatalogueContentWebTest(BaseElectronicCatalogueWebTest):
    initial_status = None

    def setUp(self):
        super(ElectronicCatalogueContentWebTest, self).setUp()
        self.create_framework()


class BaseDSElectronicCatalogueContentWebTest(ElectronicCatalogueContentWebTest):
    docservice = True
