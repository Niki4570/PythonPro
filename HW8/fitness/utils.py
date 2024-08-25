import datetime
import sqlite3


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


def calc_slots(coach_id, service_id, desired_date):
    with SQLiteDatabase('fdb.db') as db:
        booked_time = db.fetch_all("""
            SELECT * FROM reservation 
            JOIN service ON service.service_id = reservation.service_id 
            WHERE reservation.date = ? 
            AND reservation.coach_id = ? 
            AND reservation.service_id = ?""",
                                   (desired_date, coach_id, service_id))
        trainer_schedule = db.fetch_one('SELECT * FROM trainer_schedule WHERE coach_id = ? AND date = ?',
                                        (coach_id, desired_date))
        trainer_capacity = db.fetch_one('SELECT * FROM trainer_services WHERE coach_id = ? AND service_id = ?',
                                        (coach_id, service_id))
        service_info = db.fetch_one('SELECT * FROM service WHERE service_id = ?',
                                    (service_id,))
        if not trainer_schedule or not trainer_capacity or not service_info:
            print(f"trainer_schedule: {trainer_schedule}")
            print(f"trainer_capacity: {trainer_capacity}")
            print(f"service_info: {service_info}")
            return []
        def parse_datetime(date_str, time_str):
            return datetime.datetime.strptime(f"{date_str} {time_str}", '%d-%m-%Y %H:%M')
        start_dt = parse_datetime(trainer_schedule["date"], trainer_schedule["start_time"])
        end_dt = parse_datetime(trainer_schedule["date"], trainer_schedule["end_time"])
        curr_dt = start_dt
        trainer_schedule = {}
        while curr_dt <= end_dt:
            trainer_schedule[curr_dt] = trainer_capacity['capacity']
            curr_dt += datetime.timedelta(minutes=15)
        if booked_time:
            for one_booking in booked_time:
                booking_start = parse_datetime(one_booking["date"], one_booking["time"])
                booking_end = booking_start + datetime.timedelta(minutes=one_booking["duration"])
                curr_dt = booking_start
                while curr_dt < booking_end:
                    trainer_schedule[curr_dt] = max(trainer_schedule.get(curr_dt, 0) - 1, 0)
                    curr_dt += datetime.timedelta(minutes=15)
        result_times = []
        service_duration = service_info['duration']
        service_start_time = start_dt
        while service_start_time < end_dt:
            service_end_time = service_start_time + datetime.timedelta(minutes=service_duration)
            everything_is_free = True
            iter_start_time = service_start_time
            while iter_start_time < service_end_time:
                if trainer_schedule.get(iter_start_time, 0) == 0 or service_end_time > end_dt:
                    everything_is_free = False
                    break
                iter_start_time += datetime.timedelta(minutes=15)
            if everything_is_free:
                result_times.append(service_start_time)
            service_start_time += datetime.timedelta(minutes=15)
        final_result = [time.strftime('%H:%M') for time in result_times]
        return final_result
