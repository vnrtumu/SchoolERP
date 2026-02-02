"""Script to create master registry database"""
import pymysql
from app.config import settings

# Extract credentials from master DB URL
# Format: mysql+aiomysql://root:Sandyvenky%4041@localhost:3306/master_registry
import re
from urllib.parse import unquote

url = settings.MASTER_DATABASE_URL
match = re.match(r'mysql\+aiomysql://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)', url)

if not match:
    print("Error: Invalid database URL format")
    exit(1)

user, password, host, port, db_name = match.groups()
password = unquote(password)  # URL decode
port = int(port)

try:
    # Connect without specifying database
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ Master registry database '{db_name}' created successfully!")
    
    connection.commit()
    connection.close()
    
except Exception as e:
    print(f"✗ Error creating master database: {e}")
    exit(1)
