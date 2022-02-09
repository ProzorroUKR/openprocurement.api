from datetime import timedelta

ESCO = "esco"
TENDERING_DAYS = 30
TENDERING_DURATION = timedelta(days=TENDERING_DAYS)
QUESTIONS_STAND_STILL = timedelta(days=10)
ENQUIRY_STAND_STILL_TIME = timedelta(days=3)
COMPLAINT_SUBMIT_TIME = timedelta(days=4)
ESCO_KINDS = ("authority", "central", "defense", "general", "social", "special")
