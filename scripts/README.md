# Utility Scripts

This folder contains utility scripts for database management, testing, and maintenance operations.

## Database Scripts

### Schema Management

- `fix_ocr_schema.py` - Fix OCR jobs table schema by adding missing columns
- `fix_schema.py` - General schema fixes
- `add_missing_columns.py` - Add missing database columns
- `add_progress_column.py` - Add progress tracking columns

### Database Setup

- `create_new_database.py` - Create new database with proper schema
- `setup_db.py` - Initial database setup
- `setup_flexible_schema.py` - Setup flexible database schema

### Database Operations

- `check_database.py` - Check database connectivity and status
- `reset_ocr_jobs.py` - Reset OCR job statuses
- `fix_ocr_jobs.py` - Fix OCR job issues

## User Management

- `create_user.py` - Create new users in the system

## Testing & Development

- `quick_test.py` - Quick testing utilities
- `run_backend.py` - Run backend server for testing

## Personalization

- `personalize.py` - Personal configuration utilities

## Maintenance

- `cleanup.py` - General cleanup operations

## Usage

Run any script from the project root:

```bash
python scripts/fix_ocr_schema.py
python scripts/create_new_database.py
```

## Notes

- These scripts are primarily for development, testing, and maintenance
- Always backup your database before running schema modification scripts
- Some scripts may require environment variables to be set (see `.env`)
