# Healthcare SaaS - Scripts SQL

## Estrutura

```
scripts/
├── ddl/              # Data Definition Language
├── procedures/       # Stored Procedures com error handling
├── views/           # Views para consultas frequentes
├── analytics/       # Queries analíticas específicas
├── import/          # Scripts Python para importação CSV
└── setup_database.sh
```

## Setup Inicial

### 1. Configurar MySQL

```bash
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED BY 'your_password';
```

### 2. Criar Database e Estrutura

```bash
chmod +x setup_database.sh
./setup_database.sh
```

### 3. Importar Dados

```bash
cd import
pip install pymysql
python3 import_data.py
```

## Queries Analíticas

### Query 1: Top 5 Crescimento Percentual
**Abordagem**: CTE com JOIN entre primeiro e último trimestre
**Justificativa**: Garante que apenas operadoras com dados nos dois períodos sejam consideradas

```bash
mysql -u root -p healthcare_saas < analytics/query1_crescimento_operadoras.sql
```

### Query 2: Distribuição por UF
**Abordagem**: Agregação em múltiplos níveis (UF e por operadora dentro da UF)
**Justificativa**: Permite análise tanto do total quanto da média por operadora

```bash
mysql -u root -p healthcare_saas < analytics/query2_distribuicao_por_uf.sql
```

### Query 3: Operadoras Acima da Média
**Abordagem**: CTE com média por trimestre + agregação por operadora
**Justificativa**: Performance superior a subqueries aninhadas, legibilidade alta

```bash
mysql -u root -p healthcare_saas < analytics/query3_acima_media.sql
```

## Tratamento de Inconsistências

### NULL em campos obrigatórios
- **Ação**: Rejeita e loga em `import_rejects`
- **Justificativa**: Integridade referencial

### Valores inválidos em campos numéricos
- **Ação**: Converte para 0.00 e loga warning
- **Justificativa**: Preserva registro para auditoria

### CNPJs/Registro ANS ausentes
- **Ação**: Insere com flag `cadastro_incompleto = TRUE`
- **Justificativa**: Mantém dados parciais para análise

### Strings 'nan' ou vazias
- **Ação**: Converte para NULL
- **Justificativa**: Normalização de dados

## Monitoramento

```sql
-- Ver logs de importação
SELECT * FROM import_logs ORDER BY started_at DESC LIMIT 10;

-- Ver rejeições
SELECT error_type, COUNT(*) as total 
FROM import_rejects 
GROUP BY error_type 
ORDER BY total DESC;

-- Estatísticas das tabelas
SELECT 
    'operadoras' as tabela, COUNT(*) as registros FROM operadoras
UNION ALL
SELECT 
    'despesas_trimestrais', COUNT(*) FROM despesas_trimestrais
UNION ALL
SELECT 
    'metricas_operadoras', COUNT(*) FROM metricas_operadoras;
```

## Índices e Performance

- **Índices compostos** para queries analíticas frequentes
- **DECIMAL(15,2)** para valores monetários (precisão garantida)
- **Views** para consultas dashboard (performance)
- **Stored Procedures** com error handling (robustez)

## Integração FastAPI

```python
from sqlalchemy import create_engine

engine = create_engine(
    'mysql+pymysql://root:your_password@localhost/healthcare_saas?charset=utf8mb4'
)
```
