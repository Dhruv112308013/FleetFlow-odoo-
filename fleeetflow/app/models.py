from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class VehicleStatus(enum.Enum):
    AVAILABLE = 'Available'
    ON_TRIP = 'On Trip'
    IN_SHOP = 'In Shop'
    SUSPENDED = 'Suspended'

class DriverStatus(enum.Enum):
    ON_DUTY = 'On Duty'
    OFF_DUTY = 'Off Duty'
    ON_TRIP = 'On Trip'
    SUSPENDED = 'Suspended'

class TripStatus(enum.Enum):
    SCHEDULED = 'Scheduled'
    DISPATCHED = 'Dispatched'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'

class ExpenseType(enum.Enum):
    INSURANCE = 'Insurance'
    TOLLS = 'Tolls'
    FINES = 'Fines'
    PERMITS = 'Permits'
    OTHER = 'Other'

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    role = db.relationship('Role', backref=db.backref('users', lazy=True))

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    max_capacity_kg = db.Column(db.Numeric(10, 2), nullable=False)
    current_odometer = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum(VehicleStatus, native_enum=False), default=VehicleStatus.AVAILABLE)
    acquisition_cost = db.Column(db.Numeric(15, 2), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Driver(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    license_expiry = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(DriverStatus, native_enum=False), default=DriverStatus.OFF_DUTY)
    is_deleted = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref=db.backref('driver', uselist=False))

class Trip(db.Model):
    __tablename__ = 'trips'
    id = db.Column(db.Integer, primary_key=True)
    trip_number = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    origin = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    cargo_weight_kg = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(TripStatus, native_enum=False), default=TripStatus.SCHEDULED)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    start_odometer = db.Column(db.Integer)
    end_odometer = db.Column(db.Integer)
    estimated_revenue = db.Column(db.Numeric(15, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vehicle = db.relationship('Vehicle', backref=db.backref('trips', lazy=True))
    driver = db.relationship('Driver', backref=db.backref('trips', lazy=True))

class MaintenanceLog(db.Model):
    __tablename__ = 'maintenance_logs'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cost = db.Column(db.Numeric(15, 2), nullable=False)
    odometer_at_service = db.Column(db.Integer)
    performed_by = db.Column(db.String(100))
    
    vehicle = db.relationship('Vehicle', backref=db.backref('maintenance_logs', lazy=True))

class FuelLog(db.Model):
    __tablename__ = 'fuel_logs'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    fill_date = db.Column(db.DateTime, default=datetime.utcnow)
    liters = db.Column(db.Numeric(10, 2), nullable=False)
    cost_per_liter = db.Column(db.Numeric(10, 2), nullable=False)
    total_cost = db.Column(db.Numeric(15, 2), nullable=False)
    odometer_reading = db.Column(db.Integer)
    
    trip = db.relationship('Trip', backref=db.backref('fuel_logs', lazy=True))
    vehicle = db.relationship('Vehicle', backref=db.backref('fuel_logs', lazy=True))

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    expense_type = db.Column(db.Enum(ExpenseType, native_enum=False), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    
    vehicle = db.relationship('Vehicle', backref=db.backref('expenses', lazy=True))


