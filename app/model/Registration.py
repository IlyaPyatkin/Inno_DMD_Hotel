from app.model.DBQuery import DBQuery
from time import strftime


class Registration:
    @staticmethod
    def query_register_check_in(bid):
        now = strftime("%Y-%m-%d %H:%M:%S")
        return DBQuery("""INSERT INTO registration (bid, regin)
                          VALUES (%s, %s)""", (bid, now))

    @staticmethod
    def query_register_check_out(bid):
        now = strftime("%Y-%m-%d %H:%M:%S")
        return DBQuery("""UPDATE registration
                          SET regout = %s
                          WHERE bid = %s""", (now, bid))
