from openprocurement.tender.core.validation import check_requirements_active
from openprocurement.tender.core.procedure.validation import base_validate_operation_ecriteria_objects
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_tender


class BaseCriterionStateMixin:
    def _validate_operation_criterion_in_tender_status(self) -> None:
        valid_statuses = ["draft", "draft.pending", "draft.stage2", "active.tendering"]
        base_validate_operation_ecriteria_objects(self.request, valid_statuses)

    def _validate_patch_exclusion_ecriteria_objects(self, before: dict) -> None:
        if before["classification"]["id"].startswith("CRITERION.EXCLUSION"):
            raise_operation_error(self.request, "Can't update exclusion ecriteria objects")

    def invalidate_bids(self) -> None:
        tender = get_tender()
        if hasattr(self, "invalidate_bids_data"):
            self.invalidate_bids_data(tender)


class CriterionStateMixin(BaseCriterionStateMixin):
    def criterion_on_post(self, data: dict) -> None:
        self.validate_on_post(data)
        self.criterion_always(data)

    def criterion_on_patch(self, before: dict, after: dict) -> None:
        self.validate_on_patch(before, after)
        self.criterion_always(after)

    def criterion_always(self, data: dict) -> None:
        self.invalidate_bids()

    def validate_on_post(self, data: dict) -> None:
        self._validate_operation_criterion_in_tender_status()
        self._validate_criterion_uniq(data)

    def validate_on_patch(self, before: dict, after: dict) -> None:
        self._validate_operation_criterion_in_tender_status()
        self._validate_patch_exclusion_ecriteria_objects(before)
        self._validate_criterion_uniq_patch(before, after)

    def _validate_criterion_uniq(self, data):
        criteria = self.request.validated["tender"]["criteria"]
        new_criteria = {}

        def check(new_criterion: dict) -> None:
            class_id = new_criterion["classification"]["id"]
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

            for existed_criterion in criteria:
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

    def _validate_criterion_uniq_patch(self, before: dict, after: dict) -> None:
        criteria = get_tender().get("criteria")
        updated_criterion_classification = after.get("classification", {}).get("id", "")

        if updated_criterion_classification == before["classification"]["id"]:
            return

        for existed_criterion in criteria:
            if (
                    after.get("relatesTo") == existed_criterion["relatesTo"]
                    and after.get("relatedItem", "") == existed_criterion.get("relatedItem", "")
            ):
                if updated_criterion_classification == existed_criterion["classification"]["id"]:
                    if check_requirements_active(existed_criterion):
                        raise_operation_error(self.request, "Criteria are not unique")


class CriterionState(CriterionStateMixin, TenderState):
    pass
