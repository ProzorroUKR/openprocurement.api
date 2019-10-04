from datetime import datetime, timedelta

from openprocurement.api.constants import TZ
from openprocurement.tender.cfaselectionua.constants import (
    ENQUIRY_PERIOD,
    TENDERING_DURATION,
    AUCTION_DURATION,
    COMPLAINT_DURATION,
    CLARIFICATIONS_DURATION,
)

periods = {
    "active.enquiries": {
        "start": {
            "enquiryPeriod": {"startDate": timedelta(), "endDate": (+ENQUIRY_PERIOD)},
            "tenderPeriod": {"startDate": (+ENQUIRY_PERIOD), "endDate": (+ENQUIRY_PERIOD + TENDERING_DURATION)},
        },
        "end": {
            "enquiryPeriod": {"startDate": (-ENQUIRY_PERIOD), "endDate": timedelta()},
            "tenderPeriod": {"startDate": timedelta(), "endDate": (+TENDERING_DURATION)},
        },
    },
    "active.tendering": {
        "start": {
            "enquiryPeriod": {"startDate": (-ENQUIRY_PERIOD), "endDate": timedelta()},
            "tenderPeriod": {"startDate": timedelta(), "endDate": (+TENDERING_DURATION)},
        },
        "end": {
            "enquiryPeriod": {"startDate": (-ENQUIRY_PERIOD - TENDERING_DURATION), "endDate": (-TENDERING_DURATION)},
            "tenderPeriod": {"startDate": (-TENDERING_DURATION), "endDate": timedelta()},
        },
    },
    "active.auction": {
        "start": {
            "enquiryPeriod": {"startDate": (-ENQUIRY_PERIOD - TENDERING_DURATION), "endDate": (-TENDERING_DURATION)},
            "tenderPeriod": {"startDate": (-TENDERING_DURATION), "endDate": timedelta()},
            "auctionPeriod": {"startDate": timedelta()},
        },
        "end": {
            "enquiryPeriod": {
                "startDate": (-ENQUIRY_PERIOD - TENDERING_DURATION - AUCTION_DURATION),
                "endDate": (-TENDERING_DURATION - AUCTION_DURATION),
            },
            "tenderPeriod": {"startDate": (-TENDERING_DURATION - AUCTION_DURATION), "endDate": (-AUCTION_DURATION)},
            "auctionPeriod": {"startDate": (-AUCTION_DURATION), "endDate": timedelta()},
        },
    },
    "active.qualification": {
        "start": {
            "enquiryPeriod": {
                "startDate": (-ENQUIRY_PERIOD - TENDERING_DURATION - AUCTION_DURATION),
                "endDate": (-TENDERING_DURATION - AUCTION_DURATION),
            },
            "tenderPeriod": {"startDate": (-TENDERING_DURATION - AUCTION_DURATION), "endDate": (-AUCTION_DURATION)},
            "auctionPeriod": {"startDate": (-AUCTION_DURATION), "endDate": timedelta()},
            "awardPeriod": {"startDate": timedelta()},
        },
        "end": {
            "enquiryPeriod": {
                "startDate": (-ENQUIRY_PERIOD - TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION),
                "endDate": (-TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION),
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION),
                "endDate": (-AUCTION_DURATION - COMPLAINT_DURATION),
            },
            "auctionPeriod": {"startDate": (-AUCTION_DURATION - COMPLAINT_DURATION), "endDate": (-COMPLAINT_DURATION)},
            "awardPeriod": {"startDate": (-COMPLAINT_DURATION), "endDate": timedelta()},
        },
    },
    "active.awarded": {
        "start": {
            "enquiryPeriod": {
                "startDate": (-ENQUIRY_PERIOD - TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION),
                "endDate": (-TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION),
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION),
                "endDate": (-AUCTION_DURATION - COMPLAINT_DURATION),
            },
            "auctionPeriod": {"startDate": (-AUCTION_DURATION - COMPLAINT_DURATION), "endDate": (-COMPLAINT_DURATION)},
            "awardPeriod": {"startDate": (-COMPLAINT_DURATION), "endDate": timedelta()},
        },
        "end": {
            "enquiryPeriod": {
                "startDate": (
                    -ENQUIRY_PERIOD
                    - TENDERING_DURATION
                    - AUCTION_DURATION
                    - COMPLAINT_DURATION
                    - CLARIFICATIONS_DURATION
                ),
                "endDate": (-TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION),
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION),
                "endDate": (-AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION),
            },
            "auctionPeriod": {
                "startDate": (-AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION),
                "endDate": (-COMPLAINT_DURATION - CLARIFICATIONS_DURATION),
            },
            "awardPeriod": {
                "startDate": (-COMPLAINT_DURATION - CLARIFICATIONS_DURATION),
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
                ),
                "endDate": (-TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION),
            },
            "tenderPeriod": {
                "startDate": (-TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION),
                "endDate": (-AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION),
            },
            "auctionPeriod": {
                "startDate": (-AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION),
                "endDate": (-COMPLAINT_DURATION - CLARIFICATIONS_DURATION),
            },
            "awardPeriod": {
                "startDate": (-COMPLAINT_DURATION - CLARIFICATIONS_DURATION),
                "endDate": (-CLARIFICATIONS_DURATION),
            },
        }
    },
}
