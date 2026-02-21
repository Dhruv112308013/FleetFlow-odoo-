from app import create_app
from app.models import db, Role, User, Vehicle, Driver, VehicleStatus, DriverStatus

app = create_app()

with app.app_context():
    # Ensure tables are fresh
    print("Dropping and recreating database tables...")
    db.drop_all()
    db.create_all()
    
    print("Seeding database...")
    
    # 1. Roles
    roles_data = {
        'Fleet Manager': 'Full system access',
        'Dispatcher': 'Manage trips and scheduling',
        'Safety Officer': 'Vehicle compliance and maintenance',
        'Financial Analyst': 'Expense and ROI reporting'
    }
    role_objects = {}
    for r_name, r_desc in roles_data.items():
        role = Role(name=r_name, description=r_desc)
        db.session.add(role)
        role_objects[r_name] = role
    db.session.commit()

    # 2. Users
    from app.services.auth_service import AuthService
    admin_pw = AuthService.hash_password('admin123')
    admin = User(username='admin', email='admin@fleetflow.com', password_hash=admin_pw, role=role_objects['Fleet Manager'])
    db.session.add(admin)
    
    dispatch_pw = AuthService.hash_password('dispatch123')
    dispatcher = User(username='dispatcher', email='dispatch@fleetflow.com', password_hash=dispatch_pw, role=role_objects['Dispatcher'])
    db.session.add(dispatcher)
    db.session.commit()

    # 3. Vehicles
    v1 = Vehicle(
        license_plate='TRK-1001', make='Tesla', model='Semi', year=2024, type='Truck',
        max_capacity_kg=36000.0, current_odometer=1200, acquisition_cost=12000000.0, status=VehicleStatus.AVAILABLE
    )
    db.session.add(v1)
    
    v2 = Vehicle(
        license_plate='VAN-2002', make='Mercedes', model='Sprinter', year=2023, type='Van',
        max_capacity_kg=2500.0, current_odometer=5400, acquisition_cost=5200000.0, status=VehicleStatus.AVAILABLE
    )
    db.session.add(v2)
    db.session.commit()

    # 4. Drivers
    from datetime import datetime, timedelta
    d1_user = User(username='jdoe', email='jdoe@example.com', password_hash=admin_pw, role=role_objects['Dispatcher'])
    db.session.add(d1_user)
    db.session.commit()

    d1 = Driver(
        user_id=d1_user.id, full_name='John Doe', license_number='D-998877', 
        license_expiry=(datetime.now() + timedelta(days=365)).date(), status=DriverStatus.ON_DUTY
    )
    db.session.add(d1)
    db.session.commit()

    print("Seeding complete! Admin: admin/admin123, Dispatcher: dispatcher/dispatch123")
