import re


class Person:
    @staticmethod
    def check_name(name):
        return re.match("^[a-zA-Z]{2,18}$", name)

    @staticmethod
    def check_email(email):
        return re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)
