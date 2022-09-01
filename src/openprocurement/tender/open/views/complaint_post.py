# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    context_unpack,
    json_view,
)

from openprocurement.tender.core.utils import save_tender, optendersresource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD

from openprocurement.tender.open.validation import (
    validate_complaint_post_data,
    validate_complaint_post_complaint_status,
    validate_complaint_post,
    validate_complaint_post_review_date,
    validate_complaint_post_complaint_type,
)
from openprocurement.api.views.base import BaseResource


@optendersresource(
    name=f"{ABOVE_THRESHOLD}:Tender Complaint Posts",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender complaint posts",
)
class TenderComplaintPostResource(BaseResource):
    @json_view(
        content_type="application/json",
        validators=(
                validate_complaint_post_complaint_type,
                validate_complaint_post_data,
                validate_complaint_post,
                validate_complaint_post_complaint_status,
                validate_complaint_post_review_date,
        ),
        permission="edit_complaint",
    )
    def collection_post(self):
        """
        Post a complaint
        """
        complaint = self.context
        tender = self.request.validated["tender"]
        post = self.request.validated["post"]
        post.author = self.request.authenticated_role
        for document in post.documents or []:
            document.author = self.request.authenticated_role
        complaint.posts.append(post)
        if save_tender(self.request, validate=True):
            self.LOGGER.info(
                "Created post {}".format(post.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_complaint_post_create"},
                    {"post_id": post.id}
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.generate_location_url()
            return {"data": post.serialize("view")}

    @json_view(permission="view_tender")
    def collection_get(self):
        """
        List complaints
        """
        return {"data": [i.serialize("view") for i in self.context.get("posts", [])]}

    @json_view(permission="view_tender")
    def get(self):
        """
        Retrieving the complaint
        """
        return {"data": self.context.serialize("view")}

    def generate_location_url(self):
        return  self.request.route_url(
            "{}:Tender Complaint Posts".format(self.request.validated["tender"].procurementMethodType),
            tender_id=self.request.validated["tender_id"],
            complaint_id=self.request.validated["complaint_id"],
            post_id=self.request.validated["post"]["id"],
        )
