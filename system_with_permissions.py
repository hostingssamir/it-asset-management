#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام إدارة الأصول الاحترافي مع نظام الصلاحيات المتقدم
Professional Asset Management System with Advanced Permissions
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json

# إنشاء التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///asset_management_permissions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إنشاء قاعدة البيانات
db = SQLAlchemy(app)

# نماذج قاعدة البيانات مع نظام الصلاحيات
class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('user_role.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # صلاحيات مفصلة
    can_view_assets = db.Column(db.Boolean, default=True)
    can_add_assets = db.Column(db.Boolean, default=False)
    can_edit_assets = db.Column(db.Boolean, default=False)
    can_delete_assets = db.Column(db.Boolean, default=False)
    
    can_view_employees = db.Column(db.Boolean, default=True)
    can_add_employees = db.Column(db.Boolean, default=False)
    can_edit_employees = db.Column(db.Boolean, default=False)
    can_delete_employees = db.Column(db.Boolean, default=False)
    
    can_view_purchases = db.Column(db.Boolean, default=True)
    can_add_purchases = db.Column(db.Boolean, default=False)
    can_edit_purchases = db.Column(db.Boolean, default=False)
    can_delete_purchases = db.Column(db.Boolean, default=False)
    
    can_view_custody = db.Column(db.Boolean, default=True)
    can_add_custody = db.Column(db.Boolean, default=False)
    can_edit_custody = db.Column(db.Boolean, default=False)
    can_delete_custody = db.Column(db.Boolean, default=False)
    
    can_view_invoices = db.Column(db.Boolean, default=True)
    can_add_invoices = db.Column(db.Boolean, default=False)
    can_edit_invoices = db.Column(db.Boolean, default=False)
    can_delete_invoices = db.Column(db.Boolean, default=False)
    
    can_view_licenses = db.Column(db.Boolean, default=True)
    can_add_licenses = db.Column(db.Boolean, default=False)
    can_edit_licenses = db.Column(db.Boolean, default=False)
    can_delete_licenses = db.Column(db.Boolean, default=False)
    
    can_view_departments = db.Column(db.Boolean, default=True)
    can_add_departments = db.Column(db.Boolean, default=False)
    can_edit_departments = db.Column(db.Boolean, default=False)
    can_delete_departments = db.Column(db.Boolean, default=False)
    
    can_view_support = db.Column(db.Boolean, default=True)
    can_add_support = db.Column(db.Boolean, default=False)
    can_edit_support = db.Column(db.Boolean, default=False)
    can_delete_support = db.Column(db.Boolean, default=False)
    
    can_view_reports = db.Column(db.Boolean, default=True)
    can_export_reports = db.Column(db.Boolean, default=False)
    
    can_manage_users = db.Column(db.Boolean, default=False)
    
    role = db.relationship('UserRole', backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_role_name(self):
        return self.role.name if self.role else 'مستخدم'
    
    def is_admin(self):
        return self.role and self.role.name == 'مدير النظام'
    
    def is_manager(self):
        return self.role and self.role.name == 'مدير'
    
    def set_admin_permissions(self):
        """منح جميع الصلاحيات للمدير"""
        self.can_add_assets = True
        self.can_edit_assets = True
        self.can_delete_assets = True
        self.can_add_employees = True
        self.can_edit_employees = True
        self.can_delete_employees = True
        self.can_add_purchases = True
        self.can_edit_purchases = True
        self.can_delete_purchases = True
        self.can_add_custody = True
        self.can_edit_custody = True
        self.can_delete_custody = True
        self.can_add_invoices = True
        self.can_edit_invoices = True
        self.can_delete_invoices = True
        self.can_add_licenses = True
        self.can_edit_licenses = True
        self.can_delete_licenses = True
        self.can_add_departments = True
        self.can_edit_departments = True
        self.can_delete_departments = True
        self.can_add_support = True
        self.can_edit_support = True
        self.can_delete_support = True
        self.can_export_reports = True
        self.can_manage_users = True

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

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    hire_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='نشط')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# قالب تسجيل الدخول
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - نظام إدارة الأصول مع الصلاحيات</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            max-width: 400px;
            width: 100%;
        }
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        .login-body {
            padding: 2rem;
        }
        .form-control {
            border-radius: 15px;
            border: 2px solid #e9ecef;
            padding: 1rem 1.5rem;
            font-size: 1.1rem;
            transition: all 0.3s ease;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-login {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 15px;
            padding: 1rem 2rem;
            font-size: 1.2rem;
            font-weight: 600;
            color: white;
            width: 100%;
            transition: all 0.3s ease;
        }
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
            color: white;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <i class="fas fa-shield-alt fa-3x mb-3"></i>
            <h3>نظام إدارة الأصول</h3>
            <p class="mb-0">مع نظام الصلاحيات المتقدم</p>
        </div>
        <div class="login-body">
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-danger">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label">اسم المستخدم</label>
                    <input type="text" class="form-control" name="username" required>
                </div>
                <div class="mb-4">
                    <label class="form-label">كلمة المرور</label>
                    <input type="password" class="form-control" name="password" required>
                </div>
                <button type="submit" class="btn btn-login">
                    <i class="fas fa-sign-in-alt me-2"></i>دخول
                </button>
            </form>
            
            <div class="text-center mt-3">
                <small class="text-muted">
                    المستخدم الافتراضي: admin | كلمة المرور: admin123
                </small>
            </div>
        </div>
    </div>
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
        
        if user and user.check_password(password) and user.is_active:
            session['user_id'] = user.id
            session['username'] = user.username
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة أو الحساب غير مفعل', 'error')
    
    return render_template_string(LOGIN_TEMPLATE)

# الصفحة الرئيسية
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = User.query.get(session['user_id'])
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم - نظام إدارة الأصول مع الصلاحيات</title>
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
        .welcome-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 20px;
            padding: 3rem;
            margin: 2rem 0;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        }
        .module-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            text-align: center;
            border: 2px solid transparent;
        }
        .module-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            border-color: #667eea;
        }
        .module-icon {
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 1rem;
        }
        .module-title {
            color: #333;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        .module-description {
            color: #666;
            margin-bottom: 2rem;
        }
        .btn-module {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 15px;
            padding: 0.8rem 2rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        .btn-module:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
            color: white;
        }
        .permission-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 0.8rem;
        }
        .module-card.disabled {
            opacity: 0.5;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-shield-alt me-2"></i>
                نظام إدارة الأصول مع الصلاحيات
            </a>
            <div class="navbar-nav ms-auto">
                <span class="nav-link text-white">
                    <i class="fas fa-user me-1"></i>
                    {{ current_user.username }} ({{ current_user.get_role_name() }})
                </span>
                <a class="nav-link text-white" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>
                    خروج
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="welcome-card">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1 class="mb-3">
                        <i class="fas fa-hand-wave me-2"></i>
                        مرحباً بك، {{ current_user.username }}
                    </h1>
                    <p class="lead mb-0">
                        دورك: <strong>{{ current_user.get_role_name() }}</strong><br>
                        مرحباً بك في نظام إدارة الأصول مع نظام الصلاحيات المتقدم.
                    </p>
                </div>
                <div class="col-md-4 text-center">
                    <i class="fas fa-shield-alt" style="font-size: 5rem; opacity: 0.3;"></i>
                </div>
            </div>
        </div>
        
        <!-- وحدات النظام -->
        <div class="row">
            <!-- إدارة الأصول -->
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card {{ 'disabled' if not current_user.can_view_assets else '' }}" style="position: relative;">
                    {% if current_user.can_view_assets %}
                        <span class="badge bg-success permission-badge">مسموح</span>
                    {% else %}
                        <span class="badge bg-danger permission-badge">محظور</span>
                    {% endif %}
                    <div class="module-icon">
                        <i class="fas fa-laptop"></i>
                    </div>
                    <h5 class="module-title">إدارة الأصول</h5>
                    <p class="module-description">
                        إدارة شاملة لجميع أصول الشركة مع تتبع الحالة والموقع
                    </p>
                    {% if current_user.can_view_assets %}
                        <a href="/assets" class="btn-module">
                            <i class="fas fa-arrow-left me-2"></i>دخول
                        </a>
                    {% else %}
                        <button class="btn-module" disabled>
                            <i class="fas fa-ban me-2"></i>غير مسموح
                        </button>
                    {% endif %}
                </div>
            </div>
            
            <!-- إدارة الموظفين -->
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card {{ 'disabled' if not current_user.can_view_employees else '' }}" style="position: relative;">
                    {% if current_user.can_view_employees %}
                        <span class="badge bg-success permission-badge">مسموح</span>
                    {% else %}
                        <span class="badge bg-danger permission-badge">محظور</span>
                    {% endif %}
                    <div class="module-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <h5 class="module-title">إدارة الموظفين</h5>
                    <p class="module-description">
                        إدارة بيانات الموظفين والأقسام مع تتبع الحالة الوظيفية
                    </p>
                    {% if current_user.can_view_employees %}
                        <a href="/employees" class="btn-module">
                            <i class="fas fa-arrow-left me-2"></i>دخول
                        </a>
                    {% else %}
                        <button class="btn-module" disabled>
                            <i class="fas fa-ban me-2"></i>غير مسموح
                        </button>
                    {% endif %}
                </div>
            </div>
            
            <!-- إدارة المستخدمين -->
            {% if current_user.can_manage_users %}
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card" style="position: relative;">
                    <span class="badge bg-warning permission-badge">مدير</span>
                    <div class="module-icon">
                        <i class="fas fa-users-cog"></i>
                    </div>
                    <h5 class="module-title">إدارة المستخدمين</h5>
                    <p class="module-description">
                        إدارة المستخدمين والصلاحيات مع تحكم كامل في الوصول
                    </p>
                    <a href="/users" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>دخول
                    </a>
                </div>
            </div>
            {% endif %}
            
            <!-- التقارير -->
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card {{ 'disabled' if not current_user.can_view_reports else '' }}" style="position: relative;">
                    {% if current_user.can_view_reports %}
                        <span class="badge bg-success permission-badge">مسموح</span>
                    {% else %}
                        <span class="badge bg-danger permission-badge">محظور</span>
                    {% endif %}
                    <div class="module-icon">
                        <i class="fas fa-chart-bar"></i>
                    </div>
                    <h5 class="module-title">التقارير والإحصائيات</h5>
                    <p class="module-description">
                        تقارير شاملة وإحصائيات تفصيلية مع إمكانية التصدير
                    </p>
                    {% if current_user.can_view_reports %}
                        <a href="/reports" class="btn-module">
                            <i class="fas fa-arrow-left me-2"></i>دخول
                        </a>
                    {% else %}
                        <button class="btn-module" disabled>
                            <i class="fas fa-ban me-2"></i>غير مسموح
                        </button>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // رسالة ترحيب
        setTimeout(() => {
            Swal.fire({
                title: 'مرحباً بك!',
                text: 'تم تسجيل دخولك بنجاح إلى النظام',
                icon: 'success',
                timer: 2000,
                showConfirmButton: false,
                toast: true,
                position: 'top-end'
            });
        }, 500);
    </script>
</body>
</html>
    ''', current_user=current_user)

# إدارة المستخدمين والصلاحيات
@app.route('/users')
def users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # التحقق من صلاحية إدارة المستخدمين
    current_user = User.query.get(session['user_id'])
    if not current_user.can_manage_users:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    roles = UserRole.query.all()
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة المستخدمين والصلاحيات - نظام إدارة الأصول</title>
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
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
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
        .table tbody tr:hover {
            background-color: #f8f9fa;
            transform: scale(1.01);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-shield-alt me-2"></i>
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
                <h2><i class="fas fa-users-cog me-2 text-primary"></i>إدارة المستخدمين والصلاحيات</h2>
                <div>
                    <a href="/add_user" class="btn btn-primary me-2">
                        <i class="fas fa-user-plus me-2"></i>إضافة مستخدم جديد
                    </a>
                    <a href="/manage_roles" class="btn btn-outline-primary">
                        <i class="fas fa-key me-2"></i>إدارة الأدوار
                    </a>
                </div>
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
                                <span class="badge bg-info">
                                    <i class="fas fa-user-tag me-1"></i>
                                    {{ user.get_role_name() }}
                                </span>
                            </td>
                            <td>{{ user.created_at.strftime('%Y-%m-%d') }}</td>
                            <td>
                                <span class="badge bg-{{ 'success' if user.is_active else 'danger' }}">
                                    <i class="fas fa-{{ 'check' if user.is_active else 'times' }} me-1"></i>
                                    {{ 'نشط' if user.is_active else 'غير نشط' }}
                                </span>
                            </td>
                            <td>
                                <div class="btn-group" role="group">
                                    <button class="btn btn-sm btn-outline-primary" onclick="editPermissions({{ user.id }})" title="تعديل الصلاحيات">
                                        <i class="fas fa-key"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-info" onclick="editUser({{ user.id }})" title="تعديل البيانات">
                                        <i class="fas fa-edit"></i>
                                    </button>
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
        function editPermissions(id) {
            window.location.href = '/edit_permissions/' + id;
        }
        
        function editUser(id) {
            window.location.href = '/edit_user/' + id;
        }
        
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
    ''', users=users, roles=roles)

# تفعيل/إلغاء تفعيل المستخدم
@app.route('/toggle_user/<int:user_id>', methods=['POST'])
def toggle_user(user_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'غير مسجل دخول'})
    
    current_user = User.query.get(session['user_id'])
    if not current_user.can_manage_users:
        return jsonify({'success': False, 'message': 'ليس لديك صلاحية'})
    
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# صفحة تعديل الصلاحيات
@app.route('/edit_permissions/<int:user_id>', methods=['GET', 'POST'])
def edit_permissions(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # التحقق من صلاحية إدارة المستخدمين
    current_user = User.query.get(session['user_id'])
    if not current_user.can_manage_users:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    roles = UserRole.query.all()
    
    if request.method == 'POST':
        try:
            # تحديث الدور
            if request.form.get('role_id'):
                user.role_id = int(request.form['role_id'])
            
            # تحديث الصلاحيات المفصلة
            user.can_view_assets = 'can_view_assets' in request.form
            user.can_add_assets = 'can_add_assets' in request.form
            user.can_edit_assets = 'can_edit_assets' in request.form
            user.can_delete_assets = 'can_delete_assets' in request.form
            
            user.can_view_employees = 'can_view_employees' in request.form
            user.can_add_employees = 'can_add_employees' in request.form
            user.can_edit_employees = 'can_edit_employees' in request.form
            user.can_delete_employees = 'can_delete_employees' in request.form
            
            user.can_view_purchases = 'can_view_purchases' in request.form
            user.can_add_purchases = 'can_add_purchases' in request.form
            user.can_edit_purchases = 'can_edit_purchases' in request.form
            user.can_delete_purchases = 'can_delete_purchases' in request.form
            
            user.can_view_custody = 'can_view_custody' in request.form
            user.can_add_custody = 'can_add_custody' in request.form
            user.can_edit_custody = 'can_edit_custody' in request.form
            user.can_delete_custody = 'can_delete_custody' in request.form
            
            user.can_view_invoices = 'can_view_invoices' in request.form
            user.can_add_invoices = 'can_add_invoices' in request.form
            user.can_edit_invoices = 'can_edit_invoices' in request.form
            user.can_delete_invoices = 'can_delete_invoices' in request.form
            
            user.can_view_licenses = 'can_view_licenses' in request.form
            user.can_add_licenses = 'can_add_licenses' in request.form
            user.can_edit_licenses = 'can_edit_licenses' in request.form
            user.can_delete_licenses = 'can_delete_licenses' in request.form
            
            user.can_view_departments = 'can_view_departments' in request.form
            user.can_add_departments = 'can_add_departments' in request.form
            user.can_edit_departments = 'can_edit_departments' in request.form
            user.can_delete_departments = 'can_delete_departments' in request.form
            
            user.can_view_support = 'can_view_support' in request.form
            user.can_add_support = 'can_add_support' in request.form
            user.can_edit_support = 'can_edit_support' in request.form
            user.can_delete_support = 'can_delete_support' in request.form
            
            user.can_view_reports = 'can_view_reports' in request.form
            user.can_export_reports = 'can_export_reports' in request.form
            
            user.can_manage_users = 'can_manage_users' in request.form
            
            db.session.commit()
            flash('تم تحديث الصلاحيات بنجاح!', 'success')
            return redirect(url_for('users'))
        except Exception as e:
            flash(f'حدث خطأ أثناء تحديث الصلاحيات: {str(e)}', 'error')
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تعديل صلاحيات المستخدم - نظام إدارة الأصول</title>
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
            padding: 3rem;
            margin: 2rem 0;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 15px;
            padding: 0.8rem 2rem;
            font-weight: 600;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }
        .permissions-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }
        .permissions-section:hover {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }
        .permission-title {
            color: #667eea;
            font-weight: 600;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #667eea;
        }
        .form-check {
            margin: 0.5rem 0;
            padding: 0.5rem;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        .form-check:hover {
            background: rgba(102, 126, 234, 0.1);
        }
        .form-check-input:checked {
            background-color: #667eea;
            border-color: #667eea;
        }
        .user-info {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        .quick-actions {
            background: #e3f2fd;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 2rem;
        }
        .quick-btn {
            margin: 0.2rem;
            border-radius: 20px;
            padding: 0.3rem 1rem;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-shield-alt me-2"></i>
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
            <div class="user-info">
                <h2><i class="fas fa-user-cog me-2"></i>تعديل صلاحيات المستخدم</h2>
                <p class="mb-0">
                    <i class="fas fa-user me-2"></i>المستخدم: <strong>{{ user.username }}</strong> |
                    <i class="fas fa-envelope me-2"></i>البريد: <strong>{{ user.email }}</strong> |
                    <i class="fas fa-user-tag me-2"></i>الدور الحالي: <strong>{{ user.get_role_name() }}</strong>
                </p>
            </div>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <!-- إجراءات سريعة -->
            <div class="quick-actions">
                <h6><i class="fas fa-bolt me-2"></i>إجراءات سريعة:</h6>
                <button type="button" class="btn btn-success quick-btn" onclick="selectAllPermissions()">
                    <i class="fas fa-check-double me-1"></i>تحديد الكل
                </button>
                <button type="button" class="btn btn-warning quick-btn" onclick="selectViewOnly()">
                    <i class="fas fa-eye me-1"></i>عرض فقط
                </button>
                <button type="button" class="btn btn-info quick-btn" onclick="selectManagerPermissions()">
                    <i class="fas fa-user-tie me-1"></i>صلاحيات مدير
                </button>
                <button type="button" class="btn btn-danger quick-btn" onclick="clearAllPermissions()">
                    <i class="fas fa-times me-1"></i>إلغاء الكل
                </button>
            </div>
            
            <form method="POST" id="permissionsForm">
                <!-- اختيار الدور -->
                <div class="permissions-section">
                    <h5 class="permission-title"><i class="fas fa-user-tag me-2"></i>الدور الوظيفي</h5>
                    <select class="form-select" name="role_id">
                        <option value="">اختر الدور</option>
                        {% for role in roles %}
                        <option value="{{ role.id }}" {{ 'selected' if user.role_id == role.id else '' }}>
                            {{ role.name }} - {{ role.description }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                
                <!-- صلاحيات الأصول -->
                <div class="permissions-section">
                    <h5 class="permission-title"><i class="fas fa-laptop me-2"></i>صلاحيات الأصول</h5>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_view_assets" id="can_view_assets"
                                       {{ 'checked' if user.can_view_assets else '' }}>
                                <label class="form-check-label" for="can_view_assets">
                                    <i class="fas fa-eye me-1"></i>عرض الأصول
                                </label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_add_assets" id="can_add_assets"
                                       {{ 'checked' if user.can_add_assets else '' }}>
                                <label class="form-check-label" for="can_add_assets">
                                    <i class="fas fa-plus me-1"></i>إضافة أصول
                                </label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_edit_assets" id="can_edit_assets"
                                       {{ 'checked' if user.can_edit_assets else '' }}>
                                <label class="form-check-label" for="can_edit_assets">
                                    <i class="fas fa-edit me-1"></i>تعديل الأصول
                                </label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_delete_assets" id="can_delete_assets"
                                       {{ 'checked' if user.can_delete_assets else '' }}>
                                <label class="form-check-label" for="can_delete_assets">
                                    <i class="fas fa-trash me-1"></i>حذف الأصول
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- صلاحيات الموظفين -->
                <div class="permissions-section">
                    <h5 class="permission-title"><i class="fas fa-users me-2"></i>صلاحيات الموظفين</h5>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_view_employees" id="can_view_employees"
                                       {{ 'checked' if user.can_view_employees else '' }}>
                                <label class="form-check-label" for="can_view_employees">
                                    <i class="fas fa-eye me-1"></i>عرض الموظفين
                                </label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_add_employees" id="can_add_employees"
                                       {{ 'checked' if user.can_add_employees else '' }}>
                                <label class="form-check-label" for="can_add_employees">
                                    <i class="fas fa-plus me-1"></i>إضافة موظفين
                                </label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_edit_employees" id="can_edit_employees"
                                       {{ 'checked' if user.can_edit_employees else '' }}>
                                <label class="form-check-label" for="can_edit_employees">
                                    <i class="fas fa-edit me-1"></i>تعديل الموظفين
                                </label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_delete_employees" id="can_delete_employees"
                                       {{ 'checked' if user.can_delete_employees else '' }}>
                                <label class="form-check-label" for="can_delete_employees">
                                    <i class="fas fa-trash me-1"></i>حذف الموظفين
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- صلاحيات التقارير -->
                <div class="permissions-section">
                    <h5 class="permission-title"><i class="fas fa-chart-bar me-2"></i>صلاحيات التقارير</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_view_reports" id="can_view_reports"
                                       {{ 'checked' if user.can_view_reports else '' }}>
                                <label class="form-check-label" for="can_view_reports">
                                    <i class="fas fa-eye me-1"></i>عرض التقارير
                                </label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_export_reports" id="can_export_reports"
                                       {{ 'checked' if user.can_export_reports else '' }}>
                                <label class="form-check-label" for="can_export_reports">
                                    <i class="fas fa-download me-1"></i>تصدير التقارير
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- صلاحيات إدارة النظام -->
                <div class="permissions-section">
                    <h5 class="permission-title"><i class="fas fa-cogs me-2"></i>صلاحيات إدارة النظام</h5>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" name="can_manage_users" id="can_manage_users"
                               {{ 'checked' if user.can_manage_users else '' }}>
                        <label class="form-check-label" for="can_manage_users">
                            <i class="fas fa-users-cog me-1"></i>إدارة المستخدمين والصلاحيات
                        </label>
                    </div>
                </div>
                
                <div class="text-center mt-4">
                    <button type="submit" class="btn btn-primary btn-lg px-5 me-3">
                        <i class="fas fa-save me-2"></i>حفظ الصلاحيات
                    </button>
                    <a href="/users" class="btn btn-secondary btn-lg px-5">
                        <i class="fas fa-arrow-left me-2"></i>العودة
                    </a>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        // وظائف الإجراءات السريعة
        function selectAllPermissions() {
            document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = true);
            showToast('تم تحديد جميع الصلاحيات', 'success');
        }
        
        function clearAllPermissions() {
            document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
            showToast('تم إلغاء جميع الصلاحيات', 'warning');
        }
        
        function selectViewOnly() {
            clearAllPermissions();
            document.querySelectorAll('input[name*="can_view"]').forEach(cb => cb.checked = true);
            showToast('تم تحديد صلاحيات العرض فقط', 'info');
        }
        
        function selectManagerPermissions() {
            clearAllPermissions();
            const managerPermissions = [
                'can_view_assets', 'can_add_assets', 'can_edit_assets',
                'can_view_employees', 'can_add_employees', 'can_edit_employees',
                'can_view_reports', 'can_export_reports'
            ];
            managerPermissions.forEach(perm => {
                const cb = document.querySelector(`input[name="${perm}"]`);
                if (cb) cb.checked = true;
            });
            showToast('تم تحديد صلاحيات المدير', 'info');
        }
        
        function showToast(message, type) {
            Swal.fire({
                toast: true,
                position: 'top-end',
                icon: type,
                title: message,
                showConfirmButton: false,
                timer: 2000
            });
        }
        
        // تأثيرات تفاعلية
        document.addEventListener('DOMContentLoaded', function() {
            const checkboxes = document.querySelectorAll('.form-check-input');
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    const section = this.closest('.permissions-section');
                    const checkedCount = section.querySelectorAll('input:checked').length;
                    
                    if (checkedCount > 0) {
                        section.style.borderColor = '#28a745';
                        section.style.backgroundColor = 'rgba(40, 167, 69, 0.05)';
                    } else {
                        section.style.borderColor = '#e9ecef';
                        section.style.backgroundColor = '#f8f9fa';
                    }
                });
            });
        });
    </script>
</body>
</html>
    ''', user=user, roles=roles)

# إضافة مستخدم جديد
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # التحقق من صلاحية إدارة المستخدمين
    current_user = User.query.get(session['user_id'])
    if not current_user.can_manage_users:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('dashboard'))
    
    roles = UserRole.query.all()
    
    if request.method == 'POST':
        try:
            user = User(
                username=request.form['username'],
                email=request.form['email'],
                is_active=True
            )
            user.set_password(request.form['password'])
            
            # تعيين الدور
            if request.form.get('role_id'):
                user.role_id = int(request.form['role_id'])
            
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
            margin: 2rem 0;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
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
            transition: all 0.3s ease;
        }
        .form-control:focus, .form-select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-shield-alt me-2"></i>
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
                        <i class="fas fa-user-tag me-2"></i>الدور الوظيفي
                    </label>
                    <select class="form-select" name="role_id">
                        <option value="">اختر الدور</option>
                        {% for role in roles %}
                        <option value="{{ role.id }}">{{ role.name }} - {{ role.description }}</option>
                        {% endfor %}
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
    ''', roles=roles)

# خروج
@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('login'))

# تهيئة قاعدة البيانات
def init_db():
    with app.app_context():
        try:
            # إنشاء الجداول
            db.create_all()
            
            # إضافة الأدوار الافتراضية
            if not UserRole.query.filter_by(name='مدير النظام').first():
                admin_role = UserRole(
                    name='مدير النظام',
                    description='صلاحيات كاملة لإدارة النظام',
                    permissions='all'
                )
                db.session.add(admin_role)
                
                manager_role = UserRole(
                    name='مدير',
                    description='صلاحيات إدارية محدودة',
                    permissions='limited'
                )
                db.session.add(manager_role)
                
                user_role = UserRole(
                    name='مستخدم',
                    description='صلاحيات عرض فقط',
                    permissions='view_only'
                )
                db.session.add(user_role)
                
                db.session.commit()
                print("تم إنشاء الأدوار الافتراضية")
            
            # إضافة مستخدم افتراضي
            if not User.query.filter_by(username='admin').first():
                admin_role = UserRole.query.filter_by(name='مدير النظام').first()
                admin_user = User(
                    username='admin', 
                    email='admin@company.com',
                    role_id=admin_role.id if admin_role else None
                )
                admin_user.set_password('admin123')
                admin_user.set_admin_permissions()
                db.session.add(admin_user)
                db.session.commit()
                print("تم إنشاء المستخدم الافتراضي: admin")
                
        except Exception as e:
            print(f"خطأ في تهيئة قاعدة البيانات: {e}")

if __name__ == '__main__':
    init_db()
    print("\n" + "="*70)
    print("🚀 نظام إدارة الأصول مع الصلاحيات المتقدم")
    print("   Professional Asset Management System with Permissions")
    print("="*70)
    print("✅ النظام جاهز!")
    print("🌐 الرابط: http://localhost:5000")
    print("👤 المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("🛡️  نظام الصلاحيات: مفعل")
    print("🎨 التصميم: احترافي ومتقدم")
    print("📱 متجاوب: يعمل على جميع الأجهزة")
    print("🔧 للإيقاف: اضغط Ctrl+C")
    print("="*70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)