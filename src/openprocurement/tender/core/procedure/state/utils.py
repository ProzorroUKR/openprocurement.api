import dataclasses
from dataclasses import dataclass

from schematics.exceptions import ValidationError

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import error_handler
from openprocurement.tender.core.procedure.context import get_bid


def validation_error_handler(func):
    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except ValidationError as e:
            if isinstance(e.messages, dict):
                error_name = list(e.messages[0].keys())[0]
                error_msg = e.messages[0][error_name]
            else:
                error_name = "data"
                error_msg = e.messages[0]

            self.request.errors.status = 422
            self.request.errors.add("body", error_name, error_msg)
            raise error_handler(self.request)

    return wrapper


def awarding_is_unsuccessful(awards):
    """
    Check whether awarding is unsuccessful for tender/lot.
    If hasAwardingOrder is True and hasMultiSourcing is False, then only the last award's status is being checked.
    If hasAwardingOrder is False, all awards are being checked. If there are no awards with statuses
    active or pending for tender/lot, then awarding is unsuccessful.
    """
    tender = get_tender()
    awarding_order_enabled = tender["config"]["hasAwardingOrder"]
    has_multi_sourcing = tender["config"].get("hasMultiSourcing")
    awards_statuses = {award["status"] for award in awards}
    if awarding_order_enabled is False or has_multi_sourcing:
        return not awards_statuses.intersection({"active", "pending"})
    return awards and awards[-1]["status"] == "unsuccessful"


def invalidate_pending_bid():
    bid = get_bid()
    tender = get_tender()
    if tender.get("status") == "active.tendering" and bid.get("status") == "pending":
        bid["status"] = "invalid"


def _without(data: dict, key: str) -> dict:
    return {k: v for k, v in data.items() if k != key}


@dataclass
class ItemsDiff:
    """changes of a list of objects with ids (the objects are matched by id)"""

    added: list = dataclasses.field(default_factory=list)
    deleted: list = dataclasses.field(default_factory=list)
    kept: list = dataclasses.field(default_factory=list)  # the objects present before, in their new state
    changed: list = dataclasses.field(default_factory=list)  # (before, after) pairs whose own fields differ
    nested: list = dataclasses.field(default_factory=list)  # (before, after) pairs whose children differ

    def __bool__(self):
        return bool(self.added or self.deleted or self.changed or self.nested)

    @property
    def changed_after(self) -> list:
        return [item for _, item in self.changed]


def diff_items(before: list, after: list, children: str) -> ItemsDiff:
    """
    :param children: the field with the child objects, compared apart from the own fields
    """
    diff = ItemsDiff()
    before_by_id = {item["id"]: item for item in before}
    after_ids = {item["id"] for item in after}
    diff.deleted = [item for item in before if item["id"] not in after_ids]
    for item in after:
        item_before = before_by_id.get(item["id"])
        if item_before is None:
            diff.added.append(item)
            continue
        diff.kept.append(item)
        if _without(item_before, children) != _without(item, children):
            diff.changed.append((item_before, item))
        if item_before.get(children) != item.get(children):
            diff.nested.append((item_before, item))
    return diff


@dataclass
class RequirementsDiff:
    """
    changes of the requirements of a requirement group

    A requirement replaced by a new version (PUT) keeps its id and the previous version is cancelled,
    so the versions of an id are matched by position.
    """

    added: list = dataclasses.field(default_factory=list)
    replaced: list = dataclasses.field(default_factory=list)  # (previous version, new version) pairs
    changed: list = dataclasses.field(default_factory=list)  # (before, after) pairs of the same version
    nested: list = dataclasses.field(default_factory=list)  # (before, after) pairs whose eligibleEvidences differ


def diff_requirements(before: list, after: list) -> RequirementsDiff:
    diff = RequirementsDiff()
    before_versions: dict = {}
    for requirement in before:
        before_versions.setdefault(requirement["id"], []).append(requirement)
    after_versions: dict = {}
    for requirement in after:
        after_versions.setdefault(requirement["id"], []).append(requirement)
    for req_id, versions in after_versions.items():
        previous = before_versions.get(req_id, [])
        for version_before, version in zip(previous, versions):
            if _without(version_before, "eligibleEvidences") != _without(version, "eligibleEvidences"):
                diff.changed.append((version_before, version))
            if version_before.get("eligibleEvidences") != version.get("eligibleEvidences"):
                diff.nested.append((version_before, version))
        for version in versions[len(previous) :]:
            if previous:
                diff.replaced.append((previous[-1], version))
            else:
                diff.added.append(version)
    return diff
