#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام إدارة الأصول الاحترافي - تصميم متقدم وجميل
Professional Asset Management System - Advanced Beautiful Design
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

# إنشاء التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///asset_management_pro.db'
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

class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Text)
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

# قالب تسجيل الدخول الاحترافي
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - نظام إدارة الأصول الاحترافي</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Cairo', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            position: relative;
            overflow: hidden;
        }
        
        body::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><polygon fill="%23ffffff08" points="0,1000 1000,0 1000,1000"/></svg>');
            background-size: cover;
        }
        
        .login-container {
            position: relative;
            z-index: 1;
        }
        
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.2);
            overflow: hidden;
            animation: slideUp 0.8s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            position: relative;
        }
        
        .login-header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 20px;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100"><path fill="%23ffffff" d="M0,100 C150,0 350,0 500,50 C650,100 850,100 1000,50 L1000,100 Z"/></svg>');
            background-size: cover;
        }
        
        .logo-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            text-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
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
            transform: translateY(-2px);
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
            position: relative;
            overflow: hidden;
        }
        
        .btn-login:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
            color: white;
        }
        
        .btn-login::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .btn-login:hover::before {
            left: 100%;
        }
        
        .floating-shapes {
            position: absolute;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: 0;
        }
        
        .shape {
            position: absolute;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            animation: float 6s ease-in-out infinite;
        }
        
        .shape:nth-child(1) {
            width: 80px;
            height: 80px;
            top: 20%;
            left: 10%;
            animation-delay: 0s;
        }
        
        .shape:nth-child(2) {
            width: 120px;
            height: 120px;
            top: 60%;
            right: 10%;
            animation-delay: 2s;
        }
        
        .shape:nth-child(3) {
            width: 60px;
            height: 60px;
            bottom: 20%;
            left: 20%;
            animation-delay: 4s;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(180deg); }
        }
        
        .input-group {
            position: relative;
            margin-bottom: 1.5rem;
        }
        
        .input-icon {
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: #6c757d;
            z-index: 10;
        }
        
        .form-control.with-icon {
            padding-left: 3rem;
        }
    </style>
</head>
<body>
    <div class="floating-shapes">
        <div class="shape"></div>
        <div class="shape"></div>
        <div class="shape"></div>
    </div>
    
    <div class="container login-container">
        <div class="row justify-content-center">
            <div class="col-lg-5 col-md-7">
                <div class="login-card">
                    <div class="login-header">
                        <div class="logo-icon">
                            <i class="fas fa-building"></i>
                        </div>
                        <h2 class="mb-0">نظام إدارة الأصول</h2>
                        <p class="mb-0 mt-2">مرحباً بك في النظام الاحترافي</p>
                    </div>
                    
                    <div class="card-body p-5">
                        <form method="POST" id="loginForm">
                            <div class="input-group">
                                <i class="fas fa-user input-icon"></i>
                                <input type="text" class="form-control with-icon" name="username" 
                                       placeholder="اسم المستخدم" required>
                            </div>
                            
                            <div class="input-group">
                                <i class="fas fa-lock input-icon"></i>
                                <input type="password" class="form-control with-icon" name="password" 
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
                
                <div class="text-center mt-4">
                    <p class="text-white">
                        <i class="fas fa-info-circle me-2"></i>
                        للدعم الفني: support@company.com
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // تأثيرات تفاعلية
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('loginForm');
            const inputs = document.querySelectorAll('.form-control');
            
            inputs.forEach(input => {
                input.addEventListener('focus', function() {
                    this.parentElement.querySelector('.input-icon').style.color = '#667eea';
                });
                
                input.addEventListener('blur', function() {
                    this.parentElement.querySelector('.input-icon').style.color = '#6c757d';
                });
            });
            
            form.addEventListener('submit', function(e) {
                const button = this.querySelector('.btn-login');
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>جاري التحقق...';
                button.disabled = true;
            });
        });
    </script>
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
    
    return LOGIN_TEMPLATE

# قالب الصفحة الرئيسية الاحترافي
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم - نظام إدارة الأصول الاحترافي</title>
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
            backdrop-filter: blur(10px);
        }
        
        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
        }
        
        .main-container {
            padding: 2rem 0;
        }
        
        .welcome-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 20px;
            padding: 3rem;
            margin-bottom: 3rem;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .welcome-card::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 200px;
            height: 200px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            transform: translate(50%, -50%);
        }
        
        .module-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border: none;
            position: relative;
            overflow: hidden;
        }
        
        .module-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        
        .module-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #2c3e50;
        }
        
        .module-description {
            color: #6c757d;
            margin-bottom: 1.5rem;
            font-size: 0.95rem;
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
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }
        
        .stats-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #667eea;
        }
        
        .stats-label {
            color: #6c757d;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        
        .floating-elements {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }
        
        .floating-element {
            position: absolute;
            background: rgba(102, 126, 234, 0.05);
            border-radius: 50%;
            animation: float 8s ease-in-out infinite;
        }
        
        .floating-element:nth-child(1) {
            width: 100px;
            height: 100px;
            top: 10%;
            left: 10%;
            animation-delay: 0s;
        }
        
        .floating-element:nth-child(2) {
            width: 150px;
            height: 150px;
            top: 50%;
            right: 10%;
            animation-delay: 3s;
        }
        
        .floating-element:nth-child(3) {
            width: 80px;
            height: 80px;
            bottom: 20%;
            left: 20%;
            animation-delay: 6s;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-30px) rotate(180deg); }
        }
    </style>
</head>
<body>
    <div class="floating-elements">
        <div class="floating-element"></div>
        <div class="floating-element"></div>
        <div class="floating-element"></div>
    </div>
    
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-building me-2"></i>
                نظام إدارة الأصول الاحترافي
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>
                    خروج
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container main-container">
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
                <div class="module-card text-center">
                    <div class="module-icon">
                        <i class="fas fa-laptop"></i>
                    </div>
                    <h5 class="module-title">إدارة الأصول</h5>
                    <p class="module-description">
                        إدارة شاملة لجميع أصول الشركة مع تتبع الحالة والموقع والمسؤول
                    </p>
                    <a href="/assets" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>
                        دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card text-center">
                    <div class="module-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <h5 class="module-title">إدارة الموظفين</h5>
                    <p class="module-description">
                        إدارة بيانات الموظفين والأقسام مع تتبع الحالة الوظيفية
                    </p>
                    <a href="/employees" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>
                        دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card text-center">
                    <div class="module-icon">
                        <i class="fas fa-shopping-cart"></i>
                    </div>
                    <h5 class="module-title">إدارة المشتريات</h5>
                    <p class="module-description">
                        تتبع المشتريات والموردين مع إرفاق الفواتير والمستندات
                    </p>
                    <a href="/purchases" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>
                        دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card text-center">
                    <div class="module-icon">
                        <i class="fas fa-handshake"></i>
                    </div>
                    <h5 class="module-title">إدارة العهد</h5>
                    <p class="module-description">
                        إدارة عهد الموظفين مع طباعة الباركود وتتبع الحالة
                    </p>
                    <a href="/custody" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>
                        دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card text-center">
                    <div class="module-icon">
                        <i class="fas fa-file-invoice"></i>
                    </div>
                    <h5 class="module-title">إدارة الفواتير</h5>
                    <p class="module-description">
                        إدارة الفواتير والمدفوعات مع إرفاق الملفات وتتبع الاستحقاق
                    </p>
                    <a href="/invoices" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>
                        دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card text-center">
                    <div class="module-icon">
                        <i class="fas fa-key"></i>
                    </div>
                    <h5 class="module-title">إدارة التراخيص</h5>
                    <p class="module-description">
                        إدارة تراخيص البرامج مع تتبع انتهاء الصلاحية والتجديد
                    </p>
                    <a href="/licenses" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>
                        دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card text-center">
                    <div class="module-icon">
                        <i class="fas fa-building"></i>
                    </div>
                    <h5 class="module-title">إدارة الإدارات</h5>
                    <p class="module-description">
                        إدارة الإدارات والأقسام مع تحديد المسؤولين والمواقع
                    </p>
                    <a href="/departments" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>
                        دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card text-center">
                    <div class="module-icon">
                        <i class="fas fa-headset"></i>
                    </div>
                    <h5 class="module-title">الدعم الفني</h5>
                    <p class="module-description">
                        نظام تذاكر الدعم الفني مع تتبع الحالة والأولوية
                    </p>
                    <a href="/support" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>
                        دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card text-center">
                    <div class="module-icon">
                        <i class="fas fa-users-cog"></i>
                    </div>
                    <h5 class="module-title">إدارة المستخدمين</h5>
                    <p class="module-description">
                        إدارة المستخدمين والصلاحيات مع تحكم كامل في الوصول
                    </p>
                    <a href="/users" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>
                        دخول
                    </a>
                </div>
            </div>
            
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="module-card text-center">
                    <div class="module-icon">
                        <i class="fas fa-chart-bar"></i>
                    </div>
                    <h5 class="module-title">التقارير والإحصائيات</h5>
                    <p class="module-description">
                        تقارير شاملة وإحصائيات تفصيلية مع إمكانية التصدير
                    </p>
                    <a href="/reports" class="btn-module">
                        <i class="fas fa-arrow-left me-2"></i>
                        دخول
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // تأثيرات تفاعلية
        document.addEventListener('DOMContentLoaded', function() {
            // تأثير hover للبطاقات
            const cards = document.querySelectorAll('.module-card');
            cards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-10px) scale(1.02)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0) scale(1)';
                });
            });
            
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
        });
    </script>
</body>
</html>
'''

# الصفحة الرئيسية
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # حساب الإحصائيات
    total_assets = Asset.query.count()
    total_purchases = Purchase.query.count()
    total_custodies = Custody.query.count()
    total_invoices = Invoice.query.count()
    
    return render_template_string(DASHBOARD_TEMPLATE, 
        username=session.get('username', 'المستخدم'),
        total_assets=total_assets,
        total_purchases=total_purchases,
        total_custodies=total_custodies,
        total_invoices=total_invoices
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# قالب الصفحات الداخلية الاحترافي
def create_page_template(title, icon, content, add_button_text="", add_button_link=""):
    return f'''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - نظام إدارة الأصول الاحترافي</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        body {{
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        
        .navbar {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }}
        
        .navbar-brand {{
            font-weight: 700;
            font-size: 1.3rem;
        }}
        
        .main-container {{
            padding: 2rem 0;
        }}
        
        .page-header {{
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
        }}
        
        .page-header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .page-title {{
            color: #2c3e50;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .page-subtitle {{
            color: #6c757d;
            margin-bottom: 0;
        }}
        
        .content-card {{
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border: none;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 15px;
            padding: 0.8rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-home {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            border: none;
            border-radius: 15px;
            padding: 0.8rem 2rem;
            color: white;
            font-weight: 600;
            transition: all 0.3s ease;
            text-decoration: none;
        }}
        
        .btn-home:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(40, 167, 69, 0.4);
            color: white;
        }}
        
        .table {{
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }}
        
        .table thead th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
            padding: 1rem;
        }}
        
        .table tbody tr {{
            transition: all 0.3s ease;
        }}
        
        .table tbody tr:hover {{
            background-color: #f8f9fa;
            transform: scale(1.01);
        }}
        
        .btn-group .btn {{
            border-radius: 10px;
            margin: 0 2px;
            transition: all 0.3s ease;
        }}
        
        .btn-group .btn:hover {{
            transform: translateY(-2px);
        }}
        
        .empty-state {{
            text-align: center;
            padding: 4rem 2rem;
            color: #6c757d;
        }}
        
        .empty-state i {{
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }}
        
        .floating-elements {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }}
        
        .floating-element {{
            position: absolute;
            background: rgba(102, 126, 234, 0.03);
            border-radius: 50%;
            animation: float 12s ease-in-out infinite;
        }}
        
        .floating-element:nth-child(1) {{
            width: 120px;
            height: 120px;
            top: 15%;
            left: 10%;
            animation-delay: 0s;
        }}
        
        .floating-element:nth-child(2) {{
            width: 80px;
            height: 80px;
            top: 60%;
            right: 15%;
            animation-delay: 4s;
        }}
        
        .floating-element:nth-child(3) {{
            width: 100px;
            height: 100px;
            bottom: 20%;
            left: 20%;
            animation-delay: 8s;
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
            50% {{ transform: translateY(-20px) rotate(180deg); }}
        }}
    </style>
</head>
<body>
    <div class="floating-elements">
        <div class="floating-element"></div>
        <div class="floating-element"></div>
        <div class="floating-element"></div>
    </div>
    
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
    
    <div class="container main-container">
        <div class="page-header">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h2 class="page-title">
                        <i class="fas {icon} me-2"></i>
                        {title}
                    </h2>
                    <p class="page-subtitle">إدارة شاملة ومتقدمة للبيانات</p>
                </div>
                <div class="col-md-4 text-end">
                    <a href="/dashboard" class="btn btn-home me-2">
                        <i class="fas fa-home me-1"></i>
                        الرئيسية
                    </a>
                    {f'<a href="{add_button_link}" class="btn btn-primary"><i class="fas fa-plus me-1"></i>{add_button_text}</a>' if add_button_text else ''}
                </div>
            </div>
        </div>
        
        <div class="content-card">
            {content}
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# صفحة إدارة الأصول
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
                    <th><i class="fas fa-tag me-2"></i>اسم الأصل</th>
                    <th><i class="fas fa-list me-2"></i>الفئة</th>
                    <th><i class="fas fa-barcode me-2"></i>الرقم التسلسلي</th>
                    <th><i class="fas fa-calendar me-2"></i>تاريخ الشراء</th>
                    <th><i class="fas fa-money-bill me-2"></i>سعر الشراء</th>
                    <th><i class="fas fa-info-circle me-2"></i>الحالة</th>
                    <th><i class="fas fa-map-marker me-2"></i>الموقع</th>
                    <th><i class="fas fa-user me-2"></i>المسؤول</th>
                    <th><i class="fas fa-cogs me-2"></i>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for asset in assets:
        status_class = 'success' if asset.status == 'نشط' else 'warning' if asset.status == 'قيد الصيانة' else 'danger'
        content += f'''
                <tr>
                    <td><strong>{asset.name}</strong></td>
                    <td><span class="badge bg-info">{asset.category}</span></td>
                    <td><code>{asset.serial_number}</code></td>
                    <td>{asset.purchase_date.strftime('%Y-%m-%d')}</td>
                    <td><span class="text-success fw-bold">{"{:,.0f}".format(asset.purchase_price)} ريال</span></td>
                    <td>
                        <span class="badge bg-{status_class}">
                            <i class="fas fa-{'check' if asset.status == 'نشط' else 'wrench' if asset.status == 'قيد الصيانة' else 'times'} me-1"></i>
                            {asset.status}
                        </span>
                    </td>
                    <td>{asset.location or '-'}</td>
                    <td>{asset.assigned_to or '-'}</td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="editAsset({asset.id})" title="تعديل">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteAsset({asset.id})" title="حذف">
                                <i class="fas fa-trash"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-info" onclick="viewAsset({asset.id})" title="عرض">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                    </td>
                </tr>
        '''
    
    if not assets:
        content += '''
            <tr>
                <td colspan="9" class="empty-state">
                    <i class="fas fa-laptop"></i>
                    <h5>لا توجد أصول مسجلة</h5>
                    <p>ابدأ بإضافة أصل جديد للشركة</p>
                </td>
            </tr>
        '''
    
    content += '''
            </tbody>
        </table>
    </div>
    
    <script>
        function editAsset(id) {
            window.location.href = '/edit_asset/' + id;
        }
        
        function deleteAsset(id) {
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
                    fetch('/delete_asset/' + id, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire('تم الحذف!', 'تم حذف الأصل بنجاح.', 'success')
                            .then(() => location.reload());
                        } else {
                            Swal.fire('خطأ!', 'حدث خطأ أثناء الحذف.', 'error');
                        }
                    });
                }
            });
        }
        
        function viewAsset(id) {
            window.location.href = '/view_asset/' + id;
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

# صفحة إضافة أصل جديد
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
            flash(f'حدث خطأ أثناء إضافة الأصل: {str(e)}', 'error')
    
    # صفحة إضافة أصل بسيطة
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إضافة أصل جديد - نظام إدارة الأصول</title>
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
        .form-card {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
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
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.8rem 1rem;
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
    
    <div class="container">
        <div class="form-card">
            <div class="text-center mb-4">
                <h2><i class="fas fa-plus me-2 text-primary"></i>إضافة أصل جديد</h2>
                <p class="text-muted">أدخل بيانات الأصل الجديد</p>
            </div>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-tag me-2 text-primary"></i>اسم الأصل
                        </label>
                        <input type="text" class="form-control" name="name" required placeholder="أدخل اسم الأصل">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-list me-2 text-primary"></i>الفئة
                        </label>
                        <select class="form-select" name="category" required>
                            <option value="">اختر الفئة</option>
                            <option value="أجهزة كمبيوتر">💻 أجهزة كمبيوتر</option>
                            <option value="أجهزة محمولة">📱 أجهزة محمولة</option>
                            <option value="طابعات">🖨️ طابعات</option>
                            <option value="أثاث مكتبي">🪑 أثاث مكتبي</option>
                            <option value="معدات شبكة">🌐 معدات شبكة</option>
                            <option value="أخرى">📦 أخرى</option>
                        </select>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-barcode me-2 text-primary"></i>الرقم التسلسلي
                        </label>
                        <input type="text" class="form-control" name="serial_number" required placeholder="أدخل الرقم التسلسلي">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-calendar me-2 text-primary"></i>تاريخ الشراء
                        </label>
                        <input type="date" class="form-control" name="purchase_date" required>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-money-bill me-2 text-primary"></i>سعر الشراء (ريال)
                        </label>
                        <input type="number" class="form-control" name="purchase_price" step="0.01" required placeholder="0.00">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-info-circle me-2 text-primary"></i>الحالة
                        </label>
                        <select class="form-select" name="status" required>
                            <option value="">اختر الحالة</option>
                            <option value="نشط">✅ نشط</option>
                            <option value="قيد الصيانة">🔧 قيد الصيانة</option>
                            <option value="خارج الخدمة">❌ خارج الخدمة</option>
                        </select>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-map-marker me-2 text-primary"></i>الموقع
                        </label>
                        <input type="text" class="form-control" name="location" placeholder="أدخل موقع الأصل">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-user me-2 text-primary"></i>المسؤول
                        </label>
                        <input type="text" class="form-control" name="assigned_to" placeholder="أدخل اسم المسؤول">
                    </div>
                </div>
                
                <div class="text-center mt-4">
                    <button type="submit" class="btn btn-primary btn-lg px-5 me-3">
                        <i class="fas fa-save me-2"></i>حفظ الأصل
                    </button>
                    <a href="/assets" class="btn btn-secondary btn-lg px-5">
                        <i class="fas fa-arrow-left me-2"></i>العودة
                    </a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
    ''')

# وظائف حذف الأصول
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

# صفحة إدارة المشتريات
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
                    <th><i class="fas fa-box me-2"></i>اسم المنتج</th>
                    <th><i class="fas fa-building me-2"></i>المورد</th>
                    <th><i class="fas fa-sort-numeric-up me-2"></i>الكمية</th>
                    <th><i class="fas fa-money-bill me-2"></i>السعر الإجمالي</th>
                    <th><i class="fas fa-calendar me-2"></i>تاريخ الشراء</th>
                    <th><i class="fas fa-info-circle me-2"></i>الحالة</th>
                    <th><i class="fas fa-file me-2"></i>الفاتورة</th>
                    <th><i class="fas fa-cogs me-2"></i>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for purchase in purchases:
        status_class = 'success' if purchase.status == 'مكتمل' else 'warning' if purchase.status == 'قيد التنفيذ' else 'danger'
        content += f'''
                <tr>
                    <td><strong>{purchase.product_name}</strong></td>
                    <td><span class="badge bg-info">{purchase.supplier}</span></td>
                    <td><span class="badge bg-secondary">{purchase.quantity}</span></td>
                    <td><span class="text-success fw-bold">{"{:,.0f}".format(purchase.total_price)} ريال</span></td>
                    <td>{purchase.purchase_date.strftime('%Y-%m-%d')}</td>
                    <td>
                        <span class="badge bg-{status_class}">
                            <i class="fas fa-{'check' if purchase.status == 'مكتمل' else 'clock' if purchase.status == 'قيد التنفيذ' else 'times'} me-1"></i>
                            {purchase.status}
                        </span>
                    </td>
                    <td>
                        {f'<button class="btn btn-sm btn-outline-success" onclick="viewInvoiceFile({purchase.id})" title="عرض الفاتورة"><i class="fas fa-file-pdf"></i></button>' if purchase.invoice_file else '<span class="text-muted">لا يوجد</span>'}
                    </td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="editPurchase({purchase.id})" title="تعديل">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deletePurchase({purchase.id})" title="حذف">
                                <i class="fas fa-trash"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-info" onclick="viewPurchase({purchase.id})" title="عرض">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                    </td>
                </tr>
        '''
    
    if not purchases:
        content += '''
            <tr>
                <td colspan="8" class="empty-state">
                    <i class="fas fa-shopping-cart"></i>
                    <h5>لا توجد مشتريات مسجلة</h5>
                    <p>ابدأ بإضافة مشترى جديد</p>
                </td>
            </tr>
        '''
    
    content += '''
            </tbody>
        </table>
    </div>
    
    <script>
        function editPurchase(id) {
            window.location.href = '/edit_purchase/' + id;
        }
        
        function deletePurchase(id) {
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
                    fetch('/delete_purchase/' + id, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire('تم الحذف!', 'تم حذف المشترى بنجاح.', 'success')
                            .then(() => location.reload());
                        } else {
                            Swal.fire('خطأ!', 'حدث خطأ أثناء الحذف.', 'error');
                        }
                    });
                }
            });
        }
        
        function viewPurchase(id) {
            window.location.href = '/view_purchase/' + id;
        }
        
        function viewInvoiceFile(id) {
            window.open('/purchase_invoice/' + id, '_blank');
        }
    </script>
    '''
    
    return create_page_template(
        "إدارة المشتريات", 
        "fa-shopping-cart", 
        content, 
        "إضافة مشترى جديد", 
        "/add_purchase"
    )

# صفحة إضافة مشترى جديد
@app.route('/add_purchase', methods=['GET', 'POST'])
def add_purchase():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # إنشاء مجلد للفواتير إذا لم يكن موجوداً
            import os
            upload_folder = 'static/uploads/purchases'
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
            
            purchase = Purchase(
                product_name=request.form['product_name'],
                supplier=request.form['supplier'],
                quantity=int(request.form['quantity']),
                total_price=float(request.form['total_price']),
                purchase_date=datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date(),
                invoice_file=invoice_filename,
                notes=request.form.get('notes', ''),
                status=request.form['status']
            )
            db.session.add(purchase)
            db.session.commit()
            flash('تم إضافة المشترى بنجاح!', 'success')
            return redirect(url_for('purchases'))
        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة المشترى: {str(e)}', 'error')
    
    # صفحة إضافة مشترى بسيطة
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إضافة مشترى جديد - نظام إدارة الأصول</title>
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
        .form-card {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
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
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.8rem 1rem;
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
    
    <div class="container">
        <div class="form-card">
            <div class="text-center mb-4">
                <h2><i class="fas fa-shopping-cart me-2 text-primary"></i>إضافة مشترى جديد</h2>
                <p class="text-muted">أدخل بيانات المشترى الجديد مع إمكانية إرفاق الفاتورة</p>
            </div>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST" enctype="multipart/form-data">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-box me-2 text-primary"></i>اسم المنتج
                        </label>
                        <input type="text" class="form-control" name="product_name" required placeholder="أدخل اسم المنتج">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-building me-2 text-primary"></i>المورد
                        </label>
                        <input type="text" class="form-control" name="supplier" required placeholder="أدخل اسم المورد">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-sort-numeric-up me-2 text-primary"></i>الكمية
                        </label>
                        <input type="number" class="form-control" name="quantity" required min="1" placeholder="أدخل الكمية">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-money-bill me-2 text-primary"></i>السعر الإجمالي (ريال)
                        </label>
                        <input type="number" class="form-control" name="total_price" step="0.01" required placeholder="0.00">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-calendar me-2 text-primary"></i>تاريخ الشراء
                        </label>
                        <input type="date" class="form-control" name="purchase_date" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-info-circle me-2 text-primary"></i>الحالة
                        </label>
                        <select class="form-select" name="status" required>
                            <option value="">اختر الحالة</option>
                            <option value="مكتمل">✅ مكتمل</option>
                            <option value="قيد التنفيذ">⏳ قيد التنفيذ</option>
                            <option value="ملغي">❌ ملغي</option>
                        </select>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label fw-bold">
                        <i class="fas fa-paperclip me-2 text-primary"></i>إرفاق فاتورة الشراء
                    </label>
                    <input type="file" class="form-control" name="invoice_file" accept=".pdf,.jpg,.jpeg,.png">
                    <div class="form-text">
                        <i class="fas fa-info-circle me-1"></i>
                        يمكن رفع ملفات PDF أو صور (JPG, PNG) - الحد الأقصى 10 ميجابايت
                    </div>
                </div>
                
                <div class="mb-4">
                    <label class="form-label fw-bold">
                        <i class="fas fa-sticky-note me-2 text-primary"></i>ملاحظات
                    </label>
                    <textarea class="form-control" name="notes" rows="4" placeholder="أضف أي ملاحظات إضافية هنا..."></textarea>
                </div>
                
                <div class="text-center">
                    <button type="submit" class="btn btn-primary btn-lg px-5 me-3">
                        <i class="fas fa-save me-2"></i>حفظ المشترى
                    </button>
                    <a href="/purchases" class="btn btn-secondary btn-lg px-5">
                        <i class="fas fa-arrow-left me-2"></i>العودة
                    </a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
    ''')

# وظائف حذف المشتريات
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

# عرض فاتورة المشترى
@app.route('/purchase_invoice/<int:purchase_id>')
def purchase_invoice(purchase_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    purchase = Purchase.query.get_or_404(purchase_id)
    if purchase.invoice_file:
        return redirect(f'/static/uploads/purchases/{purchase.invoice_file}')
    else:
        flash('لا توجد فاتورة مرفقة لهذا المشترى', 'warning')
        return redirect(url_for('purchases'))

# صفحة إدارة العهد
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
                    <th><i class="fas fa-user me-2"></i>اسم الموظف</th>
                    <th><i class="fas fa-id-card me-2"></i>رقم الموظف</th>
                    <th><i class="fas fa-tag me-2"></i>نوع العهدة</th>
                    <th><i class="fas fa-barcode me-2"></i>الرقم التسلسلي</th>
                    <th><i class="fas fa-calendar me-2"></i>تاريخ الاستلام</th>
                    <th><i class="fas fa-money-bill me-2"></i>القيمة المقدرة</th>
                    <th><i class="fas fa-qrcode me-2"></i>الباركود</th>
                    <th><i class="fas fa-cogs me-2"></i>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for custody_item in custodies:
        status_class = 'success' if custody_item.status == 'نشط' else 'warning' if custody_item.status == 'مؤقت' else 'danger'
        content += f'''
                <tr>
                    <td><strong>{custody_item.employee_name}</strong></td>
                    <td><span class="badge bg-info">{custody_item.employee_id}</span></td>
                    <td><span class="badge bg-primary">{custody_item.custody_type}</span></td>
                    <td><code>{custody_item.serial_number}</code></td>
                    <td>{custody_item.received_date.strftime('%Y-%m-%d')}</td>
                    <td><span class="text-success fw-bold">{"{:,.0f}".format(custody_item.estimated_value or 0)} ريال</span></td>
                    <td>
                        {f'<span class="badge bg-success"><i class="fas fa-check me-1"></i>متوفر</span>' if custody_item.barcode else '<span class="badge bg-warning"><i class="fas fa-clock me-1"></i>غير متوفر</span>'}
                    </td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="editCustody({custody_item.id})" title="تعديل">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteCustody({custody_item.id})" title="حذف">
                                <i class="fas fa-trash"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-success" onclick="printBarcode({custody_item.id})" title="طباعة باركود">
                                <i class="fas fa-barcode"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-info" onclick="viewCustody({custody_item.id})" title="عرض">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                    </td>
                </tr>
        '''
    
    if not custodies:
        content += '''
            <tr>
                <td colspan="8" class="empty-state">
                    <i class="fas fa-handshake"></i>
                    <h5>لا توجد عهد مسجلة</h5>
                    <p>ابدأ بإضافة عهدة جديدة</p>
                </td>
            </tr>
        '''
    
    content += '''
            </tbody>
        </table>
    </div>
    
    <script>
        function editCustody(id) {
            window.location.href = '/edit_custody/' + id;
        }
        
        function deleteCustody(id) {
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
                    fetch('/delete_custody/' + id, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire('تم الحذف!', 'تم حذف العهدة بنجاح.', 'success')
                            .then(() => location.reload());
                        } else {
                            Swal.fire('خطأ!', 'حدث خطأ أثناء الحذف.', 'error');
                        }
                    });
                }
            });
        }
        
        function printBarcode(id) {
            window.open('/print_barcode/' + id, '_blank');
        }
        
        function viewCustody(id) {
            window.location.href = '/view_custody/' + id;
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

# صفحة إضافة عهدة جديدة
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
                notes=request.form.get('notes', ''),
                status=request.form['status']
            )
            db.session.add(custody)
            db.session.commit()
            flash('تم إضافة العهدة بنجاح!', 'success')
            return redirect(url_for('custody'))
        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة العهدة: {str(e)}', 'error')
    
    form_content = '''
    <div class="row">
        <div class="col-lg-8 mx-auto">
            <form method="POST" class="needs-validation" novalidate>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-user me-2 text-primary"></i>اسم الموظف
                        </label>
                        <input type="text" class="form-control form-control-lg" name="employee_name" required 
                               placeholder="أدخل اسم الموظف">
                        <div class="invalid-feedback">يرجى إدخال اسم الموظف</div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-id-card me-2 text-primary"></i>رقم الموظف
                        </label>
                        <input type="text" class="form-control form-control-lg" name="employee_id" required 
                               placeholder="أدخل رقم الموظف">
                        <div class="invalid-feedback">يرجى إدخال رقم الموظف</div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-tag me-2 text-primary"></i>نوع العهدة
                        </label>
                        <select class="form-select form-select-lg" name="custody_type" required>
                            <option value="">اختر نوع العهدة</option>
                            <option value="جهاز كمبيوتر">💻 جهاز كمبيوتر</option>
                            <option value="جهاز محمول">📱 جهاز محمول</option>
                            <option value="طابعة">🖨️ طابعة</option>
                            <option value="أثاث مكتبي">🪑 أثاث مكتبي</option>
                            <option value="معدات شبكة">🌐 معدات شبكة</option>
                            <option value="أخرى">📦 أخرى</option>
                        </select>
                        <div class="invalid-feedback">يرجى اختيار نوع العهدة</div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-barcode me-2 text-primary"></i>الرقم التسلسلي
                        </label>
                        <input type="text" class="form-control form-control-lg" name="serial_number" required 
                               placeholder="أدخل الرقم التسلسلي">
                        <div class="invalid-feedback">يرجى إدخال الرقم التسلسلي</div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-calendar me-2 text-primary"></i>تاريخ الاستلام
                        </label>
                        <input type="date" class="form-control form-control-lg" name="received_date" required>
                        <div class="invalid-feedback">يرجى إدخال تاريخ الاستلام</div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-money-bill me-2 text-primary"></i>القيمة المقدرة (ريال)
                        </label>
                        <input type="number" class="form-control form-control-lg" name="estimated_value" 
                               step="0.01" placeholder="0.00">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-info-circle me-2 text-primary"></i>الحالة
                        </label>
                        <select class="form-select form-select-lg" name="status" required>
                            <option value="">اختر الحالة</option>
                            <option value="نشط">✅ نشط</option>
                            <option value="مؤقت">⏳ مؤقت</option>
                            <option value="مسترد">🔄 مسترد</option>
                        </select>
                        <div class="invalid-feedback">يرجى اختيار الحالة</div>
                    </div>
                </div>
                
                <div class="mb-4">
                    <label class="form-label fw-bold">
                        <i class="fas fa-sticky-note me-2 text-primary"></i>ملاحظات
                    </label>
                    <textarea class="form-control" name="notes" rows="4" 
                              placeholder="أضف أي ملاحظات إضافية هنا..."></textarea>
                </div>
                
                <div class="text-center">
                    <button type="submit" class="btn btn-primary btn-lg px-5 me-3">
                        <i class="fas fa-save me-2"></i>حفظ العهدة
                    </button>
                    <a href="/custody" class="btn btn-secondary btn-lg px-5">
                        <i class="fas fa-times me-2"></i>إلغاء
                    </a>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        // Bootstrap form validation
        (function() {
            'use strict';
            window.addEventListener('load', function() {
                var forms = document.getElementsByClassName('needs-validation');
                var validation = Array.prototype.filter.call(forms, function(form) {
                    form.addEventListener('submit', function(event) {
                        if (form.checkValidity() === false) {
                            event.preventDefault();
                            event.stopPropagation();
                        }
                        form.classList.add('was-validated');
                    }, false);
                });
            }, false);
        })();
    </script>
    '''
    
    return create_page_template(
        "إضافة عهدة جديدة",
        "fa-plus",
        form_content
    )

# طباعة باركود العهدة
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
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ 
                font-family: 'Cairo', sans-serif; 
                text-align: center; 
                padding: 20px; 
                background: white;
            }}
            .barcode-container {{ 
                border: 3px solid #667eea; 
                border-radius: 15px;
                padding: 30px; 
                margin: 20px auto; 
                width: 400px; 
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
            }}
            .barcode {{ 
                font-family: 'Courier New', monospace; 
                font-size: 28px; 
                letter-spacing: 3px; 
                background: #2c3e50;
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .info {{ 
                margin: 15px 0; 
                font-size: 16px;
                color: #2c3e50;
                font-weight: 600;
            }}
            .logo {{
                font-size: 2rem;
                color: #667eea;
                margin-bottom: 10px;
            }}
            @media print {{ 
                body {{ margin: 0; }}
                .no-print {{ display: none; }}
                .barcode-container {{
                    box-shadow: none;
                    border: 2px solid #000;
                }}
            }}
            .btn {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                margin: 0 10px;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }}
            .btn-secondary {{
                background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            }}
        </style>
    </head>
    <body>
        <div class="barcode-container">
            <div class="header">
                <div class="logo">
                    <i class="fas fa-building"></i>
                </div>
                <h2>نظام إدارة الأصول</h2>
                <h3>بطاقة عهدة</h3>
            </div>
            
            <div class="info"><strong>نوع العهدة:</strong> {custody.custody_type}</div>
            <div class="info"><strong>الموظف:</strong> {custody.employee_name}</div>
            <div class="info"><strong>رقم الموظف:</strong> {custody.employee_id}</div>
            <div class="info"><strong>الرقم التسلسلي:</strong> {custody.serial_number}</div>
            
            <div class="barcode">{custody.barcode}</div>
            
            <div class="info"><strong>تاريخ الاستلام:</strong> {custody.received_date.strftime('%Y-%m-%d')}</div>
            <div class="info"><strong>القيمة المقدرة:</strong> {"{:,.0f}".format(custody.estimated_value or 0)} ريال</div>
        </div>
        
        <div class="no-print">
            <button class="btn" onclick="window.print()">
                <i class="fas fa-print"></i> طباعة
            </button>
            <button class="btn btn-secondary" onclick="window.close()">
                <i class="fas fa-times"></i> إغلاق
            </button>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/js/all.min.js"></script>
    </body>
    </html>
    '''
    
    return barcode_html

# وظائف حذف العهد
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

# صفحة إدارة الفواتير
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
                    <th><i class="fas fa-hashtag me-2"></i>رقم الفاتورة</th>
                    <th><i class="fas fa-calendar me-2"></i>تاريخ الفاتورة</th>
                    <th><i class="fas fa-building me-2"></i>اسم المورد</th>
                    <th><i class="fas fa-money-bill me-2"></i>المبلغ الإجمالي</th>
                    <th><i class="fas fa-credit-card me-2"></i>حالة الدفع</th>
                    <th><i class="fas fa-clock me-2"></i>تاريخ الاستحقاق</th>
                    <th><i class="fas fa-file me-2"></i>الملف</th>
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
                    <td>{invoice.invoice_date.strftime('%Y-%m-%d')}</td>
                    <td><span class="badge bg-info">{invoice.supplier_name}</span></td>
                    <td><span class="text-success fw-bold">{"{:,.0f}".format(invoice.total_amount)} ريال</span></td>
                    <td>
                        <span class="badge bg-{badge_class}">
                            <i class="fas fa-{'check' if invoice.payment_status == 'مدفوع' else 'clock' if invoice.payment_status == 'مدفوع جزئياً' else 'times'} me-1"></i>
                            {invoice.payment_status}
                        </span>
                    </td>
                    <td>{invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '-'}</td>
                    <td>
                        {f'<button class="btn btn-sm btn-outline-success" onclick="viewInvoiceFile({invoice.id})" title="عرض الملف"><i class="fas fa-file-pdf"></i></button>' if invoice.invoice_file else '<span class="text-muted">لا يوجد</span>'}
                    </td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="editInvoice({invoice.id})" title="تعديل">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteInvoice({invoice.id})" title="حذف">
                                <i class="fas fa-trash"></i>
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
                <td colspan="8" class="empty-state">
                    <i class="fas fa-file-invoice"></i>
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
    
    return create_page_template(
        "إدارة الفواتير", 
        "fa-file-invoice", 
        content, 
        "إضافة فاتورة جديدة", 
        "/add_invoice"
    )

# صفحة إضافة فاتورة جديدة
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
    <div class="row">
        <div class="col-lg-8 mx-auto">
            <form method="POST" enctype="multipart/form-data" class="needs-validation" novalidate>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-hashtag me-2 text-primary"></i>رقم الفاتورة
                        </label>
                        <input type="text" class="form-control form-control-lg" name="invoice_number" required 
                               placeholder="أدخل رقم الفاتورة">
                        <div class="invalid-feedback">يرجى إدخال رقم الفاتورة</div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-calendar me-2 text-primary"></i>تاريخ الفاتورة
                        </label>
                        <input type="date" class="form-control form-control-lg" name="invoice_date" required>
                        <div class="invalid-feedback">يرجى إدخال تاريخ الفاتورة</div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-building me-2 text-primary"></i>اسم المورد
                        </label>
                        <input type="text" class="form-control form-control-lg" name="supplier_name" required 
                               placeholder="أدخل اسم المورد">
                        <div class="invalid-feedback">يرجى إدخال اسم المورد</div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-money-bill me-2 text-primary"></i>المبلغ الإجمالي (ريال)
                        </label>
                        <input type="number" class="form-control form-control-lg" name="total_amount" 
                               step="0.01" required placeholder="0.00">
                        <div class="invalid-feedback">يرجى إدخال المبلغ الإجمالي</div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-credit-card me-2 text-primary"></i>حالة الدفع
                        </label>
                        <select class="form-select form-select-lg" name="payment_status" required>
                            <option value="">اختر حالة الدفع</option>
                            <option value="مدفوع">✅ مدفوع</option>
                            <option value="غير مدفوع">❌ غير مدفوع</option>
                            <option value="مدفوع جزئياً">⏳ مدفوع جزئياً</option>
                        </select>
                        <div class="invalid-feedback">يرجى اختيار حالة الدفع</div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-clock me-2 text-primary"></i>تاريخ الاستحقاق
                        </label>
                        <input type="date" class="form-control form-control-lg" name="due_date">
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label fw-bold">
                        <i class="fas fa-paperclip me-2 text-primary"></i>إرفاق ملف الفاتورة
                    </label>
                    <input type="file" class="form-control form-control-lg" name="invoice_file" 
                           accept=".pdf,.jpg,.jpeg,.png">
                    <div class="form-text">
                        <i class="fas fa-info-circle me-1"></i>
                        يمكن رفع ملفات PDF أو صور (JPG, PNG) - الحد الأقصى 10 ميجابايت
                    </div>
                </div>
                
                <div class="mb-4">
                    <label class="form-label fw-bold">
                        <i class="fas fa-sticky-note me-2 text-primary"></i>ملاحظات
                    </label>
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
    
    <script>
        // Bootstrap form validation
        (function() {
            'use strict';
            window.addEventListener('load', function() {
                var forms = document.getElementsByClassName('needs-validation');
                var validation = Array.prototype.filter.call(forms, function(form) {
                    form.addEventListener('submit', function(event) {
                        if (form.checkValidity() === false) {
                            event.preventDefault();
                            event.stopPropagation();
                        }
                        form.classList.add('was-validated');
                    }, false);
                });
            }, false);
        })();
    </script>
    '''
    
    return create_page_template(
        "إضافة فاتورة جديدة",
        "fa-plus",
        form_content
    )

# صفحة التقارير
@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # حساب الإحصائيات الفعلية
    total_assets = Asset.query.count()
    total_purchases = Purchase.query.count()
    total_custodies = Custody.query.count()
    total_invoices = Invoice.query.count()
    
    # حساب القيم المالية
    total_asset_value = db.session.query(db.func.sum(Asset.purchase_price)).scalar() or 0
    total_purchase_value = db.session.query(db.func.sum(Purchase.total_price)).scalar() or 0
    total_invoice_value = db.session.query(db.func.sum(Invoice.total_amount)).scalar() or 0
    
    content = f'''
    <div class="row mb-4">
        <div class="col-md-3 mb-3">
            <div class="card text-center h-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 20px;">
                <div class="card-body">
                    <i class="fas fa-laptop fa-3x mb-3"></i>
                    <h2 class="fw-bold">{total_assets}</h2>
                    <p class="mb-0">إجمالي الأصول</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-center h-100" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; border-radius: 20px;">
                <div class="card-body">
                    <i class="fas fa-shopping-cart fa-3x mb-3"></i>
                    <h2 class="fw-bold">{total_purchases}</h2>
                    <p class="mb-0">المشتريات</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-center h-100" style="background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%); color: white; border-radius: 20px;">
                <div class="card-body">
                    <i class="fas fa-handshake fa-3x mb-3"></i>
                    <h2 class="fw-bold">{total_custodies}</h2>
                    <p class="mb-0">العهد</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-center h-100" style="background: linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%); color: white; border-radius: 20px;">
                <div class="card-body">
                    <i class="fas fa-file-invoice fa-3x mb-3"></i>
                    <h2 class="fw-bold">{total_invoices}</h2>
                    <p class="mb-0">الفواتير</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-12 mb-4">
            <div class="card" style="border-radius: 20px; border: none; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);">
                <div class="card-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 20px 20px 0 0;">
                    <h5 class="mb-0">
                        <i class="fas fa-money-bill-wave me-2"></i>الملخص المالي
                    </h5>
                </div>
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-md-4 text-center">
                            <div class="p-3">
                                <i class="fas fa-laptop fa-2x text-primary mb-2"></i>
                                <h6 class="text-muted">قيمة الأصول الإجمالية</h6>
                                <h3 class="text-primary fw-bold">{"{:,.0f}".format(total_asset_value)} ريال</h3>
                            </div>
                        </div>
                        <div class="col-md-4 text-center">
                            <div class="p-3">
                                <i class="fas fa-shopping-cart fa-2x text-success mb-2"></i>
                                <h6 class="text-muted">قيمة المشتريات الإجمالية</h6>
                                <h3 class="text-success fw-bold">{"{:,.0f}".format(total_purchase_value)} ريال</h3>
                            </div>
                        </div>
                        <div class="col-md-4 text-center">
                            <div class="p-3">
                                <i class="fas fa-file-invoice fa-2x text-warning mb-2"></i>
                                <h6 class="text-muted">قيمة الفواتير الإجمالية</h6>
                                <h3 class="text-warning fw-bold">{"{:,.0f}".format(total_invoice_value)} ريال</h3>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="text-center mt-4">
        <button class="btn btn-success btn-lg px-5" onclick="exportReport()">
            <i class="fas fa-download me-2"></i>تصدير التقرير
        </button>
        <button class="btn btn-info btn-lg px-5 ms-3" onclick="printReport()">
            <i class="fas fa-print me-2"></i>طباعة التقرير
        </button>
    </div>
    
    <script>
        function exportReport() {{
            Swal.fire({{
                title: 'اختر نوع التصدير',
                html: `
                    <div class="d-grid gap-2">
                        <button class="btn btn-success" onclick="exportExcel()">
                            <i class="fas fa-file-excel me-2"></i>تصدير Excel
                        </button>
                        <button class="btn btn-danger" onclick="exportPDF()">
                            <i class="fas fa-file-pdf me-2"></i>تصدير PDF
                        </button>
                        <button class="btn btn-info" onclick="openDashboard()">
                            <i class="fas fa-chart-line me-2"></i>لوحة تحكم تفاعلية
                        </button>
                    </div>
                `,
                showConfirmButton: false,
                showCancelButton: true,
                cancelButtonText: 'إلغاء'
            }});
        }}
        
        function exportExcel() {{
            window.location.href = '/export_excel';
            Swal.close();
        }}
        
        function exportPDF() {{
            window.location.href = '/export_pdf';
            Swal.close();
        }}
        
        function openDashboard() {{
            window.open('/interactive_dashboard', '_blank');
            Swal.close();
        }}
        
        function printReport() {{
            window.print();
        }}
    </script>
    '''
    
    return create_page_template(
        "التقارير والإحصائيات", 
        "fa-chart-bar", 
        content
    )

# وظائف حذف الفواتير
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

# عرض ملف الفاتورة
@app.route('/invoice_file/<int:invoice_id>')
def invoice_file(invoice_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.invoice_file:
        return redirect(f'/static/uploads/invoices/{invoice.invoice_file}')
    else:
        flash('لا يوجد ملف مرفق لهذه الفاتورة', 'warning')
        return redirect(url_for('invoices'))

# صفحة إدارة التراخيص
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
                    <th><i class="fas fa-key me-2"></i>اسم البرنامج</th>
                    <th><i class="fas fa-code me-2"></i>مفتاح الترخيص</th>
                    <th><i class="fas fa-tag me-2"></i>نوع الترخيص</th>
                    <th><i class="fas fa-users me-2"></i>عدد المستخدمين</th>
                    <th><i class="fas fa-calendar me-2"></i>تاريخ الانتهاء</th>
                    <th><i class="fas fa-money-bill me-2"></i>التكلفة</th>
                    <th><i class="fas fa-cogs me-2"></i>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for license_item in licenses:
        status_class = 'success' if license_item.status == 'نشط' else 'warning' if license_item.status == 'منتهي قريباً' else 'danger'
        content += f'''
                <tr>
                    <td><strong>{license_item.software_name}</strong></td>
                    <td><code>{license_item.license_key[:20]}...</code></td>
                    <td><span class="badge bg-info">{license_item.license_type}</span></td>
                    <td><span class="badge bg-secondary">{license_item.user_count}</span></td>
                    <td>{license_item.expiry_date.strftime('%Y-%m-%d') if license_item.expiry_date else '-'}</td>
                    <td><span class="text-success fw-bold">{"{:,.0f}".format(license_item.cost or 0)} ريال</span></td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="editLicense({license_item.id})" title="تعديل">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteLicense({license_item.id})" title="حذف">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
        '''
    
    if not licenses:
        content += '''
            <tr>
                <td colspan="7" class="empty-state">
                    <i class="fas fa-key"></i>
                    <h5>لا توجد تراخيص مسجلة</h5>
                    <p>ابدأ بإضافة ترخيص جديد</p>
                </td>
            </tr>
        '''
    
    content += '''
            </tbody>
        </table>
    </div>
    
    <script>
        function editLicense(id) {
            window.location.href = '/edit_license/' + id;
        }
        
        function deleteLicense(id) {
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
                    fetch('/delete_license/' + id, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire('تم الحذف!', 'تم حذف الترخيص بنجاح.', 'success')
                            .then(() => location.reload());
                        } else {
                            Swal.fire('خطأ!', 'حدث خطأ أثناء الحذف.', 'error');
                        }
                    });
                }
            });
        }
    </script>
    '''
    
    return create_page_template(
        "إدارة التراخيص", 
        "fa-key", 
        content, 
        "إضافة ترخيص جديد", 
        "/add_license"
    )

# صفحة إدارة الموظفين
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
                    <th><i class="fas fa-user me-2"></i>اسم الموظف</th>
                    <th><i class="fas fa-id-card me-2"></i>رقم الموظف</th>
                    <th><i class="fas fa-building me-2"></i>القسم</th>
                    <th><i class="fas fa-briefcase me-2"></i>المنصب</th>
                    <th><i class="fas fa-envelope me-2"></i>البريد الإلكتروني</th>
                    <th><i class="fas fa-phone me-2"></i>الهاتف</th>
                    <th><i class="fas fa-info-circle me-2"></i>الحالة</th>
                    <th><i class="fas fa-cogs me-2"></i>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for employee in employees:
        status_class = 'success' if employee.status == 'نشط' else 'warning' if employee.status == 'إجازة' else 'danger'
        content += f'''
                <tr>
                    <td><strong>{employee.name}</strong></td>
                    <td><span class="badge bg-info">{employee.employee_id}</span></td>
                    <td>{employee.department}</td>
                    <td>{employee.position}</td>
                    <td>{employee.email or '-'}</td>
                    <td>{employee.phone or '-'}</td>
                    <td>
                        <span class="badge bg-{status_class}">
                            <i class="fas fa-{'check' if employee.status == 'نشط' else 'clock' if employee.status == 'إجازة' else 'times'} me-1"></i>
                            {employee.status}
                        </span>
                    </td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="editEmployee({employee.id})" title="تعديل">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteEmployee({employee.id})" title="حذف">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
        '''
    
    if not employees:
        content += '''
            <tr>
                <td colspan="8" class="empty-state">
                    <i class="fas fa-users"></i>
                    <h5>لا يوجد موظفين مسجلين</h5>
                    <p>ابدأ بإضافة موظف جديد</p>
                </td>
            </tr>
        '''
    
    content += '''
            </tbody>
        </table>
    </div>
    
    <script>
        function editEmployee(id) {
            window.location.href = '/edit_employee/' + id;
        }
        
        function deleteEmployee(id) {
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
                    fetch('/delete_employee/' + id, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire('تم الحذف!', 'تم حذف الموظف بنجاح.', 'success')
                            .then(() => location.reload());
                        } else {
                            Swal.fire('خطأ!', 'حدث خطأ أثناء الحذف.', 'error');
                        }
                    });
                }
            });
        }
    </script>
    '''
    
    return create_page_template(
        "إدارة الموظفين", 
        "fa-users", 
        content, 
        "إضافة موظف جديد", 
        "/add_employee"
    )

# صفحة إدارة الإدارات
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
                    <th><i class="fas fa-building me-2"></i>اسم الإدارة</th>
                    <th><i class="fas fa-code me-2"></i>رمز الإدارة</th>
                    <th><i class="fas fa-user-tie me-2"></i>مدير الإدارة</th>
                    <th><i class="fas fa-map-marker me-2"></i>الموقع</th>
                    <th><i class="fas fa-info-circle me-2"></i>الحالة</th>
                    <th><i class="fas fa-cogs me-2"></i>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for department in departments:
        status_class = 'success' if department.status == 'نشط' else 'warning' if department.status == 'مؤقت' else 'danger'
        content += f'''
                <tr>
                    <td><strong>{department.department_name}</strong></td>
                    <td><span class="badge bg-info">{department.department_code}</span></td>
                    <td>{department.manager_name or '-'}</td>
                    <td>{department.location or '-'}</td>
                    <td>
                        <span class="badge bg-{status_class}">
                            <i class="fas fa-{'check' if department.status == 'نشط' else 'clock' if department.status == 'مؤقت' else 'times'} me-1"></i>
                            {department.status}
                        </span>
                    </td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="editDepartment({department.id})" title="تعديل">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteDepartment({department.id})" title="حذف">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
        '''
    
    if not departments:
        content += '''
            <tr>
                <td colspan="6" class="empty-state">
                    <i class="fas fa-building"></i>
                    <h5>لا توجد إدارات مسجلة</h5>
                    <p>ابدأ بإضافة إدارة جديدة</p>
                </td>
            </tr>
        '''
    
    content += '''
            </tbody>
        </table>
    </div>
    
    <script>
        function editDepartment(id) {
            window.location.href = '/edit_department/' + id;
        }
        
        function deleteDepartment(id) {
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
                    fetch('/delete_department/' + id, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire('تم الحذف!', 'تم حذف الإدارة بنجاح.', 'success')
                            .then(() => location.reload());
                        } else {
                            Swal.fire('خطأ!', 'حدث خطأ أثناء الحذف.', 'error');
                        }
                    });
                }
            });
        }
    </script>
    '''
    
    return create_page_template(
        "إدارة الإدارات", 
        "fa-building", 
        content, 
        "إضافة إدارة جديدة", 
        "/add_department"
    )

# صفحة الدعم الفني
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
                    <th><i class="fas fa-ticket-alt me-2"></i>رقم التذكرة</th>
                    <th><i class="fas fa-user me-2"></i>مقدم الطلب</th>
                    <th><i class="fas fa-envelope me-2"></i>البريد الإلكتروني</th>
                    <th><i class="fas fa-tag me-2"></i>نوع المشكلة</th>
                    <th><i class="fas fa-exclamation me-2"></i>الأولوية</th>
                    <th><i class="fas fa-info-circle me-2"></i>الحالة</th>
                    <th><i class="fas fa-calendar me-2"></i>تاريخ الإنشاء</th>
                    <th><i class="fas fa-cogs me-2"></i>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for ticket in tickets:
        status_class = 'success' if ticket.status == 'مغلق' else 'warning' if ticket.status == 'قيد المعالجة' else 'danger'
        priority_class = 'danger' if ticket.priority == 'عالي' else 'warning' if ticket.priority == 'متوسط' else 'info'
        content += f'''
                <tr>
                    <td><strong>{ticket.ticket_number}</strong></td>
                    <td>{ticket.requester_name}</td>
                    <td>{ticket.email}</td>
                    <td><span class="badge bg-info">{ticket.issue_type}</span></td>
                    <td>
                        <span class="badge bg-{priority_class}">
                            <i class="fas fa-{'exclamation-triangle' if ticket.priority == 'عالي' else 'exclamation' if ticket.priority == 'متوسط' else 'info'} me-1"></i>
                            {ticket.priority}
                        </span>
                    </td>
                    <td>
                        <span class="badge bg-{status_class}">
                            <i class="fas fa-{'check' if ticket.status == 'مغلق' else 'clock' if ticket.status == 'قيد المعالجة' else 'folder-open'} me-1"></i>
                            {ticket.status}
                        </span>
                    </td>
                    <td>{ticket.created_at.strftime('%Y-%m-%d')}</td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="viewTicket({ticket.id})" title="عرض">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-success" onclick="closeTicket({ticket.id})" title="إغلاق">
                                <i class="fas fa-check"></i>
                            </button>
                        </div>
                    </td>
                </tr>
        '''
    
    if not tickets:
        content += '''
            <tr>
                <td colspan="8" class="empty-state">
                    <i class="fas fa-headset"></i>
                    <h5>لا توجد تذاكر دعم فني</h5>
                    <p>ابدأ بإنشاء تذكرة جديدة</p>
                </td>
            </tr>
        '''
    
    content += '''
            </tbody>
        </table>
    </div>
    
    <script>
        function viewTicket(id) {
            window.location.href = '/view_ticket/' + id;
        }
        
        function closeTicket(id) {
            Swal.fire({
                title: 'إغلاق التذكرة؟',
                text: "هل تريد إغلاق هذه التذكرة؟",
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#28a745',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'نعم، أغلق!',
                cancelButtonText: 'إلغاء'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch('/close_ticket/' + id, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire('تم الإغلاق!', 'تم إغلاق التذكرة بنجاح.', 'success')
                            .then(() => location.reload());
                        } else {
                            Swal.fire('خطأ!', 'حدث خطأ أثناء الإغلاق.', 'error');
                        }
                    });
                }
            });
        }
    </script>
    '''
    
    return create_page_template(
        "الدعم الفني", 
        "fa-headset", 
        content, 
        "إنشاء تذكرة جديدة", 
        "/create_ticket"
    )

# وظائف الحذف للصفحات الجديدة
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

# صفحة إضافة موظف جديد
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
                status=request.form['status']
            )
            db.session.add(employee)
            db.session.commit()
            flash('تم إضافة الموظف بنجاح!', 'success')
            return redirect(url_for('employees'))
        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة الموظف: {str(e)}', 'error')
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إضافة موظف جديد - نظام إدارة الأصول</title>
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
        .form-card {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
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
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.8rem 1rem;
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
    
    <div class="container">
        <div class="form-card">
            <div class="text-center mb-4">
                <h2><i class="fas fa-user-plus me-2 text-primary"></i>إضافة موظف جديد</h2>
                <p class="text-muted">أدخل بيانات الموظف الجديد</p>
            </div>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-user me-2 text-primary"></i>اسم الموظف
                        </label>
                        <input type="text" class="form-control" name="name" required placeholder="أدخل اسم الموظف">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-id-card me-2 text-primary"></i>رقم الموظف
                        </label>
                        <input type="text" class="form-control" name="employee_id" required placeholder="أدخل رقم الموظف">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-building me-2 text-primary"></i>القسم
                        </label>
                        <input type="text" class="form-control" name="department" required placeholder="أدخل اسم القسم">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-briefcase me-2 text-primary"></i>المنصب
                        </label>
                        <input type="text" class="form-control" name="position" required placeholder="أدخل المنصب">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-envelope me-2 text-primary"></i>البريد الإلكتروني
                        </label>
                        <input type="email" class="form-control" name="email" placeholder="أدخل البريد الإلكتروني">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-phone me-2 text-primary"></i>رقم الهاتف
                        </label>
                        <input type="tel" class="form-control" name="phone" placeholder="أدخل رقم الهاتف">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-info-circle me-2 text-primary"></i>الحالة
                        </label>
                        <select class="form-select" name="status" required>
                            <option value="">اختر الحالة</option>
                            <option value="نشط">✅ نشط</option>
                            <option value="إجازة">🏖️ إجازة</option>
                            <option value="غير نشط">❌ غير نشط</option>
                        </select>
                    </div>
                </div>
                
                <div class="text-center mt-4">
                    <button type="submit" class="btn btn-primary btn-lg px-5 me-3">
                        <i class="fas fa-save me-2"></i>حفظ الموظف
                    </button>
                    <a href="/employees" class="btn btn-secondary btn-lg px-5">
                        <i class="fas fa-arrow-left me-2"></i>العودة
                    </a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
    ''')

# صفحة إضافة إدارة جديدة
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
                status=request.form['status']
            )
            db.session.add(department)
            db.session.commit()
            flash('تم إضافة الإدارة بنجاح!', 'success')
            return redirect(url_for('departments'))
        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة الإدارة: {str(e)}', 'error')
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إضافة إدارة جديدة - نظام إدارة الأصول</title>
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
        .form-card {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
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
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.8rem 1rem;
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
    
    <div class="container">
        <div class="form-card">
            <div class="text-center mb-4">
                <h2><i class="fas fa-building me-2 text-primary"></i>إضافة إدارة جديدة</h2>
                <p class="text-muted">أدخل بيانات الإدارة الجديدة</p>
            </div>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-building me-2 text-primary"></i>اسم الإدارة
                        </label>
                        <input type="text" class="form-control" name="department_name" required placeholder="أدخل اسم الإدارة">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-code me-2 text-primary"></i>رمز الإدارة
                        </label>
                        <input type="text" class="form-control" name="department_code" required placeholder="أدخل رمز الإدارة">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-user-tie me-2 text-primary"></i>مدير الإدارة
                        </label>
                        <input type="text" class="form-control" name="manager_name" placeholder="أدخل اسم مدير الإدارة">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-map-marker me-2 text-primary"></i>الموقع
                        </label>
                        <input type="text" class="form-control" name="location" placeholder="أدخل موقع الإدارة">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-info-circle me-2 text-primary"></i>الحالة
                        </label>
                        <select class="form-select" name="status" required>
                            <option value="">اختر الحالة</option>
                            <option value="نشط">✅ نشط</option>
                            <option value="مؤقت">⏳ مؤقت</option>
                            <option value="غير نشط">❌ غير نشط</option>
                        </select>
                    </div>
                </div>
                
                <div class="text-center mt-4">
                    <button type="submit" class="btn btn-primary btn-lg px-5 me-3">
                        <i class="fas fa-save me-2"></i>حفظ الإدارة
                    </button>
                    <a href="/departments" class="btn btn-secondary btn-lg px-5">
                        <i class="fas fa-arrow-left me-2"></i>العودة
                    </a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
    ''')

# صفحة إضافة ترخيص جديد
@app.route('/add_license', methods=['GET', 'POST'])
def add_license():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            license_item = License(
                software_name=request.form['software_name'],
                license_key=request.form['license_key'],
                license_type=request.form['license_type'],
                user_count=int(request.form['user_count']),
                expiry_date=datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date() if request.form.get('expiry_date') else None,
                cost=float(request.form['cost']) if request.form.get('cost') else None,
                status=request.form['status']
            )
            db.session.add(license_item)
            db.session.commit()
            flash('تم إضافة الترخيص بنجاح!', 'success')
            return redirect(url_for('licenses'))
        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة الترخيص: {str(e)}', 'error')
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إضافة ترخيص جديد - نظام إدارة الأصول</title>
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
        .form-card {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
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
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.8rem 1rem;
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
    
    <div class="container">
        <div class="form-card">
            <div class="text-center mb-4">
                <h2><i class="fas fa-key me-2 text-primary"></i>إضافة ترخيص جديد</h2>
                <p class="text-muted">أدخل بيانات الترخيص الجديد</p>
            </div>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-desktop me-2 text-primary"></i>اسم البرنامج
                        </label>
                        <input type="text" class="form-control" name="software_name" required placeholder="أدخل اسم البرنامج">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-key me-2 text-primary"></i>مفتاح الترخيص
                        </label>
                        <input type="text" class="form-control" name="license_key" required placeholder="أدخل مفتاح الترخيص">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-tag me-2 text-primary"></i>نوع الترخيص
                        </label>
                        <select class="form-select" name="license_type" required>
                            <option value="">اختر نوع الترخيص</option>
                            <option value="سنوي">📅 سنوي</option>
                            <option value="دائم">♾️ دائم</option>
                            <option value="تجريبي">🧪 تجريبي</option>
                            <option value="شهري">📆 شهري</option>
                        </select>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-users me-2 text-primary"></i>عدد المستخدمين
                        </label>
                        <input type="number" class="form-control" name="user_count" required min="1" placeholder="أدخل عدد المستخدمين">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-calendar me-2 text-primary"></i>تاريخ الانتهاء
                        </label>
                        <input type="date" class="form-control" name="expiry_date">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-money-bill me-2 text-primary"></i>التكلفة (ريال)
                        </label>
                        <input type="number" class="form-control" name="cost" step="0.01" placeholder="0.00">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-info-circle me-2 text-primary"></i>الحالة
                        </label>
                        <select class="form-select" name="status" required>
                            <option value="">اختر الحالة</option>
                            <option value="نشط">✅ نشط</option>
                            <option value="منتهي قريباً">⚠️ منتهي قريباً</option>
                            <option value="منتهي">❌ منتهي</option>
                        </select>
                    </div>
                </div>
                
                <div class="text-center mt-4">
                    <button type="submit" class="btn btn-primary btn-lg px-5 me-3">
                        <i class="fas fa-save me-2"></i>حفظ الترخيص
                    </button>
                    <a href="/licenses" class="btn btn-secondary btn-lg px-5">
                        <i class="fas fa-arrow-left me-2"></i>العودة
                    </a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
    ''')

# صفحة إنشاء تذكرة دعم جديدة
@app.route('/create_ticket', methods=['GET', 'POST'])
def create_ticket():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # إنشاء رقم تذكرة تلقائي
            import random
            ticket_number = f"TK{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
            
            ticket = SupportTicket(
                ticket_number=ticket_number,
                requester_name=request.form['requester_name'],
                email=request.form['email'],
                issue_type=request.form['issue_type'],
                priority=request.form['priority'],
                description=request.form['description'],
                status='مفتوح'
            )
            db.session.add(ticket)
            db.session.commit()
            flash(f'تم إنشاء التذكرة بنجاح! رقم التذكرة: {ticket_number}', 'success')
            return redirect(url_for('support'))
        except Exception as e:
            flash(f'حدث خطأ أثناء إنشاء التذكرة: {str(e)}', 'error')
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إنشاء تذكرة دعم جديدة - نظام إدارة الأصول</title>
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
        .form-card {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
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
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.8rem 1rem;
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
    
    <div class="container">
        <div class="form-card">
            <div class="text-center mb-4">
                <h2><i class="fas fa-headset me-2 text-primary"></i>إنشاء تذكرة دعم جديدة</h2>
                <p class="text-muted">أدخل تفاصيل المشكلة أو الطلب</p>
            </div>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-user me-2 text-primary"></i>اسم مقدم الطلب
                        </label>
                        <input type="text" class="form-control" name="requester_name" required placeholder="أدخل اسم مقدم الطلب">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-envelope me-2 text-primary"></i>البريد الإلكتروني
                        </label>
                        <input type="email" class="form-control" name="email" required placeholder="أدخل البريد الإلكتروني">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-tag me-2 text-primary"></i>نوع المشكلة
                        </label>
                        <select class="form-select" name="issue_type" required>
                            <option value="">اختر نوع المشكلة</option>
                            <option value="مشكلة تقنية">🔧 مشكلة تقنية</option>
                            <option value="طلب صيانة">🛠️ طلب صيانة</option>
                            <option value="طلب جهاز جديد">💻 طلب جهاز جديد</option>
                            <option value="مشكلة شبكة">🌐 مشكلة شبكة</option>
                            <option value="مشكلة برمجيات">💿 مشكلة برمجيات</option>
                            <option value="أخرى">📋 أخرى</option>
                        </select>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-exclamation me-2 text-primary"></i>الأولوية
                        </label>
                        <select class="form-select" name="priority" required>
                            <option value="">اختر الأولوية</option>
                            <option value="عالي">🔴 عالي</option>
                            <option value="متوسط">🟡 متوسط</option>
                            <option value="منخفض">🟢 منخفض</option>
                        </select>
                    </div>
                </div>
                
                <div class="mb-4">
                    <label class="form-label fw-bold">
                        <i class="fas fa-comment me-2 text-primary"></i>وصف المشكلة
                    </label>
                    <textarea class="form-control" name="description" rows="6" required placeholder="اكتب وصفاً تفصيلياً للمشكلة أو الطلب..."></textarea>
                </div>
                
                <div class="text-center mt-4">
                    <button type="submit" class="btn btn-primary btn-lg px-5 me-3">
                        <i class="fas fa-paper-plane me-2"></i>إرسال التذكرة
                    </button>
                    <a href="/support" class="btn btn-secondary btn-lg px-5">
                        <i class="fas fa-arrow-left me-2"></i>العودة
                    </a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
    ''')

# وظائف تصدير التقارير
@app.route('/export_excel')
def export_excel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        import pandas as pd
        from io import BytesIO
        from flask import send_file
        
        # جمع البيانات
        assets_data = []
        for asset in Asset.query.all():
            assets_data.append({
                'اسم الأصل': asset.name,
                'الفئة': asset.category,
                'الرقم التسلسلي': asset.serial_number,
                'تاريخ الشراء': asset.purchase_date.strftime('%Y-%m-%d'),
                'سعر الشراء': asset.purchase_price,
                'الحالة': asset.status,
                'الموقع': asset.location or '',
                'المسؤول': asset.assigned_to or ''
            })
        
        purchases_data = []
        for purchase in Purchase.query.all():
            purchases_data.append({
                'اسم المنتج': purchase.product_name,
                'المورد': purchase.supplier,
                'الكمية': purchase.quantity,
                'السعر الإجمالي': purchase.total_price,
                'تاريخ الشراء': purchase.purchase_date.strftime('%Y-%m-%d'),
                'الحالة': purchase.status,
                'ملاحظات': purchase.notes or ''
            })
        
        # إنشاء ملف Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if assets_data:
                pd.DataFrame(assets_data).to_excel(writer, sheet_name='الأصول', index=False)
            if purchases_data:
                pd.DataFrame(purchases_data).to_excel(writer, sheet_name='المشتريات', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'تقرير_النظام_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    except ImportError:
        flash('مكتبة pandas غير مثبتة. سيتم تحميل ملف CSV بدلاً من ذلك', 'warning')
        return export_csv()
    except Exception as e:
        flash(f'حدث خطأ أثناء تصدير Excel: {str(e)}', 'error')
        return redirect(url_for('reports'))

@app.route('/export_csv')
def export_csv():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        import csv
        from io import StringIO
        from flask import Response
        
        output = StringIO()
        writer = csv.writer(output)
        
        # كتابة بيانات الأصول
        writer.writerow(['=== الأصول ==='])
        writer.writerow(['اسم الأصل', 'الفئة', 'الرقم التسلسلي', 'تاريخ الشراء', 'سعر الشراء', 'الحالة', 'الموقع', 'المسؤول'])
        
        for asset in Asset.query.all():
            writer.writerow([
                asset.name,
                asset.category,
                asset.serial_number,
                asset.purchase_date.strftime('%Y-%m-%d'),
                asset.purchase_price,
                asset.status,
                asset.location or '',
                asset.assigned_to or ''
            ])
        
        writer.writerow([])  # سطر فارغ
        writer.writerow(['=== المشتريات ==='])
        writer.writerow(['اسم المنتج', 'المورد', 'الكمية', 'السعر الإجمالي', 'تاريخ الشراء', 'الحالة', 'ملاحظات'])
        
        for purchase in Purchase.query.all():
            writer.writerow([
                purchase.product_name,
                purchase.supplier,
                purchase.quantity,
                purchase.total_price,
                purchase.purchase_date.strftime('%Y-%m-%d'),
                purchase.status,
                purchase.notes or ''
            ])
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=تقرير_النظام_{datetime.now().strftime("%Y%m%d")}.csv'}
        )
    except Exception as e:
        flash(f'حدث خطأ أثناء تصدير CSV: {str(e)}', 'error')
        return redirect(url_for('reports'))

@app.route('/export_pdf')
def export_pdf():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # نسخة مبسطة من PDF بدون مكتبات خارجية
    try:
        from flask import make_response
        
        # إنشاء محتوى HTML للطباعة
        html_content = f'''
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>تقرير نظام إدارة الأصول</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ text-align: center; color: #333; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
                th {{ background-color: #f2f2f2; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{ text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px; }}
            </style>
        </head>
        <body>
            <h1>تقرير نظام إدارة الأصول</h1>
            <p>تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            
            <div class="stats">
                <div class="stat-box">
                    <h3>{Asset.query.count()}</h3>
                    <p>إجمالي الأصول</p>
                </div>
                <div class="stat-box">
                    <h3>{Purchase.query.count()}</h3>
                    <p>المشتريات</p>
                </div>
                <div class="stat-box">
                    <h3>{Custody.query.count()}</h3>
                    <p>العهد</p>
                </div>
                <div class="stat-box">
                    <h3>{Invoice.query.count()}</h3>
                    <p>الفواتير</p>
                </div>
            </div>
            
            <h2>الأصول</h2>
            <table>
                <tr>
                    <th>اسم الأصل</th>
                    <th>الفئة</th>
                    <th>الرقم التسلسلي</th>
                    <th>تاريخ الشراء</th>
                    <th>سعر الشراء</th>
                    <th>الحالة</th>
                </tr>
        '''
        
        for asset in Asset.query.all():
            html_content += f'''
                <tr>
                    <td>{asset.name}</td>
                    <td>{asset.category}</td>
                    <td>{asset.serial_number}</td>
                    <td>{asset.purchase_date.strftime('%Y-%m-%d')}</td>
                    <td>{asset.purchase_price} ريال</td>
                    <td>{asset.status}</td>
                </tr>
            '''
        
        html_content += '''
            </table>
            
            <script>
                window.onload = function() {
                    window.print();
                }
            </script>
        </body>
        </html>
        '''
        
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
        
    except Exception as e:
        flash(f'حدث خطأ أثناء إنشاء PDF: {str(e)}', 'error')
        return redirect(url_for('reports'))

@app.route('/interactive_dashboard')
def interactive_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # حساب الإحصائيات
    total_assets = Asset.query.count()
    total_purchases = Purchase.query.count()
    total_custodies = Custody.query.count()
    total_invoices = Invoice.query.count()
    
    # حساب القيم المالية
    total_asset_value = db.session.query(db.func.sum(Asset.purchase_price)).scalar() or 0
    total_purchase_value = db.session.query(db.func.sum(Purchase.total_price)).scalar() or 0
    total_invoice_value = db.session.query(db.func.sum(Invoice.total_amount)).scalar() or 0
    
    # إحصائيات الأصول حسب الفئة
    asset_categories = db.session.query(
        Asset.category, 
        db.func.count(Asset.id)
    ).group_by(Asset.category).all()
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم التفاعلية - نظام إدارة الأصول</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
        .dashboard-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 1rem;
        }
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .chart-container {
            position: relative;
            height: 400px;
            margin: 2rem 0;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-building me-2"></i>
                نظام إدارة الأصول - لوحة التحكم التفاعلية
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/reports">
                    <i class="fas fa-arrow-left me-1"></i>
                    العودة للتقارير
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <!-- الإحصائيات الرئيسية -->
        <div class="row">
            <div class="col-md-3 mb-3">
                <div class="stat-card">
                    <div class="stat-number">{{ total_assets }}</div>
                    <div><i class="fas fa-laptop me-2"></i>إجمالي الأصول</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="stat-card">
                    <div class="stat-number">{{ total_purchases }}</div>
                    <div><i class="fas fa-shopping-cart me-2"></i>المشتريات</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="stat-card">
                    <div class="stat-number">{{ total_custodies }}</div>
                    <div><i class="fas fa-handshake me-2"></i>العهد</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="stat-card">
                    <div class="stat-number">{{ total_invoices }}</div>
                    <div><i class="fas fa-file-invoice me-2"></i>الفواتير</div>
                </div>
            </div>
        </div>
        
        <!-- الرسوم البيانية -->
        <div class="row">
            <div class="col-md-6">
                <div class="dashboard-card">
                    <h5><i class="fas fa-chart-pie me-2 text-primary"></i>توزيع الأصول حسب الفئة</h5>
                    <div class="chart-container">
                        <canvas id="assetCategoryChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="dashboard-card">
                    <h5><i class="fas fa-chart-bar me-2 text-primary"></i>القيم المالية</h5>
                    <div class="chart-container">
                        <canvas id="financialChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- معلومات إضافية -->
        <div class="row">
            <div class="col-md-12">
                <div class="dashboard-card">
                    <h5><i class="fas fa-info-circle me-2 text-primary"></i>ملخص مالي</h5>
                    <div class="row text-center">
                        <div class="col-md-4">
                            <h6 class="text-muted">قيمة الأصول الإجمالية</h6>
                            <h3 class="text-primary">{{ "{:,.0f}".format(total_asset_value) }} ريال</h3>
                        </div>
                        <div class="col-md-4">
                            <h6 class="text-muted">قيمة المشتريات الإجمالية</h6>
                            <h3 class="text-success">{{ "{:,.0f}".format(total_purchase_value) }} ريال</h3>
                        </div>
                        <div class="col-md-4">
                            <h6 class="text-muted">قيمة الفواتير الإجمالية</h6>
                            <h3 class="text-warning">{{ "{:,.0f}".format(total_invoice_value) }} ريال</h3>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // رسم بياني دائري للأصول حسب الفئة
        const assetCategoryData = {
            labels: [{% for category, count in asset_categories %}'{{ category }}'{% if not loop.last %},{% endif %}{% endfor %}],
            datasets: [{
                data: [{% for category, count in asset_categories %}{{ count }}{% if not loop.last %},{% endif %}{% endfor %}],
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40'
                ]
            }]
        };
        
        const assetCategoryChart = new Chart(document.getElementById('assetCategoryChart'), {
            type: 'doughnut',
            data: assetCategoryData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
        // رسم بياني للقيم المالية
        const financialData = {
            labels: ['قيمة الأصول', 'قيمة المشتريات', 'قيمة الفواتير'],
            datasets: [{
                label: 'القيمة بالريال',
                data: [{{ total_asset_value }}, {{ total_purchase_value }}, {{ total_invoice_value }}],
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(40, 167, 69, 0.8)',
                    'rgba(255, 193, 7, 0.8)'
                ],
                borderColor: [
                    'rgba(102, 126, 234, 1)',
                    'rgba(40, 167, 69, 1)',
                    'rgba(255, 193, 7, 1)'
                ],
                borderWidth: 2
            }]
        };
        
        const financialChart = new Chart(document.getElementById('financialChart'), {
            type: 'bar',
            data: financialData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString() + ' ريال';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    </script>
</body>
</html>
    ''', 
    total_assets=total_assets,
    total_purchases=total_purchases,
    total_custodies=total_custodies,
    total_invoices=total_invoices,
    total_asset_value=total_asset_value,
    total_purchase_value=total_purchase_value,
    total_invoice_value=total_invoice_value,
    asset_categories=asset_categories
    )

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
        .permissions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        .permission-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            border: 2px solid #e9ecef;
        }
        .permission-card.active {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.1);
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
        }
        .permission-group {
            margin-bottom: 2rem;
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
            <div class="user-info">
                <h2><i class="fas fa-user-cog me-2"></i>تعديل صلاحيات المستخدم</h2>
                <p class="mb-0">
                    <i class="fas fa-user me-2"></i>المستخدم: <strong>{{ user.username }}</strong> |
                    <i class="fas fa-envelope me-2"></i>البريد: <strong>{{ user.email }}</strong>
                </p>
            </div>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <!-- اختيار الدور -->
                <div class="permissions-section">
                    <h5 class="permission-title"><i class="fas fa-user-tag me-2"></i>الدور الوظيفي</h5>
                    <select class="form-select" name="role_id">
                        <option value="">اختر الدور</option>
                        {% for role in roles %}
                        <option value="{{ role.id }}" {{ 'selected' if user.role_id == role.id else '' }}>
                            {{ role.name }}
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
                                <input class="form-check-input" type="checkbox" name="can_view_assets" 
                                       {{ 'checked' if user.can_view_assets else '' }}>
                                <label class="form-check-label">عرض الأصول</label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_add_assets" 
                                       {{ 'checked' if user.can_add_assets else '' }}>
                                <label class="form-check-label">إضافة أصول</label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_edit_assets" 
                                       {{ 'checked' if user.can_edit_assets else '' }}>
                                <label class="form-check-label">تعديل الأصول</label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_delete_assets" 
                                       {{ 'checked' if user.can_delete_assets else '' }}>
                                <label class="form-check-label">حذف الأصول</label>
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
                                <input class="form-check-input" type="checkbox" name="can_view_employees" 
                                       {{ 'checked' if user.can_view_employees else '' }}>
                                <label class="form-check-label">عرض الموظفين</label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_add_employees" 
                                       {{ 'checked' if user.can_add_employees else '' }}>
                                <label class="form-check-label">إضافة موظفين</label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_edit_employees" 
                                       {{ 'checked' if user.can_edit_employees else '' }}>
                                <label class="form-check-label">تعديل الموظفين</label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_delete_employees" 
                                       {{ 'checked' if user.can_delete_employees else '' }}>
                                <label class="form-check-label">حذف الموظفين</label>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- صلاحيات المشتريات -->
                <div class="permissions-section">
                    <h5 class="permission-title"><i class="fas fa-shopping-cart me-2"></i>صلاحيات المشتريات</h5>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_view_purchases" 
                                       {{ 'checked' if user.can_view_purchases else '' }}>
                                <label class="form-check-label">عرض المشتريات</label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_add_purchases" 
                                       {{ 'checked' if user.can_add_purchases else '' }}>
                                <label class="form-check-label">إضافة مشتريات</label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_edit_purchases" 
                                       {{ 'checked' if user.can_edit_purchases else '' }}>
                                <label class="form-check-label">تعديل المشتريات</label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_delete_purchases" 
                                       {{ 'checked' if user.can_delete_purchases else '' }}>
                                <label class="form-check-label">حذف المشتريات</label>
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
                                <input class="form-check-input" type="checkbox" name="can_view_reports" 
                                       {{ 'checked' if user.can_view_reports else '' }}>
                                <label class="form-check-label">عرض التقارير</label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="can_export_reports" 
                                       {{ 'checked' if user.can_export_reports else '' }}>
                                <label class="form-check-label">تصدير التقارير</label>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- صلاحيات إدارة النظام -->
                <div class="permissions-section">
                    <h5 class="permission-title"><i class="fas fa-cogs me-2"></i>صلاحيات إدارة النظام</h5>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" name="can_manage_users" 
                               {{ 'checked' if user.can_manage_users else '' }}>
                        <label class="form-check-label">إدارة المستخدمين والصلاحيات</label>
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
        // تأثيرات تفاعلية للصلاحيات
        document.addEventListener('DOMContentLoaded', function() {
            const checkboxes = document.querySelectorAll('.form-check-input');
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    const section = this.closest('.permissions-section');
                    if (this.checked) {
                        section.style.borderColor = '#667eea';
                        section.style.backgroundColor = 'rgba(102, 126, 234, 0.05)';
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
        .form-card {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
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
        .form-control, .form-select {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.8rem 1rem;
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
    
    <div class="container">
        <div class="form-card">
            <div class="text-center mb-4">
                <h2><i class="fas fa-user-plus me-2 text-primary"></i>إضافة مستخدم جديد</h2>
                <p class="text-muted">أدخل بيانات المستخدم الجديد</p>
            </div>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-user me-2 text-primary"></i>اسم المستخدم
                        </label>
                        <input type="text" class="form-control" name="username" required placeholder="أدخل اسم المستخدم">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-envelope me-2 text-primary"></i>البريد الإلكتروني
                        </label>
                        <input type="email" class="form-control" name="email" required placeholder="أدخل البريد الإلكتروني">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-lock me-2 text-primary"></i>كلمة المرور
                        </label>
                        <input type="password" class="form-control" name="password" required placeholder="أدخل كلمة المرور">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">
                            <i class="fas fa-lock me-2 text-primary"></i>تأكيد كلمة المرور
                        </label>
                        <input type="password" class="form-control" name="confirm_password" required placeholder="أعد إدخال كلمة المرور">
                    </div>
                </div>
                
                <div class="text-center mt-4">
                    <button type="submit" class="btn btn-primary btn-lg px-5 me-3">
                        <i class="fas fa-save me-2"></i>حفظ المستخدم
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

@app.route('/toggle_user/<int:user_id>', methods=['POST'])
def toggle_user(user_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# صفحة إدارة الأدوار
@app.route('/manage_roles')
def manage_roles():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # التحقق من صلاحية إدارة المستخدمين
    current_user = User.query.get(session['user_id'])
    if not current_user.can_manage_users:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('dashboard'))
    
    roles = UserRole.query.all()
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة الأدوار - نظام إدارة الأصول</title>
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
        .role-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }
        .role-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1rem;
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
                <a class="nav-link text-white" href="/users">
                    <i class="fas fa-arrow-left me-1"></i>
                    العودة للمستخدمين
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="main-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-user-tag me-2 text-primary"></i>إدارة الأدوار والصلاحيات</h2>
                <a href="/add_role" class="btn btn-primary">
                    <i class="fas fa-plus me-2"></i>إضافة دور جديد
                </a>
            </div>
            
            <div class="row">
                {% for role in roles %}
                <div class="col-md-6 mb-3">
                    <div class="role-card">
                        <h5><i class="fas fa-user-tag me-2 text-primary"></i>{{ role.name }}</h5>
                        <p class="text-muted">{{ role.description or 'لا يوجد وصف' }}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-info">
                                {{ role.users|length }} مستخدم
                            </span>
                            <div class="btn-group">
                                <button class="btn btn-sm btn-outline-primary" onclick="editRole({{ role.id }})">
                                    <i class="fas fa-edit"></i> تعديل
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteRole({{ role.id }})">
                                    <i class="fas fa-trash"></i> حذف
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <script>
        function editRole(id) {
            window.location.href = '/edit_role/' + id;
        }
        
        function deleteRole(id) {
            Swal.fire({
                title: 'حذف الدور؟',
                text: "هل أنت متأكد من حذف هذا الدور؟ لا يمكن التراجع عن هذا الإجراء!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'نعم، احذف!',
                cancelButtonText: 'إلغاء'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch('/delete_role/' + id, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire('تم الحذف!', 'تم حذف الدور بنجاح.', 'success')
                            .then(() => location.reload());
                        } else {
                            Swal.fire('خطأ!', 'حدث خطأ أثناء الحذف.', 'error');
                        }
                    });
                }
            });
        }
    </script>
</body>
</html>
    ''', roles=roles)

# تهيئة قاعدة البيانات
def init_db():
    with app.app_context():
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

if __name__ == '__main__':
    init_db()
    print("=" * 70)
    print("🚀 نظام إدارة الأصول الاحترافي")
    print("   Professional Asset Management System")
    print("=" * 70)
    print("✅ النظام جاهز!")
    print("🌐 الرابط: http://localhost:5000")
    print("👤 المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("🎨 التصميم: احترافي ومتقدم")
    print("📱 متجاوب: يعمل على جميع الأجهزة")
    print("🔧 للإيقاف: اضغط Ctrl+C")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5000, debug=False)