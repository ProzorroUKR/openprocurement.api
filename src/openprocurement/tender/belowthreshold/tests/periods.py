from datetime import timedelta

PERIODS = {
    "active.enquiries": {
        "start": {
            "enquiryPeriod": {
                "startDate": timedelta(),
                "endDate": timedelta(days=7)
            },
            "tenderPeriod": {
                "startDate": timedelta(days=7),
                "endDate": timedelta(days=14),
            },
        },
    },
    "active.tendering": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=10),
                "endDate": timedelta(),
            },
            "tenderPeriod": {
                "startDate": timedelta(),
                "endDate": timedelta(days=7)
            },
        }
    },
    "active.auction": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=14),
                "endDate": -timedelta(days=7),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=7),
                "endDate": timedelta()
            },
            "auctionPeriod": {
                "startDate": timedelta()
            },
        }
    },
    "active.qualification": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=15),
                "endDate": -timedelta(days=8),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=8),
                "endDate": -timedelta(days=1),
            },
            "auctionPeriod": {
                "startDate": -timedelta(days=1),
                "endDate": timedelta()
            },
            "awardPeriod": {
                "startDate": timedelta()
            },
        }
    },
    "active.awarded": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=15),
                "endDate": -timedelta(days=8),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=8),
                "endDate": -timedelta(days=1),
            },
            "auctionPeriod": {
                "startDate": -timedelta(days=1),
                "endDate": timedelta()
            },
            "awardPeriod": {
                "startDate": timedelta(),
                "endDate": timedelta()
            },
        }
    },
    "complete": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=25),
                "endDate": -timedelta(days=18),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=18),
                "endDate": -timedelta(days=11),
            },
            "auctionPeriod": {
                "startDate": -timedelta(days=11),
                "endDate": -timedelta(days=10),
            },
            "awardPeriod": {
                "startDate": -timedelta(days=10),
                "endDate": -timedelta(days=10),
            },
        }
    }
}
