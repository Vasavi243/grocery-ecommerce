from flask import Flask, render_template
from flask_login import LoginManager
from models import db, User, Product
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.cart import cart_bp
    from routes.orders import orders_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Context processors
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        cart_count = 0
        if current_user.is_authenticated:
            cart_count = sum(item.quantity for item in current_user.cart_items)
        return dict(cart_count=cart_count)
    
    return app

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@freshmart.com').first()
        if not admin:
            admin = User(
                username='Admin',
                email='admin@freshmart.com',
                phone='1234567890',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created: admin@freshmart.com / admin123')
        
        # Seed products if none exist
        if Product.query.count() == 0:
            products = [
                # Fruits
                Product(name='Fresh Apples', description='Crisp and juicy red apples, perfect for snacking or baking.', price=3.99, original_price=4.99, stock=100, unit='kg', category='Fruits', image_url='https://placehold.co/300x300/e74c3c/ffffff?text=Apples', is_organic=True, discount_percent=20),
                Product(name='Bananas', description='Sweet and ripe bananas, rich in potassium.', price=1.49, stock=150, unit='dozen', category='Fruits', image_url='https://placehold.co/300x300/f1c40f/ffffff?text=Bananas', is_organic=False),
                Product(name='Oranges', description='Fresh, juicy oranges packed with vitamin C.', price=2.99, stock=80, unit='kg', category='Fruits', image_url='https://placehold.co/300x300/e67e22/ffffff?text=Oranges', is_organic=True),
                Product(name='Mangoes', description='Sweet, tropical mangoes. Best when ripe.', price=4.99, original_price=5.99, stock=60, unit='kg', category='Fruits', image_url='https://placehold.co/300x300/f39c12/ffffff?text=Mangoes', is_organic=True, discount_percent=17, is_featured=True),
                Product(name='Grapes', description='Seedless green grapes, sweet and crunchy.', price=3.49, stock=70, unit='kg', category='Fruits', image_url='https://placehold.co/300x300/9b59b6/ffffff?text=Grapes', is_organic=False),
                Product(name='Watermelon', description='Large, sweet watermelon. Perfect for summer.', price=5.99, stock=40, unit='piece', category='Fruits', image_url='https://placehold.co/300x300/2ecc71/ffffff?text=Watermelon', is_organic=True),
                
                # Vegetables
                Product(name='Tomatoes', description='Fresh, ripe tomatoes for salads and cooking.', price=2.49, stock=120, unit='kg', category='Vegetables', image_url='https://placehold.co/300x300/e74c3c/ffffff?text=Tomatoes', is_organic=True, is_featured=True),
                Product(name='Potatoes', description='Versatile potatoes for all your cooking needs.', price=1.99, stock=200, unit='kg', category='Vegetables', image_url='https://placehold.co/300x300/d4a373/ffffff?text=Potatoes', is_organic=False),
                Product(name='Onions', description='Fresh onions, essential for every kitchen.', price=1.29, stock=180, unit='kg', category='Vegetables', image_url='https://placehold.co/300x300/9b59b6/ffffff?text=Onions', is_organic=False),
                Product(name='Carrots', description='Crunchy, sweet carrots. Great for snacking.', price=1.79, stock=100, unit='kg', category='Vegetables', image_url='https://placehold.co/300x300/e67e22/ffffff?text=Carrots', is_organic=True),
                Product(name='Spinach', description='Fresh green spinach leaves, packed with nutrients.', price=2.29, original_price=2.99, stock=80, unit='bunch', category='Vegetables', image_url='https://placehold.co/300x300/27ae60/ffffff?text=Spinach', is_organic=True, discount_percent=23),
                Product(name='Bell Peppers', description='Colorful bell peppers, perfect for stir-fries.', price=2.99, stock=90, unit='kg', category='Vegetables', image_url='https://placehold.co/300x300/e74c3c/ffffff?text=Peppers', is_organic=False),
                
                # Dairy
                Product(name='Fresh Milk', description='Farm-fresh whole milk, 1 liter.', price=1.99, stock=100, unit='pack', category='Dairy', image_url='https://placehold.co/300x300/3498db/ffffff?text=Milk', is_organic=True),
                Product(name='Eggs', description='Free-range eggs, dozen pack.', price=3.49, stock=80, unit='dozen', category='Dairy', image_url='https://placehold.co/300x300/f5f5dc/333333?text=Eggs', is_organic=True, is_featured=True),
                Product(name='Cheddar Cheese', description='Sharp cheddar cheese, 200g block.', price=4.99, stock=50, unit='pack', category='Dairy', image_url='https://placehold.co/300x300/f1c40f/ffffff?text=Cheese', is_organic=False),
                Product(name='Yogurt', description='Creamy natural yogurt, 500g.', price=2.49, stock=60, unit='pack', category='Dairy', image_url='https://placehold.co/300x300/ffffff/333333?text=Yogurt', is_organic=True),
                
                # Bakery
                Product(name='White Bread', description='Freshly baked white bread loaf.', price=2.29, stock=40, unit='piece', category='Bakery', image_url='https://placehold.co/300x300/f4e4c1/8b4513?text=Bread', is_organic=False),
                Product(name='Croissants', description='Buttery, flaky croissants. Pack of 4.', price=4.49, stock=30, unit='pack', category='Bakery', image_url='https://placehold.co/300x300/f5deb3/8b4513?text=Croissants', is_organic=False, is_featured=True),
                
                # Beverages
                Product(name='Orange Juice', description='100% pure orange juice, 1 liter.', price=3.99, stock=70, unit='pack', category='Beverages', image_url='https://placehold.co/300x300/ffa500/ffffff?text=Juice', is_organic=True),
                Product(name='Green Tea', description='Premium green tea bags, pack of 25.', price=4.99, original_price=6.99, stock=50, unit='pack', category='Beverages', image_url='https://placehold.co/300x300/228b22/ffffff?text=Tea', is_organic=True, discount_percent=29),
                
                # Pantry
                Product(name='Rice', description='Premium basmati rice, 5kg bag.', price=8.99, stock=60, unit='pack', category='Pantry', image_url='https://placehold.co/300x300/fffaf0/333333?text=Rice', is_organic=False),
                Product(name='Olive Oil', description='Extra virgin olive oil, 500ml.', price=7.99, stock=40, unit='pack', category='Pantry', image_url='https://placehold.co/300x300/808000/ffffff?text=Oil', is_organic=True),
                
                # Snacks
                Product(name='Mixed Nuts', description='Healthy mixed nuts, 250g.', price=5.99, stock=45, unit='pack', category='Snacks', image_url='https://placehold.co/300x300/8b4513/ffffff?text=Nuts', is_organic=True),
                
                # Frozen
                Product(name='Frozen Peas', description='Sweet garden peas, 500g frozen.', price=2.49, stock=80, unit='pack', category='Frozen', image_url='https://placehold.co/300x300/90ee90/ffffff?text=Peas', is_organic=False),
            ]
            
            for product in products:
                db.session.add(product)
            
            db.session.commit()
            print(f'{len(products)} products seeded successfully!')
        
        print('Database initialized successfully!')

if __name__ == '__main__':
    init_db()
    app = create_app()
    app.run(debug=True, port=5000)
