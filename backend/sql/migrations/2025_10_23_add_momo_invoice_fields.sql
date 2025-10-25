-- Migration: add fields to invoices table to support Momo / payment receipt structure
-- Adds nullable fields so migration is safe for existing data

ALTER TABLE IF EXISTS invoices
    ADD COLUMN IF NOT EXISTS buyer_tax_id VARCHAR(64),
    ADD COLUMN IF NOT EXISTS seller_tax_id VARCHAR(64),
    ADD COLUMN IF NOT EXISTS buyer_address TEXT,
    ADD COLUMN IF NOT EXISTS seller_address TEXT,
    ADD COLUMN IF NOT EXISTS items JSONB,
    ADD COLUMN IF NOT EXISTS currency VARCHAR(16) DEFAULT 'VND',
    ADD COLUMN IF NOT EXISTS subtotal NUMERIC,
    ADD COLUMN IF NOT EXISTS tax_amount NUMERIC,
    ADD COLUMN IF NOT EXISTS tax_percentage NUMERIC,
    ADD COLUMN IF NOT EXISTS total_amount_value NUMERIC,
    ADD COLUMN IF NOT EXISTS transaction_id VARCHAR(128),
    ADD COLUMN IF NOT EXISTS payment_method VARCHAR(64),
    ADD COLUMN IF NOT EXISTS payment_account VARCHAR(128),
    ADD COLUMN IF NOT EXISTS invoice_time TIMESTAMP,
    ADD COLUMN IF NOT EXISTS due_date DATE;

-- Add index for fast lookup by transaction_id
CREATE INDEX IF NOT EXISTS idx_invoices_transaction_id ON invoices (transaction_id);
