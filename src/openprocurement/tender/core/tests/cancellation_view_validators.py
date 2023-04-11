import mock
import pytest
from datetime import timedelta
from copy import deepcopy
from openprocurement.api.tests.base import singleton_app, app
from openprocurement.api.utils import raise_operation_error, get_now
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
    test_tender_below_data,
    test_tender_below_config,
    test_tender_below_cancellation,
    test_tender_below_complaint,
)
from openprocurement.tender.openua.tests.base import (
    test_tender_openua_data,
    test_tender_openua_config,
)
from openprocurement.tender.cfaselectionua.tests.base import (
    test_tender_cfaselectionua_data,
    test_tender_cfaselectionua_lots,
    test_tender_cfaselectionua_config,
)
from openprocurement.tender.openuadefense.tests.base import (
    test_tender_openuadefense_data,
    test_tender_openuadefense_config,
)
from openprocurement.tender.simpledefense.tests.base import (
    test_tender_simpledefense_data,
    test_tender_simpledefense_config,
)
from openprocurement.tender.openeu.tests.base import (
    test_tender_openeu_data,
    test_tender_openeu_config,
)
from openprocurement.tender.esco.tests.base import (
    test_tender_esco_data,
    test_tender_esco_config,
)
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_cdua_data,
    test_tender_cdeu_data,
    test_tender_cdua_stage2_data,
    test_tender_cdeu_stage2_data,
    test_tender_cdeu_config,
    test_tender_cdua_config,
    test_tender_cdeu_stage2_config,
    test_tender_cdua_stage2_config,
)
from openprocurement.tender.cfaua.tests.base import (
    test_tender_cfaua_data,
    test_tender_cfaua_lots,
    test_tender_cfaua_config,
)
from openprocurement.tender.limited.tests.base import (
    test_tender_reporting_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
    test_tender_reporting_config,
    test_tender_negotiation_config,
    test_tender_negotiation_quick_config,
)


def post_tender(app, data, config):
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
    response = app.post_json("/tenders", dict(data=test_data, config=config))
    release_simpledef_patcher.stop()
    assert response.status == "201 Created"
    return response.json["data"], response.json["access"]["token"]


# TENDER COMPLAINTS
test_tender_cfaua_data = dict(**test_tender_cfaua_data)
test_tender_cfaua_data["lots"] = test_tender_cfaua_lots

test_tender_cfaselectionua_data = dict(**test_tender_cfaselectionua_data)
test_tender_cfaselectionua_data["lots"] = test_tender_cfaselectionua_lots

procedures = (
    (test_tender_below_data, test_tender_below_config),
    (test_tender_cfaselectionua_data, test_tender_cfaselectionua_config),
    (test_tender_cfaua_data, test_tender_cfaua_config),
    (test_tender_cdeu_data, test_tender_cdeu_config),
    (test_tender_cdua_data, test_tender_cdua_config),
    (test_tender_cdeu_stage2_data, test_tender_cdeu_stage2_config),
    (test_tender_cdua_stage2_data, test_tender_cdua_stage2_config),
    (test_tender_esco_data, test_tender_esco_config),
    (test_tender_reporting_data, test_tender_reporting_config),
    (test_tender_negotiation_data, test_tender_negotiation_config),
    (test_tender_negotiation_quick_data, test_tender_negotiation_quick_config),
    (test_tender_openua_data, test_tender_openua_config),
    (test_tender_openeu_data, test_tender_openeu_config),
    (test_tender_openuadefense_data, test_tender_openuadefense_config),
    (test_tender_simpledefense_data, test_tender_simpledefense_config),
)


@pytest.mark.parametrize("tender_data, tender_config", procedures)
def test_post_cancellation(app, tender_data, tender_config):
    """
    posting an active cancellation should trigger the validation
    """
    tender, tender_token = post_tender(app, tender_data, tender_config)

    def mock_validate(request, cancellation=None):
        raise_operation_error(request, "hello")

    if get_now() < RELEASE_2020_04_19:
        with mock.patch(
            "openprocurement.tender.core.validation.validate_absence_of_pending_accepted_satisfied_complaints",
            mock_validate
        ):
            cancellation = dict(**test_tender_below_cancellation)
            cancellation.update({"status": "active"})
            response = app.post_json(
                "/tenders/{}/cancellations?acc_token={}".format(tender["id"], tender_token),
                {"data": cancellation},
                status=403
            )
            assert response.json == {'status': 'error', 'errors': [
                {'description': 'hello', 'location': 'body', 'name': 'data'}]}


@pytest.mark.parametrize("tender_data, tender_config", procedures)
def test_patch_cancellation(app, tender_data, tender_config):
    """
    only patching to active should trigger the validation
    """
    tender, tender_token = post_tender(app, tender_data, tender_config)

    def mock_validate(request, cancellation=None):
        raise_operation_error(request, "hello")

    with mock.patch(
        "openprocurement.tender.core.validation.validate_absence_of_pending_accepted_satisfied_complaints",
        mock_validate
    ):
        if get_now() < RELEASE_2020_04_19:
            response = app.post_json(
                "/tenders/{}/cancellations?acc_token={}".format(tender["id"], tender_token),
                {"data": test_tender_below_cancellation},
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
    tender, tender_token = post_tender(app, test_tender_openeu_data, test_tender_below_config)
    tender_data = app.app.registry.mongodb.tenders.get(tender["id"])
    app.tender_id = tender["id"]

    # award complaint
    complaint = deepcopy(test_tender_below_complaint)
    tender_data["awards"] = [
        {
            "id": "0" * 32,
            "bid_id": "0" * 32,
            "suppliers": [test_tender_below_organization],
            "complaints": [complaint]
        }
    ]
    app.app.registry.mongodb.tenders.save(tender_data)

    cancellation = dict(**test_tender_below_cancellation)
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
        complaint = deepcopy(test_tender_below_complaint)
        complaint.update(
            status="accepted",
        )
        tender_data["qualifications"] = [
            {
                "id": "0" * 32,
                "complaints": [complaint]
            }
        ]
        app.app.registry.mongodb.tenders.save(tender_data)

        cancellation = dict(**test_tender_below_cancellation)
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
        complaint = deepcopy(test_tender_below_complaint)
        complaint.update(
            status="satisfied",
        )
        tender_data["complaints"] = [complaint]
        app.app.registry.mongodb.tenders.save(tender_data)

        cancellation = dict(**test_tender_below_cancellation)
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
