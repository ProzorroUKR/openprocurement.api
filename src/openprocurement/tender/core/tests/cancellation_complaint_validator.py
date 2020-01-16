from openprocurement.tender.core.validation import validate_absence_of_pending_accepted_satisfied_complaints
import mock
import pytest


affected_complaint_statuses = ("pending", "accepted", "satisfied")
other_complaint_statuses = ("draft", "claim", "answered", "invalid", "resolved", "declined", "cancelled")
all_statuses = affected_complaint_statuses + other_complaint_statuses


@pytest.mark.parametrize("complaint_status", all_statuses)
def test_validation_tender_complaint(complaint_status):
    request = mock.Mock(validated=dict(
        tender={
            "complaints": [
                {
                    "status": complaint_status,
                }
            ]
        },
        cancellation={},
    ))
    with mock.patch("openprocurement.tender.core.validation.raise_operation_error") as error_mock:
        validate_absence_of_pending_accepted_satisfied_complaints(request)

        if complaint_status in affected_complaint_statuses:
            error_mock.assert_called_once_with(
                request,
                "Can't perform operation for there is a tender complaint in {} status".format(complaint_status)
            )
        else:
            error_mock.assert_not_called()


@pytest.mark.parametrize("complaint_status", all_statuses)
def test_validation_award_complaint(complaint_status):
    request = mock.Mock(validated=dict(
        tender={
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
        cancellation={},
    ))
    with mock.patch("openprocurement.tender.core.validation.raise_operation_error") as error_mock:
        validate_absence_of_pending_accepted_satisfied_complaints(request)

        if complaint_status in affected_complaint_statuses:
            error_mock.assert_called_once_with(
                request,
                "Can't perform operation for there is an award complaint in {} status".format(complaint_status)
            )
        else:
            error_mock.assert_not_called()


@pytest.mark.parametrize("complaint_status", all_statuses)
def test_validation_qualification_complaint(complaint_status):
    request = mock.Mock(validated=dict(
        tender={
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
        cancellation={},
    ))
    with mock.patch("openprocurement.tender.core.validation.raise_operation_error") as error_mock:
        validate_absence_of_pending_accepted_satisfied_complaints(request)

        if complaint_status in affected_complaint_statuses:
            error_mock.assert_called_once_with(
                request,
                "Can't perform operation for there is a qualification complaint in {} status".format(complaint_status)
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

    request = mock.Mock(validated=dict(
        tender={
            "complaints": [
                {
                    "status": complaint_status,
                    "relatedLot": complaint_lot,
                }
            ]
        },
        cancellation={
            "relatedLot": cancellation_lot,
        }
    ))
    with mock.patch("openprocurement.tender.core.validation.raise_operation_error") as error_mock:
        validate_absence_of_pending_accepted_satisfied_complaints(request)

    error_mock.assert_called_once_with(
        request,
        "Can't perform operation for there is a tender complaint in {} status".format(complaint_status)
    )


@pytest.mark.parametrize("complaint_status", affected_complaint_statuses)
def test_tender_lot_cancellation_complaint_pass(complaint_status):
    request = mock.Mock(validated=dict(
        tender={
            "complaints": [
                {
                    "status": complaint_status,
                    "relatedLot": a_lot,
                }
            ]
        },
        cancellation={
            "relatedLot": b_lot,
        }
    ))
    with mock.patch("openprocurement.tender.core.validation.raise_operation_error") as error_mock:
        validate_absence_of_pending_accepted_satisfied_complaints(request)

    error_mock.assert_not_called()


@pytest.mark.parametrize("complaint_lot", (a_lot, None))
@pytest.mark.parametrize("cancellation_lot", (a_lot, None))
@pytest.mark.parametrize("complaint_status", affected_complaint_statuses)
def test_award_lot_cancellation_complaint(complaint_status, cancellation_lot, complaint_lot):

    request = mock.Mock(validated=dict(
        tender={
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
        cancellation={
            "relatedLot": cancellation_lot,
        }
    ))
    with mock.patch("openprocurement.tender.core.validation.raise_operation_error") as error_mock:
        validate_absence_of_pending_accepted_satisfied_complaints(request)

    error_mock.assert_called_once_with(
        request,
        "Can't perform operation for there is an award complaint in {} status".format(complaint_status)
    )


@pytest.mark.parametrize("complaint_status", affected_complaint_statuses)
def test_award_lot_cancellation_complaint_pass(complaint_status):
    request = mock.Mock(validated=dict(
        tender={
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
        cancellation={
            "relatedLot": b_lot,
        }
    ))
    with mock.patch("openprocurement.tender.core.validation.raise_operation_error") as error_mock:
        validate_absence_of_pending_accepted_satisfied_complaints(request)

    error_mock.assert_not_called()


@pytest.mark.parametrize("complaint_lot", (a_lot, None))
@pytest.mark.parametrize("cancellation_lot", (a_lot, None))
@pytest.mark.parametrize("complaint_status", affected_complaint_statuses)
def test_qualification_lot_cancellation_complaint(complaint_status, cancellation_lot, complaint_lot):
    request = mock.Mock(validated=dict(
        tender={
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
        cancellation={
            "relatedLot": cancellation_lot,
        }
    ))
    with mock.patch("openprocurement.tender.core.validation.raise_operation_error") as error_mock:
        validate_absence_of_pending_accepted_satisfied_complaints(request)

    error_mock.assert_called_once_with(
        request,
        "Can't perform operation for there is a qualification complaint in {} status".format(complaint_status)
    )


@pytest.mark.parametrize("complaint_status", affected_complaint_statuses)
def test_qualification_lot_cancellation_complaint_pass(complaint_status):
    request = mock.Mock(validated=dict(
        tender={
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
        cancellation={
            "relatedLot": b_lot,
        }
    ))
    with mock.patch("openprocurement.tender.core.validation.raise_operation_error") as error_mock:
        validate_absence_of_pending_accepted_satisfied_complaints(request)

    error_mock.assert_not_called()
