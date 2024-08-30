from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time
from database import Base

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    birth_date = Column(Date, unique=False)
    funds = Column(Integer, default=0)
    login = Column(String(50), unique=True)
    password = Column(String(50))
    phone = Column(String(13))

    def __init__(self, birth_date, login, password, phone):
        self.birth_date = birth_date
        self.login = login
        self.password = password
        self.phone = phone

    def __repr__(self):
        return f'<User {self.login!r}>'

class Gym(Base):
    __tablename__ = 'fitness_center'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    address = Column(String(50), unique=True)
    name = Column(String(50))
    contacts = Column(String(13))

    def __init__(self, address, name, contacts):
        self.address = address
        self.name = name
        self.contacts = contacts

class LoyaltyProgram(Base):
    __tablename__ = 'loyalty_program'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    program = Column(String(50))
    description = Column(String(50))

    def __init__(self, program, description):
        self.program = program
        self.description = description

class Reservation(Base):
    __tablename__ = 'reservation'
    reservation_id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'), unique=True, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    coach_id = Column(Integer, ForeignKey('trainer.coach_id'), nullable=False)
    service_id = Column(Integer, ForeignKey('service.service_id'), nullable=False)
    service = Column(String(50), ForeignKey('service.name'),)
    fitness_center_id = Column(Integer, ForeignKey('fitness_center.id'),)

    def __init__(self, user_id, time, coach_id, date, service, service_id, fitness_center_id):
        self.user_id = user_id
        self.time = time
        self.coach_id = coach_id
        self.date = date
        self.service = service
        self.service_id = service_id
        self.fitness_center_id = fitness_center_id

    def __repr__(self):
        return (f"<Reservation(reservation_id={self.reservation_id}, user_id={self.user_id}, "
                f"date={self.date}, time={self.time}, coach_id={self.coach_id}, "
                f"service_id={self.service_id}, service={self.service}, "
                f"fitness_center_id={self.fitness_center_id})>")

class Resources(Base):
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user = Column(String(50), ForeignKey('user.user_id'),)
    service = Column(String(50), ForeignKey('service.service_id'),)
    amount = Column(Integer)

    def __init__(self, user, service, amount):
        self.user = user
        self.service = service
        self.amount = amount

class Review(Base):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    trainer = Column(Integer, ForeignKey('trainer.coach_id'))
    user = Column(Integer, ForeignKey('user.user_id'),)
    points = Column(Integer)
    text = Column(String(100))

    def __init__(self, trainer, points, text, user):
        self.trainer = trainer
        self.points = points
        self.text = text
        self.user = user

class Service(Base):
    __tablename__ = 'service'
    service_id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    name = Column(String(50))
    duration = Column(Integer)
    price = Column(Integer)
    description = Column(String(150))
    max_attendees = Column(Integer, nullable=False)
    fitness_center_id = Column(Integer, ForeignKey('fitness_center.id'),)

    def __init__(self, name, duration, price, description, max_attendees, fitness_center_id):
        self.name = name
        self.duration = duration
        self.price = price
        self.description = description
        self.max_attendees = max_attendees
        self.fitness_center_id = fitness_center_id

    def __repr__(self):
        return (f"<Service(service_id={self.service_id}, name={self.name!r}, "
                f"duration={self.duration}, price={self.price}, description={self.description!r}, "
                f"max_attendees={self.max_attendees}, fitness_center_id={self.fitness_center_id})>")

class Coach(Base):
    __tablename__ = 'trainer'
    coach_id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    name = Column(String(50))
    gender = Column(String(10))
    age = Column(Integer)
    score = Column(Integer)
    fitness_center_id = Column(Integer, ForeignKey('user.user_id'),)

    def __init__(self, name, gender, age, score, fitness_center_id):
        self.name = name
        self.gender = gender
        self.age = age
        self.score = score
        self.fitness_center_id = fitness_center_id

class Slots(Base):
    __tablename__ = 'slots'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    capacity = Column(Integer)
    coach_id = Column(Integer, ForeignKey('coach.coach_id'),)
    service_id = Column(Integer, ForeignKey('service.service_id'),)

    def __init__(self, capacity, coach_id, service_id):
        self.capacity = capacity
        self.coach_id = coach_id
        self.service_id = service_id

class CoachSchedule(Base):
    __tablename__ = 'trainer_schedule'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    coach_id = Column(Integer, ForeignKey('trainer.coach_id'), unique=True, nullable=False)
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    service = Column(Integer, ForeignKey('service.service_id'),)

    def __init__(self, coach_id, date, start_time, end_time, service):
        self.coach_id = coach_id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.service = service

    def __repr__(self):
        return (f"<CoachSchedule(id={self.id}, coach_id={self.coach_id}, date={self.date}, "
                f"start_time={self.start_time}, end_time={self.end_time}, service={self.service})>")

class CoachServices(Base):
    __tablename__ = 'trainer_services'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    service_id = Column(Integer, ForeignKey('service.service_id'),)
    coach_id = Column(Integer, ForeignKey('trainer.coach_id'), unique=True, nullable=False)
    capacity = Column(Integer)

    def __init__(self, service_id, coach_id, capacity):
        self.service_id = service_id
        self.coach_id = coach_id
        self.capacity = capacity

    def __repr__(self):
        return (f"<CoachServices(id={self.id}, service_id={self.service_id}, "
                f"coach_id={self.coach_id}, capacity={self.capacity})>")
