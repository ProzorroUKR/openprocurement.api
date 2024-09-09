from openprocurement.api.utils import raise_operation_error


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
                        new_criterion.get("relatesTo") == existed_criterion["relatesTo"]
                        and new_criterion.get("relatedItem") == existed_criterion.get("relatedItem")
                        and new_criterion["classification"]["id"] == existed_criterion["classification"]["id"]
                    ):
                        raise_operation_error(self.request, "Criteria are not unique")

        if isinstance(data, list):
            for new_criterion in data:
                check(new_criterion)
        else:
            check(data)
