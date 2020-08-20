from datetime import timedelta

PERIODS = {
    "active.tendering": {
        "start": {
            "enquiryPeriod": {
                "startDate": timedelta(),
                "endDate": timedelta() + timedelta(days=13),
            },
            "tenderPeriod": {
                "startDate": timedelta(),
                "endDate": timedelta() + timedelta(days=16)
            },
        },
        "enquiry_end": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=13),
                "endDate": -timedelta(days=1),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=13),
                "endDate": timedelta(days=1),
            },
            "auctionPeriod": {"startDate": timedelta(days=2)},
        },
        "complaint_end": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=12),
                "endDate": timedelta(),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=12),
                "endDate": timedelta(days=1),
            },
            "auctionPeriod": {"startDate": timedelta(days=2)}
        },
    },
    "active.auction": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=16),
                "endDate": -timedelta(days=3),
            },
            "tenderPeriod": {"startDate": -timedelta(days=16), "endDate": timedelta()},
            "auctionPeriod": {"startDate": timedelta()},
        }
    },
    "active.qualification": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=17),
                "endDate": -timedelta(days=4),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=17),
                "endDate": -timedelta(days=1),
            },
            "auctionPeriod": {"startDate": -timedelta(days=1), "endDate": timedelta()},
            "awardPeriod": {"startDate": timedelta()},
        }
    },
    "active.awarded": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=17),
                "endDate": -timedelta(days=4),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=17),
                "endDate": -timedelta(days=1),
            },
            "auctionPeriod": {"startDate": -timedelta(days=1), "endDate": timedelta()},
            "awardPeriod": {"startDate": timedelta(), "endDate": timedelta()},
        }
    },
    "complete": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=25),
                "endDate": -timedelta(days=11),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=25),
                "endDate": -timedelta(days=8),
            },
            "auctionPeriod": {
                "startDate": -timedelta(days=8),
                "endDate": -timedelta(days=7),
            },
            "awardPeriod": {
                "startDate": -timedelta(days=7),
                "endDate": -timedelta(days=7),
            },
        }
    }
}
