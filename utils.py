#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وظائف مساعدة لنظام إدارة الأصول التقنية
IT Asset Management System Utilities
"""

import os
import qrcode
import io
import base64
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from PIL import Image as PILImage
import json

def allowed_file(filename, allowed_extensions):
    """التحقق من امتداد الملف المسموح"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_asset_tag(category_name, existing_tags=None):
    """إنشاء رقم أصل تلقائي"""
    category_prefixes = {
        'أجهزة الكمبيوتر': 'PC',
        'الخوادم': 'SRV',
        'معدات الشبكة': 'NET',
        'الطابعات والماسحات': 'PRT',
        'الهواتف': 'PHN',
        'الشاشات والعرض': 'MON',
        'أجهزة التخزين': 'STG',
        'معدات الأمان': 'SEC'
    }
    
    prefix = category_prefixes.get(category_name, 'AST')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')[-8:]
    
    base_tag = f"{prefix}-{timestamp}"
    
    # التأكد من عدم تكرار الرقم
    if existing_tags:
        counter = 1
        while base_tag in existing_tags:
            base_tag = f"{prefix}-{timestamp}-{counter:02d}"
            counter += 1
    
    return base_tag

def generate_qr_code(data, size=10, border=4):
    """إنشاء QR Code"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=border,
    )
    
    if isinstance(data, dict):
        qr_data = json.dumps(data, ensure_ascii=False)
    else:
        qr_data = str(data)
    
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # تحويل إلى base64
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer

def create_asset_label(asset, qr_size=150):
    """إنشاء ملصق للأصل مع QR Code"""
    # إنشاء QR Code
    qr_data = {
        'asset_tag': asset.asset_tag,
        'name': asset.name,
        'category': asset.category.name,
        'id': asset.id
    }
    
    qr_buffer = generate_qr_code(qr_data, size=8, border=2)
    
    # إنشاء PDF للملصق
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(6*cm, 4*cm), 
                          rightMargin=0.5*cm, leftMargin=0.5*cm,
                          topMargin=0.5*cm, bottomMargin=0.5*cm)
    
    # الأنماط
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading2'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        spaceAfter=3
    )
    
    # محتوى الملصق
    story = []
    
    # العنوان
    story.append(Paragraph(asset.name, title_style))
    
    # رقم الأصل
    story.append(Paragraph(f"<b>{asset.asset_tag}</b>", normal_style))
    
    # الفئة
    story.append(Paragraph(asset.category.name, normal_style))
    
    # QR Code
    qr_img = Image(qr_buffer, width=3*cm, height=3*cm)
    story.append(qr_img)
    
    doc.build(story)
    buffer.seek(0)
    
    return buffer

def generate_assets_report(assets, report_type='summary'):
    """إنشاء تقرير الأصول"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          rightMargin=2*cm, leftMargin=2*cm,
                          topMargin=2*cm, bottomMargin=2*cm)
    
    # الأنماط
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=TA_RIGHT,
        spaceAfter=12
    )
    
    story = []
    
    # العنوان
    story.append(Paragraph("تقرير الأصول التقنية", title_style))
    story.append(Paragraph(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    if report_type == 'summary':
        # ملخص الأصول
        story.append(Paragraph("ملخص الأصول", heading_style))
        
        # إحصائيات
        total_assets = len(assets)
        active_assets = len([a for a in assets if a.status == 'active'])
        maintenance_assets = len([a for a in assets if a.status == 'maintenance'])
        
        summary_data = [
            ['البيان', 'العدد'],
            ['إجمالي الأصول', str(total_assets)],
            ['الأصول النشطة', str(active_assets)],
            ['الأصول قيد الصيانة', str(maintenance_assets)],
        ]
        
        summary_table = Table(summary_data, colWidths=[8*cm, 4*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
    
    # جدول الأصول التفصيلي
    story.append(Paragraph("تفاصيل الأصول", heading_style))
    
    # بيانات الجدول
    table_data = [['رقم الأصل', 'الاسم', 'الفئة', 'الحالة', 'تاريخ الشراء']]
    
    for asset in assets:
        table_data.append([
            asset.asset_tag,
            asset.name[:30] + '...' if len(asset.name) > 30 else asset.name,
            asset.category.name,
            'نشط' if asset.status == 'active' else 'صيانة' if asset.status == 'maintenance' else asset.status,
            asset.purchase_date.strftime('%Y-%m-%d') if asset.purchase_date else 'غير محدد'
        ])
    
    # إنشاء الجدول
    assets_table = Table(table_data, colWidths=[3*cm, 5*cm, 3*cm, 2*cm, 3*cm])
    assets_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    story.append(assets_table)
    
    # بناء PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer

def calculate_asset_depreciation(purchase_cost, purchase_date, useful_life_years=5):
    """حساب الاستهلاك للأصل"""
    if not purchase_cost or not purchase_date:
        return None
    
    # حساب عدد السنوات منذ الشراء
    years_since_purchase = (datetime.now().date() - purchase_date).days / 365.25
    
    # الاستهلاك السنوي
    annual_depreciation = purchase_cost / useful_life_years
    
    # إجمالي الاستهلاك
    total_depreciation = min(annual_depreciation * years_since_purchase, purchase_cost)
    
    # القيمة الحالية
    current_value = purchase_cost - total_depreciation
    
    return {
        'purchase_cost': purchase_cost,
        'annual_depreciation': annual_depreciation,
        'total_depreciation': total_depreciation,
        'current_value': max(current_value, 0),
        'depreciation_percentage': (total_depreciation / purchase_cost) * 100
    }

def get_maintenance_schedule(asset, maintenance_interval_months=6):
    """حساب جدول الصيانة الوقائية"""
    if not asset.purchase_date:
        return []
    
    schedule = []
    start_date = asset.purchase_date
    current_date = datetime.now().date()
    
    # إنشاء جدول الصيانة
    maintenance_date = start_date + timedelta(days=maintenance_interval_months * 30)
    
    while maintenance_date <= current_date + timedelta(days=365):  # السنة القادمة
        schedule.append({
            'date': maintenance_date,
            'type': 'preventive',
            'description': f'صيانة وقائية دورية - {asset.name}',
            'is_overdue': maintenance_date < current_date
        })
        maintenance_date += timedelta(days=maintenance_interval_months * 30)
    
    return schedule

def validate_asset_data(data):
    """التحقق من صحة بيانات الأصل"""
    errors = []
    
    # التحقق من الحقول المطلوبة
    required_fields = ['asset_tag', 'name', 'category_id']
    for field in required_fields:
        if not data.get(field):
            errors.append(f'الحقل {field} مطلوب')
    
    # التحقق من صيغة رقم الأصل
    asset_tag = data.get('asset_tag', '')
    if asset_tag and not asset_tag.replace('-', '').replace('_', '').isalnum():
        errors.append('رقم الأصل يجب أن يحتوي على أحرف وأرقام فقط')
    
    # التحقق من التواريخ
    purchase_date = data.get('purchase_date')
    warranty_expiry = data.get('warranty_expiry')
    
    if purchase_date and warranty_expiry:
        if purchase_date > warranty_expiry:
            errors.append('تاريخ انتهاء الضمان يجب أن يكون بعد تاريخ الشراء')
    
    # التحقق من التكلفة
    purchase_cost = data.get('purchase_cost')
    if purchase_cost and purchase_cost < 0:
        errors.append('تكلفة الشراء يجب أن تكون أكبر من الصفر')
    
    return errors

def format_currency(amount, currency='ريال'):
    """تنسيق العملة"""
    if amount is None:
        return 'غير محدد'
    return f"{amount:,.2f} {currency}"

def get_asset_age(purchase_date):
    """حساب عمر الأصل"""
    if not purchase_date:
        return 'غير محدد'
    
    age = datetime.now().date() - purchase_date
    years = age.days // 365
    months = (age.days % 365) // 30
    
    if years > 0:
        return f"{years} سنة و {months} شهر"
    elif months > 0:
        return f"{months} شهر"
    else:
        return f"{age.days} يوم"

def get_warranty_status(warranty_expiry):
    """حالة الضمان"""
    if not warranty_expiry:
        return {'status': 'unknown', 'message': 'غير محدد', 'class': 'secondary'}
    
    today = datetime.now().date()
    days_remaining = (warranty_expiry - today).days
    
    if days_remaining < 0:
        return {'status': 'expired', 'message': 'منتهي الصلاحية', 'class': 'danger'}
    elif days_remaining <= 30:
        return {'status': 'expiring', 'message': f'ينتهي خلال {days_remaining} يوم', 'class': 'warning'}
    else:
        return {'status': 'valid', 'message': f'ساري لمدة {days_remaining} يوم', 'class': 'success'}

def backup_database(db_path, backup_dir='backups'):
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    import shutil
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"it_assets_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        shutil.copy2(db_path, backup_path)
        return backup_path
    except Exception as e:
        return None

def clean_old_backups(backup_dir='backups', keep_days=30):
    """حذف النسخ الاحتياطية القديمة"""
    if not os.path.exists(backup_dir):
        return
    
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    
    for filename in os.listdir(backup_dir):
        if filename.startswith('it_assets_backup_') and filename.endswith('.db'):
            file_path = os.path.join(backup_dir, filename)
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            
            if file_time < cutoff_date:
                try:
                    os.remove(file_path)
                except Exception:
                    pass