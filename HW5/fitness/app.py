import sqlite3

from flask import Flask, request, render_template

app = Flask(__name__)

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

    def insert(self, query, *args):
        cursor = self.connection.cursor()
        cursor.execute(query, args)
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
            db.insert('INSERT INTO user (login, password, birth_date, phone) VALUES (?, ?, ?, ?)',
                      login, password, birth_date, phone)
            return 'User data was added'



@app.route('/login', methods=['GET', 'POST'])
def get_login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        with SQLiteDatabase('fdb.db') as db:
            user = db.fetch_one('SELECT login, password FROM user WHERE login = ?', (login,))
            if user and user['password'] == password:
                return 'Successful login'
            else:
                return 'Incorrect login or password'
    else:
        return render_template('login.html')


@app.route('/user', methods=['GET', 'POST', 'PUT'])
def all_users():
    if request.method == 'POST':
        return ' '
    elif request.method == 'PUT':
        return ' '
    else:
        with SQLiteDatabase('fdb.db') as db:
            res = db.fetch_all('SELECT login, phone, birth_date, user_id, funds FROM user')
        return render_template('all_users.html', users=res)


@app.route('/user/<user_id>', methods=['GET', 'POST', 'PUT'])
def get_user(user_id):
    if request.method == 'POST':
        return ' '
    elif request.method == 'PUT':
        return ' '
    else:
        with SQLiteDatabase('fdb.db') as db:
            res = db.fetch_one('SELECT login, phone, birth_date, funds, user_id FROM user WHERE user_id = ?', user_id)
        return render_template('user_info.html', user=res)


@app.route('/user/<user_id>/funds', methods=['GET'])
def user_funds(user_id):
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_one('SELECT user_id, funds FROM user WHERE user_id = ?',
                           (user_id,))
        if res is None:
            return "User not found."
        return render_template('user_funds.html', user=res)


@app.route('/reservation', methods=['GET', 'POST'])
def all_reservations():
    if request.method == 'GET':
        return render_template('reservation.html')
    elif request.method == 'POST':
        form_data = request.form
        user = form_data.get('user')
        gym = form_data.get('gym_id')
        service = form_data.get('service_name')
        date = form_data.get('date')
        time = form_data.get('time')
        with SQLiteDatabase('fdb.db') as db:
            db.insert(
                'INSERT INTO reservation (user_id, fitness_center_id, service, date, time) VALUES (?, ?, ?, ?, ?)',
                user, gym, service, date, time
            )
        return 'Reservation has been created.'
    else:
        return "Method not allowed"


@app.route('/reservation/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def reservation_user_info(user_id):
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_all('SELECT fitness_center_id, service, date, time FROM reservation WHERE user_id = ?',
                           (user_id,))
        if res is None:
            return "No reservation found for this user."
        return render_template('reservation_user_id.html', reservations=res)


@app.route('/fitness_center', methods=['GET', 'POST', 'PUT'])
def all_gyms():
    if request.method == 'POST':
        return ' '
    elif request.method == 'PUT':
        return ' '
    else:
        with SQLiteDatabase('fdb.db') as db:
            res = db.fetch_all('SELECT name, id, address, contacts FROM fitness_center')
        return render_template('all_gyms.html', gyms=res)


@app.route('/fitness_center/<fitness_center_id>', methods=['GET'])
def fitness_center_info(fitness_center_id):
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_one('SELECT * FROM fitness_center WHERE fitness_center.id = ?',
                           (fitness_center_id,))
        if res is None:
            return "No fitness center with this ID."
        return render_template('fitness_center_info.html', gym=res)


@app.route('/trainer', methods=['GET'])
def all_coaches():
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_all('SELECT name, gender, age, score, fitness_center_id FROM trainer')
    return render_template('all_coaches.html', coaches=res)


@app.route('/trainer/<coach_id>', methods=['GET'])
def get_coach_info(coach_id):
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_one('SELECT name, gender, age, score, fitness_center_id FROM trainer WHERE coach_id = ?', coach_id)
    return render_template('coach_info.html', coach=res)


@app.route('/service', methods=['GET'])
def get_service_info():
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_all('SELECT name, duration, description, price, fitness_center_id, max_attendees FROM service')
        return render_template('all_services.html', services=res)


@app.route('/service/<fitness_center_id>', methods=['GET'])
def get_services(fitness_center_id):
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_all('SELECT name, duration, description, price, fitness_center_id, max_attendees FROM service WHERE fitness_center_id = ?',
                           fitness_center_id)
    return render_template('gym_services.html', fc_id=fitness_center_id, services=res)


@app.route('/review', methods=['GET', 'POST'])
def review():
    if request.method == 'GET':
        return render_template('review.html')
    elif request.method == 'POST':
        form_data = request.form
        trainer = form_data.get('trainer')
        user = form_data.get('user')
        text = form_data.get('text')
        points = form_data.get('points')
        with SQLiteDatabase('fdb.db') as db:
            db.insert(
                'INSERT INTO review (trainer, user, points, text) VALUES (?, ?, ?, ?)',
                trainer, user, points, text
            )
            db.insert(
                'UPDATE trainer SET score = score + ? WHERE coach_id = ?',
                points, trainer
            )
        return 'Review has been submitted successfully.'
    else:
        return "Method not allowed"


@app.get('/loyalty_programs')
def all_loyalty_programs():
    with SQLiteDatabase('fdb.db') as db:
        res = db.fetch_all('SELECT program, description FROM loyalty_program')
        return render_template('loyalty_programs.html', services=res)


if __name__ == '__app__':
    app.run(debug=True)
