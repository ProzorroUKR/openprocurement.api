from datetime import timedelta

PERIODS = {
    "active.tendering": {
        "start": {
            "enquiryPeriod": {
                "startDate": timedelta(),
                "endDate": timedelta(days=5),
            },
            "tenderPeriod": {
                "startDate": timedelta(),
                "endDate": timedelta(days=8),
            },
        },
        "enquiry_end": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=7),
                "endDate": -timedelta(days=1),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=7),
                "endDate": timedelta(days=2),
            },
            "auctionPeriod": {
                "startDate": timedelta(days=2),
            },
        },
        "complaint_end": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=6),
                "endDate": timedelta(days=1),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=6),
                "endDate": timedelta(days=3),
            },
            "auctionPeriod": {
                "startDate": timedelta(days=2),
            },
        }
    },
    "active.auction": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=8),
                "endDate": -timedelta(days=3),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=8),
                "endDate": timedelta(),
            },
            "auctionPeriod": {
                "startDate": timedelta(),
            },
        }
    },
    "active.qualification": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=9),
                "endDate": -timedelta(days=4),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=9),
                "endDate": -timedelta(days=1),
            },
            "complaintPeriod": {
                "startDate": -timedelta(days=9),
                "endDate": -timedelta(days=1),
            },
            "auctionPeriod": {
                "startDate": -timedelta(days=1),
                "endDate": timedelta(),
            },
            "awardPeriod": {
                "startDate": timedelta(),
            },
        }
    },
    "active.awarded": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=9),
                "endDate": -timedelta(days=4),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=9),
                "endDate": -timedelta(days=1),
            },
            "auctionPeriod": {
                "startDate": -timedelta(days=1),
                "endDate": timedelta(),
            },
            "awardPeriod": {
                "startDate": timedelta(),
                "endDate": timedelta(),
            },
        }
    },
    "complete": {
        "start": {
            "enquiryPeriod": {
                "startDate": -timedelta(days=16),
                "endDate": -timedelta(days=10),
            },
            "tenderPeriod": {
                "startDate": -timedelta(days=16),
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
