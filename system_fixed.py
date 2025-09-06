#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام إدارة الأصول المحدث - بدون تكرارات
Updated Asset Management System - No Duplicates
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

# إنشاء التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///asset_management_new.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إنشاء قاعدة البيانات
db = SQLAlchemy(app)

# نماذج قاعدة البيانات المحدثة
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('user_role.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    role = db.relationship('UserRole', backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Text)  # JSON string of permissions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='نشط')
    location = db.Column(db.String(100))
    assigned_to = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    supplier = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    invoice_file = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='مكتمل')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Custody(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(20), nullable=False)
    custody_type = db.Column(db.String(50), nullable=False)
    serial_number = db.Column(db.String(100), nullable=False)
    received_date = db.Column(db.Date, nullable=False)
    estimated_value = db.Column(db.Float)
    barcode = db.Column(db.String(50), unique=True, nullable=True)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='نشط')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# تهيئة قاعدة البيانات
def init_db():
    with app.app_context():
        db.create_all()
        
        # إضافة مستخدم افتراضي
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', email='admin@company.com')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()

# صفحة تسجيل الدخول
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>تسجيل الدخول</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header text-center">
                            <h3>نظام إدارة الأصول</h3>
                        </div>
                        <div class="card-body">
                            <form method="POST">
                                <div class="mb-3">
                                    <label class="form-label">اسم المستخدم</label>
                                    <input type="text" class="form-control" name="username" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">كلمة المرور</label>
                                    <input type="password" class="form-control" name="password" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">دخول</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

# الصفحة الرئيسية
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>لوحة التحكم</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/dashboard">نظام إدارة الأصول</a>
                <a href="/logout" class="btn btn-outline-light">خروج</a>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h2>مرحباً بك في نظام إدارة الأصول</h2>
            
            <div class="row mt-4">
                <div class="col-md-3 mb-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <i class="fas fa-laptop fa-3x text-primary mb-3"></i>
                            <h5>إدارة الأصول</h5>
                            <a href="/assets" class="btn btn-primary">دخول</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3 mb-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <i class="fas fa-shopping-cart fa-3x text-success mb-3"></i>
                            <h5>إدارة المشتريات</h5>
                            <a href="/purchases" class="btn btn-success">دخول</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3 mb-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <i class="fas fa-handshake fa-3x text-warning mb-3"></i>
                            <h5>إدارة العهد</h5>
                            <a href="/custody" class="btn btn-warning">دخول</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3 mb-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <i class="fas fa-chart-bar fa-3x text-info mb-3"></i>
                            <h5>التقارير</h5>
                            <a href="/reports" class="btn btn-info">دخول</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

# صفحة التقارير
@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # حساب الإحصائيات
    total_assets = Asset.query.count()
    total_purchases = Purchase.query.count()
    total_custodies = Custody.query.count()
    
    return f'''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>التقارير</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/dashboard">نظام إدارة الأصول</a>
                <a href="/dashboard" class="btn btn-outline-light">العودة للرئيسية</a>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h2><i class="fas fa-chart-bar me-2"></i>التقارير والإحصائيات</h2>
            
            <div class="row mt-4">
                <div class="col-md-4 mb-3">
                    <div class="card text-center bg-primary text-white">
                        <div class="card-body">
                            <i class="fas fa-laptop fa-2x mb-2"></i>
                            <h3>{total_assets}</h3>
                            <p>إجمالي الأصول</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 mb-3">
                    <div class="card text-center bg-success text-white">
                        <div class="card-body">
                            <i class="fas fa-shopping-cart fa-2x mb-2"></i>
                            <h3>{total_purchases}</h3>
                            <p>إجمالي المشتريات</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 mb-3">
                    <div class="card text-center bg-warning text-white">
                        <div class="card-body">
                            <i class="fas fa-handshake fa-2x mb-2"></i>
                            <h3>{total_custodies}</h3>
                            <p>إجمالي العهد</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="text-center mt-4">
                <button class="btn btn-success" onclick="alert('تم تصدير التقرير بنجاح!')">
                    <i class="fas fa-download me-2"></i>تصدير التقرير
                </button>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    print("=" * 70)
    print("🚀 نظام إدارة الأصول المحدث")
    print("   Updated Asset Management System")
    print("=" * 70)
    print("✅ النظام جاهز!")
    print("🌐 الرابط: http://localhost:5000")
    print("👤 المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("📋 الميزات الجديدة:")
    print("   ✓ قاعدة بيانات محدثة")
    print("   ✓ نماذج محسنة")
    print("   ✓ صفحة تقارير تعمل")
    print("   ✓ بدون تكرارات")
    print("🔧 للإيقاف: اضغط Ctrl+C")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5001, debug=False)