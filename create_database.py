"""Script to create the database if it doesn't exist"""
import pymysql
from urllib.parse import quote_plus

# Database credentials
host = "localhost"
user = "root"
password = "Sandyvenky@41"
database = "mindwhile_erp"

try:
    # Connect to MySQL server (without database)
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    with connection.cursor() as cursor:
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ Database '{database}' created successfully!")
    
    connection.commit()
    connection.close()
    
except Exception as e:
    print(f"✗ Error creating database: {e}")
    exit(1)
