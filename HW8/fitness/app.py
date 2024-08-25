from datetime import datetime

from flask import Flask, request, render_template, session, redirect, url_for
from utils import SQLiteDatabase, calc_slots
from functools import wraps

app = Flask(__name__)
app.secret_key = 'i.Jh7Ru3/85U.8tn/.4O6in.G4.o0hN2'


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
        return render_template('profile_edit.html', user_id=user_id)
    elif request.method == 'POST':
        form_data = request.form
        fields_to_update = []
        values = []
        if form_data.get('password'):
            fields_to_update.append("password = ?")
            values.append(form_data.get('password'))
        if form_data.get('birth_date'):
            fields_to_update.append("birth_date = ?")
            values.append(form_data.get('birth_date'))
        if form_data.get('phone'):
            fields_to_update.append("phone = ?")
            values.append(form_data.get('phone'))
        if not fields_to_update:
            return 'No fields to update'
        values.append(user_id)
        sql_query = f"UPDATE user SET {', '.join(fields_to_update)} WHERE user_id = ?"
        with SQLiteDatabase('fdb.db') as db:
            db.execute(sql_query, values)
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
        res = db.fetch_all('SELECT fitness_center_id, coach_id, service, date, time, reservation_id FROM reservation WHERE user_id = ?',
                           (user_id,))
        if res is None:
            return redirect(f'/user_{user_id}/reservations/pre_reservation')
        return render_template('reservation_user_id.html', reservations=res, id = user_id)


@app.route('/user_<int:user_id>/reservations/select_service', methods=['GET', 'POST'])
@login_check
def select_service(user_id):
    if request.method == 'POST':
        service = request.form.get('service')
        if service:
            return redirect(url_for('select_coach', user_id=user_id, service=service))
        else:
            return "Service is required", 400
    else:
        with SQLiteDatabase('fdb.db') as db:
            services = db.fetch_all('SELECT * FROM service')
        if services:
            return render_template('select_service.html', services=services, user_id=user_id)
        else:
            return "No services available", 400


@app.route('/user_<int:user_id>/reservations/select_coach', methods=['GET', 'POST'])
@login_check
def select_coach(user_id):
    service = request.args.get('service')
    if request.method == 'POST':
        coach = request.form.get('coach')
        desired_date = request.form.get('desired_date')
        service = request.form.get('service')
        desired_date = datetime.strptime(desired_date, '%Y-%m-%d').strftime('%d-%m-%Y')
        return redirect(url_for('pre_reservation', user_id=user_id, coach=coach, service=service, desired_date=desired_date))
    with SQLiteDatabase('fdb.db') as db:
        coaches = db.fetch_all('SELECT * FROM trainer')
    return render_template('select_coach.html', coaches=coaches, service=service, user_id=user_id)


@app.route('/user_<int:user_id>/reservations/pre_reservation', methods=['GET', 'POST'])
@login_check
def pre_reservation(user_id):
    if request.method == 'POST':
        coach = request.form.get('coach')
        service = request.form.get('service')
        desired_date = request.form.get('date')
        time = request.form.get('time')
        return redirect(url_for('place_reservation', user_id=user_id, coach=coach, service=service,
                                desired_date=desired_date, time=time))
    else:
        coach = request.args.get('coach')
        service = request.args.get('service')
        desired_date = request.args.get('desired_date')
        time_slots = calc_slots(coach, service, desired_date)
        return render_template('pre_reservation.html', coach=coach, service=service,
                               desired_date=desired_date, time_slots=time_slots, user_id=user_id)


@app.route('/user_<int:user_id>/reservations/place_reservation', methods=['GET', 'POST'])
@login_check
def place_reservation(user_id):
    if request.method == 'POST':
        coach_id = request.form.get('coach')
        service_id = request.form.get('service')
        date = request.form.get('date')
        time = request.form.get('time')
        with SQLiteDatabase('fdb.db') as db:
            service_name = db.fetch_one('SELECT name FROM service WHERE service_id = ?', (service_id,))['name']
            gym_id = db.fetch_one('SELECT fitness_center_id FROM trainer WHERE coach_id = ?', (coach_id,))['fitness_center_id']
            db.execute(
                'INSERT INTO reservation (user_id, fitness_center_id, coach_id, service, service_id, date, time) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (user_id, gym_id, coach_id, service_name, service_id, date, time))
        return redirect(f'/user_{user_id}/reservations')

    coach_id = request.args.get('coach')
    service_id = request.args.get('service')
    desired_date = request.args.get('desired_date')
    time = request.args.get('time')
    with SQLiteDatabase('fdb.db') as db:
        coach_name = db.fetch_one('SELECT name FROM trainer WHERE coach_id = ?', (coach_id,))['name']
        service_name = db.fetch_one('SELECT name FROM service WHERE service_id = ?', (service_id,))['name']
    return render_template('place_reservation.html',
                           coach_id = coach_id, service_id = service_id, coach_name=coach_name,service_name=service_name,
                           desired_date=desired_date, time=time, user_id=user_id)


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
        res = db.fetch_all('SELECT * FROM fitness_center')
    return render_template('all_gyms.html', gyms=res)


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


# @app.route('/trainer/<int:coach_id>', methods=['GET'])
# def get_coach_info(coach_id):
#     with SQLiteDatabase('fdb.db') as db:
#         res = db.fetch_one('SELECT name, gender, age, score, fitness_center_id FROM trainer WHERE coach_id = ?', (coach_id,))
#     return render_template('coach_info.html', coach=res, id=coach_id)


@app.route('/trainer/<int:coach_id>/reviews', methods=['GET'])
def get_coach_reviews(coach_id):
    with SQLiteDatabase('fdb.db') as db:
        coach_name_result = db.fetch_one('SELECT name FROM trainer WHERE coach_id = ?', (coach_id,))
        coach_name = coach_name_result.get('name', "Unknown Coach")
        res = db.fetch_all('SELECT r.points, r.text, u.login FROM review r INNER JOIN user u ON r.user = u.user_id WHERE r.trainer = ?', (coach_id,))
        if res is None:
            return "This coach doesn't have reviews."
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
