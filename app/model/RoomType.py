from app.model.DBQuery import DBQuery


class RoomType:
    @staticmethod
    def get_roomtype(rtid):
        return DBQuery("SELECT rtype, price FROM roomtype WHERE rtid = %s", (rtid,))
