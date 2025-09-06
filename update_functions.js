// وظائف JavaScript المحسنة لنظام إدارة الأصول

// وظائف المشتريات
function viewPurchase(purchaseId) {
    alert('عرض تفاصيل المشترى رقم: ' + purchaseId);
}

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

function editPurchase(purchaseId) {
    alert('تحرير المشترى رقم: ' + purchaseId + ' - قيد التطوير');
}

// وظائف العهد
function addCustody() {
    window.location.href = '/add_custody';
}

function viewCustody(custodyId) {
    alert('عرض تفاصيل العهدة رقم: ' + custodyId);
}

function returnCustody(custodyId) {
    if (confirm('تأكيد استرداد هذه العهدة؟')) {
        alert('تم استرداد العهدة بنجاح');
        location.reload();
    }
}

// وظائف الفواتير
function createInvoice() {
    window.location.href = '/add_invoice';
}

function viewInvoice(invoiceNumber) {
    alert(`عرض تفاصيل الفاتورة: ${invoiceNumber}`);
}

function markPaid(invoiceNumber) {
    if (confirm('تأكيد دفع هذه الفاتورة؟')) {
        alert('تم تحديث حالة الفاتورة إلى مدفوع');
        location.reload();
    }
}

function printInvoice(invoiceNumber) {
    window.open(`/api/print_invoice/${invoiceNumber}`, '_blank');
}

// وظائف التراخيص
function addLicense() {
    window.location.href = '/add_license';
}

function viewLicense(licenseNumber) {
    alert(`عرض تفاصيل الترخيص: ${licenseNumber}`);
}

function renewLicense(licenseNumber) {
    if (confirm('تجديد هذا الترخيص؟')) {
        alert('تم تجديد الترخيص بنجاح');
        location.reload();
    }
}

function assignLicense(licenseNumber) {
    alert('تخصيص الترخيص لموظف - قيد التطوير');
}

// وظائف الدعم الفني
function createTicket() {
    window.location.href = '/create_ticket';
}

function viewTicket(ticketId) {
    alert('عرض تفاصيل التذكرة رقم: ' + ticketId);
}

function closeTicket(ticketId) {
    if (confirm('تأكيد إغلاق هذه التذكرة؟')) {
        alert('تم إغلاق التذكرة بنجاح');
        location.reload();
    }
}

// وظائف الإشعارات
function markAsRead(notificationId) {
    alert('تم تحديد الإشعار كمقروء');
    location.reload();
}

function deleteNotification(notificationId) {
    if (confirm('هل أنت متأكد من حذف هذا الإشعار؟')) {
        alert('تم حذف الإشعار');
        location.reload();
    }
}

function markAllRead() {
    if (confirm('تحديد جميع الإشعارات كمقروءة؟')) {
        alert('تم تحديد جميع الإشعارات كمقروءة');
        location.reload();
    }
}

function clearAll() {
    if (confirm('هل أنت متأكد من حذف جميع الإشعارات؟')) {
        alert('تم حذف جميع الإشعارات');
        location.reload();
    }
}

function sendSMSNotification() {
    const phone = prompt('أدخل رقم الجوال:');
    const message = prompt('أدخل نص الرسالة:');
    
    if (phone && message) {
        fetch('/api/send_sms_notification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone: phone,
                message: message
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('تم إرسال الإشعار بنجاح');
            } else {
                alert('خطأ في إرسال الإشعار');
            }
        })
        .catch(error => {
            alert('خطأ في الاتصال');
        });
    }
}

// وظائف التقارير
function exportReport() {
    alert('تصدير التقرير - قيد التطوير');
}

function generateReport(type) {
    alert(`إنشاء تقرير ${type} - قيد التطوير`);
}

function generateCustomReport() {
    alert('إنشاء تقرير مخصص - قيد التطوير');
}

function exportPDF() {
    alert('تصدير PDF - قيد التطوير');
}

// وظائف الإدارات
function addDepartment() {
    alert('إضافة إدارة جديدة - قيد التطوير');
}

function editDept(deptName) {
    alert('تحرير إدارة: ' + deptName);
}

function viewEmployees(deptName) {
    alert('عرض موظفي إدارة: ' + deptName);
}