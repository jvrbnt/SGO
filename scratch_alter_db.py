import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE services ADD COLUMN IF NOT EXISTS original_hours FLOAT DEFAULT 0.0")
    print("Column original_hours added successfully.")
except Exception as e:
    print(f"Error: {e}")
