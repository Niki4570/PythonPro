import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_from_db(query, many=True, *args):
    con = sqlite3.connect('fdb.db')
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(query, args)
    if many:
        res = cur.fetchall()
    else:
        res = cur.fetchone()
    con.close()
    return jsonify(res)


def insert_to_db(query, *args):
    con = sqlite3.connect('fdb.db')
    cur = con.cursor()
    cur.execute(query, args)
    con.commit()
    con.close()


@app.get('/register')
def register_user_invitation():
    return f"""<form action='/register' method='post'> 
    <label for="login">login:</label><br>
    <input type="text" id="login" name="login"><br>
    <label for="password">password: </label><br>
    <input type="password" id="password" name="password"> 
    <label for="birth_date">birth_date:</label><br>
    <input type="date" id="birth_date" name="birth_date"> 
    <label for="phone">phone:</label><br>
    <input type="text" id="phone" name="phone">
    <input type="submit" value="Submit"> 
</form>"""


@app.post('/register')
def register_new_user():
    form_data = request.form
    login = form_data.get('login')
    password = form_data.get('password')
    birth_date = form_data.get('birth_date')
    phone = form_data.get('phone')
    insert_to_db('INSERT INTO user (login, password, birth_date, phone) VALUES (?, ?, ?, ?)',
                 login, password, birth_date, phone)
    return 'User data was added'


@app.get('/user')
def user_info(user_id):
    res = get_from_db('SELECT login, phone, birth_date FROM user WHERE user.user_id = ?', False, user_id)
    return res


@app.post('/user')
def add_user_info():  # put application's code here
    return 'user data was modified'


@app.put('/user')
def user_update():  # put application's code here
    return 'user info updated'


@app.get('/user/funds')
def user_deposit_info(user_id):
    res = get_from_db('SELECT funds FROM user WHERE user_id = ?', False, user_id)
    return res


@app.post('/user/funds')
def add_funds():  # put application's code here
    return 'user account was successfully funded'


@app.get('/reservations/<user_id>')
def all_reservations_info(user_id):
    res = get_from_db('SELECT fitness_center_id, service, date, time FROM reservation WHERE user_id = ?', True, user_id)
    return res


@app.post('/reservations')
def add_reservation():  # put application's code here
    return 'reservation added'


@app.get('/reservation/<reservation_id>')
def reservation_info(reservation_id):
    res = get_from_db('SELECT * FROM reservation WHERE reservation_id = ?',
                      False, reservation_id)
    return res


@app.put('/user/reservations/<reservation_id>')
def reservation_update(reservation_id):  # put application's code here
    return f'reservation {reservation_id} updated'


@app.delete('/user/reservations/<reservation_id>')
def reservation_delete(reservation_id):  # put application's code here
    return f'reservation {reservation_id} canceled'


@app.get('/user/checkout')
def checkout_info():  # put application's code here
    return 'choose payment method'


@app.post('/user/checkout')
def checkout_new():  # put application's code here
    return 'checkout complete'


@app.put('/user/checkout')
def checkout_update():  # put application's code here
    return 'checkout details updated'


@app.get('/fitness_center/<fitness_center_id>')
def fitness_center_info(fitness_center_id):
    res = get_from_db('SELECT address, contacts, name FROM fitness_center WHERE id = ?', False, fitness_center_id)
    return res


@app.get('/fitness_center/<fitness_center_id>/trainer')
def get_trainers(fitness_center_id):
    res = get_from_db('SELECT coach_id, name, age, gender FROM trainer WHERE fitness_center_id = ?', True,
                      fitness_center_id)
    return res


@app.get('/fitness_center/<fitness_center_id>/trainer/<coach_id>')
def get_coach_info(fitness_center_id, coach_id):
    res = get_from_db('SELECT coach_id, name, age, gender FROM trainer WHERE fitness_center_id = ? AND coach_id = ?',
                      False, fitness_center_id, coach_id)
    return res


@app.get('/fitness_center/<fitness_center_id>/trainer/<coach_id>/score')
def get_coach_score(fitness_center_id, coach_id):
    res = get_from_db('SELECT name, score FROM trainer WHERE fitness_center_id = ? AND coach_id = ?',
                      False, fitness_center_id, coach_id)
    return res


@app.post('/fitness_center/<id>/trainer/<coach_id>/score')
def set_coach_score(gym_id, coach_id):  # put application's code here
    return f'fitness center {gym_id} coach {coach_id} score was posted'


@app.put('/fitness_center/<gym_id>/trainer/<coach_id>/score')
def update_coach_score(gym_id, coach_id):  # put application's code here
    return f'fitness center {gym_id} trainer {coach_id} score was updated'


@app.get('/service/<fitness_center_id>')
def get_services(fitness_center_id):
    res = get_from_db('SELECT name FROM service WHERE fitness_center_id = ?', True,
                      fitness_center_id)
    return res


@app.get('/fitness_center/<fitness_center_id>/services/<service_name>')
def get_service_info(fitness_center_id, service_name):
    res = get_from_db('SELECT service.*, fitness_center.address FROM service JOIN fitness_center '
                      'ON service.fitness_center_id = fitness_center.id WHERE service.name = ? '
                      'AND fitness_center_id = ?', True, service_name, fitness_center_id)
    return res


@app.get('/loyalty_programs')
def get_loyalty_programs():
    res = get_from_db('SELECT program, description FROM loyalty_program', True)
    return res


if __name__ == '__app__':
    app.run(debug=True)
