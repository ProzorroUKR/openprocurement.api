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
    requirements = [r for e in criteria
                    for g in e.get("requirementGroups", "")
                    for r in g.get("requirements", "")]
    for r, resp in zip(requirements, responses):
        resp["requirement"]["id"] = r["id"]
    return responses
