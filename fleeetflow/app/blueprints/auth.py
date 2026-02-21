from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app.services.auth_service import AuthService
from app.models import Role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = AuthService.authenticate(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role.name
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard.index'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Registration is usually restricted in a SaaS, but we provide a way to seed the first user
    roles = Role.query.all()
    if request.method == 'POST':
        try:
            AuthService.create_user(
                request.form.get('username'),
                request.form.get('email'),
                request.form.get('password'),
                request.form.get('role')
            )
            flash('User created successfully!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(str(e), 'danger')
            
    return render_template('auth/register.html', roles=roles)
