import re
from flask import redirect, url_for
from app.model.DBQuery import DBQuery
from time import strftime


class User:
    ROLE_USER = 0
    ROLE_MANAGER = 1
    ROLE_ADMIN = 2

    @staticmethod
    def check_password(password):
        return re.match("^[a-zA-Z0-9_-]{6,24}$", password)

    @staticmethod
    def check_username(username):
        return re.match("^[a-z0-9_-]{6,16}$", username)

    @staticmethod
    def get_role(username):
        return DBQuery("SELECT role FROM users WHERE username = %s", (username,))

    @staticmethod
    def get_redirect_by_role(role):
        if role == User.ROLE_MANAGER:
            return redirect(url_for('manager'))
        elif role == User.ROLE_ADMIN:
            return redirect(url_for('admin'))
        return redirect(url_for('index'))

    @staticmethod
    def get_user_id(username):
        return DBQuery("SELECT uid FROM users WHERE username = %s", (username,))

    @staticmethod
    def get_person_id(username):
        return DBQuery("""SELECT pid FROM person
                          JOIN users ON person.uid = users.uid
                          WHERE username = %s""", (username,))

    @staticmethod
    def query_add(username, password, role):
        return DBQuery("""INSERT INTO users (username, hash, role)
                           VALUES (%s, %s, %s)""", (username, password, role))

    @staticmethod
    def query_username(username):
        return DBQuery("SELECT * FROM users WHERE username = %s", (username,))

    @staticmethod
    def query_hash_role(username):
        return DBQuery("SELECT hash, role FROM users WHERE username = %s", (username,))

    @staticmethod
    def get_manager_hotel(username):
        return DBQuery("""SELECT hotel.hid, title FROM users
                          JOIN person ON (person.uid = users.uid)
                          JOIN employee ON (employee.pid = person.pid)
                          JOIN hotel ON (employee.hid = hotel.hid)
                          WHERE username = %s""", (username,))

    @staticmethod
    def get_person(username):
        return DBQuery("""SELECT fname, lname, email FROM person
                          WHERE uid = (SELECT uid FROM users
                          WHERE username = %s)""", (username,))

    @staticmethod
    def query_update_person(fname, lname, email, username):
        userid_query = User.get_user_id(username)
        if userid_query.code == DBQuery.CODE_OK and userid_query.result:
            uid = userid_query.result[0][0]
        else:
            return userid_query

        today = strftime("%Y-%m-%d")
        return DBQuery("""UPDATE person
                          SET (fname, lname, email) = (%(fname)s, %(lname)s, %(email)s)
                          WHERE uid = %(uid)s;
                          INSERT INTO person (uid, fname, lname, email, reg_date)
                          SELECT %(uid)s, %(fname)s, %(lname)s, %(email)s, %(today)s
                          WHERE NOT EXISTS (SELECT 1 FROM person WHERE uid = %(uid)s)""",
                       {'fname': fname,
                        'lname': lname,
                        'email': email,
                        'uid': uid,
                        'today': today})

    @staticmethod
    def get_orders(username):
        person_query = User.get_person_id(username)
        if person_query.code == DBQuery.CODE_OK and person_query.result:
            pid = person_query.result[0][0]
        else:
            return person_query

        return DBQuery("""SELECT booked.bid,title,checkin,checkout,
                                 rtype,room.rid,cost,rating,regid
                          FROM booked
                          JOIN room ON booked.rid = room.rid
                          JOIN roomtype ON room.rtid = roomtype.rtid
                          JOIN hotel_rooms ON room.rid = hotel_rooms.rid
                          LEFT OUTER JOIN registration ON booked.bid = registration.bid
                          JOIN hotel ON hotel_rooms.hid = hotel.hid
                          WHERE pid = %s""", (pid,))

    @staticmethod
    def delete_person_order(username, bid):
        person_query = User.get_person_id(username)
        if person_query.code == DBQuery.CODE_OK and person_query.result:
            pid = person_query.result[0][0]
        else:
            return person_query

        return DBQuery("DELETE FROM booked WHERE bid = %s AND pid = %s", (bid, pid))

    @staticmethod
    def registered_check_query(bid):
        return DBQuery("SELECT * FROM registration WHERE bid = %s", (bid,))
