from app.model.DBQuery import DBQuery


class Hotel:
    @staticmethod
    def get_cities():
        return DBQuery("""SELECT DISTINCT city FROM hotel
                          JOIN hotel_rooms ON hotel.hid = hotel_rooms.hid
                          JOIN address ON hotel.aid = address.aid
                          ORDER BY city""")

    @staticmethod
    def get_order_extra(hid):
        return DBQuery("""SELECT title, rating, country, city, street, appartment
                          FROM hotel JOIN address ON hotel.aid = address.aid
                          WHERE hid = %s""", (hid,))