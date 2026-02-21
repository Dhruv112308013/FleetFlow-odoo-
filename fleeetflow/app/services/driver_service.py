from datetime import datetime
from app.models import db, User, Role, Driver, DriverStatus
from app.services.auth_service import AuthService

class DriverService:
    @staticmethod
    def register_driver(driver_data):
        """
        Registers a new driver by creating a User and a Driver record.
        driver_data: dict containing username, email, password, full_name, license_number, license_expiry
        """
        # 1. Ensure the 'Driver' role exists
        driver_role = Role.query.filter_by(name='Driver').first()
        if not driver_role:
            # If for some reason it doesn't exist (though it should be seeded)
            driver_role = Role(name='Driver', description='Vehicle Operator')
            db.session.add(driver_role)
            db.session.commit()

        # 2. Check if user already exists
        if User.query.filter((User.username == driver_data['username']) | (User.email == driver_data['email'])).first():
            raise ValueError("Username or Email already exists")

        # 3. Check if license number already exists
        if Driver.query.filter_by(license_number=driver_data['license_number']).first():
            raise ValueError("License number already registered to another driver")

        # 4. Create User record
        hashed_pw = AuthService.hash_password(driver_data['password'])
        new_user = User(
            username=driver_data['username'],
            email=driver_data['email'],
            password_hash=hashed_pw,
            role=driver_role
        )
        db.session.add(new_user)
        db.session.flush() # Get user ID for relationship if needed, though SQLAlchemy handles it

        # 4. Create Driver record
        # Convert license_expiry from string if necessary
        expiry_date = driver_data['license_expiry']
        if isinstance(expiry_date, str):
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()

        new_driver = Driver(
            user=new_user,
            full_name=driver_data['full_name'],
            license_number=driver_data['license_number'],
            license_expiry=expiry_date,
            status=DriverStatus.OFF_DUTY
        )
        db.session.add(new_driver)
        
        try:
            db.session.commit()
            return new_driver
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_all_drivers():
        return Driver.query.filter_by(is_deleted=False).all()

    @staticmethod
    def get_driver_stats():
        all_drivers = Driver.query.filter_by(is_deleted=False).all()
        stats = {
            'total': len(all_drivers),
            'on_duty': sum(1 for d in all_drivers if d.status == DriverStatus.ON_DUTY),
            'on_trip': sum(1 for d in all_drivers if d.status == DriverStatus.ON_TRIP),
            'off_duty': sum(1 for d in all_drivers if d.status == DriverStatus.OFF_DUTY)
        }
        return stats

    @staticmethod
    def get_driver_by_id(driver_id):
        return Driver.query.filter_by(id=driver_id, is_deleted=False).first()

    @staticmethod
    def update_driver(driver_id, data):
        driver = Driver.query.get(driver_id)
        if not driver:
            raise ValueError("Driver not found")

        # Check license number uniqueness if it changed
        if data.get('license_number') and data['license_number'] != driver.license_number:
            if Driver.query.filter_by(license_number=data['license_number']).first():
                raise ValueError("License number already registered to another driver")

        if 'full_name' in data:
            driver.full_name = data['full_name']
        if 'license_number' in data:
            driver.license_number = data['license_number']
        if 'license_expiry' in data:
            expiry_date = data['license_expiry']
            if isinstance(expiry_date, str):
                expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            driver.license_expiry = expiry_date

        try:
            db.session.commit()
            return driver
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_driver(driver_id):
        driver = Driver.query.get(driver_id)
        if not driver:
            raise ValueError("Driver not found")
        
        driver.is_deleted = True
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
