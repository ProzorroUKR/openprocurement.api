from datetime import timedelta

PERIODS = {
    "active": {
        "start": {
            "enquiryPeriod": {
                "startDate": timedelta(),
                "endDate": timedelta(days=10),
            },
            "period": {
                "startDate": timedelta(),
                "endDate": timedelta(days=30)
            },
            "qualificationPeriod": {
                "startDate": timedelta(days=10),
                "endDate": timedelta(days=61)
            },
        }
    },
    "complete": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=61),
                "endDate": -timedelta(days=51),
            },
            "period": {
                "startDate": -timedelta(days=61),
                "endDate": -timedelta(days=30)
            },
            "qualificationPeriod": {
                "startDate": -timedelta(days=51),
                "endDate": timedelta()
            }
        }
    }
}
