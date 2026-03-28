from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from models import Product, Order, User, db
from forms import ProductForm
import os
from werkzeug.utils import secure_filename
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@admin_bp.route('/admin')
@login_required
@admin_required
def dashboard():
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_users = User.query.count()
    pending_orders = Order.query.filter_by(status=Order.STATUS_PENDING).count()
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    low_stock = Product.query.filter(Product.stock < 10).all()
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         total_orders=total_orders,
                         total_users=total_users,
                         pending_orders=pending_orders,
                         recent_orders=recent_orders,
                         low_stock=low_stock)

@admin_bp.route('/admin/products')
@login_required
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/products.html', products=products)

@admin_bp.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            original_price=form.original_price.data,
            stock=form.stock.data,
            unit=form.unit.data,
            category=form.category.data,
            is_organic=form.is_organic.data,
            is_featured=form.is_featured.data,
            discount_percent=form.discount_percent.data or 0
        )
        
        if form.image.data:
            file = form.image.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                product.image_url = f'images/{filename}'
        
        db.session.add(product)
        db.session.commit()
        flash(f'Product "{product.name}" added successfully!', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/add_product.html', form=form, title='Add Product')

@admin_bp.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.original_price = form.original_price.data
        product.stock = form.stock.data
        product.unit = form.unit.data
        product.category = form.category.data
        product.is_organic = form.is_organic.data
        product.is_featured = form.is_featured.data
        product.discount_percent = form.discount_percent.data or 0
        
        if form.image.data:
            file = form.image.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                product.image_url = f'images/{filename}'
        
        db.session.commit()
        flash(f'Product "{product.name}" updated successfully!', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/add_product.html', form=form, title='Edit Product', product=product)

@admin_bp.route('/admin/product/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if product.image_url:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                  product.image_url.replace('images/', ''))
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{product.name}" deleted successfully!', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/admin/orders')
@login_required
@admin_required
def orders():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/orders.html', orders=orders, selected_status=status)

@admin_bp.route('/admin/order/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@admin_bp.route('/admin/order/update-status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    valid_statuses = [Order.STATUS_PENDING, Order.STATUS_PAID, Order.STATUS_PROCESSING, 
                      Order.STATUS_SHIPPED, Order.STATUS_DELIVERED, Order.STATUS_CANCELLED]
    
    if new_status in valid_statuses:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.id} status updated to {new_status}.', 'success')
    else:
        flash('Invalid status.', 'danger')
    
    return redirect(url_for('admin.order_detail', order_id=order.id))
