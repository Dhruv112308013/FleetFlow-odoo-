from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Trip, Vehicle, Driver, VehicleStatus, DriverStatus
from app.services.trip_service import TripService
from app.utils.rbac import login_required, roles_required

trips_bp = Blueprint('trips', __name__)

@trips_bp.route('/')
@login_required
def index():
    trips = Trip.query.order_by(Trip.created_at.desc()).all()
    return render_template('trips/index.html', trips=trips)

@trips_bp.route('/create', methods=['GET', 'POST'])
@login_required
@roles_required('Fleet Manager', 'Dispatcher')
def create():
    if request.method == 'POST':
        try:
            trip_data = {
                'vehicle_id': request.form.get('vehicle_id'),
                'driver_id': request.form.get('driver_id'),
                'origin': request.form.get('origin'),
                'destination': request.form.get('destination'),
                'cargo_weight_kg': request.form.get('cargo_weight_kg'),
                'estimated_revenue': request.form.get('estimated_revenue')
            }
            TripService.create_trip(trip_data)
            flash('Trip scheduled successfully!', 'success')
            return redirect(url_for('trips.index'))
        except ValueError as e:
            flash(str(e), 'warning')
        except Exception as e:
            flash(f"Critical Error: {str(e)}", 'danger')

    # Filters for assignment
    available_vehicles = Vehicle.query.filter_by(status=VehicleStatus.AVAILABLE, is_deleted=False).all()
    available_drivers = Driver.query.filter_by(status=DriverStatus.ON_DUTY, is_deleted=False).all()
    
    return render_template('trips/form.html', vehicles=available_vehicles, drivers=available_drivers)

@trips_bp.route('/dispatch/<int:id>')
@login_required
@roles_required('Dispatcher', 'Fleet Manager')
def dispatch(id):
    try:
        TripService.dispatch_trip(id)
        flash('Trip dispatched! Vehicle and Driver are now On Trip.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('trips.index'))

@trips_bp.route('/complete/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Dispatcher', 'Fleet Manager')
def complete(id):
    trip = Trip.query.get_or_404(id)
    if request.method == 'POST':
        try:
            end_odometer = int(request.form.get('end_odometer'))
            TripService.complete_trip(id, end_odometer)
            flash('Trip completed successfully!', 'success')
            return redirect(url_for('trips.index'))
        except ValueError as e:
            flash(str(e), 'warning')
    return render_template('trips/complete_modal.html', trip=trip)
