"""
Módulo de agregações especializadas.

Funções otimizadas para agregação de dados financeiros.
"""

import pandas as pd
import logging


def load_and_prepare_data(file_path, required_columns=None):
    # Carrega dados do CSV e prepara para análise.

    # Preservar CNPJ e RegistroANS como strings
    dtype_dict = {'CNPJ': str, 'RegistroANS': str}
    df = pd.read_csv(file_path, dtype=dtype_dict)
    
    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Colunas faltando: {missing}")
    
    # Converter ValorDespesas para numérico se for string
    if df['ValorDespesas'].dtype == 'object':
        df['ValorDespesas'] = pd.to_numeric(df['ValorDespesas'], errors='coerce')
    
    # Remover valores inválidos
    initial_count = len(df)
    df = df[df['ValorDespesas'].notna()]
    removed = initial_count - len(df)
    
    if removed > 0:
        logging.warning(f"{removed} registros removidos (ValorDespesas inválido)")
    
    logging.info(f"Dados carregados: {len(df)} registros")
    
    return df


def aggregate_by_operadora(df):
    # Agrega dados consolidando todos trimestres por operadora/UF.

    aggregated = df.groupby(['RazaoSocial', 'UF'], dropna=False).agg({
        'ValorDespesas': 'sum',
        'RegistroANS': 'first',
        'Modalidade': 'first',
        'CNPJ': 'first',
        'Trimestre': 'count'  # Contar trimestres
    }).reset_index()
    
    aggregated.rename(columns={'Trimestre': 'NumeroTrimestres'}, inplace=True)
    
    return aggregated


def filter_by_flags(df, filter_dict):
    # Filtra DataFrame baseado em flags booleanas.
    
    mask = pd.Series([True] * len(df))
    
    for column, value in filter_dict.items():
        if column in df.columns:
            mask &= (df[column] == value)
    
    return df[mask]


def create_pivot_table(df, values='ValorDespesas', index='RazaoSocial', 
                       columns='Trimestre', aggfunc='sum'):
   
    # Cria tabela pivot para análise cruzada.

    pivot = pd.pivot_table(
        df,
        values=values,
        index=index,
        columns=columns,
        aggfunc=aggfunc,
        fill_value=0
    )
    
    return pivot


def merge_with_flags(df_metrics, df_source, flags_to_merge):
   
    #Faz merge de métricas com flags do arquivo original.

    # Agregar flags por operadora (usar max para booleanos)
    flag_agg = {}
    for flag in flags_to_merge:
        if flag in df_source.columns:
            flag_agg[flag] = 'max'
    
    if not flag_agg:
        return df_metrics
    
    flags_df = df_source.groupby(['RazaoSocial', 'UF'], dropna=False).agg(flag_agg).reset_index()
    
    # Merge com métricas
    result = df_metrics.merge(
        flags_df,
        on=['RazaoSocial', 'UF'],
        how='left'
    )
    
    # Preencher flags ausentes com False
    for flag in flags_to_merge:
        if flag in result.columns:
            result[flag] = result[flag].fillna(False)
    
    return result
