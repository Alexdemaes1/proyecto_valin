import sys
import os

# Adds the parent project root folder to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.auth import User, Role

def create_admin_user():
    app = create_app('dev')
    with app.app_context():
        # Asegurar que las tablas existen
        db.create_all()
        # Clean sync DB for roles
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin', description='Permisos ilimitados sobre el sistema de Tráfico y sincronización.')
            db.session.add(admin_role)
            db.session.commit()
            print("Rol Admin Creado.")
        
        # Check Admin exists
        existent_admin = User.query.filter_by(username='admin').first()
        if not existent_admin:
            admin = User(username='admin', email='trafico@transportesvalin.com', role_id=admin_role.id)
            admin.set_password('10041004')
            db.session.add(admin)
            db.session.commit()
            print("Usuario 'admin' (pass: '10041004') CREADO con éxito para tu panel.")
        else:
            existent_admin.set_password('10041004')
            db.session.commit()
            print("Password de 'admin' actualizada a '10041004'.")

if __name__ == '__main__':
    create_admin_user()
