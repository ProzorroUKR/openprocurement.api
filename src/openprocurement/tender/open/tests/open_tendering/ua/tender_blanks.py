from copy import deepcopy


def create_tender_invalid_config(self):
    """config.openTenderingType is required and the variant (UA/EU) pins the config values"""
    request_path = "/tenders"

    config = deepcopy(self.initial_config)
    del config["openTenderingType"]
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"description": "This field is required.", "location": "body", "name": "config.openTenderingType"}],
    )

    config = deepcopy(self.initial_config)
    config["openTenderingType"] = "XX"
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": config}, status=422)
    self.assertEqual(response.json["errors"][0]["name"], "config.openTenderingType")
    self.assertIn("is not one of", response.json["errors"][0]["description"])

    # the values pinned by the variant
    for config_name, value in (
        ("minTenderingDuration", 30),
        ("enquiryPeriodRegulation", 6),
        ("hasPrequalification", True),
        ("hasQualificationComplaints", True),
        ("qualificationDuration", 20),
        ("qualificationComplainDuration", 10),
    ):
        config = deepcopy(self.initial_config)
        config[config_name] = value
        response = self.app.post_json(request_path, {"data": self.initial_data, "config": config}, status=422)
        self.assertEqual(response.json["errors"][0]["name"], f"config.{config_name}")
        self.assertIn(str(value), response.json["errors"][0]["description"])

    # the values fixed for both variants
    for config_name, value in (("minBidsNumber", 2), ("valueCurrencyEquality", False), ("hasAwardingOrder", False)):
        config = deepcopy(self.initial_config)
        config[config_name] = value
        response = self.app.post_json(request_path, {"data": self.initial_data, "config": config}, status=422)
        self.assertEqual(response.json["errors"][0]["name"], f"config.{config_name}")

    # hasAuction / hasValueRestriction are up to the procuring entity
    config = deepcopy(self.initial_config)
    config.update({"hasAuction": False, "hasValueRestriction": False})
    data = deepcopy(self.initial_data)
    data.pop("minimalStep", None)  # no auction, no minimal step
    for lot in data.get("lots", ""):
        lot.pop("minimalStep", None)
    response = self.app.post_json(request_path, {"data": data, "config": config}, status=201)
    self.assertEqual(response.json["config"]["hasAuction"], False)
    self.assertEqual(response.json["config"]["hasValueRestriction"], False)
    self.assertEqual(response.json["config"]["openTenderingType"], self.initial_config["openTenderingType"])


def patch_tender_config_is_immutable(self):
    """config (the UA/EU variant in particular) can't be changed after the tender creation"""
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config}, status=201)
    tender_id = response.json["data"]["id"]
    token = response.json["access"]["token"]
    original = response.json["config"]["openTenderingType"]
    other = "EU" if original == "UA" else "UA"

    self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"description": "patched"}, "config": {"openTenderingType": other, "hasAuction": False}},
    )
    response = self.app.get(f"/tenders/{tender_id}")
    self.assertEqual(response.json["config"]["openTenderingType"], original)
    self.assertEqual(response.json["config"]["hasAuction"], self.initial_config["hasAuction"])
