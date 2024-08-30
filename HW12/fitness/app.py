import os
import database
from celery import Celery
from tasks import send_mail
from functools import wraps
from utils import calc_slots
from datetime import datetime
from database import db_session
from flask import Flask, request, render_template, session, redirect, url_for
from models import User, Service, Coach, Reservation, Gym, Review, LoyaltyProgram

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

@app.route('/register', methods=['GET', 'POST'])
def register_user_invitation():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        form_data = request.form
        birth_date = datetime.strptime(form_data['birth_date'], '%Y-%m-%d').date()
        if not all([form_data.get('login'), form_data.get('password'), form_data.get('birth_date'),
                    form_data.get('phone')]):
            return 'All fields are required', 400
        db_user = User(login= form_data['login'], password= form_data['password'], birth_date=birth_date,
                            phone= form_data['phone'])
        database.db_session.add(db_user)
        database.db_session.commit()
        return 'User data was added'


@app.route('/login', methods=['GET', 'POST'])
def get_login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = db_session.query(User).filter_by(login=login).first()
        if user and user.password == password:
            session['user_id'] = user.user_id
            return redirect('/user_' + str(user.user_id))
        else:
            return 'Incorrect login or password'
    else:
        user_id = session.get('user_id')
        if user_id:
            return redirect(f'/user_{user_id}')
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


@app.route('/user_<int:user_id>', methods=['GET'])
@login_check
def get_user(user_id):
    res = db_session.query(User).filter(User.user_id==user_id).first()
    return render_template('user_info.html', user=res)


@app.route('/user_<int:user_id>/profile_edit', methods=['GET', 'POST'])
@login_check
def profile_edit(user_id):
    if request.method == 'GET':
        return render_template('profile_edit.html', user_id=user_id)

    elif request.method == 'POST':
        form_data = request.form
        sql_session = database.db_session()
        update_data = {}
        if form_data.get('password'):
            update_data['password'] = form_data.get('password')
        if form_data.get('birth_date'):
            birth_date = datetime.strptime(form_data.get('birth_date'), '%Y-%m-%d').date()
            update_data['birth_date'] = birth_date
        if form_data.get('phone'):
            update_data['phone'] = form_data.get('phone')

        if not update_data:
            return 'No fields to update', 400

        sql_session.query(User).filter(User.user_id == user_id).update(update_data, synchronize_session=False)
        sql_session.commit()
        send_mail.delay("sweethomie1337@gmail.com", "This is a test email.")
        return 'User data was edited'


@app.route('/user_<int:user_id>/funds', methods=['GET'])
@login_check
def user_funds(user_id):
    res = db_session.query(User.funds, User.user_id).filter_by(user_id=user_id).first()
    if res is None:
        return "User not found."
    return render_template('user_funds.html', user=res)


@app.route('/user_<int:user_id>/reservations', methods=['GET'])
@login_check
def reservation_user_info(user_id):
    res = db_session.query(Reservation.fitness_center_id, Reservation.service, Reservation.coach_id,
                           Reservation.date, Reservation.time, Reservation.reservation_id).filter(Reservation.user_id==user_id).all()
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
        services = db_session.query(Service).all()
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
        desired_date = datetime.strptime(desired_date, '%Y-%m-%d')
        return redirect(url_for('pre_reservation', user_id=user_id, coach=coach, service=service, desired_date=desired_date))
    coaches = db_session.query(Coach).all()
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
        desired_date = datetime.strptime(desired_date.split(' ')[0], '%Y-%m-%d').date()
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
        date = datetime.strptime(date,'%Y-%m-%d').date()
        time = request.form.get('time')
        time_obj = datetime.strptime(time, '%H:%M').time()
        service_name = db_session.query(Service.name).filter(Service.service_id == service_id).scalar()
        gym_id = db_session.query(Service.fitness_center_id).filter(Service.service_id == service_id).scalar()
        email = db_session.query(User.email).filter(User.user_id==user_id).scalar()
        db_reservation = Reservation(user_id=user_id, fitness_center_id=gym_id, coach_id=coach_id, service=service_name,
                                     service_id=service_id, date=date, time=time_obj)
        db_session.add(db_reservation)
        db_session.commit()
        send_mail.delay(f'{email}', 'Reservation Info', f'Hello! You placed a reservation for '
                                                        f'{service_name} in our gym at {date}, {time}')
        return redirect(f'/user_{user_id}/reservations')

    coach_id = request.args.get('coach')
    service_id = request.args.get('service')
    desired_date = request.args.get('desired_date')
    desired_date = datetime.strptime(desired_date.split(' ')[0], '%Y-%m-%d').date()
    time = request.args.get('time')

    coach_name = db_session.query(Coach.name).filter(Coach.coach_id == coach_id).scalar()
    service_name = db_session.query(Service.name).filter(Service.service_id == service_id).scalar()
    return render_template('place_reservation.html',
                        coach_id = coach_id, service_id = service_id, coach_name=coach_name,service_name=service_name,
                        desired_date=desired_date, time=time, user_id=user_id)


@app.route('/user_<int:user_id>/reservations/<int:reservation_id>/delete', methods=['POST'])
@login_check
def delete_reservation(user_id, reservation_id):
    session = database.db_session()
    db_reservation = session.query(Reservation).filter_by(reservation_id=reservation_id, user_id=user_id).first()
    if db_reservation:
        session.delete(db_reservation)
        session.commit()
    return redirect(f'/user_{user_id}/reservations')


@app.route('/fitness_center', methods=['GET'])
def all_gyms():
    res = db_session.query(Gym).all()
    return render_template('all_gyms.html', gyms=res)


@app.route('/fitness_center/<int:fitness_center_id>/services', methods=['GET'])
def get_services(fitness_center_id):
    res = db_session.query(Service).filter(fitness_center_id == Service.fitness_center_id).all()
    return render_template('gym_services.html', fc_id=fitness_center_id, services=res)


@app.route('/service', methods=['GET'])
def all_services():
    res = db_session.query(Service).all()
    return render_template('all_services.html', services=res)


@app.route('/trainer', methods=['GET'])
def all_coaches():
    res = db_session.query(Coach).all()
    return render_template('all_coaches.html', coaches=res)


@app.route('/trainer/<int:coach_id>/reviews', methods=['GET'])
def get_coach_reviews(coach_id):
    coach = db_session.query(Coach).filter_by(coach_id=coach_id).first()
    coach_name = coach.name
    res = db_session.query(Review.points, Review.text, User.login).join(User,
                                                                            Review.user == User.user_id).filter(
        Review.trainer == coach_id).all()
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
        db_review = Review(trainer=trainer, user=user, points=points, text=text)
        database.db_session.add(db_review)
        database.db_session.commit()
        return 'Review has been submitted successfully.'
    else:
        return "Method not allowed"


@app.route('/loyalty_programs', methods=['GET', 'POST'])
def all_loyalty_programs():
    res = db_session.query(LoyaltyProgram).all()
    return render_template('loyalty_programs.html', programs=res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
