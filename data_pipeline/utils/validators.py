"""
Módulo de validação e normalização de dados.

Contém funções para validar e normalizar dados do pipeline,
incluindo validação de trimestres e detecção de conflitos de CNPJ.
"""

import re
import logging
import pandas as pd


def normalize_trimestre(trimestre_str):
    if pd.isna(trimestre_str):
        return None
    
    trimestre_str = str(trimestre_str).strip()
    
    # Formato composto: 1T2024, 2T2024, etc.
    match = re.match(r'^(\d{1,2})T(\d{4})$', trimestre_str)
    if match:
        trimestre = int(match.group(1))
        if trimestre < 1 or trimestre > 4:
            logging.warning(f"Trimestre fora do range válido (1-4): {trimestre_str}")
            return None
        return trimestre
    
    # Formato simples: 1, 2, 3, 4, 01, 02, 03, 04
    if trimestre_str.isdigit():
        trimestre = int(trimestre_str)
        if trimestre < 1 or trimestre > 4:
            logging.warning(f"Trimestre fora do range válido (1-4): {trimestre_str}")
            return None
        return trimestre
    
    logging.warning(f"Formato de trimestre inválido: {trimestre_str}")
    return None


def detect_cnpj_conflicts(df, operadoras_df):
    # Criar lookup do cadastro oficial
    cadastro_lookup = operadoras_df.set_index('CNPJ')['Razao_Social'].to_dict()
    
    # Identificar CNPJs com múltiplas razões sociais
    cnpj_razoes = df.groupby('CNPJ')['RazaoSocial'].unique()
    cnpjs_conflito = cnpj_razoes[cnpj_razoes.apply(len) > 1]
    
    conflitos = []
    df_copy = df.copy()
    df_copy['CNPJConflict'] = False
    
    for cnpj, razoes in cnpjs_conflito.items():
        razoes_list = razoes.tolist()
        conflitos.append({'CNPJ': cnpj, 'RazoesEncontradas': razoes_list})
        
        # Marcar registros com conflito
        mask = df_copy['CNPJ'] == cnpj
        df_copy.loc[mask, 'CNPJConflict'] = True
        
        # Resolver conflito: priorizar cadastro oficial
        if cnpj in cadastro_lookup:
            razao_oficial = cadastro_lookup[cnpj]
            df_copy.loc[mask, 'RazaoSocial'] = razao_oficial
            logging.info(f"CNPJ {cnpj}: usando razão do cadastro oficial")
        else:
            # Usar razão mais recente (maior ano/trimestre)
            registros_cnpj = df_copy[mask].copy()
            registros_cnpj['Ano'] = pd.to_numeric(registros_cnpj['Ano'], errors='coerce')
            registros_cnpj['Trimestre'] = pd.to_numeric(registros_cnpj['Trimestre'], errors='coerce')
            
            idx_max = registros_cnpj[['Ano', 'Trimestre']].idxmax()[0]
            razao_recente = registros_cnpj.loc[idx_max, 'RazaoSocial']
            df_copy.loc[mask, 'RazaoSocial'] = razao_recente
            logging.info(f"CNPJ {cnpj}: usando razão mais recente")
    
    return df_copy, conflitos


def save_equality_issues(conflitos, output_path):
    if not conflitos:
        logging.info("Nenhum conflito de CNPJ detectado")
        return
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Expandir lista de razões em string
    for item in conflitos:
        item['RazoesEncontradas'] = ' | '.join(item['RazoesEncontradas'])
    
    df_conflitos = pd.DataFrame(conflitos)
    df_conflitos.to_csv(output_path, index=False)
    logging.info(f"Arquivo de conflitos salvo: {output_path} ({len(conflitos)} CNPJs)")


def validate_dataframe_schema(df, required_columns):
    # Valida se DataFrame contém todas as colunas obrigatórias.
    
    missing = set(required_columns) - set(df.columns)
    
    if missing:
        logging.error(f"Colunas obrigatórias faltando: {missing}")
        return False, list(missing)
    
    return True, []


def handle_missing_razao_social(df, registro_ans_col='RegistroANS'):
    # Trata registros com razão social vazia.
    
    df = df.copy()
    
    # Identificar registros sem razão social
    mask_vazio = df['RazaoSocial'].isna() | (df['RazaoSocial'].str.strip() == '')
    
    # Adicionar flag
    df['RazaoSocialAusente'] = mask_vazio
    
    # Aplicar fallback para registros vazios
    df.loc[mask_vazio, 'RazaoSocial'] = df.loc[mask_vazio, registro_ans_col].apply(
        lambda x: f"OPERADORA [{x}]" if pd.notna(x) else "OPERADORA [SEM_REG_ANS]"
    )
    
    count_ausentes = mask_vazio.sum()
    if count_ausentes > 0:
        logging.warning(f"{count_ausentes} registros sem razão social - aplicado fallback")
    
    return df


def identify_unmatched_reg_ans(df):
    # Identifica registros ANS sem match no cadastro de operadoras.
    
    df = df.copy()
    
    # Identificar registros sem CNPJ (não encontrados no cadastro)
    mask_sem_cnpj = df['CNPJ'].isna() | (df['CNPJ'].astype(str).str.strip() == '')
    
    # Adicionar flag
    df['CadastroIncompleto'] = mask_sem_cnpj
    
    # Coletar REG_ANS órfãos únicos
    reg_ans_orfaos = df[mask_sem_cnpj]['RegistroANS'].dropna().unique()
    
    # Criar lista com estatísticas
    unmatched_list = []
    for reg_ans in reg_ans_orfaos:
        mask_reg = (df['RegistroANS'] == reg_ans) & mask_sem_cnpj
        count = mask_reg.sum()
        razao_social = df[mask_reg]['RazaoSocial'].iloc[0] if count > 0 else None
        
        unmatched_list.append({
            'RegistroANS': reg_ans,
            'QuantidadeRegistros': count,
            'RazaoSocialPlaceholder': razao_social
        })
    
    count_total = mask_sem_cnpj.sum()
    if count_total > 0:
        logging.warning(f"{count_total} registros com cadastro incompleto ({len(reg_ans_orfaos)} REG_ANS únicos)")
    
    return df, unmatched_list


def save_unmatched_reg_ans(unmatched_list, output_path):
    # Salva lista de REG_ANS órfãos em arquivo separado.

    if not unmatched_list:
        logging.info("Nenhum REG_ANS órfão detectado")
        return
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df_unmatched = pd.DataFrame(unmatched_list)
    df_unmatched = df_unmatched.sort_values('QuantidadeRegistros', ascending=False)
    df_unmatched.to_csv(output_path, index=False)
    
    logging.info(f"REG_ANS órfãos salvos: {output_path} ({len(unmatched_list)} registros)")

def validate_cnpj(cnpj_str):

    if pd.isna(cnpj_str):
        return False
    
    # Remover caracteres não numéricos
    cnpj_digits = re.sub(r'\D', '', str(cnpj_str))
    
    # Validar comprimento
    if len(cnpj_digits) != 14:
        return False
    
    # Rejeitar CNPJs com todos dígitos iguais
    if cnpj_digits == cnpj_digits[0] * 14:
        return False
    
    # Calcular primeiro dígito verificador
    weights_first = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_first = 0
    for i in range(12):
        sum_first += int(cnpj_digits[i]) * weights_first[i]
    
    remainder_first = sum_first % 11
    digit_first = 0 if remainder_first < 2 else 11 - remainder_first
    
    if int(cnpj_digits[12]) != digit_first:
        return False
    
    # Calcular segundo dígito verificador
    weights_second = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_second = 0
    for i in range(13):
        sum_second += int(cnpj_digits[i]) * weights_second[i]
    
    remainder_second = sum_second % 11
    digit_second = 0 if remainder_second < 2 else 11 - remainder_second
    
    if int(cnpj_digits[13]) != digit_second:
        return False
    
    return True


def identify_invalid_cnpjs(df):
    df = df.copy()
    
    # Validar cada CNPJ (apenas para registros com cadastro completo)
    df['CNPJInvalido'] = False
    
    # Identificar registros com CNPJ presente mas inválido
    mask_com_cnpj = df['CNPJ'].notna() & (df['CNPJ'].astype(str).str.strip() != '') & (df['CNPJ'].astype(str) != 'nan')
    
    if 'CadastroIncompleto' in df.columns:
        mask_com_cnpj = mask_com_cnpj & ~df['CadastroIncompleto']
    
    df.loc[mask_com_cnpj, 'CNPJInvalido'] = ~df.loc[mask_com_cnpj, 'CNPJ'].apply(validate_cnpj)
    
    # Coletar CNPJs inválidos únicos (excluindo vazios)
    mask_invalido = df['CNPJInvalido']
    cnpjs_invalidos = df[mask_invalido]['CNPJ'].unique()
    
    # Criar estatísticas
    invalid_list = []
    for cnpj in cnpjs_invalidos:
        mask_cnpj = (df['CNPJ'] == cnpj) & mask_invalido
        count = mask_cnpj.sum()
        razao_social = df[mask_cnpj]['RazaoSocial'].iloc[0] if count > 0 else None
        reg_ans = df[mask_cnpj]['RegistroANS'].iloc[0] if count > 0 else None
        
        invalid_list.append({
            'CNPJ': cnpj,
            'RegistroANS': reg_ans,
            'RazaoSocial': razao_social,
            'QuantidadeRegistros': count
        })
    
    count_total = mask_invalido.sum()
    if count_total > 0:
        logging.warning(f"{count_total} registros com CNPJ inválido ({len(cnpjs_invalidos)} CNPJs únicos)")
    
    return df, invalid_list


def save_invalid_cnpjs(invalid_list, output_path):

    if not invalid_list:
        logging.info("Nenhum CNPJ inválido detectado")
        return
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df_invalid = pd.DataFrame(invalid_list)
    df_invalid = df_invalid.sort_values('QuantidadeRegistros', ascending=False)
    df_invalid.to_csv(output_path, index=False)
    
    logging.info(f"CNPJs inválidos salvos: {output_path} ({len(invalid_list)} CNPJs)")

