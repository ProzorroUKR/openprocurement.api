from datetime import timedelta

TENDERING_DURATION = timedelta(days=17)

PERIODS = {
    "active.tendering": {
        "start": {
            "tenderPeriod": {
                "startDate": -timedelta(days=1),
                "endDate": TENDERING_DURATION + timedelta(days=1),
            },
        },
        "enquiry_end": {
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=1),
                "endDate": timedelta(days=2),
            },
            "auctionPeriod": {"startDate": timedelta(days=2)},
        },
        "complaint_end": {
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=2),
                "endDate": timedelta(days=3),
            },
            "auctionPeriod": {"startDate": timedelta(days=2)},
        },
        "end": {
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=1),
                "endDate": timedelta(),
            },
        },
    },
    "active.auction": {
        "start": {
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=1),
                "endDate": timedelta(),
            },
            "auctionPeriod": {"startDate": timedelta()},
        }
    },
    "active.qualification": {
        "start": {
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=2),
                "endDate": -timedelta(days=1),
            },
            "auctionPeriod": {"startDate": -timedelta(days=1), "endDate": timedelta()},
            "awardPeriod": {"startDate": timedelta()},
        }
    },
    "active.awarded": {
        "start": {
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=3),
                "endDate": -timedelta(days=2),
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
            "tenderPeriod": {
                "startDate": -TENDERING_DURATION - timedelta(days=4),
                "endDate": -timedelta(days=3),
            },
            "auctionPeriod": {
                "startDate": -timedelta(days=3),
                "endDate": -timedelta(days=2),
            },
            "awardPeriod": {"startDate": -timedelta(days=1), "endDate": timedelta()},
        }
    },
}
