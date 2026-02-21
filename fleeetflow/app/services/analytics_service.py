from app.models import db, Vehicle, Trip, FuelLog, MaintenanceLog, VehicleStatus
from sqlalchemy import func

class AnalyticsService:
    @staticmethod
    def calculate_vehicle_roi(vehicle_id):
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return 0

        # Total Revenue from trips
        total_revenue = db.session.query(func.sum(Trip.estimated_revenue)).filter(Trip.vehicle_id == vehicle.id).scalar() or 0
        
        # Total Fuel Cost
        total_fuel = db.session.query(func.sum(FuelLog.total_cost)).filter(FuelLog.vehicle_id == vehicle.id).scalar() or 0
        
        # Total Maintenance Cost
        total_maint = db.session.query(func.sum(MaintenanceLog.cost)).filter(MaintenanceLog.vehicle_id == vehicle.id).scalar() or 0
        
        # Vehicle ROI = (Revenue - (Fuel + Maintenance)) / Acquisition Cost
        net_profit = float(total_revenue)
        costs = float(total_fuel) + float(total_maint)
        
        # Acquisition cost is numeric, cast to float
        acquisition_cost = float(vehicle.acquisition_cost)
        roi = ((net_profit - costs) / acquisition_cost) * 100 if acquisition_cost > 0 else 0
        
        return round(roi, 2)

    @staticmethod
    def get_fleet_kpis():
        total_vehicles = Vehicle.query.count()
        active_vehicles = Vehicle.query.filter_by(status=VehicleStatus.ON_TRIP).count()
        maintenance_alerts = Vehicle.query.filter_by(status=VehicleStatus.IN_SHOP).count()
        
        utilization_rate = (active_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0
        
        return {
            "total_fleet": total_vehicles,
            "active_fleet": active_vehicles,
            "maintenance_alerts": maintenance_alerts,
            "utilization_rate": round(utilization_rate, 2)
        }

    @staticmethod
    def get_fuel_efficiency(vehicle_id):
        # Fuel Efficiency = km / liter
        logs = FuelLog.query.filter_by(vehicle_id=vehicle_id).order_by(FuelLog.fill_date).all()
        if len(logs) < 2:
            return 0
        
        # odometer_reading is integer, liters is numeric
        total_km = float(logs[-1].odometer_reading - logs[0].odometer_reading)
        total_liters = sum(float(log.liters) for log in logs[1:]) # Liters used between first and last fill
        
        return round(total_km / total_liters, 2) if total_liters > 0 else 0
