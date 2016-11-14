import re
from flask import redirect, url_for
from app.model.DBQuery import DBQuery


class User:
    ROLE_USER = 0
    ROLE_MANAGER = 1
    ROLE_ADMIN = 2

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
    def check_password(password):
        return re.match("^[a-z0-9_-]{6,18}$", password)

    @staticmethod
    def check_username(username):
        return re.match("^[a-z0-9_-]{3,16}$", username)

    @staticmethod
    def get_redirect_by_role(role):
        if role == User.ROLE_MANAGER:
            return redirect(url_for('manager'))
        elif role == User.ROLE_ADMIN:
            return redirect(url_for('manager'))
        return redirect(url_for('index'))
