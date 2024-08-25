import sqlite3
from functools import wraps

from flask import Flask, request, render_template, session, redirect

app = Flask(__name__)
app.secret_key = 'iJh7Ru385U8tn4O6inG4o0hN2'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SQLiteDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = dict_factory
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

    def fetch_all(self, query, *args, **kwargs):
        cursor = self.connection.cursor()
        cursor.execute(query, *args, **kwargs)
        res = cursor.fetchall()
        if res:
            return res
        return None

    def fetch_one(self, query, *args, **kwargs):
        cursor = self.connection.cursor()
        cursor.execute(query, *args, **kwargs)
        res = cursor.fetchone()
        if res:
            return res
        return None

    def execute(self, query, *args, **kwargs):
        cursor = self.connection.cursor()
        cursor.execute(query, *args, **kwargs)
        self.connection.commit()


@app.route('/register', methods=['GET', 'POST'])
def register_user_invitation():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        form_data = request.form
        login = form_data.get('login')
        password = form_data.get('password')
        birth_date = form_data.get('birth_date')
        phone = form_data.get('phone')
        with SQLiteDatabase('fdb.db') as db:
            db.execute('INSERT INTO user (login, password, birth_date, phone) VALUES (?, ?, ?, ?)',
                       (login, password, birth_date, phone))
            return 'User data was added'


@app.route('/login', methods=['GET', 'POST'])
def get_login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        with SQLiteDatabase('fdb.db') as db:
            user = db.fetch_one('SELECT login, password, user_id FROM user WHERE login = ?',
                                (login,))
            if user and user['password'] == password:
                session['user_id'] = user['user_id']
                return redirect('/user_' + str(user['user_id']))
            else:
                return 'Incorrect login or password'
    else:
        user = session.get('user_id', None)
        if user:
            return redirect(f'/user_{user}')
        return render_template('login.html')


def login_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        user_id = kwargs.get('user_id')
        if user_id and str(user_id) != str(session.get('user_id')):
            return redirect(f'/user_{session.get("user_id")}')
        return func(*args, **kwargs)
    return wrapper


@app.route('/logout')
@login_check
def logout():
    session.pop('user_id', None)
    return redirect('/login')


@app.route('/user', methods=['GET'])
@login_check
def all_users():
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_all('SELECT login, phone, birth_date, user_id, funds FROM user')
    return render_template('all_users.html', users=res)


@app.route('/user_<int:user_id>', methods=['GET'])
@login_check
def get_user(user_id):
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_one('SELECT login, phone, birth_date, funds, user_id FROM user WHERE user_id = ?', (user_id,))
    return render_template('user_info.html', user=res)


@app.route('/user_<int:user_id>/profile_edit', methods=['GET', 'POST'])
@login_check
def profile_edit(user_id):
    if request.method == 'GET':
        return render_template('profile_edit.html')
    elif request.method == 'POST':
        form_data = request.form
        password = form_data.get('password')
        birth_date = form_data.get('birth_date')
        phone = form_data.get('phone')
        with SQLiteDatabase('fdb.db') as db:
            db.execute('UPDATE user SET password = ?, birth_date = ?, phone = ? WHERE user_id = ?',
                       (password, birth_date, phone, user_id))
            return 'User data was edited'


@app.route('/user_<int:user_id>/funds', methods=['GET'])
@login_check
def user_funds(user_id):
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_one('SELECT user_id, funds FROM user WHERE user_id = ?',
                           (user_id,))
        if res is None:
            return "User not found."
        return render_template('user_funds.html', user=res)


@app.route('/user_<int:user_id>/reservations', methods=['GET'])
@login_check
def reservation_user_info(user_id):
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_all('SELECT fitness_center_id, service, date, time, reservation_id FROM reservation WHERE user_id = ?',
                           (user_id,))
        if res is None:
            return redirect(f'/user_{user_id}/reservations/place_reservation')
        return render_template('reservation_user_id.html', reservations=res, id = user_id)


@app.route('/user_<int:user_id>/reservations/place_reservation', methods=['GET', 'POST'])
def place_reservation(user_id):
    if request.method == 'GET':
        return render_template('reservation.html', user_id=user_id)
    elif request.method == 'POST':
        form_data = request.form
        gym = form_data.get('gym_id')
        service = form_data.get('service_name')
        date = form_data.get('date')
        time = form_data.get('time')
        with SQLiteDatabase('fdb.db') as db:
            db.execute(
                'INSERT INTO reservation (user_id, fitness_center_id, service, date, time) VALUES (?, ?, ?, ?, ?)',
                (user_id, gym, service, date, time))
        return 'Reservation has been created.'
    else:
        return "Method not allowed"


@app.route('/user_<int:user_id>/reservations/<int:reservation_id>/delete', methods=['POST'])
@login_check
def delete_reservation(user_id, reservation_id):
    with SQLiteDatabase('fdb.db') as db:
        db.execute('DELETE FROM reservation WHERE reservation_id = ? AND user_id = ?',
                   (reservation_id, user_id))

    return redirect(f'/user_{user_id}/reservations')


@app.route('/fitness_center', methods=['GET'])
def all_gyms():
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_all('SELECT name, id, address, contacts FROM fitness_center')
    return render_template('all_gyms.html', gyms=res)


@app.route('/fitness_center/<int:fitness_center_id>', methods=['GET'])
def fitness_center_info(fitness_center_id):
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_one('SELECT * FROM fitness_center WHERE id = ?',
                           (fitness_center_id,))
        if res is None:
            return "No fitness center with this ID."
        return render_template('fitness_center_info.html', gym=res)


@app.route('/fitness_center/<int:fitness_center_id>/services', methods=['GET'])
def get_services(fitness_center_id):
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_all('SELECT name, duration, description, price, max_attendees FROM service WHERE fitness_center_id = ?',
                           (fitness_center_id,))
    return render_template('gym_services.html', fc_id=fitness_center_id, services=res)


@app.route('/service', methods=['GET'])
def all_services():
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_all('SELECT name, duration, description, price, fitness_center_id, max_attendees FROM service')
        return render_template('all_services.html', services=res)


@app.route('/trainer', methods=['GET'])
def all_coaches():
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_all('SELECT name, gender, age, score, fitness_center_id, coach_id FROM trainer')
    return render_template('all_coaches.html', coaches=res)


@app.route('/trainer/<int:coach_id>', methods=['GET'])
def get_coach_info(coach_id):
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_one('SELECT name, gender, age, score, fitness_center_id FROM trainer WHERE coach_id = ?', (coach_id,))
    return render_template('coach_info.html', coach=res, id=coach_id)


@app.route('/trainer/<int:coach_id>/reviews', methods=['GET'])
def get_coach_reviews(coach_id):
    with SQLiteDatabase('fdb.db') as db:
        coach_name_result = db.fetch_one('SELECT name FROM trainer WHERE coach_id = ?', (coach_id,))
        coach_name = coach_name_result.get('name', "Unknown Coach")
        res = db.fetch_all('SELECT r.points, r.text, u.login FROM review r INNER JOIN user u ON r.user = u.user_id WHERE r.trainer = ?', (coach_id,))
        return render_template('coach_reviews.html', reviews=res, name=coach_name, id=coach_id)


@app.route('/trainer/<int:coach_id>/reviews/write_review', methods=['GET', 'POST'])
@login_check
def review(coach_id):
    if request.method == 'GET':
        return render_template('review.html')
    elif request.method == 'POST':
        form_data = request.form
        trainer = coach_id
        user = session.get('user_id')
        text = form_data.get('text')
        points = form_data.get('points')
        with SQLiteDatabase('fdb.db') as db:
            db.execute(
                f'INSERT INTO review (trainer, user, points, text) VALUES (?, ?, ?, ?)',
                (trainer, user, points, text, coach_id))
            db.execute(
                'UPDATE trainer SET score = score + ? WHERE coach_id = ?',
                (points, coach_id))
        return 'Review has been submitted successfully.'
    else:
        return "Method not allowed"


@app.route('/loyalty_programs', methods=['GET', 'POST'])
def all_loyalty_programs():
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_all('SELECT program, description FROM loyalty_program')
        return render_template('loyalty_programs.html', programs=res)


if __name__ == '__app__':
    app.run(debug=True)
