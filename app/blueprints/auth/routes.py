from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from . import bp
from .forms import LoginForm
from app.models.auth import User, AuditLog
from app.extensions import db

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Usuario o contraseña no validos.', 'error')
            return redirect(url_for('auth.login'))
            
        if not user.active:
            flash('Usuario deshabilitado.', 'error')
            return redirect(url_for('auth.login'))
            
        login_user(user)
        # Audit Log
        audit = AuditLog(user_id=user.id, action='LOGIN', entity_type='Auth', details="Ingreso correcto", ip_address=request.remote_addr)
        db.session.add(audit)
        db.session.commit()
        
        return redirect(url_for('dashboard.index'))
        
    return render_template('auth/login.html', title='Iniciar Sesión', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
