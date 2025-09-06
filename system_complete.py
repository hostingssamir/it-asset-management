#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام إدارة الأصول الاحترافي - نسخة مستقرة
Professional Asset Management System - Stable Version
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import shutil
import json

# إنشاء التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///asset_management_complete.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إنشاء قاعدة البيانات
db = SQLAlchemy(app)

# نماذج قاعدة البيانات
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, manager, user
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_manager(self):
        return self.role in ['admin', 'manager']

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

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    supplier_name = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), nullable=False)
    due_date = db.Column(db.Date)
    invoice_file = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# قالب تسجيل الدخول
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Cairo', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
        }
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            border-radius: 25px 25px 0 0;
        }
        .btn-login {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 15px;
            padding: 1rem 2rem;
            font-size: 1.2rem;
            font-weight: 600;
            color: white;
            transition: all 0.3s ease;
        }
        .btn-login:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
            color: white;
        }
        .form-control {
            border-radius: 15px;
            border: 2px solid #e9ecef;
            padding: 1rem 1.5rem;
            font-size: 1.1rem;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-5 col-md-7">
                <div class="login-card">
                    <div class="login-header">
                        <div style="font-size: 4rem; margin-bottom: 1rem;">
                            <i class="fas fa-building"></i>
                        </div>
                        <h2 class="mb-0">نظام إدارة الأصول</h2>
                        <p class="mb-0 mt-2">مرحباً بك في النظام الاحترافي</p>
                    </div>
                    
                    <div class="card-body p-5">
                        {% with messages = get_flashed_messages() %}
                            {% if messages %}
                                {% for message in messages %}
                                    <div class="alert alert-danger">{{ message }}</div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST">
                            <div class="mb-3">
                                <input type="text" class="form-control" name="username" 
                                       placeholder="اسم المستخدم" required>
                            </div>
                            
                            <div class="mb-3">
                                <input type="password" class="form-control" name="password" 
                                       placeholder="كلمة المرور" required>
                            </div>
                            
                            <button type="submit" class="btn btn-login w-100 mb-3">
                                <i class="fas fa-sign-in-alt me-2"></i>
                                دخول النظام
                            </button>
                        </form>
                        
                        <div class="text-center text-muted">
                            <small>
                                <i class="fas fa-shield-alt me-1"></i>
                                نظام آمن ومحمي
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

# قالب الصفحة الرئيسية
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        .welcome-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 20px;
            padding: 3rem;
            margin-bottom: 3rem;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        }
        .module-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border: none;
            text-align: center;
        }
        .module-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }
        .module-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .btn-module {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 15px;
            padding: 0.8rem 2rem;
            color: white;
            font-weight: 600;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .btn-module:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
            color: white;
        }
        .stats-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
        }
        .stats-card:hover {
            transform: translateY(-5px);
        }
        .stats-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #667eea;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-building me-2"></i>
                نظام إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>
                    خروج
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="welcome-card">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1 class="mb-3">
                        <i class="fas fa-hand-wave me-2"></i>
                        مرحباً بك، {{ username }}
                    </h1>
                    <p class="lead mb-0">
                        مرحباً بك في نظام إدارة الأصول الاحترافي. يمكنك من هنا إدارة جميع أصول الشركة بكفاءة عالية.
                    </p>
                </div>
                <div class="col-md-4 text-center">
                    <i class="fas fa-chart-line" style="font-size: 5rem; opacity: 0.3;"></i>
                </div>
            </div>
        </div>
        
        <!-- إحصائيات سريعة -->
        <div class="row mb-4">
            <div class="col-md-3 mb-3">
                <div class="stats-card">
                    <i class="fas fa-laptop text-primary" style="font-size: 2rem;"></i>
                    <div class="stats-number">{{ total_assets }}</div>
                    <div class="stats-label">إجمالي الأصول</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="stats-card">
                    <i class="fas fa-shopping-cart text-success" style="font-size: 2rem;"></i>
                    <div class="stats-number">{{ total_purchases }}</div>
                    <div class="stats-label">المشتريات</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="stats-card">
                    <i class="fas fa-handshake text-warning" style="font-size: 2rem;"></i>
                    <div class="stats-number">{{ total_custodies }}</div>
                    <div class="stats-label">العهد</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="stats-card">
                    <i class="fas fa-file-invoice text-info" style="font-size: 2rem;"></i>
                    <div class="stats-number">{{ total_invoices }}</div>
                    <div class="stats-label">الفواتير</div>
                </div>
            </div>
        </div>
        
        <!-- وحدات النظام -->
        <div class="row">
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-laptop"></i>
                    </div>
                    <h5>إدارة الأصول</h5>
                    <p>إدارة شاملة لجميع أصول الشركة مع تتبع الحالة والموقع</p>
                    <a href="/assets" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-shopping-cart"></i>
                    </div>
                    <h5>إدارة المشتريات</h5>
                    <p>تتبع المشتريات والموردين مع إرفاق الفواتير</p>
                    <a href="/purchases" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-handshake"></i>
                    </div>
                    <h5>إدارة العهد</h5>
                    <p>إدارة عهد الموظفين مع طباعة الباركود</p>
                    <a href="/custody" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-file-invoice"></i>
                    </div>
                    <h5>إدارة الفواتير</h5>
                    <p>إدارة الفواتير والمدفوعات مع إرفاق الملفات</p>
                    <a href="/invoices" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-chart-bar"></i>
                    </div>
                    <h5>التقارير</h5>
                    <p>تقارير شاملة وإحصائيات تفصيلية</p>
                    <a href="/reports" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
            
            {% if current_user and current_user.is_admin() %}
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-users-cog"></i>
                    </div>
                    <h5>إدارة المستخدمين</h5>
                    <p>إدارة المستخدمين والصلاحيات</p>
                    <a href="/users" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-database"></i>
                    </div>
                    <h5>إدارة قواعد البيانات</h5>
                    <p>نسخ احتياطية واستعادة البيانات</p>
                    <a href="/database" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
            {% endif %}
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card">
                    <div class="module-icon">
                        <i class="fas fa-cog"></i>
                    </div>
                    <h5>الإعدادات</h5>
                    <p>إعدادات النظام والمستخدمين</p>
                    <a href="/settings" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

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
    
    return render_template_string(LOGIN_TEMPLATE)

# الصفحة الرئيسية
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # الحصول على المستخدم الحالي
    current_user = User.query.get(session['user_id'])
    
    # حساب الإحصائيات
    total_assets = Asset.query.count()
    total_purchases = Purchase.query.count()
    total_custodies = Custody.query.count()
    total_invoices = Invoice.query.count()
    
    return render_template_string(DASHBOARD_TEMPLATE, 
        username=session.get('username', 'المستخدم'),
        current_user=current_user,
        total_assets=total_assets,
        total_purchases=total_purchases,
        total_custodies=total_custodies,
        total_invoices=total_invoices
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# صفحات بسيطة للوحدات الأخرى
@app.route('/assets')
def assets():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    assets = Asset.query.all()
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة الأصول - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        .table {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }
        .table thead th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
            padding: 1rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-building me-2"></i>
                نظام إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/dashboard">
                    <i class="fas fa-home me-1"></i>
                    الرئيسية
                </a>
                <a class="nav-link text-white" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>
                    خروج
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="main-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-laptop me-2 text-primary"></i>إدارة الأصول</h2>
                <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                    <i class="fas fa-plus me-2"></i>إضافة أصل جديد
                </button>
            </div>
            
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th><i class="fas fa-hashtag me-2"></i>الرقم</th>
                            <th><i class="fas fa-laptop me-2"></i>اسم الأصل</th>
                            <th><i class="fas fa-tags me-2"></i>الفئة</th>
                            <th><i class="fas fa-barcode me-2"></i>الرقم التسلسلي</th>
                            <th><i class="fas fa-calendar me-2"></i>تاريخ الشراء</th>
                            <th><i class="fas fa-dollar-sign me-2"></i>السعر</th>
                            <th><i class="fas fa-info-circle me-2"></i>الحالة</th>
                            <th><i class="fas fa-cogs me-2"></i>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for asset in assets %}
                        <tr>
                            <td>{{ asset.id }}</td>
                            <td><strong>{{ asset.name }}</strong></td>
                            <td>{{ asset.category }}</td>
                            <td>{{ asset.serial_number }}</td>
                            <td>{{ asset.purchase_date.strftime('%Y-%m-%d') }}</td>
                            <td>{{ asset.purchase_price }} ريال</td>
                            <td>
                                <span class="badge bg-{{ 'success' if asset.status == 'نشط' else 'warning' }}">
                                    {{ asset.status }}
                                </span>
                            </td>
                            <td>
                                <div class="btn-group" role="group">
                                    <button class="btn btn-sm btn-outline-primary" title="عرض" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-success" title="تعديل" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" title="حذف" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="8" class="text-center">لا توجد أصول مسجلة</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
    ''', assets=assets)

@app.route('/purchases')
def purchases():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    purchases = Purchase.query.all()
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة المشتريات - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        .table {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }
        .table thead th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
            padding: 1rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-building me-2"></i>
                نظام إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/dashboard">
                    <i class="fas fa-home me-1"></i>
                    الرئيسية
                </a>
                <a class="nav-link text-white" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>
                    خروج
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="main-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-shopping-cart me-2 text-primary"></i>إدارة المشتريات</h2>
                <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                    <i class="fas fa-plus me-2"></i>إضافة مشترى جديد
                </button>
            </div>
            
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th><i class="fas fa-hashtag me-2"></i>الرقم</th>
                            <th><i class="fas fa-box me-2"></i>اسم المنتج</th>
                            <th><i class="fas fa-store me-2"></i>المورد</th>
                            <th><i class="fas fa-sort-numeric-up me-2"></i>الكمية</th>
                            <th><i class="fas fa-dollar-sign me-2"></i>السعر الإجمالي</th>
                            <th><i class="fas fa-calendar me-2"></i>تاريخ الشراء</th>
                            <th><i class="fas fa-info-circle me-2"></i>الحالة</th>
                            <th><i class="fas fa-cogs me-2"></i>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for purchase in purchases %}
                        <tr>
                            <td>{{ purchase.id }}</td>
                            <td><strong>{{ purchase.product_name }}</strong></td>
                            <td>{{ purchase.supplier }}</td>
                            <td>{{ purchase.quantity }}</td>
                            <td>{{ purchase.total_price }} ريال</td>
                            <td>{{ purchase.purchase_date.strftime('%Y-%m-%d') }}</td>
                            <td>
                                <span class="badge bg-{{ 'success' if purchase.status == 'مكتمل' else 'warning' }}">
                                    {{ purchase.status }}
                                </span>
                            </td>
                            <td>
                                <div class="btn-group" role="group">
                                    <button class="btn btn-sm btn-outline-primary" title="عرض" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-success" title="تعديل" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" title="حذف" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="8" class="text-center">لا توجد مشتريات مسجلة</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
    ''', purchases=purchases)

@app.route('/custody')
def custody():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    custodies = Custody.query.all()
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة العهد - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        .table {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }
        .table thead th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
            padding: 1rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-building me-2"></i>
                نظام إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/dashboard">
                    <i class="fas fa-home me-1"></i>
                    الرئيسية
                </a>
                <a class="nav-link text-white" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>
                    خروج
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="main-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-handshake me-2 text-primary"></i>إدارة العهد</h2>
                <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                    <i class="fas fa-plus me-2"></i>إضافة عهدة جديدة
                </button>
            </div>
            
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th><i class="fas fa-hashtag me-2"></i>الرقم</th>
                            <th><i class="fas fa-user me-2"></i>اسم الموظف</th>
                            <th><i class="fas fa-id-card me-2"></i>رقم الموظف</th>
                            <th><i class="fas fa-tags me-2"></i>نوع العهدة</th>
                            <th><i class="fas fa-barcode me-2"></i>الرقم التسلسلي</th>
                            <th><i class="fas fa-calendar me-2"></i>تاريخ الاستلام</th>
                            <th><i class="fas fa-dollar-sign me-2"></i>القيمة التقديرية</th>
                            <th><i class="fas fa-info-circle me-2"></i>الحالة</th>
                            <th><i class="fas fa-cogs me-2"></i>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for custody in custodies %}
                        <tr>
                            <td>{{ custody.id }}</td>
                            <td><strong>{{ custody.employee_name }}</strong></td>
                            <td>{{ custody.employee_id }}</td>
                            <td>{{ custody.custody_type }}</td>
                            <td>{{ custody.serial_number }}</td>
                            <td>{{ custody.received_date.strftime('%Y-%m-%d') }}</td>
                            <td>{{ custody.estimated_value or 'غير محدد' }} ريال</td>
                            <td>
                                <span class="badge bg-{{ 'success' if custody.status == 'نشط' else 'warning' }}">
                                    {{ custody.status }}
                                </span>
                            </td>
                            <td>
                                <div class="btn-group" role="group">
                                    <button class="btn btn-sm btn-outline-primary" title="عرض" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-success" title="تعديل" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" title="حذف" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="9" class="text-center">لا توجد عهد مسجلة</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
    ''', custodies=custodies)

@app.route('/invoices')
def invoices():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    invoices = Invoice.query.all()
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة الفواتير - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        .table {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }
        .table thead th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
            padding: 1rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-building me-2"></i>
                نظام إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/dashboard">
                    <i class="fas fa-home me-1"></i>
                    الرئيسية
                </a>
                <a class="nav-link text-white" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>
                    خروج
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="main-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-file-invoice me-2 text-primary"></i>إدارة الفواتير</h2>
                <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                    <i class="fas fa-plus me-2"></i>إضافة فاتورة جديدة
                </button>
            </div>
            
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th><i class="fas fa-hashtag me-2"></i>الرقم</th>
                            <th><i class="fas fa-file-invoice me-2"></i>رقم الفاتورة</th>
                            <th><i class="fas fa-calendar me-2"></i>تاريخ الفاتورة</th>
                            <th><i class="fas fa-store me-2"></i>اسم المورد</th>
                            <th><i class="fas fa-dollar-sign me-2"></i>المبلغ الإجمالي</th>
                            <th><i class="fas fa-credit-card me-2"></i>حالة الدفع</th>
                            <th><i class="fas fa-calendar-check me-2"></i>تاريخ الاستحقاق</th>
                            <th><i class="fas fa-cogs me-2"></i>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for invoice in invoices %}
                        <tr>
                            <td>{{ invoice.id }}</td>
                            <td><strong>{{ invoice.invoice_number }}</strong></td>
                            <td>{{ invoice.invoice_date.strftime('%Y-%m-%d') }}</td>
                            <td>{{ invoice.supplier_name }}</td>
                            <td>{{ invoice.total_amount }} ريال</td>
                            <td>
                                <span class="badge bg-{{ 'success' if invoice.payment_status == 'مدفوع' else 'warning' if invoice.payment_status == 'جزئي' else 'danger' }}">
                                    {{ invoice.payment_status }}
                                </span>
                            </td>
                            <td>{{ invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else 'غير محدد' }}</td>
                            <td>
                                <div class="btn-group" role="group">
                                    <button class="btn btn-sm btn-outline-primary" title="عرض" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-success" title="تعديل" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" title="حذف" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="8" class="text-center">لا توجد فواتير مسجلة</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
    ''', invoices=invoices)

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>التقارير - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .report-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            border: 2px solid #e9ecef;
            text-align: center;
            transition: all 0.3s ease;
        }
        .report-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.8rem 2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-building me-2"></i>
                نظام إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/dashboard">
                    <i class="fas fa-home me-1"></i>
                    الرئيسية
                </a>
                <a class="nav-link text-white" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>
                    خروج
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="main-card">
            <h2 class="text-center mb-4">
                <i class="fas fa-chart-bar me-2 text-primary"></i>
                التقارير والإحصائيات
            </h2>
            
            <div class="row">
                <div class="col-md-4 mb-3">
                    <div class="report-card">
                        <i class="fas fa-laptop fa-3x text-primary mb-3"></i>
                        <h5>تقرير الأصول</h5>
                        <p>تقرير شامل بجميع الأصول والحالة</p>
                        <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                            <i class="fas fa-download me-2"></i>تحميل التقرير
                        </button>
                    </div>
                </div>
                
                <div class="col-md-4 mb-3">
                    <div class="report-card">
                        <i class="fas fa-shopping-cart fa-3x text-success mb-3"></i>
                        <h5>تقرير المشتريات</h5>
                        <p>تقرير بجميع المشتريات والموردين</p>
                        <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                            <i class="fas fa-download me-2"></i>تحميل التقرير
                        </button>
                    </div>
                </div>
                
                <div class="col-md-4 mb-3">
                    <div class="report-card">
                        <i class="fas fa-handshake fa-3x text-warning mb-3"></i>
                        <h5>تقرير العهد</h5>
                        <p>تقرير بجميع العهد والموظفين</p>
                        <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                            <i class="fas fa-download me-2"></i>تحميل التقرير
                        </button>
                    </div>
                </div>
                
                <div class="col-md-4 mb-3">
                    <div class="report-card">
                        <i class="fas fa-file-invoice fa-3x text-info mb-3"></i>
                        <h5>تقرير الفواتير</h5>
                        <p>تقرير بجميع الفواتير والمدفوعات</p>
                        <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                            <i class="fas fa-download me-2"></i>تحميل التقرير
                        </button>
                    </div>
                </div>
                
                <div class="col-md-4 mb-3">
                    <div class="report-card">
                        <i class="fas fa-chart-pie fa-3x text-danger mb-3"></i>
                        <h5>التقرير المالي</h5>
                        <p>تقرير مالي شامل بالإحصائيات</p>
                        <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                            <i class="fas fa-download me-2"></i>تحميل التقرير
                        </button>
                    </div>
                </div>
                
                <div class="col-md-4 mb-3">
                    <div class="report-card">
                        <i class="fas fa-calendar fa-3x text-secondary mb-3"></i>
                        <h5>التقرير الشهري</h5>
                        <p>تقرير شهري بجميع الأنشطة</p>
                        <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                            <i class="fas fa-download me-2"></i>تحميل التقرير
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>الإعدادات - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .setting-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }
        .setting-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.8rem 2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-building me-2"></i>
                نظام إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/dashboard">
                    <i class="fas fa-home me-1"></i>
                    الرئيسية
                </a>
                <a class="nav-link text-white" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>
                    خروج
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="main-card">
            <h2 class="text-center mb-4">
                <i class="fas fa-cog me-2 text-primary"></i>
                إعدادات النظام
            </h2>
            
            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="setting-card">
                        <h5><i class="fas fa-user me-2"></i>إعدادات الملف الشخصي</h5>
                        <p>تغيير كلمة المرور والبيانات الشخصية</p>
                        <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                            <i class="fas fa-edit me-2"></i>تعديل الملف الشخصي
                        </button>
                    </div>
                </div>
                
                <div class="col-md-6 mb-3">
                    <div class="setting-card">
                        <h5><i class="fas fa-bell me-2"></i>إعدادات الإشعارات</h5>
                        <p>تخصيص الإشعارات والتنبيهات</p>
                        <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                            <i class="fas fa-cog me-2"></i>إدارة الإشعارات
                        </button>
                    </div>
                </div>
                
                <div class="col-md-6 mb-3">
                    <div class="setting-card">
                        <h5><i class="fas fa-palette me-2"></i>إعدادات المظهر</h5>
                        <p>تخصيص ألوان ومظهر النظام</p>
                        <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                            <i class="fas fa-paint-brush me-2"></i>تخصيص المظهر
                        </button>
                    </div>
                </div>
                
                <div class="col-md-6 mb-3">
                    <div class="setting-card">
                        <h5><i class="fas fa-shield-alt me-2"></i>إعدادات الأمان</h5>
                        <p>إعدادات الأمان والخصوصية</p>
                        <button class="btn btn-primary" onclick="alert('سيتم إضافة هذه الوظيفة قريباً')">
                            <i class="fas fa-lock me-2"></i>إدارة الأمان
                        </button>
                    </div>
                </div>
                
                <div class="col-md-6 mb-3">
                    <div class="setting-card">
                        <h5><i class="fas fa-download me-2"></i>النسخ الاحتياطية</h5>
                        <p>إدارة النسخ الاحتياطية للبيانات</p>
                        <a href="/database" class="btn btn-primary">
                            <i class="fas fa-database me-2"></i>إدارة النسخ الاحتياطية
                        </a>
                    </div>
                </div>
                
                <div class="col-md-6 mb-3">
                    <div class="setting-card">
                        <h5><i class="fas fa-info-circle me-2"></i>معلومات النظام</h5>
                        <p>معلومات حول النظام والإصدار</p>
                        <button class="btn btn-primary" onclick="alert('نظام إدارة الأصول - الإصدار 1.0\\nتم التطوير بواسطة فريق التطوير')">
                            <i class="fas fa-info me-2"></i>عرض المعلومات
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    ''')

# إدارة المستخدمين
@app.route('/users')
def users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = User.query.get(session['user_id'])
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة المستخدمين - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        .table {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }
        .table thead th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
            padding: 1rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-building me-2"></i>
                نظام إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/dashboard">
                    <i class="fas fa-home me-1"></i>
                    الرئيسية
                </a>
                <a class="nav-link text-white" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>
                    خروج
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="main-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-users-cog me-2 text-primary"></i>إدارة المستخدمين</h2>
                <a href="/add_user" class="btn btn-primary">
                    <i class="fas fa-user-plus me-2"></i>إضافة مستخدم جديد
                </a>
            </div>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th><i class="fas fa-user me-2"></i>اسم المستخدم</th>
                            <th><i class="fas fa-envelope me-2"></i>البريد الإلكتروني</th>
                            <th><i class="fas fa-user-tag me-2"></i>الدور</th>
                            <th><i class="fas fa-calendar me-2"></i>تاريخ الإنشاء</th>
                            <th><i class="fas fa-info-circle me-2"></i>الحالة</th>
                            <th><i class="fas fa-cogs me-2"></i>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user in users %}
                        <tr>
                            <td><strong>{{ user.username }}</strong></td>
                            <td>{{ user.email }}</td>
                            <td>
                                <span class="badge bg-{{ 'danger' if user.role == 'admin' else 'info' if user.role == 'manager' else 'secondary' }}">
                                    {{ 'مدير النظام' if user.role == 'admin' else 'مدير' if user.role == 'manager' else 'مستخدم' }}
                                </span>
                            </td>
                            <td>{{ user.created_at.strftime('%Y-%m-%d') }}</td>
                            <td>
                                <span class="badge bg-{{ 'success' if user.is_active else 'danger' }}">
                                    {{ 'نشط' if user.is_active else 'غير نشط' }}
                                </span>
                            </td>
                            <td>
                                <div class="btn-group" role="group">
                                    <button class="btn btn-sm btn-outline-{{ 'danger' if user.is_active else 'success' }}" 
                                            onclick="toggleUser({{ user.id }})" title="{{ 'إلغاء تفعيل' if user.is_active else 'تفعيل' }}">
                                        <i class="fas fa-{{ 'ban' if user.is_active else 'check' }}"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        function toggleUser(id) {
            Swal.fire({
                title: 'تغيير حالة المستخدم؟',
                text: "هل تريد تغيير حالة تفعيل هذا المستخدم؟",
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#28a745',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'نعم، غير الحالة!',
                cancelButtonText: 'إلغاء'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch('/toggle_user/' + id, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire('تم التغيير!', 'تم تغيير حالة المستخدم بنجاح.', 'success')
                            .then(() => location.reload());
                        } else {
                            Swal.fire('خطأ!', 'حدث خطأ أثناء التغيير.', 'error');
                        }
                    });
                }
            });
        }
    </script>
</body>
</html>
    ''', users=users)

# إضافة مستخدم جديد
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = User.query.get(session['user_id'])
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            user = User(
                username=request.form['username'],
                email=request.form['email'],
                role=request.form['role'],
                is_active=True
            )
            user.set_password(request.form['password'])
            db.session.add(user)
            db.session.commit()
            flash('تم إضافة المستخدم بنجاح!', 'success')
            return redirect(url_for('users'))
        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة المستخدم: {str(e)}', 'error')
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إضافة مستخدم جديد - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            margin: 2rem auto;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            max-width: 600px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 15px;
            padding: 0.8rem 2rem;
            font-weight: 600;
        }
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.8rem 1rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-building me-2"></i>
                نظام إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/users">
                    <i class="fas fa-arrow-left me-1"></i>
                    العودة للمستخدمين
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="main-card">
            <h2 class="text-center mb-4">
                <i class="fas fa-user-plus me-2 text-primary"></i>
                إضافة مستخدم جديد
            </h2>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label">
                        <i class="fas fa-user me-2"></i>اسم المستخدم
                    </label>
                    <input type="text" class="form-control" name="username" required>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">
                        <i class="fas fa-envelope me-2"></i>البريد الإلكتروني
                    </label>
                    <input type="email" class="form-control" name="email" required>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">
                        <i class="fas fa-lock me-2"></i>كلمة المرور
                    </label>
                    <input type="password" class="form-control" name="password" required>
                </div>
                
                <div class="mb-4">
                    <label class="form-label">
                        <i class="fas fa-user-tag me-2"></i>الدور
                    </label>
                    <select class="form-select" name="role" required>
                        <option value="">اختر الدور</option>
                        <option value="admin">مدير النظام</option>
                        <option value="manager">مدير</option>
                        <option value="user">مستخدم</option>
                    </select>
                </div>
                
                <div class="text-center">
                    <button type="submit" class="btn btn-primary btn-lg px-5 me-3">
                        <i class="fas fa-save me-2"></i>إضافة المستخدم
                    </button>
                    <a href="/users" class="btn btn-secondary btn-lg px-5">
                        <i class="fas fa-arrow-left me-2"></i>العودة
                    </a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
    ''')

# تفعيل/إلغاء تفعيل المستخدم
@app.route('/toggle_user/<int:user_id>', methods=['POST'])
def toggle_user(user_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'غير مسجل دخول'})
    
    current_user = User.query.get(session['user_id'])
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'ليس لديك صلاحية'})
    
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# إدارة قواعد البيانات
@app.route('/database')
def database():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = User.query.get(session['user_id'])
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة قواعد البيانات - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .action-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            border: 2px solid #e9ecef;
            text-align: center;
            transition: all 0.3s ease;
        }
        .action-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.8rem 2rem;
            font-weight: 600;
        }
        .btn-success {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            border: none;
            border-radius: 10px;
            padding: 0.8rem 2rem;
            font-weight: 600;
        }
        .btn-warning {
            background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
            border: none;
            border-radius: 10px;
            padding: 0.8rem 2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-building me-2"></i>
                نظام إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/dashboard">
                    <i class="fas fa-home me-1"></i>
                    الرئيسية
                </a>
                <a class="nav-link text-white" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>
                    خروج
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="main-card">
            <h2 class="text-center mb-4">
                <i class="fas fa-database me-2 text-primary"></i>
                إدارة قواعد البيانات
            </h2>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="row">
                <div class="col-md-4 mb-3">
                    <div class="action-card">
                        <i class="fas fa-download fa-3x text-success mb-3"></i>
                        <h5>تحميل نسخة احتياطية</h5>
                        <p>تحميل نسخة احتياطية من قاعدة البيانات</p>
                        <button class="btn btn-success" onclick="downloadBackup()">
                            <i class="fas fa-download me-2"></i>تحميل
                        </button>
                    </div>
                </div>
                
                <div class="col-md-4 mb-3">
                    <div class="action-card">
                        <i class="fas fa-upload fa-3x text-primary mb-3"></i>
                        <h5>استعادة نسخة احتياطية</h5>
                        <p>استعادة البيانات من نسخة احتياطية</p>
                        <form id="restoreForm" enctype="multipart/form-data">
                            <input type="file" class="form-control mb-2" id="backupFile" accept=".db">
                            <button type="button" class="btn btn-primary" onclick="restoreBackup()">
                                <i class="fas fa-upload me-2"></i>استعادة
                            </button>
                        </form>
                    </div>
                </div>
                
                <div class="col-md-4 mb-3">
                    <div class="action-card">
                        <i class="fas fa-trash fa-3x text-warning mb-3"></i>
                        <h5>إعادة تعيين قاعدة البيانات</h5>
                        <p>حذف جميع البيانات وإعادة التهيئة</p>
                        <button class="btn btn-warning" onclick="resetDatabase()">
                            <i class="fas fa-exclamation-triangle me-2"></i>إعادة تعيين
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="action-card">
                        <h5><i class="fas fa-info-circle me-2"></i>معلومات قاعدة البيانات</h5>
                        <div class="row text-start">
                            <div class="col-md-3">
                                <strong>عدد الأصول:</strong> {{ total_assets }}
                            </div>
                            <div class="col-md-3">
                                <strong>عدد المشتريات:</strong> {{ total_purchases }}
                            </div>
                            <div class="col-md-3">
                                <strong>عدد العهد:</strong> {{ total_custodies }}
                            </div>
                            <div class="col-md-3">
                                <strong>عدد الفواتير:</strong> {{ total_invoices }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function downloadBackup() {
            window.location.href = '/download_backup';
        }
        
        function restoreBackup() {
            const fileInput = document.getElementById('backupFile');
            if (!fileInput.files[0]) {
                Swal.fire('خطأ!', 'يرجى اختيار ملف النسخة الاحتياطية', 'error');
                return;
            }
            
            Swal.fire({
                title: 'استعادة النسخة الاحتياطية؟',
                text: "تحذير: سيتم استبدال جميع البيانات الحالية!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'نعم، استعد!',
                cancelButtonText: 'إلغاء'
            }).then((result) => {
                if (result.isConfirmed) {
                    const formData = new FormData();
                    formData.append('backup_file', fileInput.files[0]);
                    
                    fetch('/restore_backup', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire('تم!', 'تم استعادة النسخة الاحتياطية بنجاح.', 'success')
                            .then(() => location.reload());
                        } else {
                            Swal.fire('خطأ!', data.message, 'error');
                        }
                    });
                }
            });
        }
        
        function resetDatabase() {
            Swal.fire({
                title: 'إعادة تعيين قاعدة البيانات؟',
                text: "تحذير: سيتم حذف جميع البيانات نهائياً!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'نعم، احذف كل شيء!',
                cancelButtonText: 'إلغاء'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch('/reset_database', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire('تم!', 'تم إعادة تعيين قاعدة البيانات بنجاح.', 'success')
                            .then(() => location.reload());
                        } else {
                            Swal.fire('خطأ!', data.message, 'error');
                        }
                    });
                }
            });
        }
    </script>
</body>
</html>
    ''', 
    total_assets=Asset.query.count(),
    total_purchases=Purchase.query.count(),
    total_custodies=Custody.query.count(),
    total_invoices=Invoice.query.count()
    )

# تحميل نسخة احتياطية
@app.route('/download_backup')
def download_backup():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = User.query.get(session['user_id'])
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        db_path = os.path.join(app.instance_path, 'asset_management_complete.db')
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        return send_file(db_path, as_attachment=True, download_name=backup_name)
    except Exception as e:
        flash(f'حدث خطأ أثناء تحميل النسخة الاحتياطية: {str(e)}', 'error')
        return redirect(url_for('database'))

# استعادة نسخة احتياطية
@app.route('/restore_backup', methods=['POST'])
def restore_backup():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'غير مسجل دخول'})
    
    current_user = User.query.get(session['user_id'])
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'ليس لديك صلاحية'})
    
    try:
        if 'backup_file' not in request.files:
            return jsonify({'success': False, 'message': 'لم يتم اختيار ملف'})
        
        file = request.files['backup_file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'لم يتم اختيار ملف'})
        
        # حفظ الملف المرفوع
        db_path = os.path.join(app.instance_path, 'asset_management_complete.db')
        file.save(db_path)
        
        return jsonify({'success': True, 'message': 'تم استعادة النسخة الاحتياطية بنجاح'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# إعادة تعيين قاعدة البيانات
@app.route('/reset_database', methods=['POST'])
def reset_database():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'غير مسجل دخول'})
    
    current_user = User.query.get(session['user_id'])
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'ليس لديك صلاحية'})
    
    try:
        # حذف جميع الجداول وإعادة إنشائها
        db.drop_all()
        db.create_all()
        
        # إضافة المستخدم الافتراضي
        admin_user = User(username='admin', email='admin@company.com', role='admin')
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'تم إعادة تعيين قاعدة البيانات بنجاح'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# تهيئة قاعدة البيانات
def init_db():
    with app.app_context():
        db.create_all()
        
        # إضافة مستخدم افتراضي
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', email='admin@company.com', role='admin')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            
        # إضافة بيانات تجريبية
        if Asset.query.count() == 0:
            # إضافة أصول تجريبية
            assets_data = [
                {'name': 'لابتوب Dell Latitude', 'category': 'أجهزة كمبيوتر', 'serial_number': 'DL001', 'purchase_price': 3500, 'status': 'نشط'},
                {'name': 'طابعة HP LaserJet', 'category': 'طابعات', 'serial_number': 'HP001', 'purchase_price': 1200, 'status': 'نشط'},
                {'name': 'شاشة Samsung 24 بوصة', 'category': 'شاشات', 'serial_number': 'SM001', 'purchase_price': 800, 'status': 'نشط'},
                {'name': 'كيبورد لوجيتك', 'category': 'ملحقات', 'serial_number': 'LG001', 'purchase_price': 150, 'status': 'نشط'},
                {'name': 'ماوس لاسلكي', 'category': 'ملحقات', 'serial_number': 'MS001', 'purchase_price': 80, 'status': 'نشط'}
            ]
            
            for asset_data in assets_data:
                asset = Asset(
                    name=asset_data['name'],
                    category=asset_data['category'],
                    serial_number=asset_data['serial_number'],
                    purchase_date=datetime.now() - timedelta(days=30),
                    purchase_price=asset_data['purchase_price'],
                    status=asset_data['status'],
                    location='المكتب الرئيسي'
                )
                db.session.add(asset)
            
            # إضافة مشتريات تجريبية
            purchases_data = [
                {'product_name': 'أجهزة لابتوب Dell', 'supplier': 'شركة التقنية المتقدمة', 'quantity': 5, 'total_price': 17500, 'status': 'مكتمل'},
                {'product_name': 'طابعات HP', 'supplier': 'مؤسسة الحاسوب', 'quantity': 2, 'total_price': 2400, 'status': 'مكتمل'},
                {'product_name': 'شاشات Samsung', 'supplier': 'متجر الإلكترونيات', 'quantity': 10, 'total_price': 8000, 'status': 'قيد التنفيذ'},
                {'product_name': 'ملحقات متنوعة', 'supplier': 'شركة الملحقات', 'quantity': 20, 'total_price': 2000, 'status': 'مكتمل'}
            ]
            
            for purchase_data in purchases_data:
                purchase = Purchase(
                    product_name=purchase_data['product_name'],
                    supplier=purchase_data['supplier'],
                    quantity=purchase_data['quantity'],
                    total_price=purchase_data['total_price'],
                    purchase_date=datetime.now() - timedelta(days=20),
                    status=purchase_data['status']
                )
                db.session.add(purchase)
            
            # إضافة عهد تجريبية
            custodies_data = [
                {'employee_name': 'أحمد محمد علي', 'employee_id': 'EMP001', 'custody_type': 'لابتوب', 'serial_number': 'DL001', 'estimated_value': 3500},
                {'employee_name': 'فاطمة أحمد', 'employee_id': 'EMP002', 'custody_type': 'شاشة', 'serial_number': 'SM001', 'estimated_value': 800},
                {'employee_name': 'محمد سالم', 'employee_id': 'EMP003', 'custody_type': 'كيبورد وماوس', 'serial_number': 'LG001', 'estimated_value': 230},
                {'employee_name': 'نورا خالد', 'employee_id': 'EMP004', 'custody_type': 'طابعة', 'serial_number': 'HP001', 'estimated_value': 1200}
            ]
            
            for custody_data in custodies_data:
                custody = Custody(
                    employee_name=custody_data['employee_name'],
                    employee_id=custody_data['employee_id'],
                    custody_type=custody_data['custody_type'],
                    serial_number=custody_data['serial_number'],
                    received_date=datetime.now() - timedelta(days=15),
                    estimated_value=custody_data['estimated_value'],
                    status='نشط'
                )
                db.session.add(custody)
            
            # إضافة فواتير تجريبية
            invoices_data = [
                {'invoice_number': 'INV-2024-001', 'supplier_name': 'شركة التقنية المتقدمة', 'total_amount': 17500, 'payment_status': 'مدفوع'},
                {'invoice_number': 'INV-2024-002', 'supplier_name': 'مؤسسة الحاسوب', 'total_amount': 2400, 'payment_status': 'مدفوع'},
                {'invoice_number': 'INV-2024-003', 'supplier_name': 'متجر الإلكترونيات', 'total_amount': 8000, 'payment_status': 'قيد المراجعة'},
                {'invoice_number': 'INV-2024-004', 'supplier_name': 'شركة الملحقات', 'total_amount': 2000, 'payment_status': 'غير مدفوع'}
            ]
            
            for invoice_data in invoices_data:
                invoice = Invoice(
                    invoice_number=invoice_data['invoice_number'],
                    invoice_date=datetime.now() - timedelta(days=25),
                    supplier_name=invoice_data['supplier_name'],
                    total_amount=invoice_data['total_amount'],
                    payment_status=invoice_data['payment_status'],
                    due_date=datetime.now() + timedelta(days=30)
                )
                db.session.add(invoice)
            
            db.session.commit()
            print("✅ تم إضافة البيانات التجريبية بنجاح!")

if __name__ == '__main__':
    init_db()
    print("=" * 70)
    print("🚀 نظام إدارة الأصول الاحترافي - النسخة المستقرة")
    print("   Professional Asset Management System - Stable Version")
    print("=" * 70)
    print("✅ النظام جاهز!")
    print("🌐 الرابط: http://localhost:5001")
    print("👤 المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("🎨 التصميم: احترافي ومستقر")
    print("📱 متجاوب: يعمل على جميع الأجهزة")
    print("🔧 للإيقاف: اضغط Ctrl+C")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5001, debug=False)