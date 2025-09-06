#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

# حذف قاعدة البيانات القديمة
db_file = 'asset_management.db'
if os.path.exists(db_file):
    os.remove(db_file)
    print("✅ تم حذف قاعدة البيانات القديمة")

print("🔄 سيتم إنشاء قاعدة بيانات جديدة عند تشغيل النظام...")