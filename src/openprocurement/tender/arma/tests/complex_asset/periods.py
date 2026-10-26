from datetime import timedelta

TENDERING_DURATION = timedelta(weeks=4, days=1)
QUALIFICATION_DURATION = timedelta(weeks=2, days=1)
ENQUIRY_PERIOD_REGULATION = timedelta(days=10)

PERIODS = {
    "active.tendering": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=1),
                "endDate": TENDERING_DURATION - ENQUIRY_PERIOD_REGULATION,
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=1),
                # we don't want to recalculate auctionPeriod (tenderPeriod.eendDate should be the same as in draft)
                "endDate": TENDERING_DURATION + timedelta(days=1),
            },
        },
        "enquiry_end": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=1),
                "endDate": -ENQUIRY_PERIOD_REGULATION,
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=1),
                "endDate": timedelta(days=2),
            },
        },
        "complaint_end": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=2),
                "endDate": -ENQUIRY_PERIOD_REGULATION,
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=2),
                "endDate": timedelta(days=3),
            },
        },
    },
    "active.pre-qualification": {
        "start": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=1),
                "endDate": -ENQUIRY_PERIOD_REGULATION,
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=1),
                "endDate": timedelta(),
            },
        }
    },
    "active.pre-qualification.stand-still": {
        "start": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=1),
                "endDate": -ENQUIRY_PERIOD_REGULATION,
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=1),
                "endDate": timedelta(),
            },
            "qualificationPeriod": {
                "startDate": timedelta(),
                "endDate": QUALIFICATION_DURATION,
                "reportingDatePublication": timedelta(),
            },
            "auctionPeriod": {"startDate": QUALIFICATION_DURATION},
        }
    },
    "active.auction": {
        "start": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION - QUALIFICATION_DURATION,
                "endDate": -QUALIFICATION_DURATION - TENDERING_DURATION + ENQUIRY_PERIOD_REGULATION,
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - QUALIFICATION_DURATION - timedelta(days=1),
                "endDate": -QUALIFICATION_DURATION,
            },
            "qualificationPeriod": {
                "startDate": -QUALIFICATION_DURATION,
                "endDate": timedelta(),
                "reportingDatePublication": -QUALIFICATION_DURATION,
            },
            "auctionPeriod": {"startDate": timedelta()},
        }
    },
    "active.qualification": {
        "start": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION - QUALIFICATION_DURATION - timedelta(days=2),
                "endDate": -ENQUIRY_PERIOD_REGULATION - QUALIFICATION_DURATION - timedelta(days=1),
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - QUALIFICATION_DURATION - timedelta(days=2),
                "endDate": -QUALIFICATION_DURATION - timedelta(days=1),
            },
            "qualificationPeriod": {
                "startDate": -QUALIFICATION_DURATION - timedelta(days=1),
                "endDate": -timedelta(days=1),
                "reportingDatePublication": -QUALIFICATION_DURATION - timedelta(days=1),
            },
            "auctionPeriod": {"startDate": -timedelta(days=1), "endDate": timedelta()},
            "awardPeriod": {"startDate": timedelta()},
        }
    },
    "active.awarded": {
        "start": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION - QUALIFICATION_DURATION - timedelta(days=3),
                "endDate": -ENQUIRY_PERIOD_REGULATION - QUALIFICATION_DURATION - timedelta(days=2),
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - QUALIFICATION_DURATION - timedelta(days=3),
                "endDate": -QUALIFICATION_DURATION - timedelta(days=2),
            },
            "qualificationPeriod": {
                "startDate": -QUALIFICATION_DURATION - timedelta(days=2),
                "endDate": -timedelta(days=2),
                "reportingDatePublication": -QUALIFICATION_DURATION - timedelta(days=2),
            },
            "auctionPeriod": {
                "startDate": -timedelta(days=2),
                "endDate": -timedelta(days=1),
            },
            "awardPeriod": {"startDate": -timedelta(days=1), "endDate": timedelta()},
        }
    },
    "complete": {
        "start": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION - QUALIFICATION_DURATION - timedelta(days=4),
                "endDate": -ENQUIRY_PERIOD_REGULATION - QUALIFICATION_DURATION - timedelta(days=3),
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - QUALIFICATION_DURATION - timedelta(days=4),
                "endDate": -QUALIFICATION_DURATION - timedelta(days=3),
            },
            "qualificationPeriod": {
                "startDate": -QUALIFICATION_DURATION - timedelta(days=3),
                "endDate": -timedelta(days=3),
                "reportingDatePublication": -QUALIFICATION_DURATION - timedelta(days=3),
            },
            "auctionPeriod": {
                "startDate": -timedelta(days=3),
                "endDate": -timedelta(days=2),
            },
            "awardPeriod": {"startDate": -timedelta(days=1), "endDate": timedelta()},
        }
    },
}
