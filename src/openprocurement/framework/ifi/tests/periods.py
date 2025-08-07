from datetime import timedelta

PERIODS = {
    "active": {
        "start": {
            "enquiryPeriod": {
                "startDate": timedelta(),
                "endDate": timedelta(days=10),
            },
            "period": {"startDate": timedelta(), "endDate": timedelta(days=335)},
            "qualificationPeriod": {"startDate": timedelta(), "endDate": timedelta(days=366)},
        }
    },
    "complete": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=366),
                "endDate": -timedelta(days=356),
            },
            "period": {"startDate": -timedelta(days=366), "endDate": -timedelta(days=335)},
            "qualificationPeriod": {"startDate": -timedelta(days=366), "endDate": timedelta()},
        }
    },
}
