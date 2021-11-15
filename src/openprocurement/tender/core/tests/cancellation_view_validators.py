from openprocurement.api.tests.base import singleton_app, app
from openprocurement.tender.belowthreshold.tests.base import (
    test_organization,
    test_tender_data as belowthreshold_tender_data,
    test_cancellation,
    test_complaint,
)
from openprocurement.tender.openua.tests.base import test_tender_data as ua_tender_data
from openprocurement.tender.cfaselectionua.tests.base import (
    test_tender_data as cfaselection_tender_data,
    test_lots as cfaselection_lots,
)
from openprocurement.tender.openuadefense.tests.base import test_tender_data as defense_tender_data
from openprocurement.tender.simpledefense.tests.base import test_tender_data as simpledefense_tender_data
from openprocurement.tender.openeu.tests.base import test_tender_data as eu_tender_data
from openprocurement.tender.esco.tests.base import test_tender_data as esco_tender_data
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_data_ua as cd_tender_data_ua,
    test_tender_data_eu as cd_tender_data_eu,
    test_tender_stage2_data_ua as cd_tender_stage2_data_ua,
    test_tender_stage2_data_eu as cd_tender_stage2_data_eu,
)
from openprocurement.tender.cfaua.tests.base import (
    test_tender_data as cfaua_tender_data,
    test_lots as cfa_lots,
)
from openprocurement.tender.limited.tests.base import (
    test_tender_data as limited_tender_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
)
from datetime import timedelta
from openprocurement.api.utils import raise_operation_error, get_now
from openprocurement.api.constants import RELEASE_2020_04_19
from copy import deepcopy
import mock
import pytest


def post_tender(app, data):
    if data["procurementMethodType"] == "aboveThresholdUA.defense":
        release_simpledef_date = get_now() + timedelta(days=1)
    else:
        release_simpledef_date = get_now() - timedelta(days=1)
    release_simpledef_patcher = mock.patch("openprocurement.tender.core.validation.RELEASE_SIMPLE_DEFENSE_FROM",
                                          release_simpledef_date)

    release_simpledef_patcher.start()
    if data["procurementMethodType"] in (STAGE_2_EU_TYPE, STAGE_2_UA_TYPE):
        app.authorization = ("Basic", ("competitive_dialogue", ""))
    else:
        app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(data)
    response = app.post_json("/tenders", dict(data=test_data))
    release_simpledef_patcher.stop()
    assert response.status == "201 Created"
    return response.json["data"], response.json["access"]["token"]


# TENDER COMPLAINTS
cfaua_tender_data = dict(**cfaua_tender_data)
cfaua_tender_data["lots"] = cfa_lots

cfaselection_tender_data = dict(**cfaselection_tender_data)
cfaselection_tender_data["lots"] = cfaselection_lots

procedures = (
    belowthreshold_tender_data,
    cfaselection_tender_data,
    cfaua_tender_data,
    cd_tender_data_ua,
    cd_tender_data_eu,
    cd_tender_stage2_data_ua,
    cd_tender_stage2_data_eu,
    esco_tender_data,
    limited_tender_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
    ua_tender_data,
    eu_tender_data,
    defense_tender_data,
    simpledefense_tender_data,
)


@pytest.mark.parametrize("tender_data", procedures)
def test_post_cancellation(app, tender_data):
    """
    posting an active cancellation should trigger the validation
    """
    tender, tender_token = post_tender(app, tender_data)

    def mock_validate(request, cancellation=None):
        raise_operation_error(request, "hello")

    if get_now() < RELEASE_2020_04_19:
        with mock.patch(
            "openprocurement.tender.core.validation.validate_absence_of_pending_accepted_satisfied_complaints",
            mock_validate
        ):
            cancellation = dict(**test_cancellation)
            cancellation.update({"status": "active"})
            response = app.post_json(
                "/tenders/{}/cancellations?acc_token={}".format(tender["id"], tender_token),
                {"data": cancellation},
                status=403
            )
            assert response.json == {'status': 'error', 'errors': [
                {'description': 'hello', 'location': 'body', 'name': 'data'}]}


@pytest.mark.parametrize("tender_data", procedures)
def test_patch_cancellation(app, tender_data):
    """
    only patching to active should trigger the validation
    """
    tender, tender_token = post_tender(app, tender_data)

    def mock_validate(request, cancellation=None):
        raise_operation_error(request, "hello")

    with mock.patch(
        "openprocurement.tender.core.validation.validate_absence_of_pending_accepted_satisfied_complaints",
        mock_validate
    ):
        if get_now() < RELEASE_2020_04_19:
            response = app.post_json(
                "/tenders/{}/cancellations?acc_token={}".format(tender["id"], tender_token),
                {"data": test_cancellation},
            )
            assert response.status_code == 201
            cancellation = response.json["data"]

            response = app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(tender["id"], cancellation["id"], tender_token),
                {"data": {
                    "reason": "another reason",
                }},
            )
            assert response.status_code == 200

            response = app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(tender["id"], cancellation["id"], tender_token),
                {"data": {
                    "status": "active",
                }},
                status=403
            )
            assert response.json == {'status': 'error', 'errors': [
                {'description': 'hello', 'location': 'body', 'name': 'data'}]}


def test_post_cancellation_openeu(app):
    """
    test without mocking (just in case)
    """
    tender, tender_token = post_tender(app, eu_tender_data)
    tender_data = app.app.registry.db.get(tender["id"])
    app.tender_id = tender["id"]

    # award complaint
    complaint = deepcopy(test_complaint)
    tender_data["awards"] = [
        {
            "id": "0" * 32,
            "bid_id": "0" * 32,
            "suppliers": [test_organization],
            "complaints": [complaint]
        }
    ]
    app.app.registry.db.save(tender_data)

    cancellation = dict(**test_cancellation)
    cancellation.update({"status": "active"})
    if get_now() < RELEASE_2020_04_19:
        with mock.patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(1)):
            response = app.post_json(
                "/tenders/{}/cancellations?acc_token={}".format(tender["id"], tender_token),
                {"data": cancellation},
                status=403
            )
        assert response.json == {'status': 'error', 'errors': [
            {'description': "Can't perform operation for there is an award complaint in pending status",
             'location': 'body', 'name': 'data'}]}

        # qualification complaints
        complaint = deepcopy(test_complaint)
        complaint.update(
            status="accepted",
        )
        tender_data["qualifications"] = [
            {
                "id": "0" * 32,
                "complaints": [complaint]
            }
        ]
        app.app.registry.db.save(tender_data)

        cancellation = dict(**test_cancellation)
        cancellation.update({"status": "active"})
        with mock.patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(1)):
            response = app.post_json(
                "/tenders/{}/cancellations?acc_token={}".format(tender["id"], tender_token),
                {"data": cancellation},
                status=403
            )
        assert response.json == {'status': 'error', 'errors': [
            {'description': "Can't perform operation for there is a qualification complaint in accepted status",
             'location': 'body', 'name': 'data'}]}

        # tender complaint
        complaint = deepcopy(test_complaint)
        complaint.update(
            status="satisfied",
        )
        tender_data["complaints"] = [complaint]
        app.app.registry.db.save(tender_data)

        cancellation = dict(**test_cancellation)
        cancellation.update({"status": "active"})
        with mock.patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(1)):
            response = app.post_json(
                "/tenders/{}/cancellations?acc_token={}".format(tender["id"], tender_token),
                {"data": cancellation},
                status=403
            )
        assert response.json == {'status': 'error', 'errors': [
            {'description': "Can't perform operation for there is a tender complaint in satisfied status",
             'location': 'body', 'name': 'data'}]}
