#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# قوالب محدثة مع أزرار العودة للرئيسية

# قالب الأصول مع زر العودة
ASSETS_TEMPLATE_WITH_HOME = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إدارة الأصول</title>
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
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-laptop text-primary me-2"></i>إدارة الأصول</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                <a href="/add_asset" class="btn btn-primary">
                    <i class="fas fa-plus me-2"></i>إضافة أصل جديد
                </a>
            </div>
        </div>
        
        <!-- محتوى الصفحة هنا -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h5>قائمة الأصول</h5>
                        <p>هنا ستظهر قائمة الأصول...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# قالب الموظفين مع زر العودة
EMPLOYEES_TEMPLATE_WITH_HOME = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إدارة الموظفين</title>
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
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-users text-primary me-2"></i>إدارة الموظفين</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                <a href="/add_employee" class="btn btn-primary">
                    <i class="fas fa-plus me-2"></i>إضافة موظف جديد
                </a>
            </div>
        </div>
        
        <!-- محتوى الصفحة هنا -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h5>قائمة الموظفين</h5>
                        <p>هنا ستظهر قائمة الموظفين...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# قالب المشتريات مع زر العودة
PURCHASES_TEMPLATE_WITH_HOME = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إدارة المشتريات</title>
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
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-shopping-cart text-primary me-2"></i>إدارة المشتريات</h2>
            <div>
                <a href="/" class="btn btn-outline-success me-2">
                    <i class="fas fa-home me-1"></i>الرئيسية
                </a>
                <a href="/add_purchase" class="btn btn-primary">
                    <i class="fas fa-plus me-2"></i>إضافة مشترى جديد
                </a>
            </div>
        </div>
        
        <!-- محتوى الصفحة هنا -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h5>قائمة المشتريات</h5>
                        <p>هنا ستظهر قائمة المشتريات...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function updateStatus(purchaseId, newStatus) {
            if (confirm(`تأكيد تحديث حالة المشترى إلى ${newStatus}؟`)) {
                fetch('/api/update_purchase_status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        purchase_id: purchaseId,
                        status: newStatus
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('تم تحديث الحالة بنجاح');
                        location.reload();
                    } else {
                        alert('خطأ في تحديث الحالة');
                    }
                })
                .catch(error => {
                    alert('خطأ في الاتصال');
                });
            }
        }
    </script>
</body>
</html>
'''

print("✅ تم إنشاء القوالب المحدثة مع أزرار العودة للرئيسية!")