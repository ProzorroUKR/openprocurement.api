from copy import deepcopy


def create_tender_invalid_procurement_aspects_and_config(self):
    """procurementAspects is required for openTendering and the variant (UA/EU) pins the config values"""
    request_path = "/tenders"

    data = deepcopy(self.initial_data)
    del data["procurementAspects"]
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "procurementAspects"}],
    )

    # can't be empty
    data["procurementAspects"] = []
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"description": ["Please provide at least 1 item."], "location": "body", "name": "procurementAspects"}],
    )

    data["procurementAspects"] = ["XX"]
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.json["errors"][0]["name"], "procurementAspects")
    self.assertIn("must be one of", str(response.json["errors"][0]["description"]))

    # only one of the allowed combinations
    for aspects in (["UA", "EU"], ["EU", "UA"], ["UA", "UA"]):
        data["procurementAspects"] = aspects
        response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": ["Value must be one of the combinations: ['UA'], ['EU']."],
                    "location": "body",
                    "name": "procurementAspects",
                }
            ],
        )

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
    self.assertEqual(response.json["data"]["procurementAspects"], self.initial_data["procurementAspects"])

    # the variant is exposed in the listing (the tender must be public: draft tenders are not listed)
    response = self.set_initial_status(response.json)
    tender_id = response.json["data"]["id"]
    response = self.app.get("/tenders?opt_fields=procurementAspects")
    listed = [item for item in response.json["data"] if item["id"] == tender_id]
    self.assertEqual(len(listed), 1)
    self.assertEqual(listed[0]["procurementAspects"], self.initial_data["procurementAspects"])


def create_tender_generated(self):
    """the generated tender fields: the legacy set plus procurementAspects (EU: plus the prequalification period)"""
    data = self.initial_data.copy()
    data.update({"id": "hash"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    tender.pop("procurementMethodDetails", None)
    tender.pop("contractTemplateName", None)
    assert_fields = {
        "procurementMethodType",
        "procurementAspects",
        "id",
        "dateModified",
        "dateCreated",
        "tenderID",
        "status",
        "enquiryPeriod",
        "tenderPeriod",
        "complaintPeriod",
        "criteria",
        "items",
        "value",
        "procuringEntity",
        "next_check",
        "procurementMethod",
        "awardCriteria",
        "submissionMethod",
        "lots",
        "title",
        "owner",
        "date",
        "mainProcurementCategory",
        "milestones",
        "documents",
        "noticePublicationDate",
        "contractChangeRationaleTypes",
    }
    if self.initial_config["hasPrequalification"]:
        assert_fields.add("qualificationPeriod")
    if "title_en" in data:
        assert_fields.add("title_en")
    self.assertEqual(set(tender), assert_fields)
    self.assertEqual(tender["procurementAspects"], self.initial_data["procurementAspects"])
    self.assertNotEqual(data["id"], tender["id"])


def create_tender_procurement_aspects_forbidden_for_legacy(self):
    """procurementAspects is an openTendering field: the legacy open procedures don't accept it"""
    data = deepcopy(self.initial_data)
    data["procurementMethodType"] = "aboveThresholdUA"
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"description": "Rogue field", "location": "body", "name": "procurementAspects"}],
    )


def patch_tender_procurement_aspects_is_immutable(self):
    """the UA/EU variant (and the config) can't be changed after the tender creation"""
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config}, status=201)
    tender_id = response.json["data"]["id"]
    token = response.json["access"]["token"]
    original = response.json["data"]["procurementAspects"]
    other = ["EU"] if original == ["UA"] else ["UA"]

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"procurementAspects": other}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"description": "Rogue field", "location": "body", "name": "procurementAspects"}],
    )

    # the config is ignored on patch
    self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"description": "patched"}, "config": {"hasAuction": False}},
    )
    response = self.app.get(f"/tenders/{tender_id}")
    self.assertEqual(response.json["data"]["procurementAspects"], original)
    self.assertEqual(response.json["data"]["description"], "patched")
    self.assertEqual(response.json["config"]["hasAuction"], self.initial_config["hasAuction"])
