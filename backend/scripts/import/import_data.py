#!/usr/bin/env python3

import sys
import csv
import os
import pymysql
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

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

DATA_PATH = Path(__file__).parent.parent.parent.parent / 'data_pipeline' / 'data'

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def create_import_log(conn, import_type, file_name):
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO import_logs (import_type, file_name, status) VALUES (%s, %s, 'running')",
            (import_type, file_name)
        )
        conn.commit()
        return cursor.lastrowid

def update_import_log(conn, log_id, total, success, reject, status='completed', error=None):
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE import_logs 
            SET total_lines = %s, success_count = %s, reject_count = %s, 
                status = %s, error_summary = %s, finished_at = NOW()
            WHERE id = %s
        """, (total, success, reject, status, error, log_id))
        conn.commit()

def import_operadoras(conn):
    file_path = DATA_PATH / 'operadoras' / 'operadoras_de_plano_de_saude_ativas.csv'
    
    if not file_path.exists():
        print(f"Arquivo não encontrado: {file_path}")
        return
    
    log_id = create_import_log(conn, 'operadoras', file_path.name)
    total, success, reject = 0, 0, 0
    
    print(f"Importando operadoras de {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        with conn.cursor() as cursor:
            for row in reader:
                total += 1
                
                try:
                    cursor.callproc('sp_import_operadora', (
                        row.get('REGISTRO_OPERADORA'),
                        row.get('CNPJ'),
                        row.get('Razao_Social'),
                        row.get('Modalidade'),
                        row.get('UF'),
                        log_id,
                        0,
                        False
                    ))
                    success += 1
                    
                    if total % 1000 == 0:
                        conn.commit()
                        print(f"Processados: {total} | Sucesso: {success} | Rejeições: {reject}")
                
                except Exception as e:
                    reject += 1
                    print(f"Erro linha {total}: {e}")
            
            conn.commit()
    
    update_import_log(conn, log_id, total, success, reject)
    print(f"Importação concluída: {success}/{total} registros importados")

def import_despesas(conn):
    file_path = DATA_PATH / 'trimestrais_contabeis' / 'consolidado_despesas_agrupado.csv'
    
    if not file_path.exists():
        print(f"Arquivo não encontrado: {file_path}")
        return
    
    log_id = create_import_log(conn, 'despesas', file_path.name)
    total, success, reject = 0, 0, 0
    
    print(f"Importando despesas de {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        with conn.cursor() as cursor:
            for row in reader:
                total += 1
                
                try:
                    cursor.callproc('sp_import_despesa', (
                        row.get('RazaoSocial'),
                        row.get('UF'),
                        row.get('Trimestre'),
                        row.get('Ano'),
                        row.get('CNPJ'),
                        row.get('RegistroANS'),
                        row.get('Modalidade'),
                        row.get('ValorDespesas'),
                        row.get('CNPJConflict', 'False'),
                        row.get('RazaoSocialAusente', 'False'),
                        row.get('CadastroIncompleto', 'False'),
                        row.get('CNPJInvalido', 'False'),
                        False
                    ))
                    success += 1
                    
                    if total % 5000 == 0:
                        conn.commit()
                        print(f"Processados: {total} | Sucesso: {success} | Rejeições: {reject}")
                
                except Exception as e:
                    reject += 1
                    print(f"Erro linha {total}: {e}")
            
            conn.commit()
    
    update_import_log(conn, log_id, total, success, reject)
    print(f"Importação concluída: {success}/{total} registros importados")

def import_metricas(conn):
    file_path = DATA_PATH / 'trimestrais_contabeis' / 'metrics' / 'metricas_operadoras.csv'
    
    if not file_path.exists():
        print(f"Arquivo não encontrado: {file_path}")
        return
    
    log_id = create_import_log(conn, 'metricas', file_path.name)
    total, success, reject = 0, 0, 0
    
    print(f"Importando métricas de {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        with conn.cursor() as cursor:
            for row in reader:
                total += 1
                
                try:
                    cursor.callproc('sp_import_metrica', (
                        row.get('Ranking'),
                        row.get('RazaoSocial'),
                        row.get('UF'),
                        row.get('TotalDespesas'),
                        row.get('MediaTrimestral'),
                        row.get('DesvioPadrao'),
                        row.get('CoeficienteVariacao'),
                        row.get('AltaVariabilidade', 'False'),
                        row.get('QuantidadeTrimestres'),
                        row.get('CNPJConflict', 'False'),
                        row.get('RazaoSocialAusente', 'False'),
                        row.get('CadastroIncompleto', 'False'),
                        row.get('RegistroANS'),
                        row.get('Modalidade'),
                        row.get('CNPJ'),
                        False
                    ))
                    success += 1
                    
                    if total % 1000 == 0:
                        conn.commit()
                        print(f"Processados: {total} | Sucesso: {success} | Rejeições: {reject}")
                
                except Exception as e:
                    reject += 1
                    print(f"Erro linha {total}: {e}")
            
            conn.commit()
    
    update_import_log(conn, log_id, total, success, reject)
    print(f"Importação concluída: {success}/{total} registros importados")

def main():
    try:
        conn = get_connection()
        print("Conectado ao MySQL")
        
        import_operadoras(conn)
        import_despesas(conn)
        import_metricas(conn)
        
        print("\n✓ Importação completa!")
        
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    main()
