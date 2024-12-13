import standards


def load_criteria_rules(procurement_method_type, constants):
    periods_data = standards.load(f"criteria/rules/{procurement_method_type}.json")

    periods = []
    for period_data in periods_data:
        data = {"criteria": period_data["criteria"], "period": {}}

        period = period_data.get("period") or {}

        # Get start_date from constants if specified
        if start_date := period.get("start_date"):
            data["period"]["start_date"] = constants.get(start_date, None)

        # Get end_date from constants if specified
        if end_date := period.get("end_date"):
            data["period"]["end_date"] = constants.get(end_date, None)

        periods.append(data)

    # TODO: Check for overlapping periods

    return periods
