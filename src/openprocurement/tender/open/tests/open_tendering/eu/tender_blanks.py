from copy import deepcopy

from openprocurement.tender.open.tests.open_tendering.ua.tender_blanks import (  # noqa: F401
    create_tender_generated,
    patch_tender_procedure_is_immutable,
)


def create_tender_invalid_procedure_and_config(self):
    """procedure is required for openTendering and the EU variant (procedure.euPublished) pins the config values"""
    request_path = "/tenders"

    data = deepcopy(self.initial_data)
    del data["procedure"]
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "procedure"}],
    )

    # the values pinned by the variant
    for config_name, value in (
        ("minTenderingDuration", 15),
        ("enquiryPeriodRegulation", 4),
        ("hasPrequalification", False),
        ("hasQualificationComplaints", False),
        ("qualificationDuration", 0),
        ("qualificationComplainDuration", 0),
    ):
        config = deepcopy(self.initial_config)
        config[config_name] = value
        response = self.app.post_json(request_path, {"data": self.initial_data, "config": config}, status=422)
        self.assertEqual(response.json["errors"][0]["name"], f"config.{config_name}")
        self.assertIn(str(value), response.json["errors"][0]["description"])

    # the values fixed for both variants
    for config_name, value in (("minBidsNumber", 2), ("valueCurrencyEquality", False)):
        config = deepcopy(self.initial_config)
        config[config_name] = value
        response = self.app.post_json(request_path, {"data": self.initial_data, "config": config}, status=422)
        self.assertEqual(response.json["errors"][0]["name"], f"config.{config_name}")

    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=201)
    self.assertEqual(response.json["data"]["procedure"], {"euPublished": True})


def create_tender_multilingual_fields_required(self):
    """EU: the announcement is published in English as well"""
    data = deepcopy(self.initial_data)
    del data["procuringEntity"]["name_en"]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.json["errors"][0]["name"], "procuringEntity")
    self.assertIn("name_en", str(response.json["errors"][0]["description"]))

    data = deepcopy(self.initial_data)
    del data["items"][0]["description_en"]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.json["errors"][0]["name"], "items")
    self.assertIn("description_en", str(response.json["errors"][0]["description"]))

    data = deepcopy(self.initial_data)
    del data["title_en"]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "title_en", "description": ["This field is required."]}],
    )

    data = deepcopy(self.initial_data)
    data["title_en"] = ""
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.json["errors"][0]["name"], "title_en")

    data = deepcopy(self.initial_data)
    data["lots"] = deepcopy(self.initial_lots)
    del data["lots"][0]["title_en"]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "lots", "description": [{"title_en": ["This field is required."]}]}],
    )


def create_tender_lot_title_en_required(self):
    """EU: lot.title_en is required via the lots endpoint as well"""
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender_id = response.json["data"]["id"]
    token = response.json["access"]["token"]

    lot = deepcopy(self.initial_lots[0])
    lot.pop("id", None)
    lot_without_title_en = deepcopy(lot)
    del lot_without_title_en["title_en"]
    response = self.app.post_json(
        f"/tenders/{tender_id}/lots?acc_token={token}", {"data": lot_without_title_en}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "lots", "description": [{"title_en": ["This field is required."]}]}],
    )

    response = self.app.post_json(f"/tenders/{tender_id}/lots?acc_token={token}", {"data": lot})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["title_en"], lot["title_en"])
    lot_id = response.json["data"]["id"]

    response = self.app.patch_json(
        f"/tenders/{tender_id}/lots/{lot_id}?acc_token={token}",
        {"data": {"title_en": ""}},
        status=422,
    )
    self.assertEqual(response.json["errors"][0]["name"], "lots")
    self.assertIn("title_en", str(response.json["errors"][0]["description"]))

    response = self.app.patch_json(
        f"/tenders/{tender_id}/lots/{lot_id}?acc_token={token}",
        {"data": {"title_en": "new lot title en"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title_en"], "new lot title en")

    # the tender title_en can't be removed via PATCH
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"title_en": ""}},
        status=422,
    )
    self.assertEqual(response.json["errors"][0]["name"], "title_en")
