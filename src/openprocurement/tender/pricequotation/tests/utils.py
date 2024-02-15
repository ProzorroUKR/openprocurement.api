def criteria_drop_uuids(data: list, key: str = "id"):
    for e in data:
        if key in e:
            del e[key]

        for g in e.get("requirementGroups", ""):
            if key in g:
                del g[key]

            for r in g.get("requirements", ""):
                if key in r:
                    del r[key]
    return data


def copy_criteria_req_id(criteria, responses):
    requirements = [r for e in criteria for g in e.get("requirementGroups", "") for r in g.get("requirements", "")]
    for r, resp in zip(requirements, responses):
        resp["requirement"]["id"] = r["id"]
    return responses


def copy_tender_items(tender_items):
    copy_fields = ["id", "description", "unit", "quantity"]
    return [{k: item[k] for k in copy_fields} for item in tender_items]


def activate_econtract(self, contract_id, tender_token, bid_token):
    test_signer_info = {
        "name": "Test Testovich",
        "telephone": "+380950000000",
        "email": "example@email.com",
        "iban": "1" * 15,
        "authorizedBy": "статут",
        "position": "Генеральний директор",
    }
    response = self.app.put_json(
        f"/contracts/{contract_id}/suppliers/signer_info?acc_token={bid_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put_json(
        f"/contracts/{contract_id}/buyer/signer_info?acc_token={tender_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={tender_token}",
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    return response.json["data"]
