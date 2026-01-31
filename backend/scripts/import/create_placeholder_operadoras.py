#!/usr/bin/env python3
import pymysql
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent.parent / '.env')

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'healthcare_saas'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def main():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT registro_ans, razao_social, uf, modalidade
            FROM despesas_trimestrais
            WHERE operadora_id IS NULL AND registro_ans IS NOT NULL AND TRIM(registro_ans) != ''
        """)
        rows = cursor.fetchall()
        print(f"Encontradas {len(rows)} operadoras órfãs para inserir...")
        count = 0
        for row in rows:
            cursor.execute("""
                INSERT IGNORE INTO operadoras (registro_ans, razao_social, uf, modalidade, cnpj)
                VALUES (%s, %s, %s, %s, NULL)
            """, (
                row['registro_ans'],
                row['razao_social'] or f"Operadora {row['registro_ans']}",
                row['uf'],
                row['modalidade']
            ))
            count += cursor.rowcount
        conn.commit()
        print(f"Inseridas {count} operadoras placeholder.")
    conn.close()

if __name__ == "__main__":
    main()
