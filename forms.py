from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FloatField, IntegerField, SelectField, FileField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError, Optional
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=3, max=80)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    phone = StringField('Phone Number', validators=[
        Length(max=20)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    original_price = FloatField('Original Price', validators=[Optional(), NumberRange(min=0)])
    stock = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    unit = SelectField('Unit', choices=[
        ('piece', 'Per Piece'),
        ('kg', 'Per Kg'),
        ('500g', 'Per 500g'),
        ('dozen', 'Per Dozen'),
        ('bunch', 'Per Bunch'),
        ('pack', 'Per Pack')
    ], validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Fruits', 'Fruits'),
        ('Vegetables', 'Vegetables'),
        ('Dairy', 'Dairy & Eggs'),
        ('Bakery', 'Bakery'),
        ('Beverages', 'Beverages'),
        ('Snacks', 'Snacks'),
        ('Pantry', 'Pantry Staples'),
        ('Frozen', 'Frozen Foods'),
        ('Organic', 'Organic'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    is_organic = BooleanField('Organic Product')
    is_featured = BooleanField('Featured Product')
    discount_percent = IntegerField('Discount %', validators=[Optional(), NumberRange(min=0, max=99)])
    image = FileField('Product Image')

class CheckoutForm(FlaskForm):
    delivery_address = TextAreaField('Delivery Address', validators=[DataRequired(), Length(max=500)])
    delivery_phone = StringField('Contact Phone', validators=[DataRequired(), Length(max=20)])

class CartUpdateForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
