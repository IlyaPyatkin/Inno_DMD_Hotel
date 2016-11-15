from app.model.DBQuery import DBQuery
from time import strftime


class Booked:
    @staticmethod
    def query_check_in():
        now = strftime("%Y-%m-%d %H:%M:%S")
        return DBQuery("""SELECT bid, fname, lname, checkin, rid
                       FROM booked
                       JOIN person ON (booked.pid = person.pid)
                       WHERE checkin < %s""", (now,))

    @staticmethod
    def query_check_out():
        now = strftime("%Y-%m-%d %H:%M:%S")
        return DBQuery("""SELECT bid, fname, lname, checkout, rid
                           FROM booked
                           JOIN person ON (booked.pid = person.pid)
                           WHERE checkout < %s""", (now,))
