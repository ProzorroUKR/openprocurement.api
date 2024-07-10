from contextlib import contextmanager
from datetime import timedelta
from unittest import mock

import pytest

from openprocurement.api.context import get_now, set_now
from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixing,
)

affected_complaint_statuses = ("pending", "accepted", "satisfied")
other_complaint_statuses = ("draft", "claim", "answered", "invalid", "resolved", "declined", "cancelled")
all_statuses = affected_complaint_statuses + other_complaint_statuses

set_now()


@contextmanager
def mock_release_date(date=None):
    date = date or get_now() - timedelta(1)
    with mock.patch("openprocurement.tender.core.procedure.state.cancellation.RELEASE_2020_04_19", date) as m:
        yield m


@pytest.mark.parametrize("complaint_status", affected_complaint_statuses)
def test_validation_before_release(complaint_status):
    request = mock.Mock(
        validated={
            "tender": {
                "complaints": [
                    {
                        "status": complaint_status,
                    }
                ]
            },
            "cancellation": {},
        }
    )
    with mock_release_date(get_now() + timedelta(1)):
        with mock.patch("openprocurement.tender.core.procedure.state.cancellation.raise_operation_error") as error_mock:
            CancellationStateMixing.validate_absence_of_pending_accepted_satisfied_complaints(
                request,
                request.validated["tender"],
                request.validated["cancellation"],
            )

    error_mock.assert_not_called()


@pytest.mark.parametrize("complaint_status", all_statuses)
def test_validation_tender_complaint(complaint_status):
    request = mock.Mock(
        validated={
            "tender": {
                "complaints": [
                    {
                        "status": complaint_status,
                    }
                ]
            },
            "cancellation": {},
        }
    )
    with mock_release_date():
        with mock.patch("openprocurement.tender.core.procedure.state.cancellation.raise_operation_error") as error_mock:
            CancellationStateMixing.validate_absence_of_pending_accepted_satisfied_complaints(
                request,
                request.validated["tender"],
                request.validated["cancellation"],
            )

    if complaint_status in affected_complaint_statuses:
        error_mock.assert_called_once_with(
            request, "Can't perform operation for there is a tender complaint in {} status".format(complaint_status)
        )
    else:
        error_mock.assert_not_called()


@pytest.mark.parametrize("complaint_status", all_statuses)
def test_validation_award_complaint(complaint_status):
    request = mock.Mock(
        validated={
            "tender": {
                "awards": [
                    {
                        "complaints": [
                            {
                                "status": complaint_status,
                            }
                        ]
                    }
                ]
            },
            "cancellation": {},
        }
    )
    with mock_release_date():
        with mock.patch("openprocurement.tender.core.procedure.state.cancellation.raise_operation_error") as error_mock:
            CancellationStateMixing.validate_absence_of_pending_accepted_satisfied_complaints(
                request,
                request.validated["tender"],
                request.validated["cancellation"],
            )

    if complaint_status in affected_complaint_statuses:
        error_mock.assert_called_once_with(
            request, "Can't perform operation for there is an award complaint in {} status".format(complaint_status)
        )
    else:
        error_mock.assert_not_called()


@pytest.mark.parametrize("complaint_status", all_statuses)
def test_validation_qualification_complaint(complaint_status):
    request = mock.Mock(
        validated={
            "tender": {
                "qualifications": [
                    {
                        "complaints": [
                            {
                                "status": complaint_status,
                            }
                        ]
                    }
                ]
            },
            "cancellation": {},
        }
    )
    with mock_release_date():
        with mock.patch("openprocurement.tender.core.procedure.state.cancellation.raise_operation_error") as error_mock:
            CancellationStateMixing.validate_absence_of_pending_accepted_satisfied_complaints(
                request,
                request.validated["tender"],
                request.validated["cancellation"],
            )

    if complaint_status in affected_complaint_statuses:
        error_mock.assert_called_once_with(
            request,
            "Can't perform operation for there is a qualification complaint in {} status".format(complaint_status),
        )
    else:
        error_mock.assert_not_called()


# TENDER LOT COMPLAINTS
a_lot = "0" * 32
b_lot = "1" * 32


@pytest.mark.parametrize("complaint_lot", (a_lot, None))
@pytest.mark.parametrize("cancellation_lot", (a_lot, None))
@pytest.mark.parametrize("complaint_status", affected_complaint_statuses)
def test_tender_lot_cancellation_complaint(complaint_status, cancellation_lot, complaint_lot):
    request = mock.Mock(
        validated={
            "tender": {
                "complaints": [
                    {
                        "status": complaint_status,
                        "relatedLot": complaint_lot,
                    }
                ]
            },
            "cancellation": {
                "relatedLot": cancellation_lot,
            },
        }
    )
    with mock_release_date():
        with mock.patch("openprocurement.tender.core.procedure.state.cancellation.raise_operation_error") as error_mock:
            CancellationStateMixing.validate_absence_of_pending_accepted_satisfied_complaints(
                request,
                request.validated["tender"],
                request.validated["cancellation"],
            )

    error_mock.assert_called_once_with(
        request, "Can't perform operation for there is a tender complaint in {} status".format(complaint_status)
    )


@pytest.mark.parametrize("complaint_status", affected_complaint_statuses)
def test_tender_lot_cancellation_complaint_pass(complaint_status):
    request = mock.Mock(
        validated={
            "tender": {
                "complaints": [
                    {
                        "status": complaint_status,
                        "relatedLot": a_lot,
                    }
                ]
            },
            "cancellation": {
                "relatedLot": b_lot,
            },
        }
    )
    with mock_release_date():
        with mock.patch("openprocurement.tender.core.procedure.state.cancellation.raise_operation_error") as error_mock:
            CancellationStateMixing.validate_absence_of_pending_accepted_satisfied_complaints(
                request,
                request.validated["tender"],
                request.validated["cancellation"],
            )

    error_mock.assert_not_called()


@pytest.mark.parametrize("complaint_lot", (a_lot, None))
@pytest.mark.parametrize("cancellation_lot", (a_lot, None))
@pytest.mark.parametrize("complaint_status", affected_complaint_statuses)
def test_award_lot_cancellation_complaint(complaint_status, cancellation_lot, complaint_lot):
    request = mock.Mock(
        validated={
            "tender": {
                "awards": [
                    {
                        "complaints": [
                            {
                                "status": complaint_status,
                                "relatedLot": complaint_lot,
                            }
                        ]
                    }
                ]
            },
            "cancellation": {
                "relatedLot": cancellation_lot,
            },
        }
    )
    with mock_release_date():
        with mock.patch("openprocurement.tender.core.procedure.state.cancellation.raise_operation_error") as error_mock:
            CancellationStateMixing.validate_absence_of_pending_accepted_satisfied_complaints(
                request,
                request.validated["tender"],
                request.validated["cancellation"],
            )

    error_mock.assert_called_once_with(
        request, "Can't perform operation for there is an award complaint in {} status".format(complaint_status)
    )


@pytest.mark.parametrize("complaint_status", affected_complaint_statuses)
def test_award_lot_cancellation_complaint_pass(complaint_status):
    request = mock.Mock(
        validated={
            "tender": {
                "awards": [
                    {
                        "complaints": [
                            {
                                "status": complaint_status,
                                "relatedLot": a_lot,
                            }
                        ]
                    }
                ]
            },
            "cancellation": {
                "relatedLot": b_lot,
            },
        }
    )
    with mock_release_date():
        with mock.patch("openprocurement.tender.core.procedure.state.cancellation.raise_operation_error") as error_mock:
            CancellationStateMixing.validate_absence_of_pending_accepted_satisfied_complaints(
                request,
                request.validated["tender"],
                request.validated["cancellation"],
            )

    error_mock.assert_called_once()


@pytest.mark.parametrize("complaint_lot", (a_lot, None))
@pytest.mark.parametrize("cancellation_lot", (a_lot, None))
@pytest.mark.parametrize("complaint_status", affected_complaint_statuses)
def test_qualification_lot_cancellation_complaint(complaint_status, cancellation_lot, complaint_lot):
    request = mock.Mock(
        validated={
            "tender": {
                "qualifications": [
                    {
                        "complaints": [
                            {
                                "status": complaint_status,
                                "relatedLot": complaint_lot,
                            }
                        ]
                    }
                ]
            },
            "cancellation": {
                "relatedLot": cancellation_lot,
            },
        }
    )
    with mock_release_date():
        with mock.patch("openprocurement.tender.core.procedure.state.cancellation.raise_operation_error") as error_mock:
            CancellationStateMixing.validate_absence_of_pending_accepted_satisfied_complaints(
                request,
                request.validated["tender"],
                request.validated["cancellation"],
            )

    error_mock.assert_called_once_with(
        request, "Can't perform operation for there is a qualification complaint in {} status".format(complaint_status)
    )


@pytest.mark.parametrize("complaint_status", affected_complaint_statuses)
def test_qualification_lot_cancellation_complaint_pass(complaint_status):
    request = mock.Mock(
        validated={
            "tender": {
                "qualifications": [
                    {
                        "complaints": [
                            {
                                "status": complaint_status,
                                "relatedLot": a_lot,
                            }
                        ]
                    }
                ]
            },
            "cancellation": {
                "relatedLot": b_lot,
            },
        }
    )
    with mock_release_date():
        with mock.patch("openprocurement.tender.core.procedure.state.cancellation.raise_operation_error") as error_mock:
            CancellationStateMixing.validate_absence_of_pending_accepted_satisfied_complaints(
                request,
                request.validated["tender"],
                request.validated["cancellation"],
            )

    error_mock.assert_called_once()
