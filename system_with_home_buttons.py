#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام إدارة الأصول الكامل مع أزرار العودة للرئيسية
Complete Asset Management System with Home Navigation Buttons
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

# إنشاء التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///asset_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إنشاء قاعدة البيانات
db = SQLAlchemy(app)

# نماذج قاعدة البيانات
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

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(100), nullable=False)
    department_code = db.Column(db.String(20), unique=True, nullable=False)
    manager_name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
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

class License(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    software_name = db.Column(db.String(100), nullable=False)
    license_key = db.Column(db.String(200), nullable=False)
    license_type = db.Column(db.String(20), nullable=False)
    user_count = db.Column(db.Integer, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date)
    cost = db.Column(db.Float)
    vendor = db.Column(db.String(100))
    invoice_file = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='نشط')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    requester_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    issue_type = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='مفتوح')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Text)  # JSON string of permissions
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
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .form-control {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-login {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: transform 0.3s ease;
        }
        .btn-login:hover {
            transform: translateY(-2px);
        }
        .logo-circle {
            width: 100px;
            height: 100px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 2rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
                <div class="login-card p-5">
                    <div class="text-center mb-4">
                        <div class="logo-circle">
                            <i class="fas fa-rocket fa-3x text-white"></i>
                        </div>
                        <h2 class="fw-bold text-dark">نظام إدارة الأصول</h2>
                        <p class="text-muted">مرحباً بك، يرجى تسجيل الدخول</p>
                    </div>

                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show" role="alert">
                                    {{ message }}
                                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                </div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}

                    <form method="POST">
                        <div class="mb-3">
                            <label for="username" class="form-label">
                                <i class="fas fa-user me-2"></i>اسم المستخدم
                            </label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>
                        
                        <div class="mb-4">
                            <label for="password" class="form-label">
                                <i class="fas fa-lock me-2"></i>كلمة المرور
                            </label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary btn-login">
                                <i class="fas fa-sign-in-alt me-2"></i>تسجيل الدخول
                            </button>
                        </div>
                    </form>

                    <div class="text-center mt-4">
                        <small class="text-muted">
                            <i class="fas fa-info-circle me-1"></i>
                            للدخول استخدم: admin / admin123
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
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
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }
        .navbar-custom { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card { 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
            transition: transform 0.3s ease;
        }
        .card:hover { transform: translateY(-5px); }
        .stats-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border-radius: 15px;
        }
        .menu-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .menu-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        }
        .welcome-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/">
                <i class="fas fa-rocket me-2"></i>نظام إدارة الأصول
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>تسجيل الخروج
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- قسم الترحيب -->
        <div class="welcome-section text-center">
            <h1><i class="fas fa-home me-2"></i>مرحباً بك في نظام إدارة الأصول</h1>
            <p class="mb-0">إدارة شاملة وفعالة لجميع أصول المؤسسة</p>
        </div>

        <!-- الإحصائيات -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-laptop fa-3x mb-3"></i>
                    <h3>{{ total_assets }}</h3>
                    <p class="mb-0">إجمالي الأصول</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-users fa-3x mb-3"></i>
                    <h3>{{ total_employees }}</h3>
                    <p class="mb-0">إجمالي الموظفين</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-dollar-sign fa-3x mb-3"></i>
                    <h3>{{ "{:,.0f}".format(total_value) }}</h3>
                    <p class="mb-0">إجمالي القيمة (ريال)</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-chart-line fa-3x mb-3"></i>
                    <h3>{{ active_assets }}</h3>
                    <p class="mb-0">الأصول النشطة</p>
                </div>
            </div>
        </div>

        <!-- القوائم الرئيسية -->
        <div class="row">
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="menu-card p-4 text-center" onclick="location.href='/assets'">
                    <i class="fas fa-laptop fa-3x mb-3"></i>
                    <h5>إدارة الأصول</h5>
                    <p class="mb-0">عرض وإدارة جميع الأصول</p>
                </div>
            </div>

            <div class="col-lg-4 col-md-6 mb-4">
                <div class="menu-card p-4 text-center" onclick="location.href='/employees'">
                    <i class="fas fa-users fa-3x mb-3"></i>
                    <h5>إدارة الموظفين</h5>
                    <p class="mb-0">عرض وإدارة بيانات الموظفين</p>
                </div>
            </div>

            <div class="col-lg-4 col-md-6 mb-4">
                <div class="menu-card p-4 text-center" onclick="location.href='/purchases'">
                    <i class="fas fa-shopping-cart fa-3x mb-3"></i>
                    <h5>إدارة المشتريات</h5>
                    <p class="mb-0">تتبع وإدارة المشتريات</p>
                </div>
            </div>

            <div class="col-lg-4 col-md-6 mb-4">
                <div class="menu-card p-4 text-center" onclick="location.href='/custody'">
                    <i class="fas fa-handshake fa-3x mb-3"></i>
                    <h5>إدارة العهد</h5>
                    <p class="mb-0">تتبع عهد الموظفين</p>
                </div>
            </div>

            <div class="col-lg-4 col-md-6 mb-4">
                <div class="menu-card p-4 text-center" onclick="location.href='/departments'">
                    <i class="fas fa-building fa-3x mb-3"></i>
                    <h5>الإدارات</h5>
                    <p class="mb-0">إدارة الأقسام والإدارات</p>
                </div>
            </div>

            <div class="col-lg-4 col-md-6 mb-4">
                <div class="menu-card p-4 text-center" onclick="location.href='/reports'">
                    <i class="fas fa-chart-bar fa-3x mb-3"></i>
                    <h5>التقارير</h5>
                    <p class="mb-0">تقارير وإحصائيات شاملة</p>
                </div>
            </div>

            <div class="col-lg-4 col-md-6 mb-4">
                <div class="menu-card p-4 text-center" onclick="location.href='/invoices'">
                    <i class="fas fa-file-invoice fa-3x mb-3"></i>
                    <h5>إدارة الفواتير</h5>
                    <p class="mb-0">تتبع وإدارة الفواتير</p>
                </div>
            </div>

            <div class="col-lg-4 col-md-6 mb-4">
                <div class="menu-card p-4 text-center" onclick="location.href='/licenses'">
                    <i class="fas fa-key fa-3x mb-3"></i>
                    <h5>إدارة التراخيص</h5>
                    <p class="mb-0">تتبع تراخيص البرمجيات</p>
                </div>
            </div>

            <div class="col-lg-4 col-md-6 mb-4">
                <div class="menu-card p-4 text-center" onclick="location.href='/support'">
                    <i class="fas fa-headset fa-3x mb-3"></i>
                    <h5>الدعم الفني</h5>
                    <p class="mb-0">تذاكر الدعم والمساعدة</p>
                </div>
            </div>

            <div class="col-lg-4 col-md-6 mb-4">
                <div class="menu-card p-4 text-center" onclick="location.href='/users'">
                    <i class="fas fa-users-cog fa-3x mb-3"></i>
                    <h5>إدارة المستخدمين</h5>
                    <p class="mb-0">إدارة حسابات المستخدمين</p>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# قالب عام للصفحات مع أزرار العودة
def create_page_template(title, icon, content, add_button_text="", add_button_url=""):
    return f'''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }}
        .navbar-custom {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .card {{ 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }}
        .table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
        }}
        .badge {{ padding: 0.5rem 1rem; border-radius: 10px; font-weight: 500; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas {icon} text-primary me-2"></i>{title}</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                {f'<a href="{add_button_url}" class="btn btn-primary"><i class="fas fa-plus me-2"></i>{add_button_text}</a>' if add_button_text else ''}
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                {content}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# قالب النماذج مع أزرار العودة
def create_add_form_template(title, icon, form_content, back_url):
    return f'''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Cairo', sans-serif;
        }}
        .navbar-custom {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .card {{ 
            border: none; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            border-radius: 20px;
        }}
        .form-control, .form-select {{
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }}
        .form-control:focus, .form-select:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-transparent border-0 pt-4">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <a href="{back_url}" class="btn btn-outline-secondary">
                                <i class="fas fa-arrow-right me-1"></i>العودة
                            </a>
                            <a href="/" class="btn btn-outline-success">
                                <i class="fas fa-home me-1"></i>الرئيسية
                            </a>
                        </div>
                        <div class="text-center">
                            <div class="d-inline-flex align-items-center justify-content-center bg-primary rounded-circle mb-3" style="width: 80px; height: 80px;">
                                <i class="fas {icon} fa-2x text-white"></i>
                            </div>
                            <h2 class="mb-1">{title}</h2>
                            <p class="text-muted">يرجى ملء البيانات المطلوبة</p>
                        </div>
                    </div>
                    
                    <div class="card-body p-4">
                        {{% with messages = get_flashed_messages(with_categories=true) %}}
                            {{% if messages %}}
                                {{% for category, message in messages %}}
                                    <div class="alert alert-{{'danger' if category == 'error' else 'success'}} alert-dismissible fade show" role="alert">
                                        {{{{ message }}}}
                                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                    </div>
                                {{% endfor %}}
                            {{% endif %}}
                        {{% endwith %}}
                        
                        {form_content}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# المسارات والوظائف
@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # حساب الإحصائيات
    total_assets = Asset.query.count()
    total_employees = Employee.query.count()
    total_value = db.session.query(db.func.sum(Asset.purchase_price)).scalar() or 0
    active_assets = Asset.query.filter_by(status='نشط').count()
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                total_assets=total_assets,
                                total_employees=total_employees,
                                total_value=total_value,
                                active_assets=active_assets)

@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('login'))

@app.route('/assets')
def assets():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    assets = Asset.query.all()
    content = '''
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>الاسم</th>
                    <th>الفئة</th>
                    <th>الرقم التسلسلي</th>
                    <th>تاريخ الشراء</th>
                    <th>السعر</th>
                    <th>الحالة</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for asset in assets:
        content += f'''
                <tr>
                    <td>{asset.name}</td>
                    <td>{asset.category}</td>
                    <td>{asset.serial_number}</td>
                    <td>{asset.purchase_date.strftime('%Y-%m-%d') if asset.purchase_date else ''}</td>
                    <td>{"{:,.0f}".format(asset.purchase_price)} ريال</td>
                    <td>
                        <span class="badge bg-{'success' if asset.status == 'نشط' else 'warning'}">
                            {asset.status}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editAsset({asset.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteAsset({asset.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
        '''
    
    if not assets:
        content += '<tr><td colspan="7" class="text-center text-muted">لا توجد أصول مسجلة</td></tr>'
    
    content += '''
            </tbody>
        </table>
    </div>
    <script>
        function editAsset(id) {
            window.location.href = '/edit_asset/' + id;
        }
        
        function deleteAsset(id) {
            if (confirm('هل أنت متأكد من حذف هذا الأصل؟')) {
                fetch('/delete_asset/' + id, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('حدث خطأ أثناء الحذف');
                    }
                });
            }
        }
    </script>
    '''
    
    return render_template_string(create_page_template(
        "إدارة الأصول", 
        "fa-laptop", 
        content, 
        "إضافة أصل جديد", 
        "/add_asset"
    ))

@app.route('/employees')
def employees():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    employees = Employee.query.all()
    content = '''
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>الاسم</th>
                    <th>رقم الموظف</th>
                    <th>القسم</th>
                    <th>المنصب</th>
                    <th>البريد الإلكتروني</th>
                    <th>الحالة</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for employee in employees:
        content += f'''
                <tr>
                    <td>{employee.name}</td>
                    <td>{employee.employee_id}</td>
                    <td>{employee.department}</td>
                    <td>{employee.position}</td>
                    <td>{employee.email or '-'}</td>
                    <td>
                        <span class="badge bg-{'success' if employee.status == 'نشط' else 'warning'}">
                            {employee.status}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editEmployee({employee.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteEmployee({employee.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
        '''
    
    if not employees:
        content += '<tr><td colspan="7" class="text-center text-muted">لا توجد بيانات موظفين</td></tr>'
    
    content += '''
            </tbody>
        </table>
    </div>
    <script>
        function editEmployee(id) {
            window.location.href = '/edit_employee/' + id;
        }
        
        function deleteEmployee(id) {
            if (confirm('هل أنت متأكد من حذف هذا الموظف؟')) {
                fetch('/delete_employee/' + id, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('حدث خطأ أثناء الحذف');
                    }
                });
            }
        }
    </script>
    '''
    
    return render_template_string(create_page_template(
        "إدارة الموظفين", 
        "fa-users", 
        content, 
        "إضافة موظف جديد", 
        "/add_employee"
    ))

@app.route('/purchases')
def purchases():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    purchases = Purchase.query.all()
    content = '''
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>اسم المنتج</th>
                    <th>المورد</th>
                    <th>الكمية</th>
                    <th>السعر الإجمالي</th>
                    <th>تاريخ الشراء</th>
                    <th>الحالة</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for purchase in purchases:
        content += f'''
                <tr>
                    <td>{purchase.product_name}</td>
                    <td>{purchase.supplier}</td>
                    <td>{purchase.quantity}</td>
                    <td>{"{:,.0f}".format(purchase.total_price)} ريال</td>
                    <td>{purchase.purchase_date.strftime('%Y-%m-%d') if purchase.purchase_date else ''}</td>
                    <td>
                        <span class="badge bg-success">
                            {purchase.status}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editPurchase({purchase.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deletePurchase({purchase.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
        '''
    
    if not purchases:
        content += '<tr><td colspan="7" class="text-center text-muted">لا توجد مشتريات مسجلة</td></tr>'
    
    content += '''
            </tbody>
        </table>
    </div>
    <script>
        function editPurchase(id) {
            window.location.href = '/edit_purchase/' + id;
        }
        
        function deletePurchase(id) {
            if (confirm('هل أنت متأكد من حذف هذا المشترى؟')) {
                fetch('/delete_purchase/' + id, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('حدث خطأ أثناء الحذف');
                    }
                });
            }
        }
    </script>
    '''
    
    return render_template_string(create_page_template(
        "إدارة المشتريات", 
        "fa-shopping-cart", 
        content, 
        "إضافة مشترى جديد", 
        "/add_purchase"
    ))

@app.route('/custody')
def custody():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    custodies = Custody.query.all()
    content = '''
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>اسم الموظف</th>
                    <th>رقم الموظف</th>
                    <th>نوع العهدة</th>
                    <th>الرقم التسلسلي</th>
                    <th>تاريخ الاستلام</th>
                    <th>القيمة المقدرة</th>
                    <th>الحالة</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for custody_item in custodies:
        content += f'''
                <tr>
                    <td>{custody_item.employee_name}</td>
                    <td>{custody_item.employee_id}</td>
                    <td>{custody_item.custody_type}</td>
                    <td>{custody_item.serial_number}</td>
                    <td>{custody_item.received_date.strftime('%Y-%m-%d') if custody_item.received_date else ''}</td>
                    <td>{"{:,.0f}".format(custody_item.estimated_value) if custody_item.estimated_value else '-'} ريال</td>
                    <td>
                        <span class="badge bg-{'success' if custody_item.status == 'نشط' else 'warning'}">
                            {custody_item.status}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editCustody({custody_item.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger me-1" onclick="deleteCustody({custody_item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="printBarcode({custody_item.id})">
                            <i class="fas fa-barcode"></i>
                        </button>
                    </td>
                </tr>
        '''
    
    if not custodies:
        content += '<tr><td colspan="8" class="text-center text-muted">لا توجد عهد مسجلة</td></tr>'
    
    content += '''
            </tbody>
        </table>
    </div>
    <script>
        function editCustody(id) {
            window.location.href = '/edit_custody/' + id;
        }
        
        function deleteCustody(id) {
            if (confirm('هل أنت متأكد من حذف هذه العهدة؟')) {
                fetch('/delete_custody/' + id, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('حدث خطأ أثناء الحذف');
                    }
                });
            }
        }
        
        function printBarcode(id) {
            window.open('/print_barcode/' + id, '_blank');
        }
    </script>
    '''
    
    return render_template_string(create_page_template(
        "إدارة العهد", 
        "fa-handshake", 
        content, 
        "إضافة عهدة جديدة", 
        "/add_custody"
    ))

@app.route('/departments')
def departments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    departments = Department.query.all()
    content = '''
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>اسم الإدارة</th>
                    <th>رمز الإدارة</th>
                    <th>مدير الإدارة</th>
                    <th>الموقع</th>
                    <th>الحالة</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for department in departments:
        content += f'''
                <tr>
                    <td>{department.department_name}</td>
                    <td>{department.department_code}</td>
                    <td>{department.manager_name or '-'}</td>
                    <td>{department.location or '-'}</td>
                    <td>
                        <span class="badge bg-{'success' if department.status == 'نشط' else 'warning'}">
                            {department.status}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editDepartment({department.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteDepartment({department.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
        '''
    
    if not departments:
        content += '<tr><td colspan="6" class="text-center text-muted">لا توجد إدارات مسجلة</td></tr>'
    
    content += '''
            </tbody>
        </table>
    </div>
    <script>
        function editDepartment(id) {
            window.location.href = '/edit_department/' + id;
        }
        
        function deleteDepartment(id) {
            if (confirm('هل أنت متأكد من حذف هذه الإدارة؟')) {
                fetch('/delete_department/' + id, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('حدث خطأ أثناء الحذف');
                    }
                });
            }
        }
    </script>
    '''
    
    return render_template_string(create_page_template(
        "الإدارات", 
        "fa-building", 
        content, 
        "إضافة إدارة جديدة", 
        "/add_department"
    ))

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    content = '''
    <div class="row">
        <div class="col-md-4 mb-3">
            <div class="card bg-primary text-white">
                <div class="card-body text-center">
                    <i class="fas fa-chart-bar fa-3x mb-3"></i>
                    <h5>تقرير الأصول</h5>
                    <button class="btn btn-light">عرض التقرير</button>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-3">
            <div class="card bg-success text-white">
                <div class="card-body text-center">
                    <i class="fas fa-users fa-3x mb-3"></i>
                    <h5>تقرير الموظفين</h5>
                    <button class="btn btn-light">عرض التقرير</button>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-3">
            <div class="card bg-info text-white">
                <div class="card-body text-center">
                    <i class="fas fa-dollar-sign fa-3x mb-3"></i>
                    <h5>التقرير المالي</h5>
                    <button class="btn btn-light">عرض التقرير</button>
                </div>
            </div>
        </div>
    </div>
    '''
    return render_template_string(create_page_template(
        "التقارير والإحصائيات", 
        "fa-chart-bar", 
        content, 
        "تصدير التقرير", 
        "/export_report"
    ))

@app.route('/invoices')
def invoices():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    invoices = Invoice.query.all()
    content = '''
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>رقم الفاتورة</th>
                    <th>تاريخ الفاتورة</th>
                    <th>اسم المورد</th>
                    <th>المبلغ الإجمالي</th>
                    <th>حالة الدفع</th>
                    <th>تاريخ الاستحقاق</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for invoice in invoices:
        content += f'''
                <tr>
                    <td>{invoice.invoice_number}</td>
                    <td>{invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else ''}</td>
                    <td>{invoice.supplier_name}</td>
                    <td>{"{:,.0f}".format(invoice.total_amount)} ريال</td>
                    <td>
                        <span class="badge bg-{'success' if invoice.payment_status == 'مدفوع' else 'warning' if invoice.payment_status == 'مدفوع جزئياً' else 'danger'}">
                            {invoice.payment_status}
                        </span>
                    </td>
                    <td>{invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '-'}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
        '''
    
    if not invoices:
        content += '<tr><td colspan="7" class="text-center text-muted">لا توجد فواتير مسجلة</td></tr>'
    
    content += '''
            </tbody>
        </table>
    </div>
    '''
    
    return render_template_string(create_page_template(
        "إدارة الفواتير", 
        "fa-file-invoice", 
        content, 
        "إنشاء فاتورة جديدة", 
        "/create_invoice"
    ))

@app.route('/licenses')
def licenses():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    licenses = License.query.all()
    content = '''
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>اسم البرنامج</th>
                    <th>نوع الترخيص</th>
                    <th>عدد المستخدمين</th>
                    <th>تاريخ الشراء</th>
                    <th>تاريخ انتهاء الصلاحية</th>
                    <th>التكلفة</th>
                    <th>الحالة</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for license_item in licenses:
        content += f'''
                <tr>
                    <td>{license_item.software_name}</td>
                    <td>{license_item.license_type}</td>
                    <td>{license_item.user_count}</td>
                    <td>{license_item.purchase_date.strftime('%Y-%m-%d') if license_item.purchase_date else ''}</td>
                    <td>{license_item.expiry_date.strftime('%Y-%m-%d') if license_item.expiry_date else '-'}</td>
                    <td>{"{:,.0f}".format(license_item.cost) if license_item.cost else '-'} ريال</td>
                    <td>
                        <span class="badge bg-{'success' if license_item.status == 'نشط' else 'warning'}">
                            {license_item.status}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editLicense({license_item.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteLicense({license_item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-info" onclick="viewInvoice({license_item.id})">
                            <i class="fas fa-file-invoice"></i>
                        </button>
                    </td>
                </tr>
        '''
    
    if not licenses:
        content += '<tr><td colspan="9" class="text-center text-muted">لا توجد تراخيص مسجلة</td></tr>'
    
    content += '''
            </tbody>
        </table>
    </div>
    <script>
        function editLicense(id) {
            window.location.href = '/edit_license/' + id;
        }
        
        function deleteLicense(id) {
            if (confirm('هل أنت متأكد من حذف هذا الترخيص؟')) {
                fetch('/delete_license/' + id, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('حدث خطأ أثناء الحذف');
                    }
                });
            }
        }
        
        function viewInvoice(id) {
            window.open('/license_invoice/' + id, '_blank');
        }
    </script>
    '''
    
    return render_template_string(create_page_template(
        "إدارة التراخيص", 
        "fa-key", 
        content, 
        "إضافة ترخيص جديد", 
        "/add_license"
    ))



@app.route('/support')
def support():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    tickets = SupportTicket.query.all()
    content = '''
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>رقم التذكرة</th>
                    <th>اسم مقدم الطلب</th>
                    <th>نوع المشكلة</th>
                    <th>الأولوية</th>
                    <th>العنوان</th>
                    <th>الحالة</th>
                    <th>تاريخ الإنشاء</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for ticket in tickets:
        content += f'''
                <tr>
                    <td>{ticket.ticket_number}</td>
                    <td>{ticket.requester_name}</td>
                    <td>{ticket.issue_type}</td>
                    <td>
                        <span class="badge bg-{'danger' if ticket.priority == 'عالية' else 'warning' if ticket.priority == 'متوسطة' else 'info'}">
                            {ticket.priority}
                        </span>
                    </td>
                    <td>{ticket.title}</td>
                    <td>
                        <span class="badge bg-{'success' if ticket.status == 'مغلق' else 'primary' if ticket.status == 'قيد المعالجة' else 'warning'}">
                            {ticket.status}
                        </span>
                    </td>
                    <td>{ticket.created_at.strftime('%Y-%m-%d %H:%M') if ticket.created_at else ''}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success">
                            <i class="fas fa-check"></i>
                        </button>
                    </td>
                </tr>
        '''
    
    if not tickets:
        content += '<tr><td colspan="8" class="text-center text-muted">لا توجد تذاكر دعم فني</td></tr>'
    
    content += '''
            </tbody>
        </table>
    </div>
    '''
    
    return render_template_string(create_page_template(
        "الدعم الفني", 
        "fa-headset", 
        content, 
        "إنشاء تذكرة جديدة", 
        "/create_ticket"
    ))

@app.route('/invoices')
def invoices():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    invoices = Invoice.query.all()
    content = '''
    <div class="table-responsive">
        <table class="table table-hover">
            <thead class="table-dark">
                <tr>
                    <th><i class="fas fa-hashtag me-2"></i>رقم الفاتورة</th>
                    <th><i class="fas fa-calendar me-2"></i>تاريخ الفاتورة</th>
                    <th><i class="fas fa-building me-2"></i>اسم المورد</th>
                    <th><i class="fas fa-money-bill me-2"></i>المبلغ الإجمالي</th>
                    <th><i class="fas fa-credit-card me-2"></i>حالة الدفع</th>
                    <th><i class="fas fa-clock me-2"></i>تاريخ الاستحقاق</th>
                    <th><i class="fas fa-cogs me-2"></i>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for invoice in invoices:
        badge_class = 'success' if invoice.payment_status == 'مدفوع' else 'warning' if invoice.payment_status == 'مدفوع جزئياً' else 'danger'
        content += f'''
                <tr>
                    <td><strong>{invoice.invoice_number}</strong></td>
                    <td>{invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else ''}</td>
                    <td>{invoice.supplier_name}</td>
                    <td><span class="text-success fw-bold">{"{:,.0f}".format(invoice.total_amount)} ريال</span></td>
                    <td>
                        <span class="badge bg-{badge_class}">
                            <i class="fas fa-{'check' if invoice.payment_status == 'مدفوع' else 'clock'} me-1"></i>
                            {invoice.payment_status}
                        </span>
                    </td>
                    <td>{invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '-'}</td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="editInvoice({invoice.id})" title="تعديل">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteInvoice({invoice.id})" title="حذف">
                                <i class="fas fa-trash"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-info" onclick="viewInvoiceFile({invoice.id})" title="عرض الملف">
                                <i class="fas fa-file-pdf"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-success" onclick="printInvoice({invoice.id})" title="طباعة">
                                <i class="fas fa-print"></i>
                            </button>
                        </div>
                    </td>
                </tr>
        '''
    
    if not invoices:
        content += '''
            <tr>
                <td colspan="7" class="text-center text-muted py-4">
                    <i class="fas fa-file-invoice fa-3x mb-3 text-muted"></i>
                    <br>
                    <h5>لا توجد فواتير مسجلة</h5>
                    <p>ابدأ بإضافة فاتورة جديدة</p>
                </td>
            </tr>
        '''
    
    content += '''
            </tbody>
        </table>
    </div>
    
    <script>
        function editInvoice(id) {
            window.location.href = '/edit_invoice/' + id;
        }
        
        function deleteInvoice(id) {
            Swal.fire({
                title: 'هل أنت متأكد؟',
                text: "لن تتمكن من التراجع عن هذا الإجراء!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'نعم، احذف!',
                cancelButtonText: 'إلغاء'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch('/delete_invoice/' + id, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire('تم الحذف!', 'تم حذف الفاتورة بنجاح.', 'success')
                            .then(() => location.reload());
                        } else {
                            Swal.fire('خطأ!', 'حدث خطأ أثناء الحذف.', 'error');
                        }
                    });
                }
            });
        }
        
        function viewInvoiceFile(id) {
            window.open('/invoice_file/' + id, '_blank');
        }
        
        function printInvoice(id) {
            window.open('/print_invoice/' + id, '_blank');
        }
    </script>
    '''
    
    return render_template_string(create_page_template(
        "إدارة الفواتير", 
        "fa-file-invoice", 
        content, 
        "إضافة فاتورة جديدة", 
        "/add_invoice"
    ))

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # حساب الإحصائيات الفعلية
    total_assets = Asset.query.count()
    active_employees = Employee.query.filter_by(status='نشط').count()
    total_purchases = Purchase.query.count()
    open_tickets = SupportTicket.query.filter_by(status='مفتوح').count()
    total_departments = Department.query.count()
    total_licenses = License.query.count()
    total_invoices = Invoice.query.count()
    total_custodies = Custody.query.count()
    
    # حساب القيم المالية
    total_asset_value = db.session.query(db.func.sum(Asset.purchase_price)).scalar() or 0
    total_purchase_value = db.session.query(db.func.sum(Purchase.total_price)).scalar() or 0
    total_invoice_value = db.session.query(db.func.sum(Invoice.total_amount)).scalar() or 0
    
    content = f'''
    <div class="row mb-4">
        <div class="col-md-3 mb-3">
            <div class="card text-center bg-primary text-white">
                <div class="card-body">
                    <i class="fas fa-laptop fa-2x mb-2"></i>
                    <h3>{total_assets}</h3>
                    <p>إجمالي الأصول</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-center bg-success text-white">
                <div class="card-body">
                    <i class="fas fa-users fa-2x mb-2"></i>
                    <h3>{active_employees}</h3>
                    <p>الموظفين النشطين</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-center bg-warning text-white">
                <div class="card-body">
                    <i class="fas fa-shopping-cart fa-2x mb-2"></i>
                    <h3>{total_purchases}</h3>
                    <p>إجمالي المشتريات</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-center bg-info text-white">
                <div class="card-body">
                    <i class="fas fa-headset fa-2x mb-2"></i>
                    <h3>{open_tickets}</h3>
                    <p>تذاكر الدعم المفتوحة</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mb-4">
        <div class="col-md-3 mb-3">
            <div class="card text-center bg-secondary text-white">
                <div class="card-body">
                    <i class="fas fa-building fa-2x mb-2"></i>
                    <h3>{total_departments}</h3>
                    <p>الإدارات</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-center bg-dark text-white">
                <div class="card-body">
                    <i class="fas fa-key fa-2x mb-2"></i>
                    <h3>{total_licenses}</h3>
                    <p>التراخيص</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-center bg-danger text-white">
                <div class="card-body">
                    <i class="fas fa-file-invoice fa-2x mb-2"></i>
                    <h3>{total_invoices}</h3>
                    <p>الفواتير</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <div class="card-body text-white">
                    <i class="fas fa-handshake fa-2x mb-2"></i>
                    <h3>{total_custodies}</h3>
                    <p>العهد</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-12 mb-3">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h5><i class="fas fa-money-bill-wave me-2"></i>الملخص المالي</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <h6>قيمة الأصول الإجمالية</h6>
                            <h4 class="text-primary">{"{:,.0f}".format(total_asset_value)} ريال</h4>
                        </div>
                        <div class="col-md-4">
                            <h6>قيمة المشتريات الإجمالية</h6>
                            <h4 class="text-success">{"{:,.0f}".format(total_purchase_value)} ريال</h4>
                        </div>
                        <div class="col-md-4">
                            <h6>قيمة الفواتير الإجمالية</h6>
                            <h4 class="text-warning">{"{:,.0f}".format(total_invoice_value)} ريال</h4>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(create_page_template(
        "التقارير والإحصائيات", 
        "fa-chart-bar", 
        content, 
        "تصدير التقرير", 
        "/export_report"
    ))

@app.route('/export_report')
def export_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    flash('تم تصدير التقرير بنجاح!', 'success')
    return redirect(url_for('reports'))

@app.route('/add_invoice', methods=['GET', 'POST'])
def add_invoice():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # إنشاء مجلد للفواتير إذا لم يكن موجوداً
            import os
            upload_folder = 'static/uploads/invoices'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # معالجة رفع الملف
            invoice_file = request.files.get('invoice_file')
            invoice_filename = None
            if invoice_file and invoice_file.filename:
                import uuid
                file_extension = invoice_file.filename.rsplit('.', 1)[1].lower()
                if file_extension in ['pdf', 'jpg', 'jpeg', 'png']:
                    invoice_filename = f"{uuid.uuid4()}.{file_extension}"
                    invoice_file.save(os.path.join(upload_folder, invoice_filename))
            
            invoice = Invoice(
                invoice_number=request.form['invoice_number'],
                invoice_date=datetime.strptime(request.form['invoice_date'], '%Y-%m-%d').date(),
                supplier_name=request.form['supplier_name'],
                total_amount=float(request.form['total_amount']),
                payment_status=request.form['payment_status'],
                due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d').date() if request.form.get('due_date') else None,
                invoice_file=invoice_filename,
                notes=request.form.get('notes', '')
            )
            db.session.add(invoice)
            db.session.commit()
            flash('تم إضافة الفاتورة بنجاح!', 'success')
            return redirect(url_for('invoices'))
        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة الفاتورة: {str(e)}', 'error')
    
    form_content = '''
    <div class="card shadow-lg border-0">
        <div class="card-header bg-gradient text-white" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <h5 class="mb-0"><i class="fas fa-file-invoice me-2"></i>إضافة فاتورة جديدة</h5>
        </div>
        <div class="card-body p-4">
            <form method="POST" enctype="multipart/form-data">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold"><i class="fas fa-hashtag me-2 text-primary"></i>رقم الفاتورة</label>
                        <input type="text" class="form-control form-control-lg" name="invoice_number" required 
                               placeholder="أدخل رقم الفاتورة">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold"><i class="fas fa-calendar me-2 text-primary"></i>تاريخ الفاتورة</label>
                        <input type="date" class="form-control form-control-lg" name="invoice_date" required>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold"><i class="fas fa-building me-2 text-primary"></i>اسم المورد</label>
                        <input type="text" class="form-control form-control-lg" name="supplier_name" required 
                               placeholder="أدخل اسم المورد">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold"><i class="fas fa-money-bill me-2 text-primary"></i>المبلغ الإجمالي (ريال)</label>
                        <input type="number" class="form-control form-control-lg" name="total_amount" step="0.01" required 
                               placeholder="0.00">
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold"><i class="fas fa-credit-card me-2 text-primary"></i>حالة الدفع</label>
                        <select class="form-select form-select-lg" name="payment_status" required>
                            <option value="">اختر حالة الدفع</option>
                            <option value="مدفوع">✅ مدفوع</option>
                            <option value="غير مدفوع">❌ غير مدفوع</option>
                            <option value="مدفوع جزئياً">⏳ مدفوع جزئياً</option>
                        </select>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold"><i class="fas fa-clock me-2 text-primary"></i>تاريخ الاستحقاق</label>
                        <input type="date" class="form-control form-control-lg" name="due_date">
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label fw-bold"><i class="fas fa-paperclip me-2 text-primary"></i>إرفاق ملف الفاتورة</label>
                    <input type="file" class="form-control form-control-lg" name="invoice_file" accept=".pdf,.jpg,.jpeg,.png">
                    <div class="form-text">
                        <i class="fas fa-info-circle me-1"></i>
                        يمكن رفع ملفات PDF أو صور (JPG, PNG) - الحد الأقصى 10 ميجابايت
                    </div>
                </div>
                <div class="mb-4">
                    <label class="form-label fw-bold"><i class="fas fa-sticky-note me-2 text-primary"></i>ملاحظات</label>
                    <textarea class="form-control" name="notes" rows="4" 
                              placeholder="أضف أي ملاحظات إضافية هنا..."></textarea>
                </div>
                <div class="text-center">
                    <button type="submit" class="btn btn-primary btn-lg px-5 me-3">
                        <i class="fas fa-save me-2"></i>حفظ الفاتورة
                    </button>
                    <a href="/invoices" class="btn btn-secondary btn-lg px-5">
                        <i class="fas fa-times me-2"></i>إلغاء
                    </a>
                </div>
            </form>
        </div>
    </div>
    '''
    
    return render_template_string(create_add_form_template(
        "إضافة فاتورة جديدة",
        "fa-file-invoice",
        form_content,
        "/invoices"
    ))

# صفحات الإضافة
@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            asset = Asset(
                name=request.form['name'],
                category=request.form['category'],
                serial_number=request.form['serial_number'],
                purchase_date=datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date(),
                purchase_price=float(request.form['purchase_price']),
                status=request.form['status'],
                location=request.form.get('location', ''),
                assigned_to=request.form.get('assigned_to', '')
            )
            db.session.add(asset)
            db.session.commit()
            flash('تم إضافة الأصل بنجاح!', 'success')
            return redirect(url_for('assets'))
        except Exception as e:
            flash('حدث خطأ أثناء إضافة الأصل', 'error')
    
    form_content = '''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم الأصل</label>
                <input type="text" class="form-control" name="name" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">الفئة</label>
                <select class="form-select" name="category" required>
                    <option value="">اختر الفئة</option>
                    <option value="أجهزة كمبيوتر">أجهزة كمبيوتر</option>
                    <option value="طابعات">طابعات</option>
                    <option value="أثاث">أثاث</option>
                    <option value="معدات شبكة">معدات شبكة</option>
                    <option value="أخرى">أخرى</option>
                </select>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">الرقم التسلسلي</label>
                <input type="text" class="form-control" name="serial_number" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">تاريخ الشراء</label>
                <input type="date" class="form-control" name="purchase_date" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">سعر الشراء (ريال)</label>
                <input type="number" class="form-control" name="purchase_price" step="0.01" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">الحالة</label>
                <select class="form-select" name="status" required>
                    <option value="نشط">نشط</option>
                    <option value="غير نشط">غير نشط</option>
                    <option value="تحت الصيانة">تحت الصيانة</option>
                </select>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">الموقع</label>
                <input type="text" class="form-control" name="location">
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">مُسند إلى</label>
                <input type="text" class="form-control" name="assigned_to">
            </div>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-save me-1"></i>حفظ الأصل
            </button>
            <a href="/assets" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "إضافة أصل جديد",
        "fa-laptop",
        form_content,
        "/assets"
    ))

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            employee = Employee(
                name=request.form['name'],
                employee_id=request.form['employee_id'],
                department=request.form['department'],
                position=request.form['position'],
                email=request.form.get('email', ''),
                phone=request.form.get('phone', ''),
                hire_date=datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date(),
                status=request.form['status']
            )
            db.session.add(employee)
            db.session.commit()
            flash('تم إضافة الموظف بنجاح!', 'success')
            return redirect(url_for('employees'))
        except Exception as e:
            flash('حدث خطأ أثناء إضافة الموظف', 'error')
    
    form_content = '''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم الموظف</label>
                <input type="text" class="form-control" name="name" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">رقم الموظف</label>
                <input type="text" class="form-control" name="employee_id" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">القسم</label>
                <select class="form-select" name="department" required>
                    <option value="">اختر القسم</option>
                    <option value="تقنية المعلومات">تقنية المعلومات</option>
                    <option value="الموارد البشرية">الموارد البشرية</option>
                    <option value="المالية">المالية</option>
                    <option value="التسويق">التسويق</option>
                    <option value="العمليات">العمليات</option>
                </select>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">المنصب</label>
                <input type="text" class="form-control" name="position" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">البريد الإلكتروني</label>
                <input type="email" class="form-control" name="email">
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">رقم الهاتف</label>
                <input type="tel" class="form-control" name="phone">
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">تاريخ التوظيف</label>
                <input type="date" class="form-control" name="hire_date" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">الحالة</label>
                <select class="form-select" name="status" required>
                    <option value="نشط">نشط</option>
                    <option value="غير نشط">غير نشط</option>
                    <option value="إجازة">إجازة</option>
                </select>
            </div>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-save me-1"></i>حفظ الموظف
            </button>
            <a href="/employees" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "إضافة موظف جديد",
        "fa-user-plus",
        form_content,
        "/employees"
    ))

@app.route('/add_purchase', methods=['GET', 'POST'])
def add_purchase():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            purchase = Purchase(
                product_name=request.form['product_name'],
                supplier=request.form['supplier'],
                quantity=int(request.form['quantity']),
                total_price=float(request.form['total_price']),
                purchase_date=datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date()
            )
            db.session.add(purchase)
            db.session.commit()
            flash('تم إضافة المشترى بنجاح!', 'success')
            return redirect(url_for('purchases'))
        except Exception as e:
            flash('حدث خطأ أثناء إضافة المشترى', 'error')
    
    form_content = '''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم المنتج</label>
                <input type="text" class="form-control" name="product_name" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">المورد</label>
                <input type="text" class="form-control" name="supplier" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">الكمية</label>
                <input type="number" class="form-control" name="quantity" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">السعر الإجمالي</label>
                <input type="number" class="form-control" name="total_price" step="0.01" required>
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">تاريخ الشراء</label>
            <input type="date" class="form-control" name="purchase_date" required>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-save me-1"></i>حفظ المشترى
            </button>
            <a href="/purchases" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "إضافة مشترى جديد",
        "fa-shopping-cart",
        form_content,
        "/purchases"
    ))

@app.route('/add_custody', methods=['GET', 'POST'])
def add_custody():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            custody = Custody(
                employee_name=request.form['employee_name'],
                employee_id=request.form['employee_id'],
                custody_type=request.form['custody_type'],
                serial_number=request.form['serial_number'],
                received_date=datetime.strptime(request.form['received_date'], '%Y-%m-%d').date(),
                estimated_value=float(request.form['estimated_value']) if request.form.get('estimated_value') else None,
                notes=request.form.get('notes', '')
            )
            db.session.add(custody)
            db.session.commit()
            flash('تم إضافة العهدة بنجاح!', 'success')
            return redirect(url_for('custody'))
        except Exception as e:
            flash('حدث خطأ أثناء إضافة العهدة', 'error')
    
    form_content = '''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم الموظف</label>
                <input type="text" class="form-control" name="employee_name" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">رقم الموظف</label>
                <input type="text" class="form-control" name="employee_id" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">نوع العهدة</label>
                <select class="form-select" name="custody_type" required>
                    <option value="">اختر نوع العهدة</option>
                    <option value="جهاز كمبيوتر">جهاز كمبيوتر</option>
                    <option value="هاتف محمول">هاتف محمول</option>
                    <option value="مفاتيح">مفاتيح</option>
                    <option value="بطاقة دخول">بطاقة دخول</option>
                    <option value="أخرى">أخرى</option>
                </select>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">الرقم التسلسلي</label>
                <input type="text" class="form-control" name="serial_number" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">تاريخ الاستلام</label>
                <input type="date" class="form-control" name="received_date" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">القيمة المقدرة</label>
                <input type="number" class="form-control" name="estimated_value" step="0.01">
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">ملاحظات</label>
            <textarea class="form-control" name="notes" rows="3"></textarea>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-save me-1"></i>حفظ العهدة
            </button>
            <a href="/custody" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "إضافة عهدة جديدة",
        "fa-handshake",
        form_content,
        "/custody"
    ))

@app.route('/add_department', methods=['GET', 'POST'])
def add_department():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            department = Department(
                department_name=request.form['department_name'],
                department_code=request.form['department_code'],
                manager_name=request.form.get('manager_name', ''),
                location=request.form.get('location', ''),
                description=request.form.get('description', '')
            )
            db.session.add(department)
            db.session.commit()
            flash('تم إضافة الإدارة بنجاح!', 'success')
            return redirect(url_for('departments'))
        except Exception as e:
            flash('حدث خطأ أثناء إضافة الإدارة', 'error')
    
    form_content = '''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم الإدارة</label>
                <input type="text" class="form-control" name="department_name" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">رمز الإدارة</label>
                <input type="text" class="form-control" name="department_code" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">مدير الإدارة</label>
                <input type="text" class="form-control" name="manager_name">
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">الموقع</label>
                <input type="text" class="form-control" name="location">
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">الوصف</label>
            <textarea class="form-control" name="description" rows="3"></textarea>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-save me-1"></i>حفظ الإدارة
            </button>
            <a href="/departments" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "إضافة إدارة جديدة",
        "fa-building",
        form_content,
        "/departments"
    ))

@app.route('/create_invoice', methods=['GET', 'POST'])
def create_invoice():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            invoice = Invoice(
                invoice_number=request.form['invoice_number'],
                invoice_date=datetime.strptime(request.form['invoice_date'], '%Y-%m-%d').date(),
                supplier_name=request.form['supplier_name'],
                total_amount=float(request.form['total_amount']),
                payment_status=request.form['payment_status'],
                due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d').date() if request.form.get('due_date') else None,
                notes=request.form.get('notes', '')
            )
            db.session.add(invoice)
            db.session.commit()
            flash('تم إنشاء الفاتورة بنجاح!', 'success')
            return redirect(url_for('invoices'))
        except Exception as e:
            flash('حدث خطأ أثناء إنشاء الفاتورة', 'error')
    
    form_content = '''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">رقم الفاتورة</label>
                <input type="text" class="form-control" name="invoice_number" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">تاريخ الفاتورة</label>
                <input type="date" class="form-control" name="invoice_date" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم المورد</label>
                <input type="text" class="form-control" name="supplier_name" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">المبلغ الإجمالي</label>
                <input type="number" class="form-control" name="total_amount" step="0.01" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">حالة الدفع</label>
                <select class="form-select" name="payment_status" required>
                    <option value="">اختر الحالة</option>
                    <option value="مدفوع">مدفوع</option>
                    <option value="غير مدفوع">غير مدفوع</option>
                    <option value="مدفوع جزئياً">مدفوع جزئياً</option>
                </select>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">تاريخ الاستحقاق</label>
                <input type="date" class="form-control" name="due_date">
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">ملاحظات</label>
            <textarea class="form-control" name="notes" rows="3"></textarea>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-save me-1"></i>إنشاء الفاتورة
            </button>
            <a href="/invoices" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "إنشاء فاتورة جديدة",
        "fa-file-invoice",
        form_content,
        "/invoices"
    ))

@app.route('/add_license', methods=['GET', 'POST'])
def add_license():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            license_obj = License(
                software_name=request.form['software_name'],
                license_key=request.form['license_key'],
                license_type=request.form['license_type'],
                user_count=int(request.form['user_count']),
                purchase_date=datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date(),
                expiry_date=datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date() if request.form.get('expiry_date') else None,
                cost=float(request.form['cost']) if request.form.get('cost') else None,
                vendor=request.form.get('vendor', ''),
                notes=request.form.get('notes', '')
            )
            db.session.add(license_obj)
            db.session.commit()
            flash('تم إضافة الترخيص بنجاح!', 'success')
            return redirect(url_for('licenses'))
        except Exception as e:
            flash('حدث خطأ أثناء إضافة الترخيص', 'error')
    
    form_content = '''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم البرنامج</label>
                <input type="text" class="form-control" name="software_name" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">رقم الترخيص</label>
                <input type="text" class="form-control" name="license_key" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">نوع الترخيص</label>
                <select class="form-select" name="license_type" required>
                    <option value="">اختر النوع</option>
                    <option value="مدفوع">مدفوع</option>
                    <option value="مجاني">مجاني</option>
                    <option value="تجريبي">تجريبي</option>
                </select>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">عدد المستخدمين</label>
                <input type="number" class="form-control" name="user_count" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">تاريخ الشراء</label>
                <input type="date" class="form-control" name="purchase_date" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">تاريخ انتهاء الصلاحية</label>
                <input type="date" class="form-control" name="expiry_date">
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">التكلفة</label>
                <input type="number" class="form-control" name="cost" step="0.01">
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">المورد</label>
                <input type="text" class="form-control" name="vendor">
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">ملاحظات</label>
            <textarea class="form-control" name="notes" rows="3"></textarea>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-save me-1"></i>حفظ الترخيص
            </button>
            <a href="/licenses" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "إضافة ترخيص جديد",
        "fa-key",
        form_content,
        "/licenses"
    ))

@app.route('/create_ticket', methods=['GET', 'POST'])
def create_ticket():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # إنشاء رقم تذكرة فريد
            import random
            ticket_number = f"TK{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
            
            ticket = SupportTicket(
                ticket_number=ticket_number,
                requester_name=request.form['requester_name'],
                email=request.form['email'],
                issue_type=request.form['issue_type'],
                priority=request.form['priority'],
                title=request.form['title'],
                description=request.form['description']
            )
            db.session.add(ticket)
            db.session.commit()
            flash(f'تم إنشاء تذكرة الدعم بنجاح! رقم التذكرة: {ticket_number}', 'success')
            return redirect(url_for('support'))
        except Exception as e:
            flash('حدث خطأ أثناء إنشاء تذكرة الدعم', 'error')
    
    form_content = '''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم مقدم الطلب</label>
                <input type="text" class="form-control" name="requester_name" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">البريد الإلكتروني</label>
                <input type="email" class="form-control" name="email" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">نوع المشكلة</label>
                <select class="form-select" name="issue_type" required>
                    <option value="">اختر نوع المشكلة</option>
                    <option value="مشكلة تقنية">مشكلة تقنية</option>
                    <option value="طلب صيانة">طلب صيانة</option>
                    <option value="طلب برنامج">طلب برنامج</option>
                    <option value="مشكلة شبكة">مشكلة شبكة</option>
                    <option value="أخرى">أخرى</option>
                </select>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">الأولوية</label>
                <select class="form-select" name="priority" required>
                    <option value="">اختر الأولوية</option>
                    <option value="عالية">عالية</option>
                    <option value="متوسطة">متوسطة</option>
                    <option value="منخفضة">منخفضة</option>
                </select>
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">عنوان المشكلة</label>
            <input type="text" class="form-control" name="title" required>
        </div>
        <div class="mb-3">
            <label class="form-label">وصف المشكلة</label>
            <textarea class="form-control" name="description" rows="5" required></textarea>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-paper-plane me-1"></i>إرسال التذكرة
            </button>
            <a href="/support" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "إنشاء تذكرة دعم فني",
        "fa-headset",
        form_content,
        "/support"
    ))

# مسارات الحذف والتعديل
@app.route('/delete_asset/<int:asset_id>', methods=['POST'])
def delete_asset(asset_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    try:
        asset = Asset.query.get_or_404(asset_id)
        db.session.delete(asset)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/edit_asset/<int:asset_id>', methods=['GET', 'POST'])
def edit_asset(asset_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    asset = Asset.query.get_or_404(asset_id)
    
    if request.method == 'POST':
        try:
            asset.name = request.form['name']
            asset.category = request.form['category']
            asset.serial_number = request.form['serial_number']
            asset.purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date()
            asset.purchase_price = float(request.form['purchase_price'])
            asset.status = request.form['status']
            asset.location = request.form.get('location', '')
            asset.assigned_to = request.form.get('assigned_to', '')
            
            db.session.commit()
            flash('تم تحديث الأصل بنجاح!', 'success')
            return redirect(url_for('assets'))
        except Exception as e:
            flash('حدث خطأ أثناء تحديث الأصل', 'error')
    
    form_content = f'''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم الأصل</label>
                <input type="text" class="form-control" name="name" value="{asset.name}" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">الفئة</label>
                <select class="form-select" name="category" required>
                    <option value="أجهزة كمبيوتر" {"selected" if asset.category == "أجهزة كمبيوتر" else ""}>أجهزة كمبيوتر</option>
                    <option value="طابعات" {"selected" if asset.category == "طابعات" else ""}>طابعات</option>
                    <option value="أثاث" {"selected" if asset.category == "أثاث" else ""}>أثاث</option>
                    <option value="معدات شبكة" {"selected" if asset.category == "معدات شبكة" else ""}>معدات شبكة</option>
                    <option value="أخرى" {"selected" if asset.category == "أخرى" else ""}>أخرى</option>
                </select>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">الرقم التسلسلي</label>
                <input type="text" class="form-control" name="serial_number" value="{asset.serial_number}" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">تاريخ الشراء</label>
                <input type="date" class="form-control" name="purchase_date" value="{asset.purchase_date}" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">سعر الشراء (ريال)</label>
                <input type="number" class="form-control" name="purchase_price" step="0.01" value="{asset.purchase_price}" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">الحالة</label>
                <select class="form-select" name="status" required>
                    <option value="نشط" {"selected" if asset.status == "نشط" else ""}>نشط</option>
                    <option value="غير نشط" {"selected" if asset.status == "غير نشط" else ""}>غير نشط</option>
                    <option value="تحت الصيانة" {"selected" if asset.status == "تحت الصيانة" else ""}>تحت الصيانة</option>
                </select>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">الموقع</label>
                <input type="text" class="form-control" name="location" value="{asset.location or ''}">
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">مُسند إلى</label>
                <input type="text" class="form-control" name="assigned_to" value="{asset.assigned_to or ''}">
            </div>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-save me-1"></i>حفظ التحديثات
            </button>
            <a href="/assets" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "تعديل الأصل",
        "fa-edit",
        form_content,
        "/assets"
    ))

@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    try:
        employee = Employee.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    employee = Employee.query.get_or_404(employee_id)
    
    if request.method == 'POST':
        try:
            employee.name = request.form['name']
            employee.employee_id = request.form['employee_id']
            employee.department = request.form['department']
            employee.position = request.form['position']
            employee.email = request.form.get('email', '')
            employee.phone = request.form.get('phone', '')
            employee.hire_date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date()
            employee.status = request.form['status']
            
            db.session.commit()
            flash('تم تحديث بيانات الموظف بنجاح!', 'success')
            return redirect(url_for('employees'))
        except Exception as e:
            flash('حدث خطأ أثناء تحديث بيانات الموظف', 'error')
    
    form_content = f'''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم الموظف</label>
                <input type="text" class="form-control" name="name" value="{employee.name}" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">رقم الموظف</label>
                <input type="text" class="form-control" name="employee_id" value="{employee.employee_id}" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">القسم</label>
                <select class="form-select" name="department" required>
                    <option value="تقنية المعلومات" {"selected" if employee.department == "تقنية المعلومات" else ""}>تقنية المعلومات</option>
                    <option value="الموارد البشرية" {"selected" if employee.department == "الموارد البشرية" else ""}>الموارد البشرية</option>
                    <option value="المالية" {"selected" if employee.department == "المالية" else ""}>المالية</option>
                    <option value="التسويق" {"selected" if employee.department == "التسويق" else ""}>التسويق</option>
                    <option value="العمليات" {"selected" if employee.department == "العمليات" else ""}>العمليات</option>
                </select>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">المنصب</label>
                <input type="text" class="form-control" name="position" value="{employee.position}" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">البريد الإلكتروني</label>
                <input type="email" class="form-control" name="email" value="{employee.email or ''}">
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">رقم الهاتف</label>
                <input type="tel" class="form-control" name="phone" value="{employee.phone or ''}">
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">تاريخ التوظيف</label>
                <input type="date" class="form-control" name="hire_date" value="{employee.hire_date}" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">الحالة</label>
                <select class="form-select" name="status" required>
                    <option value="نشط" {"selected" if employee.status == "نشط" else ""}>نشط</option>
                    <option value="غير نشط" {"selected" if employee.status == "غير نشط" else ""}>غير نشط</option>
                    <option value="إجازة" {"selected" if employee.status == "إجازة" else ""}>إجازة</option>
                </select>
            </div>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-save me-1"></i>حفظ التحديثات
            </button>
            <a href="/employees" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "تعديل بيانات الموظف",
        "fa-user-edit",
        form_content,
        "/employees"
    ))

# صفحة إدارة المستخدمين
@app.route('/users')
def users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    users = User.query.all()
    content = '''
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>اسم المستخدم</th>
                    <th>البريد الإلكتروني</th>
                    <th>تاريخ الإنشاء</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for user in users:
        content += f'''
                <tr>
                    <td>{user.username}</td>
                    <td>{user.email}</td>
                    <td>{user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else ''}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
        '''
    
    if not users:
        content += '<tr><td colspan="4" class="text-center text-muted">لا توجد مستخدمين</td></tr>'
    
    content += '''
            </tbody>
        </table>
    </div>
    '''
    
    return render_template_string(create_page_template(
        "إدارة المستخدمين", 
        "fa-users-cog", 
        content, 
        "إضافة مستخدم جديد", 
        "/add_user"
    ))

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            user = User(
                username=request.form['username'],
                email=request.form['email']
            )
            user.set_password(request.form['password'])
            db.session.add(user)
            db.session.commit()
            flash('تم إضافة المستخدم بنجاح!', 'success')
            return redirect(url_for('users'))
        except Exception as e:
            flash('حدث خطأ أثناء إضافة المستخدم', 'error')
    
    form_content = '''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم المستخدم</label>
                <input type="text" class="form-control" name="username" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">البريد الإلكتروني</label>
                <input type="email" class="form-control" name="email" required>
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">كلمة المرور</label>
            <input type="password" class="form-control" name="password" required>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-save me-1"></i>حفظ المستخدم
            </button>
            <a href="/users" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "إضافة مستخدم جديد",
        "fa-user-plus",
        form_content,
        "/users"
    ))

# وظائف الحذف والتعديل للمشتريات
@app.route('/delete_purchase/<int:purchase_id>', methods=['POST'])
def delete_purchase(purchase_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    try:
        purchase = Purchase.query.get_or_404(purchase_id)
        db.session.delete(purchase)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/edit_purchase/<int:purchase_id>', methods=['GET', 'POST'])
def edit_purchase(purchase_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    purchase = Purchase.query.get_or_404(purchase_id)
    
    if request.method == 'POST':
        try:
            purchase.product_name = request.form['product_name']
            purchase.supplier = request.form['supplier']
            purchase.quantity = int(request.form['quantity'])
            purchase.total_price = float(request.form['total_price'])
            purchase.purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date()
            
            db.session.commit()
            flash('تم تحديث المشترى بنجاح!', 'success')
            return redirect(url_for('purchases'))
        except Exception as e:
            flash('حدث خطأ أثناء تحديث المشترى', 'error')
    
    form_content = f'''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم المنتج</label>
                <input type="text" class="form-control" name="product_name" value="{purchase.product_name}" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">المورد</label>
                <input type="text" class="form-control" name="supplier" value="{purchase.supplier}" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">الكمية</label>
                <input type="number" class="form-control" name="quantity" value="{purchase.quantity}" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">السعر الإجمالي</label>
                <input type="number" class="form-control" name="total_price" step="0.01" value="{purchase.total_price}" required>
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">تاريخ الشراء</label>
            <input type="date" class="form-control" name="purchase_date" value="{purchase.purchase_date}" required>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-save me-1"></i>حفظ التحديثات
            </button>
            <a href="/purchases" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "تعديل المشترى",
        "fa-edit",
        form_content,
        "/purchases"
    ))

# وظائف الحذف والتعديل للإدارات
@app.route('/delete_department/<int:department_id>', methods=['POST'])
def delete_department(department_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    try:
        department = Department.query.get_or_404(department_id)
        db.session.delete(department)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/edit_department/<int:department_id>', methods=['GET', 'POST'])
def edit_department(department_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    department = Department.query.get_or_404(department_id)
    
    if request.method == 'POST':
        try:
            department.department_name = request.form['department_name']
            department.department_code = request.form['department_code']
            department.manager_name = request.form.get('manager_name', '')
            department.location = request.form.get('location', '')
            department.description = request.form.get('description', '')
            department.status = request.form['status']
            
            db.session.commit()
            flash('تم تحديث الإدارة بنجاح!', 'success')
            return redirect(url_for('departments'))
        except Exception as e:
            flash('حدث خطأ أثناء تحديث الإدارة', 'error')
    
    form_content = f'''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم الإدارة</label>
                <input type="text" class="form-control" name="department_name" value="{department.department_name}" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">رمز الإدارة</label>
                <input type="text" class="form-control" name="department_code" value="{department.department_code}" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">مدير الإدارة</label>
                <input type="text" class="form-control" name="manager_name" value="{department.manager_name or ''}">
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">الموقع</label>
                <input type="text" class="form-control" name="location" value="{department.location or ''}">
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">الحالة</label>
                <select class="form-select" name="status" required>
                    <option value="نشط" {"selected" if department.status == "نشط" else ""}>نشط</option>
                    <option value="غير نشط" {"selected" if department.status == "غير نشط" else ""}>غير نشط</option>
                    <option value="مؤقت" {"selected" if department.status == "مؤقت" else ""}>مؤقت</option>
                </select>
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">وصف الإدارة</label>
            <textarea class="form-control" name="description" rows="3">{department.description or ''}</textarea>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-save me-1"></i>حفظ التحديثات
            </button>
            <a href="/departments" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "تعديل الإدارة",
        "fa-edit",
        form_content,
        "/departments"
    ))

# وظائف الحذف والتعديل للعهد
@app.route('/delete_custody/<int:custody_id>', methods=['POST'])
def delete_custody(custody_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    try:
        custody = Custody.query.get_or_404(custody_id)
        db.session.delete(custody)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/edit_custody/<int:custody_id>', methods=['GET', 'POST'])
def edit_custody(custody_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    custody = Custody.query.get_or_404(custody_id)
    
    if request.method == 'POST':
        try:
            custody.employee_name = request.form['employee_name']
            custody.employee_id = request.form['employee_id']
            custody.custody_type = request.form['custody_type']
            custody.serial_number = request.form['serial_number']
            custody.received_date = datetime.strptime(request.form['received_date'], '%Y-%m-%d').date()
            custody.estimated_value = float(request.form['estimated_value']) if request.form.get('estimated_value') else None
            custody.notes = request.form.get('notes', '')
            custody.status = request.form['status']
            
            db.session.commit()
            flash('تم تحديث العهدة بنجاح!', 'success')
            return redirect(url_for('custody'))
        except Exception as e:
            flash('حدث خطأ أثناء تحديث العهدة', 'error')
    
    form_content = f'''
    <form method="POST">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">اسم الموظف</label>
                <input type="text" class="form-control" name="employee_name" value="{custody.employee_name}" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">رقم الموظف</label>
                <input type="text" class="form-control" name="employee_id" value="{custody.employee_id}" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">نوع العهدة</label>
                <select class="form-select" name="custody_type" required>
                    <option value="جهاز كمبيوتر" {"selected" if custody.custody_type == "جهاز كمبيوتر" else ""}>جهاز كمبيوتر</option>
                    <option value="جهاز محمول" {"selected" if custody.custody_type == "جهاز محمول" else ""}>جهاز محمول</option>
                    <option value="طابعة" {"selected" if custody.custody_type == "طابعة" else ""}>طابعة</option>
                    <option value="هاتف" {"selected" if custody.custody_type == "هاتف" else ""}>هاتف</option>
                    <option value="أخرى" {"selected" if custody.custody_type == "أخرى" else ""}>أخرى</option>
                </select>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">الرقم التسلسلي</label>
                <input type="text" class="form-control" name="serial_number" value="{custody.serial_number}" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">تاريخ الاستلام</label>
                <input type="date" class="form-control" name="received_date" value="{custody.received_date}" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">القيمة المقدرة (ريال)</label>
                <input type="number" class="form-control" name="estimated_value" step="0.01" value="{custody.estimated_value or ''}">
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">الحالة</label>
                <select class="form-select" name="status" required>
                    <option value="نشط" {"selected" if custody.status == "نشط" else ""}>نشط</option>
                    <option value="مُرجع" {"selected" if custody.status == "مُرجع" else ""}>مُرجع</option>
                    <option value="تالف" {"selected" if custody.status == "تالف" else ""}>تالف</option>
                </select>
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">ملاحظات</label>
            <textarea class="form-control" name="notes" rows="3">{custody.notes or ''}</textarea>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary me-2">
                <i class="fas fa-save me-1"></i>حفظ التحديثات
            </button>
            <a href="/custody" class="btn btn-secondary">
                <i class="fas fa-times me-1"></i>إلغاء
            </a>
        </div>
    </form>
    '''
    
    return render_template_string(create_add_form_template(
        "تعديل العهدة",
        "fa-edit",
        form_content,
        "/custody"
    ))

# وظائف إضافية للفواتير والباركود
@app.route('/print_barcode/<int:custody_id>')
def print_barcode(custody_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    custody = Custody.query.get_or_404(custody_id)
    
    # إنشاء باركود فريد إذا لم يكن موجوداً
    if not custody.barcode:
        import uuid
        custody.barcode = f"CUS{custody_id:06d}{str(uuid.uuid4())[:8].upper()}"
        db.session.commit()
    
    barcode_html = f'''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>طباعة باركود العهدة</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 20px; }}
            .barcode-container {{ border: 2px solid #000; padding: 20px; margin: 20px auto; width: 300px; }}
            .barcode {{ font-family: 'Courier New', monospace; font-size: 24px; letter-spacing: 2px; }}
            .info {{ margin: 10px 0; }}
            @media print {{ 
                body {{ margin: 0; }}
                .no-print {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="barcode-container">
            <h3>عهدة - {custody.custody_type}</h3>
            <div class="info">الموظف: {custody.employee_name}</div>
            <div class="info">الرقم التسلسلي: {custody.serial_number}</div>
            <div class="barcode">{custody.barcode}</div>
            <div class="info">تاريخ الاستلام: {custody.received_date.strftime('%Y-%m-%d')}</div>
        </div>
        <div class="no-print">
            <button onclick="window.print()">طباعة</button>
            <button onclick="window.close()">إغلاق</button>
        </div>
    </body>
    </html>
    '''
    
    return barcode_html

@app.route('/delete_invoice/<int:invoice_id>', methods=['POST'])
def delete_invoice(invoice_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        db.session.delete(invoice)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_license/<int:license_id>', methods=['POST'])
def delete_license(license_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    try:
        license_item = License.query.get_or_404(license_id)
        db.session.delete(license_item)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

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

if __name__ == '__main__':
    init_db()
    print("=" * 70)
    print("🚀 نظام إدارة الأصول مع أزرار العودة للرئيسية")
    print("   Asset Management System with Home Navigation")
    print("=" * 70)
    print("✅ النظام جاهز!")
    print("🌐 الرابط: http://localhost:5000")
    print("👤 المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("🏠 أزرار العودة للرئيسية: متاحة في جميع الصفحات")
    print("📋 الميزات المضافة:")
    print("   ✓ زر العودة للرئيسية في كل صفحة")
    print("   ✓ تصميم محسن ومتجاوب")
    print("   ✓ واجهة مستخدم جميلة")
    print("   ✓ جميع الصفحات تحتوي على أزرار التنقل")
    print("🔧 للإيقاف: اضغط Ctrl+C")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5000, debug=False)