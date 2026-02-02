#!/usr/bin/env python3
"""
Script de importação de dados para MySQL/TiDB.
Usa INSERTs diretos para compatibilidade com TiDB Cloud.
"""

import sys
import csv
import os
import ssl
import pymysql
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / '.env', override=False)

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


def str_to_bool(value):
    """Converte string para boolean."""
    if value is None:
        return False
    return str(value).lower() in ('true', '1', 'yes')


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
                registro_ans = row.get('REGISTRO_OPERADORA')
                
                if not registro_ans:
                    reject += 1
                    continue
                
                try:
                    # Verificar se já existe
                    cursor.execute(
                        "SELECT id FROM operadoras WHERE registro_ans = %s LIMIT 1",
                        (registro_ans,)
                    )
                    existing = cursor.fetchone()
                    
                    if existing is None:
                        cursor.execute("""
                            INSERT INTO operadoras (registro_ans, cnpj, razao_social, modalidade, uf)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            registro_ans,
                            row.get('CNPJ'),
                            row.get('Razao_Social'),
                            row.get('Modalidade'),
                            row.get('UF')
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
    
    # Criar lookup de operadoras
    operadora_ids = {}
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, registro_ans FROM operadoras")
        for row in cursor.fetchall():
            operadora_ids[row['registro_ans']] = row['id']
    
    print(f"Importando despesas de {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        with conn.cursor() as cursor:
            for row in reader:
                total += 1
                
                try:
                    registro_ans = row.get('RegistroANS')
                    operadora_id = operadora_ids.get(registro_ans)
                    
                    # Converter valor
                    valor = row.get('ValorDespesas', '0')
                    try:
                        valor_decimal = float(valor) if valor else 0.0
                    except ValueError:
                        valor_decimal = 0.0
                    
                    cursor.execute("""
                        INSERT INTO despesas_trimestrais (
                            operadora_id, registro_ans, cnpj, razao_social, uf, modalidade,
                            ano, trimestre, valor_despesas,
                            cadastro_incompleto, cnpj_conflict, cnpj_invalido, razao_social_ausente
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        operadora_id,
                        registro_ans,
                        row.get('CNPJ'),
                        row.get('RazaoSocial'),
                        row.get('UF'),
                        row.get('Modalidade'),
                        int(row.get('Ano', 0)),
                        int(row.get('Trimestre', 0)),
                        valor_decimal,
                        str_to_bool(row.get('CadastroIncompleto')),
                        str_to_bool(row.get('CNPJConflict')),
                        str_to_bool(row.get('CNPJInvalido')),
                        str_to_bool(row.get('RazaoSocialAusente'))
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
        print(f"Arquivo de métricas não encontrado (opcional): {file_path}")
        return
    
    log_id = create_import_log(conn, 'metricas', file_path.name)
    total, success, reject = 0, 0, 0
    
    # Criar lookup de operadoras
    operadora_ids = {}
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, registro_ans FROM operadoras")
        for row in cursor.fetchall():
            operadora_ids[row['registro_ans']] = row['id']
    
    print(f"Importando métricas de {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        with conn.cursor() as cursor:
            for row in reader:
                total += 1
                
                try:
                    registro_ans = row.get('RegistroANS')
                    operadora_id = operadora_ids.get(registro_ans)
                    
                    cursor.execute("""
                        INSERT INTO metricas_operadoras (
                            operadora_id, registro_ans, cnpj, razao_social, uf, modalidade,
                            ranking, total_despesas, media_trimestral, desvio_padrao,
                            coeficiente_variacao, alta_variabilidade, quantidade_trimestres,
                            cadastro_incompleto, cnpj_conflict, razao_social_ausente
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        operadora_id,
                        registro_ans,
                        row.get('CNPJ'),
                        row.get('RazaoSocial'),
                        row.get('UF'),
                        row.get('Modalidade'),
                        int(row.get('Ranking', 0)) if row.get('Ranking') else None,
                        float(row.get('TotalDespesas', 0) or 0),
                        float(row.get('MediaTrimestral', 0) or 0),
                        float(row.get('DesvioPadrao', 0) or 0),
                        float(row.get('CoeficienteVariacao', 0) or 0),
                        str_to_bool(row.get('AltaVariabilidade')),
                        int(row.get('QuantidadeTrimestres', 0) or 0),
                        str_to_bool(row.get('CadastroIncompleto')),
                        str_to_bool(row.get('CNPJConflict')),
                        str_to_bool(row.get('RazaoSocialAusente'))
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
        print(f"Conectando a {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
        conn = get_connection()
        print("✓ Conectado ao banco de dados")
        
        import_operadoras(conn)
        import_despesas(conn)
        import_metricas(conn)
        
        print("\n✓ Importação completa!")
        
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn:
            conn.close()


if __name__ == '__main__':
    main()
