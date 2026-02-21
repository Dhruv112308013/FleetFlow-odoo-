import os
from flask import Flask, redirect, url_for, session
from flask_session import Session
from app.models import db
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fleetflow-secret-12345')
    
    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    
    # Session Configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    
    # Register Blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.vehicles import vehicles_bp
    from app.blueprints.trips import trips_bp
    from app.blueprints.maintenance import maintenance_bp
    from app.blueprints.financials import financials_bp
    from app.blueprints.drivers import drivers_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(vehicles_bp, url_prefix='/vehicles')
    app.register_blueprint(trips_bp, url_prefix='/trips')
    app.register_blueprint(maintenance_bp, url_prefix='/maintenance')
    app.register_blueprint(financials_bp, url_prefix='/financials')
    app.register_blueprint(drivers_bp, url_prefix='/drivers')
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app
