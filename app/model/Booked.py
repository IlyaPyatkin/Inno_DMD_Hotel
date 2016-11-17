from app.model.DBQuery import DBQuery
from time import strftime


class Booked:
    @staticmethod
    def query_check_in(hid):
        now = strftime("%Y-%m-%d %H:%M:%S")
        return DBQuery("""SELECT bid, fname, lname, checkin, booked.rid
                       FROM booked
                       JOIN person ON (booked.pid = person.pid)
                       JOIN hotel_rooms ON (booked.rid = hotel_rooms.rid)
                       WHERE hid = %s AND checkin < %s AND checkout > %s
                       AND bid NOT IN (SELECT bid FROM registration)
                       ORDER BY checkin""", (hid, now, now))

    @staticmethod
    def query_check_out(hid):
        return DBQuery("""SELECT bid, fname, lname, checkout, booked.rid
                          FROM booked
                          JOIN person ON (booked.pid = person.pid)
                          JOIN hotel_rooms ON (booked.rid = hotel_rooms.rid)
                          WHERE hid = %s
                          AND bid IN (SELECT bid FROM registration
                              WHERE regout IS NULL)
                          ORDER BY checkout""", (hid,))

    @staticmethod
    def search_hotels(arrival, departure, city, people):
        return DBQuery("""SELECT hotel_rooms.hid,title,rating,room.rtid,rtype,price
                          FROM room
                            JOIN roomtype ON room.rtid = roomtype.rtid
                            JOIN hotel_rooms ON hotel_rooms.rid = room.rid
                            JOIN hotel ON hotel_rooms.hid = hotel.hid
                            JOIN address ON hotel.aid = address.aid
                          WHERE room.rid IN (SELECT free_rooms_in_time_set(%s,%s))
                                AND city = %s
                                AND capacity >= %s
                          GROUP BY hotel_rooms.hid, rtype, room.rtid, price,title,rating
                          ORDER BY price ASC""", (arrival, departure, city, people))

    @staticmethod
    def get_free_hotel_room(hid, rtid, arrival, departure):
        return DBQuery("""SELECT room.rid FROM room
                            JOIN hotel_rooms ON hotel_rooms.rid = room.rid
                          WHERE room.rid IN (SELECT free_rooms_in_time_set(%s,%s))
                          AND hid = %s AND rtid = %s
                          LIMIT 1""", (arrival, departure, hid, rtid))

    @staticmethod
    def query_add(rid,pid,arrival,departure):
        return DBQuery("""INSERT INTO booked (rid,pid,checkin,checkout)
                          VALUES (%s, %s, %s, %s)""", (rid, pid, arrival, departure))
