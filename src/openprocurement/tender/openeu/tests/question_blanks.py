# -*- coding: utf-8 -*-


def answering_question(self):
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question["id"], self.tender_token),
        {"data": {"answer": "answer"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["answer"], "answer")
    self.assertIn("dateAnswered", response.json["data"])
    question["answer"] = "answer"
    question["dateAnswered"] = response.json["data"]["dateAnswered"]

    self.time_shift("active.pre-qualification")
    self.check_chronograph()
