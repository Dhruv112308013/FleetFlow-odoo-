from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Vehicle, Driver, VehicleStatus
from app.utils.rbac import login_required, roles_required

vehicles_bp = Blueprint('vehicles', __name__)

@vehicles_bp.route('/')
@login_required
def index():
    vehicles = Vehicle.query.filter_by(is_deleted=False).all()
    return render_template('vehicles/index.html', vehicles=vehicles)

@vehicles_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('Fleet Manager', 'Safety Officer')
def add():
    if request.method == 'POST':
        try:
            new_vehicle = Vehicle(
                license_plate=request.form.get('license_plate'),
                make=request.form.get('make'),
                model=request.form.get('model'),
                year=int(request.form.get('year')),
                type=request.form.get('type'),
                max_capacity_kg=float(request.form.get('max_capacity_kg')),
                acquisition_cost=float(request.form.get('acquisition_cost')),
                current_odometer=int(request.form.get('current_odometer', 0)),
                status=VehicleStatus.AVAILABLE
            )
            db.session.add(new_vehicle)
            db.session.commit()
            flash('Vehicle added successfully!', 'success')
            return redirect(url_for('vehicles.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'danger')
            
    return render_template('vehicles/form.html', vehicle=None)

@vehicles_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Fleet Manager', 'Safety Officer')
def edit(id):
    vehicle = Vehicle.query.get_or_404(id)
    if request.method == 'POST':
        try:
            vehicle.license_plate = request.form.get('license_plate')
            vehicle.make = request.form.get('make')
            vehicle.model = request.form.get('model')
            vehicle.year = int(request.form.get('year'))
            vehicle.max_capacity_kg = float(request.form.get('max_capacity_kg'))
            vehicle.status = VehicleStatus(request.form.get('status'))
            
            db.session.commit()
            flash('Vehicle updated successfully!', 'success')
            return redirect(url_for('vehicles.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'danger')
            
    return render_template('vehicles/form.html', vehicle=vehicle)

@vehicles_bp.route('/drivers')
@login_required
def drivers():
    drivers_list = Driver.query.filter_by(is_deleted=False).all()
    return render_template('drivers/index.html', drivers=drivers_list)
