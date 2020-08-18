from datetime import timedelta

from openprocurement.tender.cfaselectionua.constants import (
    ENQUIRY_PERIOD,
    TENDERING_DURATION,
    AUCTION_DURATION,
    COMPLAINT_DURATION,
    CLARIFICATIONS_DURATION,
)

PERIODS = {
    "active.enquiries": {
        "start": {
            "enquiryPeriod": {
                "startDate": timedelta(),
                "endDate": (+ENQUIRY_PERIOD + timedelta(days=1))
            },
            "tenderPeriod": {
                "startDate": (+ENQUIRY_PERIOD + timedelta(days=1)),
                "endDate": (+ENQUIRY_PERIOD + TENDERING_DURATION + timedelta(days=2))
            },
        },
        "end": {
            "enquiryPeriod": {
                "startDate": (-ENQUIRY_PERIOD - timedelta(days=1)),
                "endDate": timedelta()
            },
            "tenderPeriod": {
                "startDate": timedelta(),
                "endDate": (+TENDERING_DURATION + timedelta(days=1))},
        },
    },
    "active.tendering": {
        "start": {
            "enquiryPeriod": {
                "startDate": (-ENQUIRY_PERIOD - timedelta(days=1)),
                "endDate": timedelta()
            },
            "tenderPeriod": {
                "startDate": timedelta(),
                "endDate": (+TENDERING_DURATION + timedelta(days=1))
            },
        },
        "end": {
            "enquiryPeriod": {
                "startDate": (-ENQUIRY_PERIOD - TENDERING_DURATION - timedelta(days=2)),
                "endDate": (-TENDERING_DURATION - timedelta(days=1))
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - timedelta(days=1)),
                "endDate": timedelta()
            },
        },
    },
    "active.auction": {
        "start": {
            "enquiryPeriod": {
                "startDate": (-ENQUIRY_PERIOD - TENDERING_DURATION - timedelta(days=2)),
                "endDate": (-TENDERING_DURATION - timedelta(days=1))
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - timedelta(days=1)),
                "endDate": timedelta()},
            "auctionPeriod": {
                "startDate": timedelta()
            },
        },
        "end": {
            "enquiryPeriod": {
                "startDate": (-ENQUIRY_PERIOD - TENDERING_DURATION - AUCTION_DURATION - timedelta(days=3)),
                "endDate": (-TENDERING_DURATION - AUCTION_DURATION - timedelta(days=2)),
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - AUCTION_DURATION - timedelta(days=2)),
                "endDate": (-AUCTION_DURATION - timedelta(days=1))
            },
            "auctionPeriod": {
                "startDate": (-AUCTION_DURATION - timedelta(days=1)),
                "endDate": timedelta()
            },
        },
    },
    "active.qualification": {
        "start": {
            "enquiryPeriod": {
                "startDate": (-ENQUIRY_PERIOD - TENDERING_DURATION - AUCTION_DURATION - timedelta(days=3)),
                "endDate": (-TENDERING_DURATION - AUCTION_DURATION - timedelta(days=2)),
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - AUCTION_DURATION - timedelta(days=2)),
                "endDate": (-AUCTION_DURATION - timedelta(days=1))
            },
            "auctionPeriod": {
                "startDate": (-AUCTION_DURATION - timedelta(days=1)),
                "endDate": timedelta()
            },
            "awardPeriod": {"startDate": timedelta()},
        },
        "end": {
            "enquiryPeriod": {
                "startDate": (
                    -ENQUIRY_PERIOD
                    - TENDERING_DURATION
                    - AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - timedelta(days=3)
                ),
                "endDate": (
                    -TENDERING_DURATION
                    - AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - timedelta(days=2)
                ),
            },
            "tenderPeriod": {
                "startDate": (
                    -TENDERING_DURATION
                    - AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - timedelta(days=2)
                ),
                "endDate": (
                    -AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - timedelta(days=1)
                ),
            },
            "auctionPeriod": {
                "startDate": (-AUCTION_DURATION - COMPLAINT_DURATION - timedelta(days=1)),
                "endDate": (-COMPLAINT_DURATION - timedelta(days=1))
            },
            "awardPeriod": {
                "startDate": (-COMPLAINT_DURATION - timedelta(days=1)),
                "endDate": timedelta()
            },
        },
    },
    "active.awarded": {
        "start": {
            "enquiryPeriod": {
                "startDate": (
                    -ENQUIRY_PERIOD
                    - TENDERING_DURATION
                    - AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - timedelta(days=3)
                ),
                "endDate": (
                    -TENDERING_DURATION
                    - AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - timedelta(days=2)
                ),
            },
            "tenderPeriod": {
                "startDate": (
                    -TENDERING_DURATION
                    - AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - timedelta(days=2)
                ),
                "endDate": (
                    -AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - timedelta(days=1)
                ),
            },
            "auctionPeriod": {
                "startDate": (-AUCTION_DURATION - COMPLAINT_DURATION - timedelta(days=1)),
                "endDate": (-COMPLAINT_DURATION - timedelta(days=1))
            },
            "awardPeriod": {
                "startDate": (-COMPLAINT_DURATION - timedelta(days=1)),
                "endDate": timedelta()
            },
        },
        "end": {
            "enquiryPeriod": {
                "startDate": (
                    -ENQUIRY_PERIOD
                    - TENDERING_DURATION
                    - AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - CLARIFICATIONS_DURATION
                    - timedelta(days=3)
                ),
                "endDate": (
                    -TENDERING_DURATION
                    - AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - CLARIFICATIONS_DURATION
                    - timedelta(days=2)
                ),
            },
            "tenderPeriod": {
                "startDate": (
                    -TENDERING_DURATION
                    - AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - CLARIFICATIONS_DURATION
                    - timedelta(days=2)
                ),
                "endDate": (
                    -AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - CLARIFICATIONS_DURATION
                    - timedelta(days=1)
                ),
            },
            "auctionPeriod": {
                "startDate": (
                    -AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - CLARIFICATIONS_DURATION
                    - timedelta(days=1)
                ),
                "endDate": (-COMPLAINT_DURATION - CLARIFICATIONS_DURATION - timedelta(days=1)),
            },
            "awardPeriod": {
                "startDate": (-COMPLAINT_DURATION - CLARIFICATIONS_DURATION - timedelta(days=1)),
                "endDate": (-CLARIFICATIONS_DURATION),
            },
        },
    },
    "complete": {
        "start": {
            "enquiryPeriod": {
                "startDate": (
                    -ENQUIRY_PERIOD
                    - TENDERING_DURATION
                    - AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - CLARIFICATIONS_DURATION
                    - timedelta(days=3)
                ),
                "endDate": (
                    -TENDERING_DURATION
                    - AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - CLARIFICATIONS_DURATION
                    - timedelta(days=2)
                ),
            },
            "tenderPeriod": {
                "startDate": (
                    -TENDERING_DURATION
                    - AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - CLARIFICATIONS_DURATION
                    - timedelta(days=2)
                ),
                "endDate": (
                    -AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - CLARIFICATIONS_DURATION
                    - timedelta(days=1)
                ),
            },
            "auctionPeriod": {
                "startDate": (
                    -AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - CLARIFICATIONS_DURATION
                    - timedelta(days=1)
                ),
                "endDate": (
                    -COMPLAINT_DURATION
                    - CLARIFICATIONS_DURATION
                    - timedelta(days=1)
                ),
            },
            "awardPeriod": {
                "startDate": (
                    -COMPLAINT_DURATION
                    - CLARIFICATIONS_DURATION
                    - timedelta(days=1)
                ),
                "endDate": (
                    -CLARIFICATIONS_DURATION
                ),
            },
        }
    },
}
