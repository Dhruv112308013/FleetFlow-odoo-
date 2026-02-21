from datetime import datetime
from app.models import db, Trip, Vehicle, Driver, VehicleStatus, DriverStatus, TripStatus

class TripService:
    @staticmethod
    def create_trip(trip_data):
        vehicle = Vehicle.query.get(trip_data['vehicle_id'])
        driver = Driver.query.get(trip_data['driver_id'])

        # Business Rule 1: Prevent trip creation if cargo_weight > vehicle.max_capacity
        if float(trip_data['cargo_weight_kg']) > float(vehicle.max_capacity_kg):
            raise ValueError(f"Cargo weight exceeds vehicle capacity ({vehicle.max_capacity_kg} kg)")

        # Business Rule 2: Block driver assignment if driver status != "On Duty" or license expired
        if driver.status != DriverStatus.ON_DUTY:
            raise ValueError(f"Driver is currently {driver.status.value}. Must be On Duty.")
        
        # Ensure driver.license_expiry is a date object for comparison
        license_expiry = driver.license_expiry
        if isinstance(license_expiry, str):
            license_expiry = datetime.strptime(license_expiry, '%Y-%m-%d').date()
            
        if license_expiry < datetime.now().date():
            raise ValueError("Driver license has expired.")

        new_trip = Trip(
            trip_number=f"TRP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            vehicle_id=vehicle.id,
            driver_id=driver.id,
            origin=trip_data['origin'],
            destination=trip_data['destination'],
            cargo_weight_kg=float(trip_data['cargo_weight_kg']),
            estimated_revenue=float(trip_data.get('estimated_revenue', 0)),
            status=TripStatus.SCHEDULED
        )
        db.session.add(new_trip)
        db.session.commit()
        return new_trip

    @staticmethod
    def dispatch_trip(trip_id):
        trip = Trip.query.get(trip_id)
        if not trip:
            raise ValueError("Trip not found")

        # Business Rule 3: When trip status changes to "Dispatched"
        trip.status = TripStatus.DISPATCHED
        trip.start_time = datetime.now()
        
        # Vehicle status = "On Trip"
        trip.vehicle.status = VehicleStatus.ON_TRIP
        
        # Driver status = "On Trip"
        trip.driver.status = DriverStatus.ON_TRIP

        db.session.commit()
        return trip

    @staticmethod
    def complete_trip(trip_id, end_odometer):
        trip = Trip.query.get(trip_id)
        if not trip:
            raise ValueError("Trip not found")

        if end_odometer <= trip.vehicle.current_odometer:
            raise ValueError("End odometer must be greater than starting odometer")

        # Business Rule 4: When trip marked "Completed"
        trip.status = TripStatus.COMPLETED
        trip.end_time = datetime.now()
        trip.end_odometer = end_odometer
        
        # Vehicle status = "Available"
        trip.vehicle.status = VehicleStatus.AVAILABLE
        # Odometer must update
        trip.vehicle.current_odometer = end_odometer
        
        # Driver status = "Available" (Set back to 'On Duty' so they can be assigned again)
        trip.driver.status = DriverStatus.ON_DUTY

        db.session.commit()
        return trip
