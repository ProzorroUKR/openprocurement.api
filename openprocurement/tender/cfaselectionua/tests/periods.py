from datetime import datetime, timedelta

from openprocurement.api.constants import TZ
from openprocurement.tender.cfaselectionua.constants import (
    ENQUIRY_PERIOD, TENDERING_DURATION, AUCTION_DURATION,
    COMPLAINT_DURATION, CLARIFICATIONS_DURATION
)


def get_periods():
    now = datetime.now(TZ)
    periods = {
        'active.enquiries': {
            'start': {
                'enquiryPeriod': {
                    'startDate': now.isoformat(),
                    'endDate': (now + ENQUIRY_PERIOD).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now + ENQUIRY_PERIOD).isoformat(),
                    'endDate': (now + ENQUIRY_PERIOD + TENDERING_DURATION).isoformat(),
                }
            },
            'end': {
                'enquiryPeriod': {
                    'startDate': (now - ENQUIRY_PERIOD).isoformat(),
                    'endDate': now.isoformat()
                },
                'tenderPeriod': {
                    'startDate': now.isoformat(),
                    'endDate': (now + TENDERING_DURATION).isoformat(),
                }
            }
        },
        'active.tendering': {
            'start': {
                'enquiryPeriod': {
                    'startDate': (now - ENQUIRY_PERIOD).isoformat(),
                    'endDate': now.isoformat()
                },
                'tenderPeriod': {
                    'startDate': now.isoformat(),
                    'endDate': (now + TENDERING_DURATION).isoformat(),
                }
            },
            'end': {
                'enquiryPeriod': {
                    'startDate': (now - ENQUIRY_PERIOD - TENDERING_DURATION).isoformat(),
                    'endDate': (now - TENDERING_DURATION).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION).isoformat(),
                    'endDate': now.isoformat(),
                }
            }
        },
        'active.auction': {
            'start': {
                'enquiryPeriod': {
                    'startDate': (now - ENQUIRY_PERIOD - TENDERING_DURATION).isoformat(),
                    'endDate': (now - TENDERING_DURATION).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION).isoformat(),
                    'endDate': now.isoformat(),
                },
                'auctionPeriod': {
                    'startDate': now.isoformat()
                }
            },
            'end': {
                'enquiryPeriod': {
                    'startDate': (now - ENQUIRY_PERIOD - TENDERING_DURATION - AUCTION_DURATION).isoformat(),
                    'endDate': (now - TENDERING_DURATION - AUCTION_DURATION).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - AUCTION_DURATION).isoformat(),
                    'endDate': (now - AUCTION_DURATION).isoformat(),
                },
                'auctionPeriod': {
                    'startDate': (now - AUCTION_DURATION).isoformat(),
                    'endDate': now.isoformat(),
                }

            }
        },
        'active.qualification': {
            'start': {
                'enquiryPeriod': {
                    'startDate': (now - ENQUIRY_PERIOD - TENDERING_DURATION - AUCTION_DURATION).isoformat(),
                    'endDate': (now - TENDERING_DURATION - AUCTION_DURATION).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - AUCTION_DURATION).isoformat(),
                    'endDate': (now - AUCTION_DURATION).isoformat(),
                },
                'auctionPeriod': {
                    'startDate': (now - AUCTION_DURATION).isoformat(),
                    'endDate': now.isoformat(),
                },
                'awardPeriod': {
                    'startDate': now.isoformat()
                }
            },
            'end': {
                'enquiryPeriod': {
                    'startDate': (now - ENQUIRY_PERIOD - TENDERING_DURATION
                                  - AUCTION_DURATION - COMPLAINT_DURATION).isoformat(),
                    'endDate': (now - TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION).isoformat(),
                    'endDate': (now - AUCTION_DURATION - COMPLAINT_DURATION).isoformat(),
                },
                'auctionPeriod': {
                    'startDate': (now - AUCTION_DURATION - COMPLAINT_DURATION).isoformat(),
                    'endDate': (now - COMPLAINT_DURATION).isoformat(),
                },
                'awardPeriod': {
                    'startDate': (now - COMPLAINT_DURATION).isoformat(),
                    'endDate': now.isoformat()
                }

            }
        },
        'active.awarded': {
            'start': {
                'enquiryPeriod': {
                    'startDate': (now - ENQUIRY_PERIOD - TENDERING_DURATION
                                  - AUCTION_DURATION - COMPLAINT_DURATION).isoformat(),
                    'endDate': (now - TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - AUCTION_DURATION - COMPLAINT_DURATION).isoformat(),
                    'endDate': (now - AUCTION_DURATION - COMPLAINT_DURATION).isoformat(),
                },
                'auctionPeriod': {
                    'startDate': (now - AUCTION_DURATION - COMPLAINT_DURATION).isoformat(),
                    'endDate': (now - COMPLAINT_DURATION).isoformat(),
                },
                'awardPeriod': {
                    'startDate': (now - COMPLAINT_DURATION).isoformat(),
                    'endDate': now.isoformat()
                }
            },
            'end': {
                'enquiryPeriod': {
                    'startDate': (now - ENQUIRY_PERIOD - TENDERING_DURATION
                                  - AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat(),
                    'endDate': (now - TENDERING_DURATION - AUCTION_DURATION
                                - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - AUCTION_DURATION
                                  - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat(),
                    'endDate': (now - AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat(),
                },
                'auctionPeriod': {
                    'startDate': (now - AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat(),
                    'endDate': (now - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat(),
                },
                'awardPeriod': {
                    'startDate': (now - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat(),
                    'endDate': (now - CLARIFICATIONS_DURATION).isoformat()
                }
            },
        },
        'complete': {
            'start': {
                'enquiryPeriod': {
                    'startDate': (now - ENQUIRY_PERIOD - TENDERING_DURATION
                                  - AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat(),
                    'endDate': (now - TENDERING_DURATION - AUCTION_DURATION
                                - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - AUCTION_DURATION
                                  - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat(),
                    'endDate': (now - AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat(),
                },
                'auctionPeriod': {
                    'startDate': (now - AUCTION_DURATION - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat(),
                    'endDate': (now - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat(),
                },
                'awardPeriod': {
                    'startDate': (now - COMPLAINT_DURATION - CLARIFICATIONS_DURATION).isoformat(),
                    'endDate': (now - CLARIFICATIONS_DURATION).isoformat()
                }
            }
        }
    }
    return periods
