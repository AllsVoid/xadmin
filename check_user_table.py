#!/usr/bin/env python
"""检查 sys_user 表的列结构"""
import django
import os
import sys

# Setup Django
sys.path.insert(0, '/home/zx/xadmin_zx')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadmin.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_name = 'sys_user' 
    ORDER BY ordinal_position;
""")

print('\nColumns in sys_user table:')
print('-' * 100)
print(f"{'Column Name':30s} | {'Data Type':20s} | {'Nullable':10s} | {'Default':20s}")
print('-' * 100)

for row in cursor.fetchall():
    col_name, data_type, is_nullable, col_default = row
    default_str = str(col_default)[:20] if col_default else ''
    print(f'{col_name:30s} | {data_type:20s} | {is_nullable:10s} | {default_str:20s}')

print('-' * 100)

