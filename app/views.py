from flask import render_template, request, session, redirect, url_for
from passlib.apps import custom_app_context as pwd_context

from app import app
from app.model.DBQuery import DBQuery
from app.model.User import User


def logged_in():
    return 'username' in session


def log_in_as(username, role=User.ROLE_USER):
    session['username'] = username
    session['role'] = role


def log_out():
    if logged_in():
        del session['username']


@app.route('/')
def index():
    if logged_in():
        user = session['username']
    else:
        user = 'guest'
    return render_template("index.html",
                           user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if logged_in():
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        pwd_hash_role_query = User.query_hash_role(username)
        if pwd_hash_role_query.code == DBQuery.CODE_OK and pwd_hash_role_query.result:
            pwd_hash = pwd_hash_role_query.result[0][0]
            role = pwd_hash_role_query.result[0][1]
            if pwd_context.verify(password, pwd_hash):
                # If login successful
                log_in_as(username, role)
                return User.get_redirect_by_role(role)
        return render_template("login.html",
                               error='Invalid credentials',
                               session=session)
    return render_template("login.html",
                           session=session)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if logged_in():
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User.check_username(username):
            return render_template("signup.html",
                                   error="Invalid username")

        if not User.check_password(password):
            return render_template("signup.html",
                                   error="Invalid password")

        # Check if user with given username already exists
        check_query = User.query_username(username)
        if check_query.code == DBQuery.CODE_OK:
            if check_query.result:
                return render_template("signup.html",
                                       error="Username %s is already taken" % username)
        else:
            return render_template("signup.html",
                                   error="An error occurred, try again later")

        pwd_hash = pwd_context.encrypt(password)

        add_query = User.query_add(username, pwd_hash, User.ROLE_USER)
        if add_query.code == DBQuery.CODE_OK:
            # Automatically login
            log_in_as(username)
            return redirect(url_for('index'))
        else:
            return render_template("signup.html",
                                   error="An error occurred, try again later")

    return render_template("signup.html")


@app.route('/logout')
def logout():
    log_out()
    return redirect(url_for('index'))


@app.route('/manager', methods=['GET', 'POST'])
def manager():
    if not logged_in() or session['role'] < User.ROLE_MANAGER:
        return error404(404)
    return render_template("manager.html")


@app.errorhandler(404)
def error404(e):
    return render_template("page_not_found.html"), 404


app.secret_key = b'7\xeb\xc8^\xc2~\xe4]p\x981NC\xee\xca\ndvc\x05\xec\xec\x18\x0c'


# @app.route('/table/<table>', methods=['GET', 'POST'])
# def show_table(table):
#     rows = run_query("SELECT * FROM %s" % table)[1]
#     columns = run_query("""SELECT column_name
#                                FROM information_schema.columns
#                                WHERE table_name = '%s'""" % table)[1]
#
#     return render_template("table.html",
#                            table=table,
#                            rows=rows,
#                            columns=columns)
