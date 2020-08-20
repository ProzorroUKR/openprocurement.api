from datetime import timedelta

from openprocurement.tender.openeu.constants import TENDERING_DURATION, QUESTIONS_STAND_STILL, COMPLAINT_STAND_STILL

PERIODS = {
    "active.tendering": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=1),
                "endDate": TENDERING_DURATION - QUESTIONS_STAND_STILL,
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=1),
                "endDate": TENDERING_DURATION,
            },
        },
        "enquiry_end": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=29),
                "endDate": -timedelta(days=1),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=29),
                "endDate": timedelta(days=2),
            },
        },
        "complaint_end":
        {
            "enquiryPeriod": {
                "startDate": -timedelta(days=28),
                "endDate": -timedelta(days=2),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=28),
                "endDate": timedelta(days=3),
            },
        },
    },
    "active.pre-qualification": {
        "start": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION,
                "endDate": -QUESTIONS_STAND_STILL,
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
                "startDate": -TENDERING_DURATION,
                "endDate": -QUESTIONS_STAND_STILL,
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=1),
                "endDate": timedelta(),
            },
            "qualificationPeriod": {"startDate": timedelta()},
            "auctionPeriod": {"startDate": COMPLAINT_STAND_STILL},
        }
    },
    "active.auction": {
        "start": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION - COMPLAINT_STAND_STILL,
                "endDate": -COMPLAINT_STAND_STILL - TENDERING_DURATION + QUESTIONS_STAND_STILL,
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=1),
                "endDate": -COMPLAINT_STAND_STILL,
            },
            "qualificationPeriod": {
                "startDate": -COMPLAINT_STAND_STILL,
                "endDate": timedelta(),
            },
            "auctionPeriod": {"startDate": timedelta()},
        }
    },
    "active.qualification": {
        "start": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2),
                "endDate": -QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=1),
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2),
                "endDate": -COMPLAINT_STAND_STILL - timedelta(days=1),
            },
            "auctionPeriod": {"startDate": -timedelta(days=1), "endDate": timedelta()},
            "awardPeriod": {"startDate": timedelta()},
        }
    },
    "active.awarded": {
        "start": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=3),
                "endDate": -QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=2),
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=3),
                "endDate": -COMPLAINT_STAND_STILL - timedelta(days=2),
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
                "startDate": -TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=4),
                "endDate": -QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=3)
                ,
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=4),
                "endDate": -COMPLAINT_STAND_STILL - timedelta(days=3),
            },
            "auctionPeriod": {
                "startDate": -timedelta(days=3),
                "endDate": -timedelta(days=2),
            },
            "awardPeriod": {"startDate": -timedelta(days=1), "endDate": timedelta()},
        }
    }
}
