from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.driver_service import DriverService
from app.utils.rbac import login_required, roles_required

drivers_bp = Blueprint('drivers', __name__)

@drivers_bp.route('/')
@login_required
@roles_required('Fleet Manager', 'Dispatcher', 'Admin')
def index():
    drivers = DriverService.get_all_drivers()
    stats = DriverService.get_driver_stats()
    return render_template('drivers/index.html', drivers=drivers, stats=stats)

@drivers_bp.route('/register', methods=['GET', 'POST'])
@login_required
@roles_required('Fleet Manager', 'Dispatcher', 'Admin')
def register():
    if request.method == 'POST':
        try:
            driver_data = {
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'password': request.form.get('password'),
                'full_name': request.form.get('full_name'),
                'license_number': request.form.get('license_number'),
                'license_expiry': request.form.get('license_expiry')
            }
            DriverService.register_driver(driver_data)
            flash('Driver registered successfully!', 'success')
            return redirect(url_for('drivers.index'))
        except ValueError as e:
            flash(str(e), 'warning')
        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
            
    return render_template('drivers/register.html')

@drivers_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Fleet Manager', 'Admin')
def edit(id):
    driver = DriverService.get_driver_by_id(id)
    if not driver:
        flash("Driver not found", "danger")
        return redirect(url_for('drivers.index'))

    if request.method == 'POST':
        try:
            update_data = {
                'full_name': request.form.get('full_name'),
                'license_number': request.form.get('license_number'),
                'license_expiry': request.form.get('license_expiry')
            }
            DriverService.update_driver(id, update_data)
            flash('Driver profile updated!', 'success')
            return redirect(url_for('drivers.index'))
        except ValueError as e:
            flash(str(e), 'warning')
        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')

    return render_template('drivers/edit.html', driver=driver)

@drivers_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@roles_required('Fleet Manager', 'Admin')
def delete(id):
    try:
        DriverService.delete_driver(id)
        flash('Driver record deactivated', 'success')
    except Exception as e:
        flash(f"Error: {str(e)}", 'danger')
    return redirect(url_for('drivers.index'))
