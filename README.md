# Healthcare SaaS

Projeto de SaaS vertical focado em healthcare, com ênfase em tradeoffs técnicos de processamento de dados, técnicas de normalização, consumo de APIs, queries otimizadas e paginação eficiente no frontend. 
O sistema proporciona dashboards e estatísticas sobre despesas de eventos/sinistros em operadoras de healthcare, com dados obtidos de API Restful pública da Associação de Saúde Suplementar (ANS).

## Tecnologias Utilizadas

- **Pandas (Python):** Processamento e análise de dados.
- **MySQL:** Armazenamento e normalização de dados.
- **FastAPI:** Backend ágil e performático para APIs.
- **VueJS:** Frontend moderno com paginação eficiente.

## Como rodar o projeto

### 1. Pipeline de dados (primeiro passo)
Os scripts em `data_pipeline/` permitem baixar, enriquecer e analisar os dados antes da importação no banco. Exemplo de uso:

```bash
cd data_pipeline
python3 -m venv venv
source venv/bin/activate
pip install -r ../backend/requirements.txt  # Reaproveita dependências do backend
# Baixar dados brutos
data_pipeline$ python3 download.py
# Enriquecer e processar dados
data_pipeline$ python3 enrich.py
# Analisar dados (opcional)
data_pipeline$ python3 analyze.py
```

Os arquivos processados ficarão em `data_pipeline/data/`. Após o processamento, utilize os scripts de importação do backend para carregar os dados no banco de dados.

### 2. Backend (API)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edite as variáveis conforme necessário
cd src
uvicorn api.main:app --reload
```

### 3. Frontend (SPA)
```bash
cd frontend
npm install
npm run dev
```

### 4. Banco de Dados
- MySQL 8+ rodando (ajuste .env se necessário)
- Scripts de criação em `backend/scripts/ddl/`

### 5. Importação de dados para o banco
```bash
cd backend/scripts/import
source ../../venv/bin/activate  # Ative o venv do backend
python3 import_data.py
python3 create_placeholder_operadoras.py
```

Acesse o frontend em: http://localhost:5173
Acesse a API em: http://localhost:8000/docs
