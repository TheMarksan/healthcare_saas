import requests
from pathlib import Path
import pandas as pd
from io import StringIO
import zipfile
import shutil # para remoção de diretórios


def clean_html_table(tables, column_name='Name', exclude_patterns=None):
    # Remove linhas vazias e cabeçalhos de navegação das tabelas HTML
    if exclude_patterns is None:
        exclude_patterns = ['Parent Directory']
    
    df = tables[0]
    df_clean = df[df[column_name].notna()].copy()
    
    for pattern in exclude_patterns:
        df_clean = df_clean[~df_clean[column_name].str.contains(pattern, na=False)]
    
    df_clean = df_clean[df_clean[column_name].str.strip() != '']
    return df_clean


def get_folders(url):
    # retorna DataFrame com pastas disponíveis, ordenadas por data
    response = requests.get(url)
    tables = pd.read_html(StringIO(response.text))
    df_clean = clean_html_table(tables)
    return df_clean[df_clean['Name'].str.endswith('/', na=False)]


def get_zip_files(folder_url):
    # Retorna dataframe com arquivos zip de uma pasta
    response = requests.get(folder_url)
    tables = pd.read_html(StringIO(response.text))
    df_clean = clean_html_table(tables)
    return df_clean[df_clean['Name'].str.endswith('.zip', na=False)]


def collect_required_zips(folders, required_count=3):
    # coleta os arquivos ZIP mais recentes até atingir os últimos 3 trimestres
    required_zip_files = pd.DataFrame()
    base_url = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis"
    
    for idx, row in folders.iterrows():
        if len(required_zip_files) >= required_count:
            break
        
        folder_name = row['Name']
        folder_url = f"{base_url}/{folder_name}?C=M;O=D"
        zip_files = get_zip_files(folder_url)
        
        if len(zip_files) > 0:
            needed = required_count - len(required_zip_files)
            files_to_add = zip_files.head(needed)
            required_zip_files = pd.concat([required_zip_files, files_to_add], ignore_index=True)
    
    return required_zip_files


def process_extracted_files(extract_dir):
    # processando arquivos extraídos (csvs) usando chunking (melhor perfomance)
    processed_data = []
    
    for file_path in extract_dir.rglob('*'):
        if file_path.is_file():
            try:
                if file_path.suffix.lower() == '.csv':
                    chunks = []
                    for chunk in pd.read_csv(file_path, encoding='latin-1', sep=';', 
                                            on_bad_lines='skip', chunksize=10000):
                        chunk.columns = chunk.columns.str.strip().str.upper()
                        descricao_cols = [col for col in chunk.columns if 'DESCRI' in col]
                        
                        if descricao_cols:
                            desc_col = descricao_cols[0]
                            filtered = chunk[chunk[desc_col].astype(str).str.contains(
                                'Despesas com Eventos / Sinistros|Despesas com Eventos/Sinistros', 
                                case=False, na=False)]
                            
                            if not filtered.empty:
                                filtered['SOURCE_FILE'] = file_path.name
                                chunks.append(filtered)
                    
                    if chunks:
                        df = pd.concat(chunks, ignore_index=True)
                        processed_data.append(df)
                        print(f"  Processado: {file_path.name} ({len(df)} registros)")
                
                elif file_path.suffix.lower() == '.txt':
                    # .txt geralmente são menores, sem chunking
                    df = pd.read_csv(file_path, encoding='latin-1', sep='\t', on_bad_lines='skip')
                    df.columns = df.columns.str.strip().str.upper()
                    descricao_cols = [col for col in df.columns if 'DESCRI' in col]
                    
                    if descricao_cols:
                        desc_col = descricao_cols[0]
                        filtered = df[df[desc_col].astype(str).str.contains(
                            'Despesas com Eventos / Sinistros|Despesas com Eventos/Sinistros', 
                            case=False, na=False)]
                        
                        if not filtered.empty:
                            filtered['SOURCE_FILE'] = file_path.name
                            processed_data.append(filtered)
                            print(f"  ✓ Processado: {file_path.name} ({len(filtered)} registros)")
            
            except Exception as e:
                print(f"  ✗ Erro ao processar {file_path.name}: {e}")
    
    return pd.concat(processed_data, ignore_index=True) if processed_data else pd.DataFrame()


def download_and_extract_zips(zip_files_df, output_dir):
    # baixa, extrai e processa os arquivos zip em lote
    base_url = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    all_processed_data = []
    
    for _, row in zip_files_df.iterrows():
        zip_name = row['Name']
        ano = str(row['Last modified'])[:4]
        zip_url = f"{base_url}/{ano}/{zip_name}"
        zip_path = output_dir / zip_name
        
        print(f"\nBaixando {zip_name}...")
        response = requests.get(zip_url)
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        extract_dir = output_dir / zip_name.replace('.zip', '')
        print(f"Extraindo para {extract_dir}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print(f"Processando arquivos de {zip_name}...")
        processed_df = process_extracted_files(extract_dir)
        
        if not processed_df.empty:
            processed_file = output_dir / f"processado_{zip_name.replace('.zip', '.csv')}"
            processed_df.to_csv(processed_file, index=False, encoding='utf-8-sig')
            print(f"  ✓ Salvo: {processed_file.name} ({len(processed_df)} registros)")
            all_processed_data.append(processed_df)
        
        # Remover arquivos extraídos para economizar espaço
        shutil.rmtree(extract_dir)
        zip_path.unlink()
        print(f"Limpeza concluída para {zip_name}")
    
    # Consolidar todos os dados processados
    if all_processed_data:
        consolidated = pd.concat(all_processed_data, ignore_index=True)
        
        def extract_period(filename):
            if 'T' in filename:
                parts = filename.replace('.csv', '').split('T')
                trimestre = parts[0][-2:].zfill(2)  # ultimos 2 dígitos antes do T
                ano = parts[1][:4]  # primeiros 4 dígitos após o T
                return trimestre, ano
            return None, None
        
        consolidated['Trimestre'], consolidated['Ano'] = zip(*consolidated['SOURCE_FILE'].apply(extract_period))
        
        # Calcular despesas do período: diferença entre saldo final e inicial
        if 'VL_SALDO_FINAL' in consolidated.columns and 'VL_SALDO_INICIAL' in consolidated.columns:
            # Converter para numérico, tratando valores com vírgula
            saldo_final = pd.to_numeric(
                consolidated['VL_SALDO_FINAL'].astype(str).str.replace(',', '.'),
                errors='coerce'
            ).fillna(0)
            
            saldo_inicial = pd.to_numeric(
                consolidated['VL_SALDO_INICIAL'].astype(str).str.replace(',', '.'),
                errors='coerce'
            ).fillna(0)
            
            consolidated['ValorDespesas'] = saldo_final - saldo_inicial
        elif 'VL_SALDO_FINAL' in consolidated.columns:
            # fallback: usar apenas saldo final se inicial não existir
            consolidated['ValorDespesas'] = consolidated['VL_SALDO_FINAL']
        
        # Criar DataFrame final apenas com as colunas solicitadas
        final_df = pd.DataFrame({
            'CNPJ': consolidated.get('CNPJ', None),
            'REG_ANS': consolidated.get('REG_ANS', None),
            'RazaoSocial': consolidated.get('RazaoSocial', None),
            'Trimestre': consolidated['Trimestre'],
            'Ano': consolidated['Ano'],
            'ValorDespesas': consolidated.get('ValorDespesas', None)
        })
        
        consolidated_file = output_dir / "consolidado_despesas.csv"
        final_df.to_csv(consolidated_file, index=False, encoding='utf-8-sig')
        print(f"\nArquivo consolidado salvo: {consolidated_file} ({len(final_df)} registros)")
    
    return all_processed_data


if __name__ == "__main__":
    # URL base com ordenação por data decrescente
    url_base = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/?C=M;O=D"
    
    folders = get_folders(url_base)
    print(f"Pastas encontradas: {len(folders)}")
    
    # Coletar os 3 arquivos ZIP mais recentes
    required_zips = collect_required_zips(folders, required_count=3)
    print(f"\nArquivos ZIP selecionados: {len(required_zips)}")
    print(required_zips[['Name', 'Last modified']])
    
    output_dir = Path("data/trimestrais_contabeis")
    download_and_extract_zips(required_zips, output_dir)
    print("\nProcesso concluído!")
    
