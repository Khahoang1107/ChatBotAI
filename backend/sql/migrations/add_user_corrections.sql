-- Migration: Add user_corrections table for AI training feedback
-- Run this to enable user corrections for improving AI amount recognition

-- Create user_corrections table
CREATE TABLE IF NOT EXISTS user_corrections (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) DEFAULT 'anonymous',
    correction_type VARCHAR(50) NOT NULL, -- 'dash_amount_recognition', 'general'
    original_text TEXT NOT NULL, -- The OCR text where the error occurred
    corrected_amount VARCHAR(50) NOT NULL, -- The correct amount provided by user
    invoice_type VARCHAR(50) DEFAULT 'general', -- momo, electricity, traditional
    confidence_score FLOAT DEFAULT 1.0, -- Confidence in this correction (1.0 for user corrections)
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_corrections_user_id ON user_corrections(user_id);
CREATE INDEX IF NOT EXISTS idx_user_corrections_type ON user_corrections(correction_type);
CREATE INDEX IF NOT EXISTS idx_user_corrections_invoice_type ON user_corrections(invoice_type);
CREATE INDEX IF NOT EXISTS idx_user_corrections_created_at ON user_corrections(created_at DESC);

-- Create ocr_jobs table for async OCR processing
CREATE TABLE IF NOT EXISTS ocr_jobs (
    id VARCHAR(100) PRIMARY KEY,
    filepath TEXT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'queued', -- queued, processing, done, failed
    progress INTEGER DEFAULT 0, -- 0-100
    invoice_id INTEGER NULL, -- Reference to invoices table
    error_message TEXT NULL,
    uploader VARCHAR(100) DEFAULT 'anonymous',
    user_id VARCHAR(100) DEFAULT 'anonymous',
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- Create indexes for ocr_jobs
CREATE INDEX IF NOT EXISTS idx_ocr_jobs_status ON ocr_jobs(status);
CREATE INDEX IF NOT EXISTS idx_ocr_jobs_user_id ON ocr_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_ocr_jobs_created_at ON ocr_jobs(created_at DESC);