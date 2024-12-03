from copy import deepcopy

from openprocurement.tender.belowthreshold.tests.base import test_tender_below_author


def create_tender_question_valid_author_co(self):
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": test_tender_below_author,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")


def create_tender_question_check_author_co(self):
    # supplier not form agreement contract
    author_data = deepcopy(test_tender_below_author)
    author_data["identifier"]["id"] = "111111"
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": author_data,
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden to add question for non-qualified suppliers")

    # suspended contract supplier
    author_data["identifier"]["id"] = "87654321"
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": author_data,
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden to add question for non-qualified suppliers")

    # active contract supplier
    author_data["identifier"]["id"] = "00037256"
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": author_data,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
