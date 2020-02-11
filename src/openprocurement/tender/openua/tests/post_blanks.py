from openprocurement.tender.core.tests.base import change_auth


def create_complaint_post_status_forbidden(self):
    # try in draft
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.post_post({
            "title": "Lorem ipsum",
            "description": "Lorem ipsum dolor sit amet",
            "recipient": "complaint_owner",
        }, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add post in current (draft) complaint status"
    )

def create_complaint_post_claim_forbidden(self):
    # make complaint type claim
    response = self.patch_complaint({"type": "claim", "status": "claim"}, self.complaint_owner_token)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "claim")

    # try in claim
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.post_post({
            "title": "Lorem ipsum",
            "description": "Lorem ipsum dolor sit amet",
            "recipient": "complaint_owner",
        }, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add post in current (claim) complaint status"
    )

def create_complaint_post_complaint_owner(self):
    # make complaint type complaint
    response = self.patch_complaint({"type": "complaint", "status": "pending"}, self.complaint_owner_token)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    # create post by reviewer
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.post_post({
            "title": "Lorem ipsum",
            "description": "Lorem ipsum dolor sit amet",
            "recipient": "complaint_owner",
            "documents": [{
                "title": "lorem.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }],
        })
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["author"], "aboveThresholdReviewers")

    post = response.json["data"]

    # create answer by complaint owner
    response = self.post_post({
        "title": "Lorem ipsum",
        "description": "Lorem ipsum dolor sit amet",
        "recipient": "aboveThresholdReviewers",
        "relatedPost": post["id"],
    }, acc_token=self.complaint_owner_token)
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["author"], "complaint_owner")

def create_complaint_post_tender_owner(self):
    # make complaint type complaint
    response = self.patch_complaint({"type": "complaint", "status": "pending"}, self.complaint_owner_token)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    # create post by reviewer
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.post_post({
            "title": "Lorem ipsum",
            "description": "Lorem ipsum dolor sit amet",
            "recipient": "tender_owner",
            "documents": [{
                "title": "lorem.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }],
        })
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["author"], "aboveThresholdReviewers")

    post = response.json["data"]

    # create answer by complaint owner
    response = self.post_post({
        "title": "Lorem ipsum",
        "description": "Lorem ipsum dolor sit amet",
        "recipient": "aboveThresholdReviewers",
        "relatedPost": post["id"],
    }, acc_token=self.tender_token)
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["author"], "tender_owner")

def create_complaint_post_validate_recipient(self):
    # make complaint type complaint
    response = self.patch_complaint({"type": "complaint", "status": "pending"}, self.complaint_owner_token)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    # create post by reviewer with invalid recipient
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.post_post({
            "title": "Lorem ipsum",
            "description": "Lorem ipsum dolor sit amet",
            "recipient": "aboveThresholdReviewers",
        }, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("Value must be one of ['complaint_owner', 'tender_owner'].", str(response.json["errors"]))

    # create post by reviewer
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.post_post({
            "title": "Lorem ipsum",
            "description": "Lorem ipsum dolor sit amet",
            "recipient": "complaint_owner",
        })
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["author"], "aboveThresholdReviewers")

    post = response.json["data"]

    # create answer by complaint owner invalid recipient
    response = self.post_post({
        "title": "Lorem ipsum",
        "description": "Lorem ipsum dolor sit amet",
        "recipient": "complaint_owner",
        "relatedPost": post["id"]
    }, acc_token=self.complaint_owner_token, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("Value must be one of ['aboveThresholdReviewers'].", str(response.json["errors"]))

def create_complaint_post_validate_related_post(self):
    # make complaint type complaint
    response = self.patch_complaint({"type": "complaint", "status": "pending"}, self.complaint_owner_token)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    # create post by reviewer
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.post_post({
            "title": "Lorem ipsum",
            "description": "Lorem ipsum dolor sit amet",
            "recipient": "tender_owner",
        })
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["author"], "aboveThresholdReviewers")

    post = response.json["data"]

    # create answer by complaint owner invalid recipient
    response = self.post_post({
        "title": "Lorem ipsum",
        "description": "Lorem ipsum dolor sit amet",
        "recipient": "aboveThresholdReviewers",
        "relatedPost": post["id"]
    }, acc_token=self.complaint_owner_token, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("relatedPost invalid recipient.", str(response.json["errors"]))

    # create answer by complaint owner invalid recipient
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.post_post({
            "title": "Lorem ipsum",
            "description": "Lorem ipsum dolor sit amet",
            "recipient": "aboveThresholdReviewers",
            "relatedPost": post["id"]
        }, acc_token=self.complaint_owner_token, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("relatedPost can't have the same author.", str(response.json["errors"]))

    # create answer by complaint owner invalid recipient
    response = self.post_post({
        "title": "Lorem ipsum",
        "description": "Lorem ipsum dolor sit amet",
        "recipient": "aboveThresholdReviewers",
        "relatedPost": "some_id"
    }, acc_token=self.complaint_owner_token, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("relatedPost should be one of posts.", str(response.json["errors"]))

    # create answer by tender owner without related post
    response = self.post_post({
        "title": "Lorem ipsum",
        "description": "Lorem ipsum dolor sit amet",
        "recipient": "aboveThresholdReviewers",
    }, acc_token=self.tender_token, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("This field is required.", str(response.json["errors"]))

    # create answer by tender owner
    response = self.post_post({
        "title": "Lorem ipsum",
        "description": "Lorem ipsum dolor sit amet",
        "recipient": "aboveThresholdReviewers",
        "relatedPost": post["id"],
    }, acc_token=self.tender_token)
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["author"], "tender_owner")

    # create answer by tender owner invalid recipient
    response = self.post_post({
        "title": "Lorem ipsum",
        "description": "Lorem ipsum dolor sit amet",
        "recipient": "aboveThresholdReviewers",
        "relatedPost": post["id"],
    }, acc_token=self.tender_token, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("relatedPost must be unique.", str(response.json["errors"]))


def patch_complaint_post(self):
    # make complaint type complaint
    response = self.patch_complaint({"type": "complaint", "status": "pending"}, self.complaint_owner_token)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    # create post by reviewer
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.post_post({
            "title": "Lorem ipsum",
            "description": "Lorem ipsum dolor sit amet",
            "recipient": "complaint_owner",
        })
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    post = response.json["data"]
    self.post_id = post["id"]

    # try patch post by reviewer
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.patch_post({
            "title": "Test"
        }, status=405)
    self.assertEqual(response.status, "405 Method Not Allowed")
    self.assertEqual(response.content_type, "text/plain")


def get_complaint_post(self):
    # make complaint type complaint
    response = self.patch_complaint({"type": "complaint", "status": "pending"}, self.complaint_owner_token)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    # create post by reviewer
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.post_post({
            "title": "Lorem ipsum",
            "description": "Lorem ipsum dolor sit amet",
            "recipient": "complaint_owner",
            "documents": [{
                "title": "lorem.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }],
        })
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    post = response.json["data"]

    self.post_id = post["id"]

    response = self.get_post()
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        set(response.json["data"]),
        set(["id", "title", "description", "author", "recipient", "datePublished", "documents"])
    )

    self.post_id = "some_id"

    response = self.get_post(status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{
            "description": "Not Found",
            "location": "url",
            "name": "post_id"
        }]
    )


def get_complaint_posts(self):
    # make complaint type complaint
    response = self.patch_complaint({"type": "complaint", "status": "pending"}, self.complaint_owner_token)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    # create post by reviewer
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.post_post({
            "title": "Lorem ipsum",
            "description": "Lorem ipsum dolor sit amet",
            "recipient": "complaint_owner",
            "documents": [{
                "title": "lorem.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }],
        })
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    post = response.json["data"]

    response = self.get_posts()
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        set(response.json["data"][0]),
        set(["id", "title", "description", "author", "recipient", "datePublished", "documents"])
    )
