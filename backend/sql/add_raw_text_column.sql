-- Add missing raw_text column to invoices table
-- This column stores the raw OCR text extracted from images

ALTER TABLE invoices ADD COLUMN IF NOT EXISTS raw_text TEXT;

-- Add comment for documentation
COMMENT ON COLUMN invoices.raw_text IS 'Raw OCR text extracted from invoice images';