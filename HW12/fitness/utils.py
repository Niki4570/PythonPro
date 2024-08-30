import datetime
from database import db_session
from models import Service, Reservation, CoachSchedule, CoachServices


def calc_slots(coach_id, service_id, desired_date):
    booked_time = (
        db_session.query(Reservation)
        .join(Service, Service.service_id == Reservation.service_id)
        .filter(
            Reservation.date == desired_date,
            Reservation.coach_id == coach_id,
            Reservation.service_id == service_id).all())

    trainer_schedule = db_session.query(CoachSchedule).filter(
        CoachSchedule.coach_id == coach_id,
        CoachSchedule.date == desired_date).first()

    trainer_capacity = db_session.query(CoachServices).filter(
        CoachServices.coach_id == coach_id,
        CoachServices.service_id == service_id).first()

    service_info = db_session.query(Service).filter(
        Service.service_id == service_id).first()

    if not trainer_schedule or not trainer_capacity or not service_info:
        print(f"trainer_schedule: {trainer_schedule}")
        print(f"trainer_capacity: {trainer_capacity}")
        print(f"service_info: {service_info}")
        return []

    def parse_datetime(date_str, time_str):
        return datetime.datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
    start_dt = parse_datetime(desired_date, trainer_schedule.start_time.strftime('%H:%M'))
    end_dt = parse_datetime(desired_date, trainer_schedule.end_time.strftime('%H:%M'))
    curr_dt = start_dt
    trainer_schedule_slots = {}

    while curr_dt <= end_dt:
        trainer_schedule_slots[curr_dt] = trainer_capacity.capacity
        curr_dt += datetime.timedelta(minutes=15)

    if booked_time:
        for one_booking in booked_time:
            service_duration = db_session.query(Service.duration).filter(Service.service_id == service_id).scalar()
            service_duration = int(service_duration)
            booking_start = parse_datetime(one_booking.date, one_booking.time.strftime('%H:%M'))
            booking_end = booking_start + datetime.timedelta(minutes=service_duration)
            curr_dt = booking_start
            while curr_dt < booking_end:
                if curr_dt in trainer_schedule_slots:
                    trainer_schedule_slots[curr_dt] = max(trainer_schedule_slots.get(curr_dt, 0) - 1, 0)
                curr_dt += datetime.timedelta(minutes=15)

    result_times = []
    service_duration = service_info.duration
    service_start_time = start_dt

    while service_start_time < end_dt:
        service_end_time = service_start_time + datetime.timedelta(minutes=service_duration)
        everything_is_free = True
        iter_start_time = service_start_time
        while iter_start_time < service_end_time:
            if trainer_schedule_slots.get(iter_start_time,0) == 0 or service_end_time > end_dt:  # <--- Изменение здесь: проверка свободного слота
                everything_is_free = False
                break
            iter_start_time += datetime.timedelta(minutes=15)
        if everything_is_free:
            result_times.append(service_start_time)
        service_start_time += datetime.timedelta(minutes=15)
    final_result = [time.strftime('%H:%M') for time in result_times]
    return final_result
