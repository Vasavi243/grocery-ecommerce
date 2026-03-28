from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import Cart, Product, db

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
@login_required
def view_cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total = sum(item.get_total_price() for item in cart_items)
    item_count = sum(item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total, item_count=item_count)

@cart_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity < 1:
        flash('Quantity must be at least 1.', 'danger')
        return redirect(url_for('main.product_detail', product_id=product_id))
    
    if not product.is_in_stock(quantity):
        flash('Sorry, insufficient stock available.', 'danger')
        return redirect(url_for('main.product_detail', product_id=product_id))
    
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        new_quantity = cart_item.quantity + quantity
        if not product.is_in_stock(new_quantity):
            flash('Cannot add more items. Stock limit reached.', 'danger')
            return redirect(url_for('cart.view_cart'))
        cart_item.quantity = new_quantity
        message = f'Updated {product.name} quantity in cart!'
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
        message = f'{product.name} added to cart!'
    
    db.session.commit()
    flash(message, 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/cart/update/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    
    if cart_item.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity < 1:
        flash('Quantity must be at least 1.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    if not cart_item.product.is_in_stock(quantity):
        flash('Insufficient stock available.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    cart_item.quantity = quantity
    db.session.commit()
    flash('Cart updated successfully!', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/cart/remove/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    
    if cart_item.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    Cart.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Cart cleared.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/api/cart/count')
@login_required
def cart_count():
    count = sum(item.quantity for item in current_user.cart_items)
    return jsonify({'count': count})
