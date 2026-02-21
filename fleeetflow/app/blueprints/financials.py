from flask import Blueprint, render_template
from app.models import Vehicle
from app.services.analytics_service import AnalyticsService
from app.utils.rbac import login_required, roles_required

financials_bp = Blueprint('financials', __name__)

@financials_bp.route('/')
@login_required
@roles_required('Fleet Manager', 'Financial Analyst')
def index():
    vehicles = Vehicle.query.filter_by(is_deleted=False).all()
    fleet_roi = []
    
    for v in vehicles:
        roi = AnalyticsService.calculate_vehicle_roi(v.id)
        fleet_roi.append({
            'vehicle': v,
            'roi': roi,
            'efficiency': AnalyticsService.get_fuel_efficiency(v.id)
        })
        
    return render_template('financials/index.html', fleet_roi=fleet_roi)
