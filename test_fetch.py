import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

connection_string = (
    f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
    f"SERVER={os.getenv('DB_HOST')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
)

try:
    conn = pyodbc.connect(connection_string)
    
    # 최근 거래 내역 10건 조회
    query = """
    SELECT TOP 10 
        day, 
        maingroup, 
        subgroup, 
        [where], 
        abstract01, 
        deposit, 
        withdrawal
    FROM dbo.AccountBook
    ORDER BY day DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print("✅ 데이터 조회 성공!\n")
    print(df.to_string(index=False))

except Exception as e:
    print("❌ 데이터 조회 실패:", e)