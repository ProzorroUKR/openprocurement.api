from datetime import timedelta
from openprocurement.tender.cfaua.constants import (
    TENDERING_DURATION,
    QUESTIONS_STAND_STILL,
    TENDERING_EXTRA_PERIOD,
    COMPLAINT_STAND_STILL,
    QUALIFICATION_COMPLAINT_STAND_STILL,
    CLARIFICATIONS_UNTIL_PERIOD,
)

PERIODS = {
    "active.tendering": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=1),
                "endDate": TENDERING_DURATION - QUESTIONS_STAND_STILL
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=1),
                "endDate": TENDERING_DURATION
            },
        },
        "end": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=1),
                "endDate": -QUESTIONS_STAND_STILL,
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=1),
                "endDate":  timedelta()
            },
        },
        "enquiry_end": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION + TENDERING_EXTRA_PERIOD - timedelta(days=2),
                "endDate": -timedelta(days=1),
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION + TENDERING_EXTRA_PERIOD - timedelta(days=2),
                "endDate": TENDERING_EXTRA_PERIOD - timedelta(days=1),
            },
        },
    },
    "active.pre-qualification": {
        "start": {
            "enquiryPeriod": {
                "startDate": (-TENDERING_DURATION - timedelta(days=1)),
                "endDate": (-QUESTIONS_STAND_STILL),
            },
            "tenderPeriod": {"startDate": (-TENDERING_DURATION - timedelta(days=1)), "endDate": timedelta()},
            "qualificationPeriod": {"startDate": timedelta()},
        },
        "end": {
            "enquiryPeriod": {
                "startDate": (-TENDERING_DURATION - timedelta(days=1)),
                "endDate": (-QUESTIONS_STAND_STILL),
            },
            "tenderPeriod": {"startDate": (-TENDERING_DURATION - timedelta(days=1)), "endDate": timedelta()},
            "qualificationPeriod": {"startDate": timedelta()},
        },
    },
    "active.pre-qualification.stand-still": {
        "start": {
            "enquiryPeriod": {
                "startDate": (-TENDERING_DURATION - timedelta(days=1)),
                "endDate": (-QUESTIONS_STAND_STILL),
            },
            "tenderPeriod": {"startDate": (-TENDERING_DURATION - timedelta(days=1)), "endDate": timedelta()},
            "qualificationPeriod": {"startDate": timedelta()},
            "auctionPeriod": {"startDate": (+COMPLAINT_STAND_STILL)},
        },
        "end": {
            "enquiryPeriod": {
                "startDate": (-TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=1)),
                "endDate": (-COMPLAINT_STAND_STILL - TENDERING_DURATION + QUESTIONS_STAND_STILL),
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=1)),
                "endDate": (-COMPLAINT_STAND_STILL),
            },
            "qualificationPeriod": {"startDate": (-COMPLAINT_STAND_STILL), "endDate": timedelta()},
            "auctionPeriod": {"startDate": timedelta()},
        },
    },
    "active.auction": {
        "start": {
            "enquiryPeriod": {
                "startDate": (-TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=1)),
                "endDate": (-COMPLAINT_STAND_STILL - TENDERING_DURATION + QUESTIONS_STAND_STILL),
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=1)),
                "endDate": (-COMPLAINT_STAND_STILL),
            },
            "qualificationPeriod": {"startDate": (-COMPLAINT_STAND_STILL), "endDate": timedelta()},
            "auctionPeriod": {"startDate": timedelta()},
        },
        "end": {
            "enquiryPeriod": {
                "startDate": (-TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)),
                "endDate": (-QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=1)),
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)),
                "endDate": (-COMPLAINT_STAND_STILL - timedelta(days=1)),
            },
            "qualificationPeriod": {
                "startDate": (-COMPLAINT_STAND_STILL - timedelta(days=1)),
                "endDate": (-timedelta(days=1)),
            },
            "auctionPeriod": {"startDate": -timedelta(days=1), "endDate": timedelta()},
        },
    },
    "active.qualification": {
        "start": {
            "enquiryPeriod": {
                "startDate": (-TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)),
                "endDate": (-QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=1)),
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)),
                "endDate": (-COMPLAINT_STAND_STILL - timedelta(days=1)),
            },
            "qualificationPeriod": {
                "startDate": (-COMPLAINT_STAND_STILL - timedelta(days=1)),
                "endDate": (-timedelta(days=1)),
            },
            "auctionPeriod": {"startDate": -timedelta(days=1), "endDate": timedelta()},
            "awardPeriod": {"startDate": timedelta()},
        },
        "end": {
            "enquiryPeriod": {
                "startDate": (-TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)),
                "endDate": (-QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=1)),
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)),
                "endDate": (-COMPLAINT_STAND_STILL - timedelta(days=1)),
            },
            "qualificationPeriod": {
                "startDate": (-COMPLAINT_STAND_STILL - timedelta(days=1)),
                "endDate": (-timedelta(days=1)),
            },
            "auctionPeriod": {"startDate": -timedelta(days=1), "endDate": timedelta()},
            "awardPeriod": {"startDate": timedelta()},
        },
    },
    "active.qualification.stand-still": {
        "start": {
            "enquiryPeriod": {
                "startDate": (-TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)),
                "endDate": (-QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=1)),
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)),
                "endDate": (-COMPLAINT_STAND_STILL - timedelta(days=1)),
            },
            "qualificationPeriod": {
                "startDate": (-COMPLAINT_STAND_STILL - timedelta(days=1)),
                "endDate": (-timedelta(days=1)),
            },
            "auctionPeriod": {"startDate": -timedelta(days=1), "endDate": timedelta()},
            "awardPeriod": {"startDate": timedelta(), "endDate": QUALIFICATION_COMPLAINT_STAND_STILL},
        },
        "end": {
            "enquiryPeriod": {
                "startDate": (
                    -TENDERING_DURATION
                    - COMPLAINT_STAND_STILL
                    - QUALIFICATION_COMPLAINT_STAND_STILL
                    - timedelta(days=2)
                ),
                "endDate": (
                    -QUESTIONS_STAND_STILL
                    - COMPLAINT_STAND_STILL
                    - QUALIFICATION_COMPLAINT_STAND_STILL
                    - timedelta(days=1)
                ),
            },
            "tenderPeriod": {
                "startDate": (
                    -TENDERING_DURATION
                    - COMPLAINT_STAND_STILL
                    - QUALIFICATION_COMPLAINT_STAND_STILL
                    - timedelta(days=2)
                ),
                "endDate": (-COMPLAINT_STAND_STILL - QUALIFICATION_COMPLAINT_STAND_STILL - timedelta(days=1)),
            },
            "qualificationPeriod": {
                "startDate": (-COMPLAINT_STAND_STILL - QUALIFICATION_COMPLAINT_STAND_STILL - timedelta(days=1)),
                "endDate": (-QUALIFICATION_COMPLAINT_STAND_STILL - timedelta(days=1)),
            },
            "auctionPeriod": {
                "startDate": (-QUALIFICATION_COMPLAINT_STAND_STILL - timedelta(days=1)),
                "endDate": (-QUALIFICATION_COMPLAINT_STAND_STILL),
            },
            "awardPeriod": {"startDate": (-QUALIFICATION_COMPLAINT_STAND_STILL), "endDate": timedelta()},
        },
    },
    "active.awarded": {
        "start": {
            "enquiryPeriod": {
                "startDate": (
                    -TENDERING_DURATION
                    - COMPLAINT_STAND_STILL
                    - QUALIFICATION_COMPLAINT_STAND_STILL
                    - timedelta(days=2)
                ),
                "endDate": (
                    -QUESTIONS_STAND_STILL
                    - COMPLAINT_STAND_STILL
                    - QUALIFICATION_COMPLAINT_STAND_STILL
                    - timedelta(days=1)
                ),
            },
            "tenderPeriod": {
                "startDate": (
                    -TENDERING_DURATION
                    - COMPLAINT_STAND_STILL
                    - QUALIFICATION_COMPLAINT_STAND_STILL
                    - timedelta(days=2)
                ),
                "endDate": (-COMPLAINT_STAND_STILL - QUALIFICATION_COMPLAINT_STAND_STILL - timedelta(days=1)),
            },
            "qualificationPeriod": {
                "startDate": (-COMPLAINT_STAND_STILL - QUALIFICATION_COMPLAINT_STAND_STILL - timedelta(days=1)),
                "endDate": (-QUALIFICATION_COMPLAINT_STAND_STILL - timedelta(days=1)),
            },
            "auctionPeriod": {
                "startDate": (-QUALIFICATION_COMPLAINT_STAND_STILL - timedelta(days=1)),
                "endDate": (-QUALIFICATION_COMPLAINT_STAND_STILL),
            },
            "awardPeriod": {"startDate": (-QUALIFICATION_COMPLAINT_STAND_STILL), "endDate": timedelta()},
            "contractPeriod": {"startDate": timedelta(), "clarificationsUntil": CLARIFICATIONS_UNTIL_PERIOD},
        },
        "end": {
            "enquiryPeriod": {
                "startDate": -TENDERING_DURATION
                - COMPLAINT_STAND_STILL
                - QUALIFICATION_COMPLAINT_STAND_STILL
                - CLARIFICATIONS_UNTIL_PERIOD
                - timedelta(days=3),
                "endDate": -QUESTIONS_STAND_STILL
                - COMPLAINT_STAND_STILL
                - QUALIFICATION_COMPLAINT_STAND_STILL
                - CLARIFICATIONS_UNTIL_PERIOD
                - timedelta(days=2),
            },
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION
                - COMPLAINT_STAND_STILL
                - QUALIFICATION_COMPLAINT_STAND_STILL
                - CLARIFICATIONS_UNTIL_PERIOD
                - timedelta(days=3),
                "endDate": -COMPLAINT_STAND_STILL
                - QUALIFICATION_COMPLAINT_STAND_STILL
                - CLARIFICATIONS_UNTIL_PERIOD
                - timedelta(days=2),
            },
            "qualificationPeriod": {
                "startDate": -COMPLAINT_STAND_STILL
                - QUALIFICATION_COMPLAINT_STAND_STILL
                - CLARIFICATIONS_UNTIL_PERIOD
                - timedelta(days=2),
                "endDate": -QUALIFICATION_COMPLAINT_STAND_STILL - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=2),
            },
            "auctionPeriod": {
                "startDate": -QUALIFICATION_COMPLAINT_STAND_STILL - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=2),
                "endDate": -QUALIFICATION_COMPLAINT_STAND_STILL - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1),
            },
            "awardPeriod": {
                "startDate": -QUALIFICATION_COMPLAINT_STAND_STILL - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1),
                "endDate": -CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1),
            },
            "contractPeriod": {
                "startDate": -CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1),
                "clarificationsUntil": -timedelta(days=1),
            },
        },
    },
    "complete": {
        "start": {
            "enquiryPeriod": {
                "startDate": (
                    -TENDERING_DURATION
                    - COMPLAINT_STAND_STILL
                    - QUALIFICATION_COMPLAINT_STAND_STILL
                    - timedelta(days=2)
                    - (CLARIFICATIONS_UNTIL_PERIOD + timedelta(days=1))
                ),
                "endDate": (
                    -QUESTIONS_STAND_STILL
                    - COMPLAINT_STAND_STILL
                    - QUALIFICATION_COMPLAINT_STAND_STILL
                    - timedelta(days=1)
                    - (CLARIFICATIONS_UNTIL_PERIOD + timedelta(days=1))
                ),
            },
            "tenderPeriod": {
                "startDate": (
                    -TENDERING_DURATION
                    - COMPLAINT_STAND_STILL
                    - QUALIFICATION_COMPLAINT_STAND_STILL
                    - timedelta(days=2)
                    - (CLARIFICATIONS_UNTIL_PERIOD + timedelta(days=1))
                ),
                "endDate": (
                    -COMPLAINT_STAND_STILL
                    - QUALIFICATION_COMPLAINT_STAND_STILL
                    - timedelta(days=1)
                    - (CLARIFICATIONS_UNTIL_PERIOD + timedelta(days=1))
                ),
            },
            "qualificationPeriod": {
                "startDate": (
                    -COMPLAINT_STAND_STILL
                    - QUALIFICATION_COMPLAINT_STAND_STILL
                    - timedelta(days=1)
                    - (CLARIFICATIONS_UNTIL_PERIOD + timedelta(days=1))
                ),
                "endDate": (
                    -QUALIFICATION_COMPLAINT_STAND_STILL
                    - timedelta(days=1)
                    - (CLARIFICATIONS_UNTIL_PERIOD + timedelta(days=1))
                ),
            },
            "auctionPeriod": {
                "startDate": (
                    -QUALIFICATION_COMPLAINT_STAND_STILL
                    - timedelta(days=1)
                    - (CLARIFICATIONS_UNTIL_PERIOD + timedelta(days=1))
                ),
                "endDate": (-QUALIFICATION_COMPLAINT_STAND_STILL - (CLARIFICATIONS_UNTIL_PERIOD + timedelta(days=1))),
            },
            "awardPeriod": {
                "startDate": (-QUALIFICATION_COMPLAINT_STAND_STILL - (CLARIFICATIONS_UNTIL_PERIOD + timedelta(days=1))),
                "endDate": (-(CLARIFICATIONS_UNTIL_PERIOD + timedelta(days=1))),
            },
            "contractPeriod": {
                "startDate": (-(CLARIFICATIONS_UNTIL_PERIOD + timedelta(days=1))),
                "clarificationsUntil": (-timedelta(days=1)),
                "endDate": timedelta(),
            },
        }
    },
}
