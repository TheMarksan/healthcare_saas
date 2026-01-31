"""
Script de análise e geração de métricas.

Processa dados agrupados e gera relatórios com estatísticas
sobre despesas de operadoras de saúde.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

from utils.metrics import (
    calculate_operadora_metrics,
    add_ranking,
    calculate_uf_summary,
    get_top_n_operadoras,
    calculate_quartiles
)
from utils.aggregators import (
    load_and_prepare_data,
    merge_with_flags
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def generate_metrics_report(input_path, output_metrics_path, output_report_path, cv_threshold=0.5, top_n=10):
   
    # Gera relatório completo de métricas.

    logging.info(f"Iniciando análise de métricas...")
    logging.info(f"Arquivo de entrada: {input_path}")
    
    df = load_and_prepare_data(
        input_path,
        required_columns=['RazaoSocial', 'UF', 'ValorDespesas']
    )
    
    logging.info("Calculando métricas por operadora/UF...")
    metrics_df = calculate_operadora_metrics(df, cv_threshold=cv_threshold)
    
    # Adicionar ranking
    metrics_df = add_ranking(metrics_df, rank_column='TotalDespesas')
    
    # Merge com flags originais
    flags_to_include = ['CNPJConflict', 'RazaoSocialAusente', 'CadastroIncompleto']
    metrics_df = merge_with_flags(metrics_df, df, flags_to_include)
    
    # Adicionar informações adicionais do dataset original
    info_cols = ['RegistroANS', 'Modalidade', 'CNPJ']
    available_info = [col for col in info_cols if col in df.columns]
    
    if available_info:
        info_df = df.groupby(['RazaoSocial', 'UF'], dropna=False)[available_info].first().reset_index()
        metrics_df = metrics_df.merge(info_df, on=['RazaoSocial', 'UF'], how='left')
    
    cols_order = ['Ranking', 'RazaoSocial', 'UF', 'TotalDespesas', 'MediaTrimestral', 
                  'DesvioPadrao', 'CoeficienteVariacao', 'AltaVariabilidade', 
                  'QuantidadeTrimestres']
    
    # Adicionar colunas adicionais que existem
    additional_cols = [col for col in metrics_df.columns if col not in cols_order]
    final_cols = cols_order + additional_cols
    final_cols = [col for col in final_cols if col in metrics_df.columns]
    
    metrics_df = metrics_df[final_cols]
    
    # Preservar CNPJ e RegistroANS como strings
    if 'CNPJ' in metrics_df.columns:
        metrics_df['CNPJ'] = metrics_df['CNPJ'].astype(str)
    if 'RegistroANS' in metrics_df.columns:
        metrics_df['RegistroANS'] = metrics_df['RegistroANS'].astype(str)
    
    metrics_df.to_csv(output_metrics_path, index=False)
    logging.info(f"Métricas salvas: {output_metrics_path} ({len(metrics_df)} registros)")
    
    # Gerar relatório JSON
    logging.info("Gerando relatório agregado...")
    report = generate_json_report(metrics_df, df, top_n)
    
    # Salvar JSON
    output_report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logging.info(f"Relatório JSON salvo: {output_report_path}")
    
    uf_summary = calculate_uf_summary(metrics_df)
    logging.info(f"\nResumo por UF:")
    logging.info(f"  UFs com dados: {len(uf_summary)}")
    logging.info(f"  Top 3 UFs por despesas:")
    for idx, row in uf_summary.head(3).iterrows():
        uf_name = row['UF'] if pd.notna(row['UF']) else 'Sem UF'
        logging.info(f"    {uf_name}: R$ {row['TotalDespesasUF']:,.2f} ({row['QuantidadeOperadoras']} operadoras)")
    
    return metrics_df, report


def generate_json_report(metrics_df, source_df, top_n=10):

    # Gera relatório JSON com estatísticas agregadas.
    
    # Top N operadoras
    top_operadoras = get_top_n_operadoras(metrics_df, n=top_n)
    top_list = []
    for idx, row in top_operadoras.iterrows():
        top_list.append({
            'razao_social': row['RazaoSocial'],
            'uf': row['UF'] if pd.notna(row['UF']) else None,
            'total_despesas': float(row['TotalDespesas']),
            'media_trimestral': float(row['MediaTrimestral']),
            'coeficiente_variacao': float(row['CoeficienteVariacao']),
            'alta_variabilidade': bool(row['AltaVariabilidade'])
        })
    
    # Estatísticas por UF
    uf_stats = {}
    for uf in metrics_df['UF'].dropna().unique():
        uf_data = metrics_df[metrics_df['UF'] == uf]
        uf_stats[uf] = {
            'quantidade_operadoras': int(len(uf_data)),
            'total_despesas': float(uf_data['TotalDespesas'].sum()),
            'media_despesas': float(uf_data['TotalDespesas'].mean()),
            'operadoras_alta_variabilidade': int(uf_data['AltaVariabilidade'].sum())
        }
    
    # Estatísticas gerais
    quartiles = calculate_quartiles(metrics_df, 'TotalDespesas')
    
    report = {
        'metadata': {
            'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'arquivo_fonte': str(source_df),
            'total_registros_fonte': len(source_df)
        },
        'resumo_geral': {
            'total_operadoras': int(len(metrics_df)),
            'total_despesas_geral': float(metrics_df['TotalDespesas'].sum()),
            'media_despesas_operadora': float(metrics_df['TotalDespesas'].mean()),
            'operadoras_alta_variabilidade': int(metrics_df['AltaVariabilidade'].sum()),
            'percentual_alta_variabilidade': float(
                (metrics_df['AltaVariabilidade'].sum() / len(metrics_df)) * 100
            )
        },
        'estatisticas_distribuicao': quartiles,
        f'top_{top_n}_operadoras': top_list,
        'metricas_por_uf': uf_stats
    }
    
    return report


if __name__ == "__main__":
    input_path = Path("data/trimestrais_contabeis/consolidado_despesas_agrupado.csv")
    output_metrics_path = Path("data/trimestrais_contabeis/metrics/despesas_agregadas.csv")
    output_report_path = Path("data/trimestrais_contabeis/reports/relatorio_agregacao.json")
    
    # Se o caminho não existir, criar diretórios
    if not output_metrics_path.parent.exists(): 
        output_metrics_path.parent.mkdir(parents=True, exist_ok=True)
    if not output_report_path.parent.exists():
        output_report_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Validar entrada
    if not input_path.exists():
        logging.error(f"Arquivo não encontrado: {input_path}")
        logging.error("Execute primeiro o script enrich.py para gerar os dados agrupados")
        sys.exit(1)
    
    try:
        # Gerar métricas e relatório
        metrics_df, report = generate_metrics_report(
            input_path=input_path,
            output_metrics_path=output_metrics_path,
            output_report_path=output_report_path,
            cv_threshold=0.5,
            top_n=10
        )
        
        print("\n" + "="*70)
        print("RESUMO DA ANÁLISE")
        print("="*70)
        print(f"Total de operadoras analisadas: {len(metrics_df)}")
        print(f"Despesas totais: R$ {metrics_df['TotalDespesas'].sum():,.2f}")
        print(f"Operadoras com alta variabilidade: {metrics_df['AltaVariabilidade'].sum()}")
        print(f"\nTop 3 Operadoras por Despesas:")
        for idx, row in metrics_df.head(3).iterrows():
            print(f"  {row['Ranking']}. {row['RazaoSocial']} ({row['UF']})")
            print(f"     Total: R$ {row['TotalDespesas']:,.2f}")
        print("="*70)
        
    except Exception as e:
        logging.error(f"Erro ao gerar análise: {e}")
        raise
