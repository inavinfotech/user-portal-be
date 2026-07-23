#!/bin/bash

# Script to handle database migrations using Alembic for portal-user backend
# Usage: 
#   ./scripts/migrate.sh create "migration message"  - To create a new migration
#   ./scripts/migrate.sh apply                        - To apply migrations to the database
#   ./scripts/migrate.sh stamp                        - To stamp the database with the current head

set -e

# Navigate to the backend directory (where alembic.ini is located)
cd "$(dirname "$0")/.."

# Check if venv exists and activate it
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
else
    echo "Warning: venv not found. Using system python/alembic."
fi

COMMAND=$1

if [ "$COMMAND" == "create" ]; then
    MESSAGE=$2
    if [ -z "$MESSAGE" ]; then
        echo "Error: Migration message is required."
        echo "Usage: ./scripts/migrate.sh create \"migration message\""
        exit 1
    fi
    echo "Generating new migration: $MESSAGE"
    alembic revision --autogenerate -m "$MESSAGE"
elif [ "$COMMAND" == "apply" ]; then
    echo "Checking database state for migrations..."
    STATUS=0
    python3 -c "
import os, sys
sys.path.insert(0, '.')
from sqlalchemy import create_engine, inspect

db_url = os.getenv('DATABASE_URL', 'sqlite:///./sql_app.db')
try:
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if ('users' in tables or 'applications' in tables) and 'alembic_version' not in tables:
        sys.exit(10)
except Exception:
    pass
sys.exit(0)
" 2>/dev/null || STATUS=$?
    if [ $STATUS -eq 10 ]; then
        echo "Existing database detected without Alembic tracking. Stamping database with head revision..."
        alembic stamp head
    fi

    echo "Applying migrations to the database..."
    alembic upgrade heads
elif [ "$COMMAND" == "stamp" ]; then
    echo "Stamping the database with the current head..."
    alembic stamp head
else
    echo "Invalid command: $COMMAND"
    echo "Usage:"
    echo "  ./scripts/migrate.sh create \"message\""
    echo "  ./scripts/migrate.sh apply"
    echo "  ./scripts/migrate.sh stamp"
    exit 1
fi
