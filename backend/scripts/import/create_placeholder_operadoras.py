#!/usr/bin/env python3
"""
Script para criar operadoras placeholder no banco.
Insere operadoras órfãs (que existem em despesas mas não em operadoras).
Compatível com TiDB Cloud (SSL).
"""
import pymysql
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent.parent / '.env')

# Configuração SSL para TiDB/PlanetScale
ssl_config = None
if os.getenv('MYSQL_SSL', 'false').lower() in ('true', '1', 'yes'):
    ssl_config = {'ssl': {'ssl_mode': 'VERIFY_IDENTITY'}}

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'healthcare_saas'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    **(ssl_config or {})
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def main():
    conn = get_connection()
    print(f"Conectando a {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
    
    with conn.cursor() as cursor:
        # 1. Buscar operadoras órfãs (despesas sem operadora linkada)
        cursor.execute("""
            SELECT DISTINCT registro_ans, razao_social, uf, modalidade
            FROM despesas_trimestrais
            WHERE operadora_id IS NULL AND registro_ans IS NOT NULL AND TRIM(registro_ans) != ''
        """)
        rows = cursor.fetchall()
        print(f"Encontradas {len(rows)} operadoras órfãs para inserir...")
        
        # 2. Inserir operadoras placeholder
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
        print(f"✓ Inseridas {count} operadoras placeholder.")
        
        # 3. Atualizar despesas para linkar operadora_id
        cursor.execute("""
            UPDATE despesas_trimestrais d
            INNER JOIN operadoras o ON d.registro_ans = o.registro_ans
            SET d.operadora_id = o.id
            WHERE d.operadora_id IS NULL
        """)
        updated = cursor.rowcount
        conn.commit()
        print(f"✓ Atualizadas {updated} despesas com operadora_id linkado.")
        
        # 4. Atualizar metricas também
        cursor.execute("""
            UPDATE metricas_operadoras m
            INNER JOIN operadoras o ON m.registro_ans = o.registro_ans
            SET m.operadora_id = o.id
            WHERE m.operadora_id IS NULL
        """)
        updated_metricas = cursor.rowcount
        conn.commit()
        print(f"✓ Atualizadas {updated_metricas} métricas com operadora_id linkado.")
        
    conn.close()
    print("\n✓ Processo concluído!")

if __name__ == "__main__":
    main()
