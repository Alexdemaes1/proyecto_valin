from app import create_app
from app.extensions import db

app = create_app('dev')

if __name__ == '__main__':
    with app.app_context():
        # Creacion de DB local instantánea para desarrollo
        db.create_all()
    
    app.run(debug=True, port=5000)
