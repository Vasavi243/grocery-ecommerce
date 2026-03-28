from flask import Blueprint, render_template, request
from models import Product, db
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Product.query
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    # Get featured products for homepage
    featured_products = Product.query.filter_by(is_featured=True).limit(6).all()
    
    # Get all products with pagination
    products = query.paginate(page=page, per_page=12, error_out=False)
    
    # Get categories for filter
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('index.html', 
                         products=products,
                         featured_products=featured_products,
                         categories=categories,
                         selected_category=category,
                         search_query=search)

@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Get related products from same category
    related_products = Product.query.filter(
        Product.category == product.category,
        Product.id != product.id
    ).limit(4).all()
    
    return render_template('product.html', 
                         product=product, 
                         related_products=related_products)

@main_bp.route('/categories')
def categories():
    all_categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in all_categories if c[0]]
    
    category_data = {}
    for cat in categories:
        count = Product.query.filter_by(category=cat).count()
        sample = Product.query.filter_by(category=cat).first()
        category_data[cat] = {'count': count, 'sample_image': sample.image_url if sample else None}
    
    return render_template('categories.html', categories=category_data)
