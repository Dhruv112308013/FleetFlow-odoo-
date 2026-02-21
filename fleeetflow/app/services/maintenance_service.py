from datetime import datetime
from app.models import db, MaintenanceLog, Vehicle, VehicleStatus

class MaintenanceService:
    @staticmethod
    def create_log(maintenance_data):
        vehicle = Vehicle.query.get(maintenance_data['vehicle_id'])
        if not vehicle:
            raise ValueError("Vehicle not found")

        # Handle service date string conversion if necessary
        service_date = maintenance_data['service_date']
        if isinstance(service_date, str):
            service_date = datetime.strptime(service_date, '%Y-%m-%d').date()

        log = MaintenanceLog(
            vehicle_id=vehicle.id,
            service_date=service_date,
            service_type=maintenance_data['service_type'],
            description=maintenance_data.get('description'),
            cost=float(maintenance_data['cost']),
            odometer_at_service=int(maintenance_data.get('odometer_at_service', 0)),
            performed_by=maintenance_data.get('performed_by')
        )

        # Business Rule 5: When maintenance log created, vehicle auto-switches to "In Shop"
        vehicle.status = VehicleStatus.IN_SHOP
        
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def release_from_shop(vehicle_id):
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            raise ValueError("Vehicle not found")
        
        vehicle.status = VehicleStatus.AVAILABLE
        db.session.commit()
        return vehicle
