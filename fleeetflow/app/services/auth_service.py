import bcrypt
from app.models import db, User, Role

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def authenticate(username_or_email, password):
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and AuthService.check_password(password, user.password_hash):
            return user
        return None

    @staticmethod
    def create_user(username, email, password, role_name):
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise ValueError(f"Role {role_name} does not exist")
        
        hashed_pw = AuthService.hash_password(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_pw,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user
