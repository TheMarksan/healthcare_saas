#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_PASSWORD}"
MYSQL_HOST="${MYSQL_HOST:-localhost}"
MYSQL_PORT="${MYSQL_PORT:-3306}"

MYSQL_CMD="mysql -h$MYSQL_HOST -P$MYSQL_PORT -u$MYSQL_USER"
if [ -n "$MYSQL_PASSWORD" ]; then
    MYSQL_CMD="$MYSQL_CMD -p$MYSQL_PASSWORD"
fi

echo "=== Setup Healthcare SaaS Database ==="

echo "1. Criando database..."
$MYSQL_CMD < "$SCRIPT_DIR/ddl/01_create_database.sql"

echo "2. Criando tabelas..."
$MYSQL_CMD < "$SCRIPT_DIR/ddl/02_create_tables.sql"

echo "3. Criando índices adicionais..."
$MYSQL_CMD < "$SCRIPT_DIR/ddl/03_create_indexes.sql"

echo "4. Criando stored procedures..."
$MYSQL_CMD < "$SCRIPT_DIR/procedures/sp_import_operadora.sql"
$MYSQL_CMD < "$SCRIPT_DIR/procedures/sp_import_despesa.sql"
$MYSQL_CMD < "$SCRIPT_DIR/procedures/sp_import_metrica.sql"

echo "5. Criando views..."
$MYSQL_CMD < "$SCRIPT_DIR/views/vw_despesas_dashboard.sql"

echo "✓ Database setup completo!"
echo ""
echo "Próximo passo: Execute a importação de dados"
echo "python3 scripts/import/import_data.py"
