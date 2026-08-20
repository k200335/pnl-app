import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

# DB 연결 문자열 생성
connection_string = (
    f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
    f"SERVER={os.getenv('DB_HOST')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    print("✅ Cafe24 MS SQL DB 연결 성공!")
    
    # DB 내의 테이블 목록 가져오기 테스트
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    tables = cursor.fetchall()
    
    print("\n[현재 DB 내 주요 테이블 목록]")
    for table in tables[:10]: # 상위 10개만 출력
        print(f"- {table[0]}")
        
    conn.close()

except Exception as e:
    print("❌ DB 연결 실패:", e)