from copy import deepcopy

from openprocurement.tender.open.tests.open_tendering.ua.tender_blanks import (  # noqa: F401
    patch_tender_config_is_immutable,
)


def create_tender_invalid_config(self):
    """config.openTenderingType is required and the EU variant pins the config values"""
    request_path = "/tenders"

    config = deepcopy(self.initial_config)
    del config["openTenderingType"]
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"description": "This field is required.", "location": "body", "name": "config.openTenderingType"}],
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
