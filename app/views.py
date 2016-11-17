from flask import render_template, request, session, redirect, url_for, abort
from passlib.apps import custom_app_context as pwd_context
import datetime

from app import app
from app.model.DBQuery import DBQuery
from app.model.User import User
from app.model.Booked import Booked
from app.model.Registration import Registration
from app.model.Person import Person
from app.model.Hotel import Hotel
from app.model.RoomType import RoomType
from app.model.Performance import Performance

ERROR_MSG = "An error occurred, please try again later"


def logged_in():
    return 'username' in session


def log_in_as(username, role=User.ROLE_USER):
    session['username'] = username
    session['role'] = role


def log_out():
    if logged_in():
        del session['username']
    if 'role' in session:
        del session['role']
    if 'search' in session:
        del session['search']


@app.route('/switch-user/<username>')
def switch_user(username):
    role = User.get_role(username)
    if role.code == DBQuery.CODE_OK and role.result:
        log_in_as(username, role.result[0][0])
    return redirect(url_for('index'))


@app.route('/detail', methods=['GET', 'POST'])
def detail():
    for param in ('arrival', 'departure', 'hid', 'rtid'):
        if param not in request.args:
            return render_template("no_results.html")
    arrival = datetime.datetime.strptime(request.args['arrival'], "%Y-%m-%d").date()
    departure = datetime.datetime.strptime(request.args['departure'], "%Y-%m-%d").date()
    hid = request.args['hid']
    rtid = request.args['rtid']

    if not logged_in():
        session['search'] = [arrival.strftime("%Y-%m-%d"), departure.strftime("%Y-%m-%d"), hid, rtid]
        return redirect(url_for("login", error="Please log in or sign up to continue"))
    if 'search' in session:
        del session['search']

    room_query = Booked.get_free_hotel_room(hid, rtid, arrival, departure)
    if room_query.code == DBQuery.CODE_OK and room_query.result:
        rid = room_query.result[0][0]
    else:
        return redirect(url_for('index', error='This order is no longer available'))

    if request.method == 'POST':
        checkin = datetime.datetime.strptime(request.form['checkin'], "%H:%M").time()
        checkout = datetime.datetime.strptime(request.form['checkout'], "%H:%M").time()
        person_query = User.get_person_id(session['username'])
        if person_query.code == DBQuery.CODE_OK:
            if not person_query.result:
                session['search'] = [arrival.strftime("%Y-%m-%d"), departure.strftime("%Y-%m-%d"), hid, rtid]
                return redirect(url_for("profile", error="Please fill your profile info"))
            pid = person_query.result[0][0]
            arrival = datetime.datetime.combine(arrival, checkin)
            departure = datetime.datetime.combine(departure, checkout)
            order_add_query = Booked.query_add(rid, pid, arrival, departure)
            if order_add_query.code == DBQuery.CODE_OK:
                return redirect(url_for('orders'))
        return redirect(url_for('index', error='This order is no longer available'))

    rtype_query = RoomType.get_roomtype(rtid)
    order_extra = Hotel.get_order_extra(hid)
    if rtype_query.code != DBQuery.CODE_OK or not rtype_query.result or order_extra.code != DBQuery.CODE_OK or not order_extra.result:
        return redirect(url_for('index', error='This order is no longer available'))
    info = order_extra.result[0]
    rtype = rtype_query.result[0][0]
    cost = ((departure - arrival).days + 1) * rtype_query.result[0][1]
    return render_template("detail.html",
                           arrival=arrival,
                           departure=departure,
                           rtype=rtype,
                           rid=rid,
                           address=info[2:6],
                           title=info[0],
                           rating=info[1],
                           cost=cost)


@app.route('/register', methods=['GET', 'POST'])
def register():
    for param in ('arrival', 'departure', 'city', 'people'):
        if param not in request.args:
            return render_template("no_results.html")
    arrival = request.args['arrival']
    departure = request.args['departure']
    city = request.args['city']
    people = request.args['people']
    results = Booked.search_hotels(arrival, departure, city, people)
    if results.code != DBQuery.CODE_OK or not results.result:
        return render_template("no_results.html")

    if request.method == 'POST':
        hid = request.form['hid']
        rtid = request.form['rtid']
        return redirect(url_for('detail',
                                arrival=arrival,
                                departure=departure,
                                hid=hid,
                                rtid=rtid))

    hotels = {}
    for row in results.result:
        if row[0] not in hotels:
            hotels[row[0]] = {'title': row[1], 'rating': row[2], 'rtypes': []}
        hotels[row[0]]['rtypes'].append((row[3], row[4], row[5]))
    return render_template("register.html",
                           hotels=hotels)


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'search' in session:
        return redirect(url_for('detail',
                                arrival=session['search'][0],
                                departure=session['search'][1],
                                hid=session['search'][2],
                                rtid=session['search'][3]))
    error = None
    if 'error' in request.args:
        error = request.args['error']
    if request.method == 'POST':
        for param in ('arrival', 'departure', 'city', 'people'):
            if param not in request.form:
                error = "Please enter all forms"
        if not error:
            return redirect(url_for('register',
                                    arrival=request.form['arrival'],
                                    departure=request.form['departure'],
                                    city=request.form['city'],
                                    people=request.form['people']))
    tomorrow = (datetime.date.today() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    today = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    cities_query = Hotel.get_cities()
    if cities_query.code == DBQuery.CODE_OK and cities_query.result:
        cities = cities_query.result
        return render_template("index.html",
                               today=today,
                               tomorrow=tomorrow,
                               cities=cities,
                               error=error)
    return render_template("index.html",
                           fatal_error=ERROR_MSG)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if 'error' in request.args:
        error = request.args['error']
    if logged_in():
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password'].lower()
        pwd_hash_role_query = User.query_hash_role(username)
        if pwd_hash_role_query.code == DBQuery.CODE_OK and pwd_hash_role_query.result:
            pwd_hash = pwd_hash_role_query.result[0][0]
            role = pwd_hash_role_query.result[0][1]
            if pwd_context.verify(password, pwd_hash):
                # If login successful
                log_in_as(username, role)
                return User.get_redirect_by_role(role)
        error = 'Invalid credentials'
    return render_template("login.html",
                           error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if logged_in():
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password'].lower()

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
                                   error=ERROR_MSG)

        pwd_hash = pwd_context.encrypt(password)

        add_query = User.query_add(username, pwd_hash, User.ROLE_USER)
        if add_query.code == DBQuery.CODE_OK:
            # Automatically login user and redirect to profile page
            log_in_as(username, User.ROLE_USER)
            return redirect(url_for('profile'))
        else:
            return render_template("signup.html",
                                   error=ERROR_MSG)

    return render_template("signup.html")


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if not logged_in():
        return redirect(url_for('login'))

    if request.method == 'POST':
        bid = request.form['bid']
        username = session['username']
        registered_check_query = User.registered_check_query(bid)
        if registered_check_query.code == DBQuery.CODE_OK:
            if not registered_check_query.result:
                delete_query = User.delete_person_order(username, bid)
                if delete_query.code == DBQuery.CODE_OK:
                    return redirect(url_for('orders'))

        return render_template("orders.html",
                               error=ERROR_MSG)

    orders_query = User.get_orders(session['username'])
    if orders_query.code == DBQuery.CODE_OK:
        orders_list = orders_query.result
        return render_template("orders.html",
                               orders=orders_list)
    return render_template("orders.html",
                           error=ERROR_MSG)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not logged_in():
        return redirect(url_for('login'))
    error = None
    if 'error' in request.args:
        error = request.args['error']

    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        username = session['username']
        for name in (fname, lname):
            if not Person.check_name(name):
                return render_template("profile.html",
                                       error="Invalid name",
                                       fname=fname,
                                       lname=lname,
                                       email=email)

        if not Person.check_email(email):
            return render_template("profile.html",
                                   error="Invalid email",
                                   fname=fname,
                                   lname=lname,
                                   email=email)

        update_query = User.query_update_person(fname, lname, email, username)
        if update_query.code == DBQuery.CODE_OK:
            return redirect(url_for('profile'))
        return render_template("profile.html",
                               error=ERROR_MSG,
                               fname=fname,
                               lname=lname,
                               email=email)

    fname = ""
    lname = ""
    email = ""
    profile_data = User.get_person(session['username'])
    if profile_data.code == profile_data.CODE_OK:
        if profile_data.result:
            fname = profile_data.result[0][0]
            lname = profile_data.result[0][1]
            email = profile_data.result[0][2]

    return render_template("profile.html",
                           fname=fname,
                           lname=lname,
                           email=email,
                           error=error)


@app.route('/logout')
def logout():
    log_out()
    return redirect(url_for('index'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not logged_in() or session['role'] != User.ROLE_ADMIN:
        abort(404)

    if request.method == 'POST':
        if 'privileges' in request.form:
            username = request.form['username']
            role = request.form['role']
        if 'add_employee' in request.form:
            hid = request.form['username']
            username = request.form['username']
            salary = request.form['salary']
            position = request.form['position']
            status = request.form['status']
        return ""

    disk_performance = Performance.get_disk_performance()
    i_o_performance_cache = Performance.get_io_cache_performance()
    i_o_performance_index = Performance.get_io_index_performance()

    disk_columns = ['table', 'index', 'table', 'total']
    i_o_columns_cache = ['table', 'read', 'hit', 'ratio']
    i_o_columns_index = ['table', 'read', 'hit', 'ratio']
    if disk_performance.code == DBQuery.CODE_OK and \
                    i_o_performance_cache.code == DBQuery.CODE_OK and \
                    i_o_performance_index.code == DBQuery.CODE_OK:
        if disk_performance.result and \
                i_o_performance_cache.result and \
                i_o_performance_index.result:
            return render_template('admin.html',
                                   IO_cache=i_o_performance_cache.result,
                                   IO_cache_columns=i_o_columns_cache,
                                   IO_index=i_o_performance_index.result,
                                   IO_index_columns=i_o_columns_index,
                                   disk=disk_performance.result,
                                   disk_columns=disk_columns)
    return render_template('admin.html')


@app.route('/manager', methods=['GET', 'POST'])
def manager():
    if not logged_in() or session['role'] != User.ROLE_MANAGER:
        abort(404)

    hotel_data = User.get_manager_hotel(session['username'])
    if hotel_data.code != DBQuery.CODE_OK or not hotel_data.result:
        abort(404)
    hotel_id = hotel_data.result[0][0]
    hotel_title = hotel_data.result[0][1]

    if request.method == 'POST':
        bid = request.form['bid']
        if 'check_in' in request.form:
            reg_check = Registration.query_register_check_in(bid)
        else:
            reg_check = Registration.query_register_check_out(bid)

        if reg_check.code != DBQuery.CODE_OK:
            return render_template("manager.html",
                                   hotel=hotel_title,
                                   error=ERROR_MSG)
        return redirect(url_for('manager'))

    query_check_in = Booked.query_check_in(hotel_id)
    query_check_out = Booked.query_check_out(hotel_id)
    if query_check_in.code == DBQuery.CODE_OK:
        if query_check_out.code == DBQuery.CODE_OK:
            check_ins = [i for i in query_check_in.result]
            check_outs = query_check_out.result
            return render_template("manager.html",
                                   hotel=hotel_title,
                                   check_ins=check_ins,
                                   check_outs=check_outs)
    return render_template("manager.html",
                           hotel=hotel_title,
                           error=ERROR_MSG)


@app.errorhandler(404)
def error404(e):
    return render_template("page_not_found.html"), 404


app.secret_key = b'7\xeb\xc8^\xc2~\xe4]p\x981NC\xee\xca\ndvc\x05\xec\xec\x18\x0c'
