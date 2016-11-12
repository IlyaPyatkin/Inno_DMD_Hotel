from flask import render_template, request, session, redirect, url_for, flash
import re

from app import app
from db import run_query
from passlib.apps import custom_app_context as pwd_context

user_re = re.compile("^[a-z0-9_-]{3,16}$")
pass_re = re.compile("^[a-z0-9_-]{6,18}$")


@app.route('/')
def index():
    if 'username' in session:
        user = session['username']
    else:
        user = 'guest'
    return render_template("index.html",
                           user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        pwd_hash = run_query("""SELECT hash FROM person
                                WHERE username = '%s'""" % request.form['username'])[1]
        if pwd_hash:
            if pwd_context.verify(request.form['password'], pwd_hash[0][0]):
                # If login successful
                session['username'] = request.form['username']
                return redirect(url_for('index'))
        return render_template("login.html",
                               error='Invalid credentials')
    return render_template("login.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if not re.match("^[a-z0-9_-]{3,16}$", request.form['username']):
            return render_template("signup.html",
                                   error="Invalid username")
        if not re.match("^[a-z0-9_-]{6,18}$", request.form['password']):
            return render_template("signup.html",
                                   error="Invalid password")
        if run_query("SELECT * FROM person WHERE username = '%s'" % request.form['username'])[1]:
            return render_template("signup.html",
                                   error="Username is already taken")

        pwd_hash = pwd_context.encrypt(request.form['password'])
        run_query("""INSERT INTO person (username, hash)
                     VALUES ('%s', '%s')""" % (request.form['username'], pwd_hash))

        # Automatically login
        session['username'] = request.form['username']
        return redirect(url_for('index'))

    return render_template("signup.html")


@app.route('/logout')
def logout():
    if 'username' in session:
        del session['username']
    return redirect(url_for('index'))


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
