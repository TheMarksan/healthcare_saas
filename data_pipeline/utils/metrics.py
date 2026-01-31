"""
Módulo de cálculo de métricas financeiras.

Funções puras para calcular estatísticas sobre despesas de operadoras.
"""

import pandas as pd
import logging


def calculate_operadora_metrics(df, cv_threshold=0.5):
    # Calcula métricas agregadas por operadora e UF.
    
    # Agrupar e calcular todas métricas em uma operação
    metrics = df.groupby(['RazaoSocial', 'UF'], dropna=False).agg({
        'ValorDespesas': ['sum', 'mean', 'std', 'count']
    }).reset_index()
    
    # Achatar colunas multi-índice
    metrics.columns = ['RazaoSocial', 'UF', 'TotalDespesas', 'MediaTrimestral', 
                       'DesvioPadrao', 'QuantidadeTrimestres']
    
    # Calcular coeficiente de variação (evitar divisão por zero)
    metrics['CoeficienteVariacao'] = metrics.apply(
        lambda row: row['DesvioPadrao'] / row['MediaTrimestral'] 
        if row['MediaTrimestral'] > 0 else 0,
        axis=1
    )
    
    # Marcar alta variabilidade
    metrics['AltaVariabilidade'] = metrics['CoeficienteVariacao'] > cv_threshold
    
    # Preencher NaN no desvio padrão (quando há apenas 1 trimestre)
    metrics['DesvioPadrao'] = metrics['DesvioPadrao'].fillna(0)
    metrics['CoeficienteVariacao'] = metrics['CoeficienteVariacao'].fillna(0)
    
    logging.info(f"Métricas calculadas para {len(metrics)} operadoras/UF")
    logging.info(f"Operadoras com alta variabilidade: {metrics['AltaVariabilidade'].sum()}")
    
    return metrics


def add_ranking(df, rank_column='TotalDespesas', rank_name='Ranking'):

    # Adiciona coluna de ranking baseada em uma métrica.

    df = df.copy()
    df = df.sort_values(rank_column, ascending=False)
    df[rank_name] = range(1, len(df) + 1)
    
    return df


def calculate_uf_summary(df):
    #Calcula estatísticas agregadas por UF.

    uf_summary = df.groupby('UF', dropna=False).agg({
        'TotalDespesas': 'sum',
        'RazaoSocial': 'count',
        'AltaVariabilidade': 'sum'
    }).reset_index()
    
    uf_summary.columns = ['UF', 'TotalDespesasUF', 'QuantidadeOperadoras', 
                          'OperadorasAltaVariabilidade']
    
    uf_summary = uf_summary.sort_values('TotalDespesasUF', ascending=False)
    
    return uf_summary


def get_top_n_operadoras(df, n=10, metric='TotalDespesas'):
    # Retorna as top N operadoras por uma métrica específica.
    return df.nlargest(n, metric)[['RazaoSocial', 'UF', metric, 'MediaTrimestral', 
                                     'CoeficienteVariacao', 'AltaVariabilidade']]


def calculate_quartiles(df, column='TotalDespesas'):
    # Calcula quartis de uma métrica para análise de distribuição.

    stats = {
        'min': float(df[column].min()),
        'q1': float(df[column].quantile(0.25)),
        'median': float(df[column].median()),
        'q3': float(df[column].quantile(0.75)),
        'max': float(df[column].max()),
        'mean': float(df[column].mean()),
        'std': float(df[column].std())
    }
    
    return stats
