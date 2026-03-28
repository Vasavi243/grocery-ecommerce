import os
from flask import Flask
from models import db
from routes.auth import auth_bp
from routes.main import main_bp
from routes.cart import cart_bp
from routes.orders import orders_bp

app = Flask(__name__)

uri = os.environ.get('DATABASE_URL', 'sqlite:///grocery.db')
if uri and uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(orders_bp)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
from flask_login import LoginManager
from models import User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    if not Product.query.first():
        db.session.add(Product(name='Organic Apples', price=2.99, description='Fresh and crunchy apples.', stock=50, image_url='https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6'))
        db.session.add(Product(name='Whole Milk', price=3.49, description='1 gallon of fresh farm milk.', stock=20, image_url='https://images.unsplash.com/photo-1550583724-12558142ab15'))
        db.session.add(Product(name='Sourdough Bread', price=4.50, description='Freshly baked loaf.', stock=15, image_url='https://images.unsplash.com/photo-1585478259715-876a6a81fc08'))
        db.session.commit()
        print('? Database seeded automatically!')
