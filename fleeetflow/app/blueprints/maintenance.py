from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Vehicle, MaintenanceLog
from app.services.maintenance_service import MaintenanceService
from app.utils.rbac import login_required, roles_required

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/')
@login_required
def index():
    logs = MaintenanceLog.query.order_by(MaintenanceLog.service_date.desc()).all()
    return render_template('maintenance/index.html', logs=logs)

@maintenance_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('Fleet Manager', 'Safety Officer')
def add():
    if request.method == 'POST':
        try:
            maintenance_data = {
                'vehicle_id': request.form.get('vehicle_id'),
                'service_date': request.form.get('service_date'),
                'service_type': request.form.get('service_type'),
                'description': request.form.get('description'),
                'cost': float(request.form.get('cost')),
                'odometer_at_service': int(request.form.get('odometer_at_service')),
                'performed_by': request.form.get('performed_by')
            }
            MaintenanceService.create_log(maintenance_data)
            flash('Maintenance log created. Vehicle status changed to In Shop.', 'success')
            return redirect(url_for('maintenance.index'))
        except Exception as e:
            flash(str(e), 'danger')
            
    vehicles = Vehicle.query.filter_by(is_deleted=False).all()
    return render_template('maintenance/form.html', vehicles=vehicles)

@maintenance_bp.route('/release/<int:vehicle_id>')
@login_required
@roles_required('Fleet Manager', 'Safety Officer')
def release(vehicle_id):
    try:
        MaintenanceService.release_from_shop(vehicle_id)
        flash('Vehicle released from shop and is now Available.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('vehicles.index'))
