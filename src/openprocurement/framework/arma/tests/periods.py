from datetime import timedelta

# enquiryPeriod repeats period: for ARMA enquiries are open for the whole
# submission period (see ARMAFrameworkState.enquiry_period_lasts_until_qualification)
PERIODS = {
    "active": {
        "start": {
            "enquiryPeriod": {
                "startDate": timedelta(),
                "endDate": timedelta(days=335),
            },
            "period": {"startDate": timedelta(), "endDate": timedelta(days=335)},
            "qualificationPeriod": {"startDate": timedelta(), "endDate": timedelta(days=366)},
        }
    },
    "complete": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=366),
                "endDate": -timedelta(days=30),
            },
            "period": {"startDate": -timedelta(days=366), "endDate": -timedelta(days=30)},
            "qualificationPeriod": {"startDate": -timedelta(days=366), "endDate": timedelta()},
        }
    },
}
