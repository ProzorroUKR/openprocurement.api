# -*- coding: utf-8 -*-
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.models import ListType
from openprocurement.api.utils import get_first_revision_date, get_now
from openprocurement.tender.core.models import (
    ComplaintModelType as BaseComplaintModelType,
    get_tender,
    Complaint as BaseComplaint,
    EUDocument,
)
from schematics.types.compound import ModelType
from schematics.types import StringType, BooleanType
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist
from openprocurement.api.models import IsoDateTimeType
from pyramid.security import Allow

from openprocurement.tender.openua.models import ComplaintPost


class ComplaintModelType(BaseComplaintModelType):
    view_claim_statuses = [
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
        "active.auction",
    ]


class Complaint(BaseComplaint):
    class Options:
        _base_roles = BaseComplaint.Options.roles
        _view_claim = whitelist(
            'acceptance', 'bid_id', 'cancellationReason', 'complaintID', 'date', 'dateAccepted',
            'dateAnswered', 'dateCanceled', 'dateDecision', 'dateEscalated', 'dateSubmitted', 'decision',
            'description', 'documents', 'id', 'rejectReason', 'rejectReasonDescription', 'relatedLot', 'resolution',
            'resolutionType', 'reviewDate', 'reviewPlace', 'satisfied', 'status', 'tendererAction',
            'tendererActionDate', 'title', 'type', 'value', 'calculate_value',
        )
        _open_view = _view_claim + whitelist('author', 'posts')
        _embedded = _open_view - whitelist('bid_id')  # "-bid_id" looks like a typo in the original csv
        roles = {
            "view_claim": _view_claim,
            "embedded": _embedded,
            "view": _embedded,
            "default": _open_view + whitelist('owner', 'owner_token'),

            "create": _base_roles["create"],
            "draft": whitelist('author', 'description', 'title', 'status'),
            "bot": whitelist("rejectReason", "status"),
            "answer": whitelist('resolution', 'resolutionType', 'status', 'tendererAction'),
            "review": whitelist(
                "decision", "status",
                "rejectReason", "rejectReasonDescription",
                "reviewDate", "reviewPlace"
            ),
            "satisfy": whitelist('satisfied', 'status'),
            "escalate": whitelist('status'),
            "resolve": whitelist('status', 'tendererAction'),
            "action": whitelist('tendererAction'),
            "cancellation": whitelist('cancellationReason', 'status'),
        }

    documents = ListType(ModelType(EUDocument, required=True), default=list())
    status = StringType(
        choices=[
            "draft",
            "claim",
            "answered",
            "pending",
            "accepted",
            "invalid",
            "resolved",
            "declined",
            "cancelled",
            "satisfied",
            "stopping",
            "stopped",
            "mistaken",
        ],
        default="draft",
    )
    acceptance = BooleanType()
    dateAccepted = IsoDateTimeType()
    rejectReasonDescription = StringType()
    reviewDate = IsoDateTimeType()
    reviewPlace = StringType()
    bid_id = StringType()
    posts = ListType(ModelType(ComplaintPost), default=list())

    def __acl__(self):
        return [
            (Allow, "g:bots", "edit_complaint"),
            (Allow, "g:aboveThresholdReviewers", "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_complaint_documents"),
        ]

    def get_role(self):
        root = self.get_root()
        request = root.request
        data = request.json_body["data"]
        auth_role = request.authenticated_role
        status = data.get("status", self.status)
        if auth_role == "Administrator":
            role = auth_role
        elif auth_role == "complaint_owner" and self.status != "mistaken" and status == "cancelled":
            role = "cancellation"
        elif auth_role == "complaint_owner" and self.status in ["pending", "accepted"] and status == "stopping":
            role = "cancellation"
        elif auth_role == "complaint_owner" and self.status == "draft":
            role = "draft"
        elif auth_role == "complaint_owner" and self.status == "claim":
            role = "escalate"
        elif auth_role == "bots" and self.status == "draft":
            role = "bot"
        elif auth_role == "tender_owner" and self.status == "claim":
            role = "answer"
        elif auth_role == "tender_owner" and self.status in ["pending", "accepted"]:
            role = "action"
        elif auth_role == "tender_owner" and self.status == "satisfied":
            role = "resolve"
        elif auth_role == "complaint_owner" and self.status == "answered":
            role = "satisfy"
        elif auth_role == "aboveThresholdReviewers" and self.status in ["pending", "accepted", "stopping"]:
            role = "review"
        else:
            role = "invalid"
        return role

    def validate_cancellationReason(self, data, cancellationReason):
        if not cancellationReason and data.get("status") in ["cancelled", "stopping"]:
            raise ValidationError(u"This field is required.")

    def validate_rejectReason(self, data, rejectReason):
        tender_date = get_first_revision_date(get_tender(data["__parent__"]), default=get_now())
        if tender_date < RELEASE_2020_04_19:
            return
        if not rejectReason and data.get("status") in ["invalid", "stopped"] and data.get("type") == "complaint":
            raise ValidationError(u"This field is required.")

    def validate_reviewDate(self, data, reviewDate):
        tender_date = get_first_revision_date(get_tender(data["__parent__"]), default=get_now())
        if tender_date < RELEASE_2020_04_19:
            return
        if not reviewDate and data.get("status") == "accepted":
            raise ValidationError(u"This field is required.")

    def validate_reviewPlace(self, data, reviewPlace):
        tender_date = get_first_revision_date(get_tender(data["__parent__"]), default=get_now())
        if tender_date < RELEASE_2020_04_19:
            return
        if not reviewPlace and data.get("status") == "accepted":
            raise ValidationError(u"This field is required.")

    def serialize(self, role=None, context=None):
        if (
            role == "view"
            and self.type == "claim"
            and get_tender(self).status
            in [
                "active.tendering",
                "active.pre-qualification",
                "active.pre-qualification.stand-still",
                "active.auction",
            ]
        ):
            role = "view_claim"
        return super(Complaint, self).serialize(role=role, context=context)
