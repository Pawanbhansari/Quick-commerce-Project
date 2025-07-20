from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pickle
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps

# Import our existing models
import sys
sys.path.append('..')

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quickcart.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    icon = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, preparing, delivering, delivered
    total_amount = db.Column(db.Float, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_lat = db.Column(db.Float)
    delivery_lng = db.Column(db.Float)
    mfu_id = db.Column(db.Integer, db.ForeignKey('mfu.id'))
    estimated_delivery_time = db.Column(db.DateTime)
    actual_delivery_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product')

class MFU(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location_lat = db.Column(db.Float, nullable=False)
    location_lng = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, default=1000)  # items capacity
    current_load = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='available')  # available, busy, maintenance
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='mfu', lazy=True)

class DemandForecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    forecast_date = db.Column(db.Date, nullable=False)
    predicted_demand = db.Column(db.Float, nullable=False)
    confidence_interval_lower = db.Column(db.Float)
    confidence_interval_upper = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# JWT Token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400
    
    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        email=data['email'],
        password_hash=hashed_password,
        name=data['name'],
        address=data.get('address', ''),
        phone=data.get('phone', '')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    token = jwt.encode(
        {'user_id': new_user.id, 'email': new_user.email},
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return jsonify({
        'message': 'User registered successfully',
        'token': token,
        'user': {
            'id': new_user.id,
            'email': new_user.email,
            'name': new_user.name
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        token = jwt.encode(
            {'user_id': user.id, 'email': user.email},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        })
    
    return jsonify({'message': 'Invalid credentials'}), 401

# Product routes
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'category': p.category,
        'stock_quantity': p.stock_quantity,
        'image_url': p.image_url,
        'icon': p.icon
    } for p in products])

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'category': product.category,
        'stock_quantity': product.stock_quantity,
        'image_url': product.image_url,
        'icon': product.icon
    })

@app.route('/api/products/category/<category>', methods=['GET'])
def get_products_by_category(category):
    products = Product.query.filter_by(category=category, is_active=True).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'category': p.category,
        'stock_quantity': p.stock_quantity,
        'image_url': p.image_url,
        'icon': p.icon
    } for p in products])

# Order routes
@app.route('/api/orders', methods=['POST'])
@token_required
def create_order(current_user):
    data = request.get_json()
    
    # Calculate total amount
    total_amount = 0
    order_items = []
    
    for item in data['items']:
        product = Product.query.get(item['product_id'])
        if not product or product.stock_quantity < item['quantity']:
            return jsonify({'message': f'Insufficient stock for {product.name}'}), 400
        
        total_amount += product.price * item['quantity']
        order_items.append({
            'product': product,
            'quantity': item['quantity'],
            'price': product.price
        })
    
    # Create order
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        delivery_address=data['delivery_address'],
        delivery_lat=data.get('delivery_lat'),
        delivery_lng=data.get('delivery_lng'),
        estimated_delivery_time=datetime.utcnow() + timedelta(minutes=10)
    )
    
    db.session.add(new_order)
    db.session.flush()  # Get the order ID
    
    # Create order items and update stock
    for item_data in order_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data['product'].id,
            quantity=item_data['quantity'],
            price=item_data['price']
        )
        db.session.add(order_item)
        
        # Update stock
        item_data['product'].stock_quantity -= item_data['quantity']
    
    db.session.commit()
    
    # Assign MFU (simplified logic)
    available_mfu = MFU.query.filter_by(status='available').first()
    if available_mfu:
        new_order.mfu_id = available_mfu.id
        db.session.commit()
    
    return jsonify({
        'message': 'Order created successfully',
        'order_id': new_order.id,
        'estimated_delivery_time': new_order.estimated_delivery_time.isoformat()
    }), 201

@app.route('/api/orders', methods=['GET'])
@token_required
def get_user_orders(current_user):
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return jsonify([{
        'id': order.id,
        'status': order.status,
        'total_amount': order.total_amount,
        'delivery_address': order.delivery_address,
        'estimated_delivery_time': order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None,
        'actual_delivery_time': order.actual_delivery_time.isoformat() if order.actual_delivery_time else None,
        'created_at': order.created_at.isoformat(),
        'items': [{
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price': item.price
        } for item in order.order_items]
    } for order in orders])

@app.route('/api/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'id': order.id,
        'status': order.status,
        'total_amount': order.total_amount,
        'delivery_address': order.delivery_address,
        'estimated_delivery_time': order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None,
        'actual_delivery_time': order.actual_delivery_time.isoformat() if order.actual_delivery_time else None,
        'created_at': order.created_at.isoformat(),
        'mfu_id': order.mfu_id,
        'items': [{
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price': item.price
        } for item in order.order_items]
    })

# MFU routes
@app.route('/api/mfu', methods=['GET'])
def get_mfu_locations():
    mfus = MFU.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': mfu.id,
        'name': mfu.name,
        'location_lat': mfu.location_lat,
        'location_lng': mfu.location_lng,
        'capacity': mfu.capacity,
        'current_load': mfu.current_load,
        'status': mfu.status
    } for mfu in mfus])

@app.route('/api/mfu/<int:mfu_id>/orders', methods=['GET'])
def get_mfu_orders(mfu_id):
    orders = Order.query.filter_by(mfu_id=mfu_id).order_by(Order.created_at.desc()).all()
    return jsonify([{
        'id': order.id,
        'status': order.status,
        'delivery_address': order.delivery_address,
        'delivery_lat': order.delivery_lat,
        'delivery_lng': order.delivery_lng,
        'estimated_delivery_time': order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None,
        'created_at': order.created_at.isoformat()
    } for order in orders])

# Demand forecasting routes
@app.route('/api/forecast/product/<int:product_id>', methods=['GET'])
def get_product_forecast(product_id):
    # Get forecast for next 7 days
    today = datetime.now().date()
    forecasts = DemandForecast.query.filter(
        DemandForecast.product_id == product_id,
        DemandForecast.forecast_date >= today
    ).order_by(DemandForecast.forecast_date).limit(7).all()
    
    return jsonify([{
        'date': forecast.forecast_date.isoformat(),
        'predicted_demand': forecast.predicted_demand,
        'confidence_interval_lower': forecast.confidence_interval_lower,
        'confidence_interval_upper': forecast.confidence_interval_upper
    } for forecast in forecasts])

@app.route('/api/forecast/category/<category>', methods=['GET'])
def get_category_forecast(category):
    # Get forecast for products in category
    products = Product.query.filter_by(category=category).all()
    product_ids = [p.id for p in products]
    
    today = datetime.now().date()
    forecasts = DemandForecast.query.filter(
        DemandForecast.product_id.in_(product_ids),
        DemandForecast.forecast_date >= today
    ).order_by(DemandForecast.forecast_date).limit(7).all()
    
    # Group by date
    forecast_by_date = {}
    for forecast in forecasts:
        date_str = forecast.forecast_date.isoformat()
        if date_str not in forecast_by_date:
            forecast_by_date[date_str] = {
                'date': date_str,
                'total_demand': 0,
                'product_count': 0
            }
        forecast_by_date[date_str]['total_demand'] += forecast.predicted_demand
        forecast_by_date[date_str]['product_count'] += 1
    
    return jsonify(list(forecast_by_date.values()))

# Analytics routes
@app.route('/api/analytics/sales', methods=['GET'])
def get_sales_analytics():
    # Get sales data for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    orders = Order.query.filter(Order.created_at >= thirty_days_ago).all()
    
    # Group by date
    sales_by_date = {}
    for order in orders:
        date_str = order.created_at.date().isoformat()
        if date_str not in sales_by_date:
            sales_by_date[date_str] = {
                'date': date_str,
                'total_sales': 0,
                'order_count': 0
            }
        sales_by_date[date_str]['total_sales'] += order.total_amount
        sales_by_date[date_str]['order_count'] += 1
    
    return jsonify(list(sales_by_date.values()))

@app.route('/api/analytics/products', methods=['GET'])
def get_product_analytics():
    # Get top selling products
    order_items = db.session.query(
        OrderItem.product_id,
        Product.name,
        db.func.sum(OrderItem.quantity).label('total_quantity'),
        db.func.sum(OrderItem.quantity * OrderItem.price).label('total_revenue')
    ).join(Product).group_by(OrderItem.product_id, Product.name).order_by(
        db.func.sum(OrderItem.quantity).desc()
    ).limit(10).all()
    
    return jsonify([{
        'product_id': item.product_id,
        'product_name': item.product_name,
        'total_quantity': int(item.total_quantity),
        'total_revenue': float(item.total_revenue)
    } for item in order_items])

# Search route
@app.route('/api/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    products = Product.query.filter(
        db.or_(
            Product.name.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%'),
            Product.category.ilike(f'%{query}%')
        ),
        Product.is_active == True
    ).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'category': p.category,
        'stock_quantity': p.stock_quantity,
        'image_url': p.image_url,
        'icon': p.icon
    } for p in products])

# Initialize database with sample data
def init_db():
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if Product.query.first():
            return
        
        # Add sample products
        sample_products = [
            {
                'name': 'Organic Bananas',
                'description': 'Fresh organic bananas, perfect for smoothies',
                'price': 2.99,
                'category': 'Fruits & Vegetables',
                'stock_quantity': 100,
                'icon': 'fas fa-apple-alt'
            },
            {
                'name': 'Whole Grain Bread',
                'description': 'Freshly baked whole grain bread',
                'price': 3.49,
                'category': 'Bakery & Bread',
                'stock_quantity': 50,
                'icon': 'fas fa-bread-slice'
            },
            {
                'name': 'Farm Fresh Eggs',
                'description': 'Farm fresh organic eggs, 12 count',
                'price': 4.99,
                'category': 'Dairy & Eggs',
                'stock_quantity': 75,
                'icon': 'fas fa-egg'
            },
            {
                'name': 'Chicken Breast',
                'description': 'Premium boneless chicken breast',
                'price': 8.99,
                'category': 'Meat & Fish',
                'stock_quantity': 30,
                'icon': 'fas fa-drumstick-bite'
            },
            {
                'name': 'Sparkling Water',
                'description': 'Refreshing sparkling water',
                'price': 1.99,
                'category': 'Beverages',
                'stock_quantity': 200,
                'icon': 'fas fa-wine-bottle'
            },
            {
                'name': 'Dark Chocolate',
                'description': 'Premium dark chocolate bar',
                'price': 3.99,
                'category': 'Snacks',
                'stock_quantity': 80,
                'icon': 'fas fa-cookie-bite'
            },
            {
                'name': 'Vitamin C Supplements',
                'description': 'High-potency vitamin C supplements',
                'price': 12.99,
                'category': 'Health & Beauty',
                'stock_quantity': 60,
                'icon': 'fas fa-pills'
            },
            {
                'name': 'Baby Formula',
                'description': 'Premium baby formula, stage 1',
                'price': 24.99,
                'category': 'Baby Care',
                'stock_quantity': 40,
                'icon': 'fas fa-baby'
            }
        ]
        
        for product_data in sample_products:
            product = Product(**product_data)
            db.session.add(product)
        
        # Add sample MFUs
        sample_mfus = [
            {
                'name': 'MFU Central Park',
                'location_lat': 40.7829,
                'location_lng': -73.9654,
                'capacity': 1000,
                'status': 'available'
            },
            {
                'name': 'MFU Times Square',
                'location_lat': 40.7580,
                'location_lng': -73.9855,
                'capacity': 1000,
                'status': 'available'
            },
            {
                'name': 'MFU Brooklyn Bridge',
                'location_lat': 40.7061,
                'location_lng': -73.9969,
                'capacity': 1000,
                'status': 'available'
            }
        ]
        
        for mfu_data in sample_mfus:
            mfu = MFU(**mfu_data)
            db.session.add(mfu)
        
        db.session.commit()
        print("Database initialized with sample data!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000) 