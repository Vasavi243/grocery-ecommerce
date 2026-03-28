from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from models import Order, OrderItem, Cart, Product, db
from forms import CheckoutForm
import stripe

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('main.index'))
    
    for item in cart_items:
        if not item.product.is_in_stock(item.quantity):
            flash(f'Sorry, {item.product.name} is out of stock.', 'danger')
            return redirect(url_for('cart.view_cart'))
    
    total = sum(item.get_total_price() for item in cart_items)
    form = CheckoutForm()
    
    if form.validate_on_submit():
        # Create order
        order = Order(
            user_id=current_user.id,
            total_amount=total,
            delivery_address=form.delivery_address.data,
            delivery_phone=form.delivery_phone.data,
            status=Order.STATUS_PENDING
        )
        db.session.add(order)
        db.session.flush()
        
        # Create order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price_at_time=cart_item.product.get_discount_price()
            )
            db.session.add(order_item)
            cart_item.product.reduce_stock(cart_item.quantity)
        
        # Clear cart
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        # If Stripe is configured, redirect to payment
        if current_app.config['STRIPE_SECRET_KEY']:
            return redirect(url_for('orders.payment', order_id=order.id))
        else:
            # Mock payment for demo
            order.status = Order.STATUS_PAID
            order.payment_method = 'Cash on Delivery'
            db.session.commit()
            flash(f'Order placed successfully! Order ID: #{order.id}', 'success')
            return redirect(url_for('orders.order_success', order_id=order.id))
    
    return render_template('checkout.html', cart_items=cart_items, total=total, form=form)

@orders_bp.route('/payment/<int:order_id>')
@login_required
def payment(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))
    
    if not current_app.config['STRIPE_SECRET_KEY']:
        flash('Payment gateway not configured.', 'warning')
        return redirect(url_for('orders.order_success', order_id=order.id))
    
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),  # Convert to cents
            currency='usd',
            metadata={'order_id': order.id}
        )
        
        return render_template('payment.html', 
                             order=order, 
                             client_secret=intent.client_secret,
                             stripe_public_key=current_app.config['STRIPE_PUBLIC_KEY'])
    except Exception as e:
        flash(f'Payment error: {str(e)}', 'danger')
        return redirect(url_for('orders.order_detail', order_id=order.id))

@orders_bp.route('/payment/confirm/<int:order_id>', methods=['POST'])
@login_required
def confirm_payment(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    payment_intent_id = request.json.get('payment_intent_id')
    
    if payment_intent_id:
        order.status = Order.STATUS_PAID
        order.payment_id = payment_intent_id
        order.payment_method = 'Stripe'
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Invalid payment'}), 400

@orders_bp.route('/order/success/<int:order_id>')
@login_required
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('order_success.html', order=order)

@orders_bp.route('/orders')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)

@orders_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('orders.order_history'))
    
    return render_template('order_detail.html', order=order)
