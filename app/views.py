from flask import render_template
from app import app
from db import run_query


@app.route('/')
def index():
    name = run_query('SELECT name FROM person '
                     'ORDER BY name ASC LIMIT 1')
    user = {'nickname': name[0][0]}
    return render_template("index.html",
                           title='Home',
                           user=user)


@app.route('/table/<table>')
def show_table(table):
    rows = run_query("SELECT * FROM " + table)
    columns = run_query("SELECT column_name " +
                        "FROM information_schema.columns " +
                        "WHERE table_name = '" + table + "'")

    return render_template("table.html",
                           rows=rows,
                           columns=columns,
                           table=table)
