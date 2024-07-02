from datetime import timedelta

ESCO = "esco"
TENDERING_DAYS = 30
TENDERING_DURATION = timedelta(days=TENDERING_DAYS)
QUESTIONS_STAND_STILL = timedelta(days=10)
COMPLAINT_SUBMIT_TIME = timedelta(days=4)
ESCO_KINDS = ("authority", "central", "defense", "general", "social", "special")
