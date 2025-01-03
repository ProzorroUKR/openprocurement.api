from openprocurement.api.constants import NEW_REQUIREMENTS_RULES_FROM
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.utils import tender_created_after


class TenderCriterionMixin:
    def _validate_criterion_uniq(self, data, previous_criteria=[]) -> None:
        new_criteria = {}

        def check(new_criterion: dict) -> None:
            if class_id := new_criterion.get("classification", {}).get("id"):
                if class_id in new_criteria:
                    if new_criterion.get("relatesTo") in ("lot", "item"):
                        if new_criterion["relatedItem"] in new_criteria[class_id].get("lots", []):
                            raise_operation_error(self.request, "Criteria are not unique")
                        elif not new_criteria[class_id].get("lots", []):
                            new_criteria[class_id]["lots"] = [new_criterion["relatedItem"]]
                        else:
                            new_criteria[class_id]["lots"].append(new_criterion["relatedItem"])
                    elif not new_criteria[class_id].get("tenderer", False):
                        new_criteria[class_id] = {"tenderer": True}
                    else:
                        raise_operation_error(self.request, "Criteria are not unique")
                elif new_criterion.get("relatesTo") in ("lot", "item"):
                    new_criteria[class_id] = {"lots": [new_criterion["relatedItem"]]}
                else:
                    new_criteria[class_id] = {"tenderer": True}

                for existed_criterion in previous_criteria:
                    if (
                        new_criterion.get("relatesTo") == existed_criterion.get("relatesTo")
                        and new_criterion.get("relatedItem") == existed_criterion.get("relatedItem")
                        and new_criterion["classification"]["id"] == existed_criterion["classification"]["id"]
                    ):
                        raise_operation_error(self.request, "Criteria are not unique")

        if isinstance(data, list):
            for new_criterion in data:
                check(new_criterion)
        else:
            check(data)

    def validate_criteria_requirements_rules(self, data: dict) -> None:
        if not tender_created_after(NEW_REQUIREMENTS_RULES_FROM):
            return
        if not isinstance(data, list):
            data = [data]

        def raise_requirement_error(message):
            raise_operation_error(
                self.request,
                message,
                status=422,
                name="requirements",
            )

        for tender_criterion in data:
            for rg in tender_criterion.get("requirementGroups", []):
                for req in rg.get("requirements", []):
                    if req.get("dataType") == "string":
                        if req.get("expectedValues") is None:
                            raise_requirement_error(
                                f"req: {req['title']}: expectedValues is required when dataType string",
                            )
                        if req.get("expectedMinItems") != 1:
                            raise_requirement_error(
                                f"req: {req['title']}: expectedMinItems is required and should be equal 1",
                            )
                        if req.get("expectedMaxItems") and req["expectedMaxItems"] != 1:
                            raise_requirement_error(
                                f"req: {req['title']}: expectedMaxItems permitted value is 1",
                            )
                        if req.get("unit"):
                            raise_requirement_error(
                                f"req: {req['title']}: unit is forbidden for dataType string",
                            )
                    elif req.get("dataType") == "boolean":
                        if req.get("expectedValues") is not None:  # minValue/maxValue check exists in Requirement model
                            raise_requirement_error(
                                f"req: {req['title']}: only expectedValue is allowed for dataType boolean",
                            )
                        if req.get("unit"):
                            raise_requirement_error(
                                f"req: {req['title']}: unit is forbidden for dataType boolean",
                            )
                    elif req.get("dataType") in ("number", "integer"):
                        if req.get("expectedValues") is not None:
                            raise_requirement_error(
                                f"req: {req['title']}: expectedValues is allowed only for dataType string",
                            )
                        if req.get("expectedValue") is None and req.get("minValue") is None:
                            raise_requirement_error(
                                f"req: {req['title']}: expectedValue or minValue is required for dataType {req['dataType']}",
                            )
                        if not req.get("unit"):
                            raise_requirement_error(
                                f"req: {req['title']}: unit is required for dataType {req['dataType']}",
                            )
