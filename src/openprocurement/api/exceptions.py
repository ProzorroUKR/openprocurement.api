#  mongodb
class MongodbResourceConflict(Exception):
    """
    On doc update we pass _id and _rev as filter
    _rev can be changed by concurrent requests
    then update_one(or replace_one) doesn't find any document to update and returns matched_count = 0
    that causes MongodbResourceConflict that is shown to the User as 409 response code
    that means they have to retry his request
    """
