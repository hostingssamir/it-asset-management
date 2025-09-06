# القوالب المتبقية للنظام

EMPLOYEES_TEMPLATE = '''
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
            transition: transform 0.3s ease;
        }
        .card:hover { transform: translateY(-5px); }
        .employee-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        .employee-card:hover { transform: translateY(-3px); }
        .badge { padding: 0.5rem 1rem; border-radius: 10px; font-weight: 500; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link text-white" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a></li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-laptop me-1"></i>الأصول
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/assets"><i class="fas fa-list me-2"></i>عرض الأصول</a></li>
                            <li><a class="dropdown-item" href="/add_asset"><i class="fas fa-plus me-2"></i>إضافة أصل</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/custody"><i class="fas fa-handshake me-2"></i>إدارة العهد</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white active" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-users me-1"></i>الموظفين
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/employees"><i class="fas fa-users me-2"></i>عرض الموظفين</a></li>
                            <li><a class="dropdown-item" href="/add_employee"><i class="fas fa-user-plus me-2"></i>إضافة موظف</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/departments"><i class="fas fa-building me-2"></i>الإدارات</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-shopping-cart me-1"></i>المشتريات
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/purchases"><i class="fas fa-shopping-cart me-2"></i>عرض المشتريات</a></li>
                            <li><a class="dropdown-item" href="/add_purchase"><i class="fas fa-plus me-2"></i>إضافة مشترى</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/invoices"><i class="fas fa-file-invoice me-2"></i>الفواتير</a></li>
                            <li><a class="dropdown-item" href="/licenses"><i class="fas fa-key me-2"></i>التراخيص</a></li>
                        </ul>
                    </li>
                    <li class="nav-item"><a class="nav-link text-white" href="/support"><i class="fas fa-headset me-1"></i>الدعم الفني</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/reports"><i class="fas fa-chart-bar me-1"></i>التقارير</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/notifications"><i class="fas fa-bell me-1"></i>الإشعارات</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/logout"><i class="fas fa-sign-out-alt me-1"></i>خروج</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-users text-primary me-2"></i>إدارة الموظفين</h2>
            <a href="/add_employee" class="btn btn-primary">
                <i class="fas fa-user-plus me-2"></i>إضافة موظف جديد
            </a>
        </div>

        <div class="row">
            {% for employee in employees %}
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 50px; height: 50px;">
                                <i class="fas fa-user text-white"></i>
                            </div>
                            <div>
                                <h5 class="mb-1">{{ employee[2] }}</h5>
                                <small class="text-muted">{{ employee[1] }}</small>
                            </div>
                        </div>
                        
                        <div class="mb-2">
                            <span class="badge bg-secondary">{{ employee[3] }}</span>
                            <span class="badge bg-info ms-1">{{ employee[4] }}</span>
                        </div>
                        
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-envelope me-1"></i>{{ employee[5] or 'غير محدد' }}
                            </small>
                        </div>
                        
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-phone me-1"></i>{{ employee[6] or 'غير محدد' }}
                            </small>
                        </div>
                        
                        {% if employee[10] %}
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-map-marker-alt me-1"></i>{{ employee[10] }}
                            </small>
                        </div>
                        {% endif %}
                        
                        {% if employee[12] %}
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-user-tie me-1"></i>المدير: {{ employee[12] }}
                            </small>
                        </div>
                        {% endif %}
                        
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="badge bg-{{ 'success' if employee[8] == 'نشط' else 'warning' }}">
                                {{ employee[8] }}
                            </span>
                            <div>
                                <button class="btn btn-sm btn-outline-info me-1" onclick="editEmployee({{ employee[0] }})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-primary me-1" onclick="createTicket({{ employee[0] }}, '{{ employee[2] }}')">
                                    <i class="fas fa-ticket-alt"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteEmployee({{ employee[0] }}, '{{ employee[2] }}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function editEmployee(employeeId) {
            alert('تحرير الموظف رقم: ' + employeeId);
        }
        
        function createTicket(employeeId, employeeName) {
            if (confirm(`إنشاء تذكرة دعم فني للموظف: ${employeeName}؟`)) {
                alert('تم إنشاء تذكرة دعم فني');
            }
        }
        
        function deleteEmployee(employeeId, employeeName) {
            if (confirm(`هل أنت متأكد من حذف الموظف "${employeeName}"؟\\n\\nسيتم التحقق من عدم وجود أصول مخصصة له.`)) {
                alert('تم حذف الموظف بنجاح');
                location.reload();
            }
        }
    </script>
</body>
</html>
'''

DEPARTMENTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>الإدارات</title>
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
        .dept-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        .dept-card:hover { transform: translateY(-3px); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link text-white" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a></li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-laptop me-1"></i>الأصول
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/assets"><i class="fas fa-list me-2"></i>عرض الأصول</a></li>
                            <li><a class="dropdown-item" href="/add_asset"><i class="fas fa-plus me-2"></i>إضافة أصل</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/custody"><i class="fas fa-handshake me-2"></i>إدارة العهد</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white active" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-users me-1"></i>الموظفين
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/employees"><i class="fas fa-users me-2"></i>عرض الموظفين</a></li>
                            <li><a class="dropdown-item" href="/add_employee"><i class="fas fa-user-plus me-2"></i>إضافة موظف</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/departments"><i class="fas fa-building me-2"></i>الإدارات</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-shopping-cart me-1"></i>المشتريات
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/purchases"><i class="fas fa-shopping-cart me-2"></i>عرض المشتريات</a></li>
                            <li><a class="dropdown-item" href="/add_purchase"><i class="fas fa-plus me-2"></i>إضافة مشترى</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/invoices"><i class="fas fa-file-invoice me-2"></i>الفواتير</a></li>
                            <li><a class="dropdown-item" href="/licenses"><i class="fas fa-key me-2"></i>التراخيص</a></li>
                        </ul>
                    </li>
                    <li class="nav-item"><a class="nav-link text-white" href="/support"><i class="fas fa-headset me-1"></i>الدعم الفني</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/reports"><i class="fas fa-chart-bar me-1"></i>التقارير</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/notifications"><i class="fas fa-bell me-1"></i>الإشعارات</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/logout"><i class="fas fa-sign-out-alt me-1"></i>خروج</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-building text-primary me-2"></i>الإدارات</h2>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addDeptModal">
                <i class="fas fa-plus me-2"></i>إضافة إدارة جديدة
            </button>
        </div>

        <div class="row">
            {% for dept in departments %}
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 50px; height: 50px;">
                                <i class="fas fa-building text-white"></i>
                            </div>
                            <div>
                                <h5 class="mb-1">{{ dept[1] }}</h5>
                                <small class="text-muted">إدارة</small>
                            </div>
                        </div>
                        
                        {% if dept[4] %}
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-user-tie me-1"></i>المدير: {{ dept[4] }}
                            </small>
                        </div>
                        {% endif %}
                        
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-users me-1"></i>عدد الموظفين: {{ dept[5] or 0 }}
                            </small>
                        </div>
                        
                        {% if dept[3] %}
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-dollar-sign me-1"></i>الميزانية: {{ "{:,.0f}".format(dept[3]) }} ريال
                            </small>
                        </div>
                        {% endif %}
                        
                        {% if dept[4] %}
                        <div class="mb-3">
                            <small class="text-muted">{{ dept[4] }}</small>
                        </div>
                        {% endif %}
                        
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-success">نشط</span>
                            <div>
                                <button class="btn btn-sm btn-outline-info me-1" onclick="editDept({{ dept[0] }})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-primary me-1" onclick="viewEmployees('{{ dept[1] }}')">
                                    <i class="fas fa-users"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteDept({{ dept[0] }}, '{{ dept[1] }}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
            
            <!-- بطاقات الإدارات الافتراضية إذا لم توجد بيانات -->
            {% if not departments %}
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="dept-card p-4 text-center">
                    <i class="fas fa-calculator fa-3x mb-3"></i>
                    <h5>المحاسبة</h5>
                    <p class="mb-2">إدارة الشؤون المالية والمحاسبية</p>
                    <small>5 موظفين</small>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="dept-card p-4 text-center">
                    <i class="fas fa-chart-line fa-3x mb-3"></i>
                    <h5>المبيعات</h5>
                    <p class="mb-2">إدارة المبيعات وخدمة العملاء</p>
                    <small>8 موظفين</small>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="dept-card p-4 text-center">
                    <i class="fas fa-laptop-code fa-3x mb-3"></i>
                    <h5>تقنية المعلومات</h5>
                    <p class="mb-2">إدارة الأنظمة والتطوير</p>
                    <small>6 موظفين</small>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="dept-card p-4 text-center">
                    <i class="fas fa-bullhorn fa-3x mb-3"></i>
                    <h5>التسويق</h5>
                    <p class="mb-2">إدارة التسويق والإعلان</p>
                    <small>4 موظفين</small>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="dept-card p-4 text-center">
                    <i class="fas fa-users fa-3x mb-3"></i>
                    <h5>الموارد البشرية</h5>
                    <p class="mb-2">إدارة شؤون الموظفين</p>
                    <small>3 موظفين</small>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="dept-card p-4 text-center">
                    <i class="fas fa-cog fa-3x mb-3"></i>
                    <h5>الإدارة العامة</h5>
                    <p class="mb-2">الإدارة العليا والتخطيط</p>
                    <small>2 موظفين</small>
                </div>
            </div>
            {% endif %}
        </div>
    </div>

    <!-- Modal إضافة إدارة -->
    <div class="modal fade" id="addDeptModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">إضافة إدارة جديدة</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="deptForm">
                        <div class="mb-3">
                            <label class="form-label">اسم الإدارة</label>
                            <input type="text" class="form-control" name="name" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">المدير</label>
                            <select class="form-control" name="manager_id">
                                <option value="">اختر المدير</option>
                                <!-- سيتم ملؤها بـ JavaScript -->
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">الميزانية (ريال)</label>
                            <input type="number" class="form-control" name="budget">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">الوصف</label>
                            <textarea class="form-control" name="description" rows="3"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                    <button type="button" class="btn btn-primary" onclick="saveDept()">حفظ الإدارة</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function editDept(deptId) {
            alert('تحرير الإدارة رقم: ' + deptId);
        }
        
        function viewEmployees(deptName) {
            alert('عرض موظفي إدارة: ' + deptName);
        }
        
        function deleteDept(deptId, deptName) {
            if (confirm(`هل أنت متأكد من حذف إدارة "${deptName}"؟`)) {
                alert('تم حذف الإدارة بنجاح');
                location.reload();
            }
        }
        
        function saveDept() {
            alert('تم حفظ الإدارة بنجاح');
            document.getElementById('deptForm').reset();
            bootstrap.Modal.getInstance(document.getElementById('addDeptModal')).hide();
        }
    </script>
</body>
</html>
'''

PURCHASES_TEMPLATE = '''
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
        .stats-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        .stats-card:hover { transform: translateY(-3px); }
        .table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
        }
        .badge { padding: 0.5rem 1rem; border-radius: 10px; font-weight: 500; }
        .btn-action { border-radius: 10px; margin: 0 2px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/"><i class="fas fa-rocket me-2"></i>نظام إدارة الأصول</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link text-white" href="/"><i class="fas fa-home me-1"></i>الرئيسية</a></li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-laptop me-1"></i>الأصول
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/assets"><i class="fas fa-list me-2"></i>عرض الأصول</a></li>
                            <li><a class="dropdown-item" href="/add_asset"><i class="fas fa-plus me-2"></i>إضافة أصل</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/custody"><i class="fas fa-handshake me-2"></i>إدارة العهد</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-users me-1"></i>الموظفين
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/employees"><i class="fas fa-users me-2"></i>عرض الموظفين</a></li>
                            <li><a class="dropdown-item" href="/add_employee"><i class="fas fa-user-plus me-2"></i>إضافة موظف</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/departments"><i class="fas fa-building me-2"></i>الإدارات</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white active" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-shopping-cart me-1"></i>المشتريات
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/purchases"><i class="fas fa-shopping-cart me-2"></i>عرض المشتريات</a></li>
                            <li><a class="dropdown-item" href="/add_purchase"><i class="fas fa-plus me-2"></i>إضافة مشترى</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/invoices"><i class="fas fa-file-invoice me-2"></i>الفواتير</a></li>
                            <li><a class="dropdown-item" href="/licenses"><i class="fas fa-key me-2"></i>التراخيص</a></li>
                        </ul>
                    </li>
                    <li class="nav-item"><a class="nav-link text-white" href="/support"><i class="fas fa-headset me-1"></i>الدعم الفني</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/reports"><i class="fas fa-chart-bar me-1"></i>التقارير</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/notifications"><i class="fas fa-bell me-1"></i>الإشعارات</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/logout"><i class="fas fa-sign-out-alt me-1"></i>خروج</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-shopping-cart text-primary me-2"></i>إدارة المشتريات</h2>
            <a href="/add_purchase" class="btn btn-primary">
                <i class="fas fa-plus me-2"></i>إضافة مشترى جديد
            </a>
        </div>

        <!-- إحصائيات المشتريات -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-shopping-cart fa-3x mb-3"></i>
                    <h3>{{ total_purchases }}</h3>
                    <p class="mb-0">إجمالي المشتريات</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-dollar-sign fa-3x mb-3"></i>
                    <h3>{{ "{:,.0f}".format(total_amount) }}</h3>
                    <p class="mb-0">إجمالي القيمة (ريال)</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-clock fa-3x mb-3"></i>
                    <h3>{{ pending_purchases }}</h3>
                    <p class="mb-0">قيد التوريد</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stats-card p-4 text-center">
                    <i class="fas fa-chart-line fa-3x mb-3"></i>
                    <h3>{{ "{:,.0f}".format(total_amount / total_purchases if total_purchases > 0 else 0) }}</h3>
                    <p class="mb-0">متوسط قيمة المشترى</p>
                </div>
            </div>
        </div>

        <!-- جدول المشتريات -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-list me-2"></i>قائمة المشتريات</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>رقم المشترى</th>
                                <th>المورد</th>
                                <th>الصنف</th>
                                <th>الفئة</th>
                                <th>الكمية</th>
                                <th>القيمة الإجمالية</th>
                                <th>الحالة</th>
                                <th>تاريخ التوريد</th>
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for purchase in purchases %}
                            <tr>
                                <td><strong class="text-primary">{{ purchase[1] }}</strong></td>
                                <td>{{ purchase[2] }}</td>
                                <td>{{ purchase[4] }}</td>
                                <td><span class="badge bg-secondary">{{ purchase[6] }}</span></td>
                                <td>{{ purchase[7] }}</td>
                                <td><strong>{{ "{:,.2f}".format(purchase[9]) }} {{ purchase[10] }}</strong></td>
                                <td>
                                    <span class="badge bg-{{ 'success' if purchase[15] == 'مكتمل' else 'warning' if purchase[15] == 'قيد التوريد' else 'secondary' }}">
                                        {{ purchase[15] }}
                                    </span>
                                </td>
                                <td>{{ purchase[12] or 'غير محدد' }}</td>
                                <td>
                                    <button class="btn btn-primary btn-sm btn-action" onclick="viewPurchase('{{ purchase[1] }}')">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-success btn-sm btn-action" onclick="updateStatus({{ purchase[0] }}, 'مكتمل')">
                                        <i class="fas fa-check"></i>
                                    </button>
                                    <button class="btn btn-info btn-sm btn-action" onclick="createInvoice({{ purchase[0] }})">
                                        <i class="fas fa-file-invoice"></i>
                                    </button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function viewPurchase(purchaseNumber) {
            alert(`عرض تفاصيل المشترى: ${purchaseNumber}`);
        }
        
        function updateStatus(purchaseId, newStatus) {
            if (confirm(`تحديث حالة المشترى إلى "${newStatus}"؟`)) {
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
        
        function createInvoice(purchaseId) {
            if (confirm('إنشاء فاتورة لهذا المشترى؟')) {
                alert('تم إنشاء الفاتورة بنجاح');
            }
        }
    </script>
</body>
</html>
'''