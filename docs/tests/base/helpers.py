def complaint_create_pending(self, uri, data, token=None):
    url = "{}?acc_token={}".format(uri, token) if token else uri

    response = self.app.post_json(url, data)
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]
    complaint_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "{}/{}?acc_token={}".format(uri, complaint_id, complaint_token),
        {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    return complaint_id, complaint_token
