import requests
import pandas as pd
import logging
import sys
from pathlib import Path
from utils.validators import (
    normalize_trimestre,
    detect_cnpj_conflicts,
    save_equality_issues,
    handle_missing_razao_social,
    identify_unmatched_reg_ans,
    save_unmatched_reg_ans,
    identify_invalid_cnpjs,
    save_invalid_cnpjs
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def download_operadoras(output_path):
    url = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    response = requests.get(url)
    output_path.write_bytes(response.content)
    print(f"Cadastro de operadoras baixado: {output_path}")


def load_operadoras(path):
    colunas = ['REGISTRO_OPERADORA', 'Razao_Social', 'CNPJ', 'Modalidade', 'UF']
    return pd.read_csv(path, sep=';', usecols=colunas, dtype=str)


def enrich_chunk(chunk, operadoras_lookup):
    # Enriquece um chunk de dados com informações das operadoras
    if len(chunk) == 0:
        return pd.DataFrame()
    
    # Normalizar trimestres se a coluna existir
    if 'Trimestre' in chunk.columns:
        chunk['Trimestre'] = chunk['Trimestre'].apply(normalize_trimestre)
        
        chunk = chunk[chunk['Trimestre'].notna()]
    
    if len(chunk) == 0:
        return pd.DataFrame()
    
    enriched = chunk.merge(
        operadoras_lookup,
        left_on='REG_ANS',
        right_on='REGISTRO_OPERADORA',
        how='left',
        suffixes=('_old', '')
    )
    
    # Normalizar colunas
    result = enriched[[
        'CNPJ', 'Razao_Social', 'Trimestre', 'Ano', 'ValorDespesas', 'REG_ANS', 'Modalidade', 'UF'
    ]].rename(columns={'Razao_Social': 'RazaoSocial', 'REG_ANS': 'RegistroANS'})
    
    # Preservar tipos do cadastro: CNPJ e RegistroANS como strings
    result['CNPJ'] = result['CNPJ'].astype(str)
    result['RegistroANS'] = result['RegistroANS'].astype(str)
    
    result['CadastroIncompleto'] = result['CNPJ'].isna() | (result['CNPJ'].str.strip() == '')
    
    result = handle_missing_razao_social(result)
    
    # Adicionar flags (inicialmente False)
    result['CNPJConflict'] = False
    result['CNPJInvalido'] = False
    
    return result


def process_consolidado_in_chunks(input_path, output_path, operadoras_df, chunksize=50000):
    # processa arquivo consolidado em chunks para otimizar memória
    first_chunk = True
    total_records = 0
    
    for chunk in pd.read_csv(input_path, dtype=str, chunksize=chunksize):
        enriched_chunk = enrich_chunk(chunk, operadoras_df)
        
        mode = 'w' if first_chunk else 'a'
        header = first_chunk
        enriched_chunk.to_csv(output_path, mode=mode, header=header, index=False)
        
        total_records += len(enriched_chunk)
        first_chunk = False
        print(f"Processados: {total_records} registros")
    
    return total_records


def aggregate_by_razao_uf(input_path, output_path, chunksize=50000):
    # agrupa dados por RazaoSocial, UF, Trimestre e Ano, somando ValorDespesas
    chunks = []
    
    # Preservar CNPJ e RegistroANS como strings ao ler
    dtype_dict = {'CNPJ': str, 'RegistroANS': str}
    
    for chunk in pd.read_csv(input_path, dtype=dtype_dict, chunksize=chunksize):
        chunk['ValorDespesas'] = pd.to_numeric(chunk['ValorDespesas'], errors='coerce')
        
        # Converter flags booleanas (string -> bool)
        bool_flags = ['CNPJConflict', 'RazaoSocialAusente', 'CadastroIncompleto', 'CNPJInvalido']
        for col in bool_flags:
            if col in chunk.columns:
                chunk[col] = chunk[col].astype(str).str.lower().isin(['true', '1', 'yes'])
        
        # definir agregação: flags usam 'max' (True > False)
        agg_dict = {
            'CNPJ': 'first',
            'RegistroANS': 'first',
            'Modalidade': 'first',
            'ValorDespesas': 'sum'
        }
        
        # Adicionar flags existentes
        for col in bool_flags:
            if col in chunk.columns:
                agg_dict[col] = 'max'
        
        grouped = chunk.groupby(['RazaoSocial', 'UF', 'Trimestre', 'Ano'], dropna=False, as_index=False).agg(agg_dict)
        chunks.append(grouped)
    
    # Consolidar e reagrupar
    all_data = pd.concat(chunks, ignore_index=True)
    
    final_agg_dict = {
        'CNPJ': 'first',
        'RegistroANS': 'first',
        'Modalidade': 'first',
        'ValorDespesas': 'sum'
    }
    
    for col in bool_flags:
        if col in all_data.columns:
            final_agg_dict[col] = 'max'
    
    final_grouped = all_data.groupby(['RazaoSocial', 'UF', 'Trimestre', 'Ano'], dropna=False, as_index=False).agg(final_agg_dict)
    
    # Reordenar colunas
    base_cols = ['RazaoSocial', 'UF', 'Trimestre', 'Ano', 'CNPJ', 'RegistroANS', 'Modalidade', 'ValorDespesas']
    for col in bool_flags:
        if col in final_grouped.columns:
            base_cols.append(col)
    
    final_grouped = final_grouped[base_cols]
    final_grouped = final_grouped.sort_values(['RazaoSocial', 'UF', 'Ano', 'Trimestre'])
    final_grouped.to_csv(output_path, index=False, float_format='%.2f')
    
    return len(final_grouped)


if __name__ == "__main__":
    # Configuração de paths
    operadoras_path = Path("data/operadoras/operadoras_de_plano_de_saude_ativas.csv")
    consolidado_path = Path("data/trimestrais_contabeis/consolidado_despesas.csv")
    enriquecido_path = Path("data/trimestrais_contabeis/consolidado_despesas_enriquecido.csv")
    agrupado_path = Path("data/trimestrais_contabeis/consolidado_despesas_agrupado.csv")
    conflitos_path = Path("data/trimestrais_contabeis/logs/data_equality_issues.csv")
    unmatched_path = Path("data/trimestrais_contabeis/logs/unmatched_reg_ans.csv")
    invalid_cnpj_path = Path("data/trimestrais_contabeis/logs/invalid_cnpjs.csv")

    download_operadoras(operadoras_path)
    
    # Carregar lookup de operadoras (mantém em memória por ser pequeno)
    print("Carregando cadastro de operadoras...")
    operadoras_df = load_operadoras(operadoras_path)
    print(f"✓ {len(operadoras_df)} operadoras carregadas")
    
    # Processar consolidado em chunks
    print("\nEnriquecendo dados...")
    total = process_consolidado_in_chunks(consolidado_path, enriquecido_path, operadoras_df)
    print(f"\nArquivo enriquecido salvo: {enriquecido_path} ({total} registros)")
    
    if total == 0 or not enriquecido_path.exists():
        logging.error("Nenhum registro válido encontrado após enriquecimento")
        sys.exit(0)

    print("\nIdentificando REG_ANS sem correspondência no cadastro...")
    try:
        df_enriquecido = pd.read_csv(enriquecido_path, dtype=str)
        
        if len(df_enriquecido) == 0:
            logging.warning("Arquivo enriquecido está vazio")
            sys.exit(0)
        
        # Identificar e salvar REG_ANS órfãos
        df_validado, unmatched_list = identify_unmatched_reg_ans(df_enriquecido)
        df_validado.to_csv(enriquecido_path, index=False)
        save_unmatched_reg_ans(unmatched_list, unmatched_path)

        print("\nValidando CNPJs...")
        df_validado_cnpj, invalid_list = identify_invalid_cnpjs(df_validado)
        df_validado_cnpj.to_csv(enriquecido_path, index=False)
        save_invalid_cnpjs(invalid_list, invalid_cnpj_path)

        print("\nDetectando conflitos de CNPJ...")
        df_resolvido, conflitos = detect_cnpj_conflicts(df_validado_cnpj, operadoras_df)
         
        df_resolvido.to_csv(enriquecido_path, index=False)
        print(f"Conflitos resolvidos: {len(conflitos)} CNPJs com múltiplas razões sociais")
        
        # Salvar lista de conflitos
        save_equality_issues(conflitos, conflitos_path)
        
        print("\nAgrupando por RazaoSocial, UF, Trimestre e Ano...")
        total_grouped = aggregate_by_razao_uf(enriquecido_path, agrupado_path)
        print(f"Arquivo agrupado salvo: {agrupado_path} ({total_grouped} grupos)")
        
    except pd.errors.EmptyDataError:
        logging.error("Erro: Arquivo enriquecido vazio ou sem colunas válidas")
    except Exception as e:
        logging.error(f"Erro ao processar dados: {e}")
        raise

