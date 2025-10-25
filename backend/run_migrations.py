"""Run SQL migrations from backend/sql/migrations directory"""
import os
import glob
from pathlib import Path
from utils.database_tools import DatabaseTools
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration_file(db: DatabaseTools, sql_path: str):
    logger.info(f"Running migration: {sql_path}")
    with open(sql_path, 'r', encoding='utf-8') as fh:
        sql = fh.read()
    conn = db.connect()
    if not conn:
        logger.error("Cannot connect to DB")
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            conn.commit()
        logger.info(f"Applied: {sql_path}")
        return True
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False


def main():
    project_root = Path(__file__).resolve().parent
    migrations_dir = project_root / 'sql' / 'migrations'
    migration_files = sorted(glob.glob(str(migrations_dir / '*.sql')))
    logger.info(f"Looking for migrations in: {migrations_dir}")
    logger.info(f"Found files: {migration_files}")
    if not migration_files:
        logger.info("No migration files found")
        return

    db = DatabaseTools()
    for mf in migration_files:
        success = run_migration_file(db, mf)
        if not success:
            logger.error(f"Stopping on failed migration: {mf}")
            break

if __name__ == '__main__':
    main()
