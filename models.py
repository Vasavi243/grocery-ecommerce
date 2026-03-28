from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('Cart', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(50), default='piece')  # kg, piece, dozen, etc.
    image_url = db.Column(db.String(500))
    category = db.Column(db.String(100))
    is_organic = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    discount_percent = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('Cart', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def is_in_stock(self, quantity=1):
        return self.stock >= quantity
    
    def reduce_stock(self, quantity):
        if self.is_in_stock(quantity):
            self.stock -= quantity
            return True
        return False
    
    def get_discount_price(self):
        if self.discount_percent > 0:
            return round(self.price * (1 - self.discount_percent / 100), 2)
        return self.price

class Cart(db.Model):
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_total_price(self):
        return self.quantity * self.product.get_discount_price()

class Order(db.Model):
    __tablename__ = 'orders'
    
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default=STATUS_PENDING)
    payment_id = db.Column(db.String(100))
    payment_method = db.Column(db.String(50))
    delivery_address = db.Column(db.Text)
    delivery_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def get_status_color(self):
        colors = {
            self.STATUS_PENDING: 'warning',
            self.STATUS_PAID: 'info',
            self.STATUS_PROCESSING: 'primary',
            self.STATUS_SHIPPED: 'secondary',
            self.STATUS_DELIVERED: 'success',
            self.STATUS_CANCELLED: 'danger'
        }
        return colors.get(self.status, 'secondary')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False)
    
    def get_total(self):
        return self.quantity * self.price_at_time
