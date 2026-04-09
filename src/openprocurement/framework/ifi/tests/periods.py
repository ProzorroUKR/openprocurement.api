from datetime import timedelta

PERIODS = {
    "active": {
        "start": {
            "enquiryPeriod": {
                "startDate": timedelta(),
                "endDate": timedelta(days=10),
            },
            "period": {"startDate": timedelta(), "endDate": timedelta(days=10)},
            "qualificationPeriod": {"startDate": timedelta(), "endDate": timedelta(days=41)},
        }
    },
    "complete": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=41),
                "endDate": -timedelta(days=31),
            },
            "period": {"startDate": -timedelta(days=41), "endDate": -timedelta(days=31)},
            "qualificationPeriod": {"startDate": -timedelta(days=41), "endDate": timedelta()},
        }
    },
}
