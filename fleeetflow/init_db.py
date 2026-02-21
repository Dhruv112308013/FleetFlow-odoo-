import pymysql
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

db_url = os.getenv('DATABASE_URL')
url = urlparse(db_url)

# Extract connection info
host = url.hostname or 'localhost'
user = url.username or 'root'
password = url.password or 'password'
port = url.port or 3306

try:
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port
    )
    with connection.cursor() as cursor:
        print(f"Creating database 'fleetflow' if not exists...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS fleetflow;")
    connection.commit()
    connection.close()
    print("Database ready.")
except Exception as e:
    print(f"Error creating database: {e}")
    exit(1)
