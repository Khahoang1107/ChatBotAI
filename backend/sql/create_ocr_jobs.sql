-- Create ocr_jobs table for async OCR processing
-- Run this migration to enable the enqueue/worker system

CREATE TABLE IF NOT EXISTS ocr_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filepath TEXT NOT NULL,
    filename TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'queued',
    attempts INT DEFAULT 0,
    max_attempts INT DEFAULT 3,
    invoice_id INT NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL
);

-- Create index on status and created_at for efficient polling
CREATE INDEX IF NOT EXISTS idx_ocr_jobs_status ON ocr_jobs(status, created_at);
CREATE INDEX IF NOT EXISTS idx_ocr_jobs_created_at ON ocr_jobs(created_at DESC);

-- Add columns to track uploader/user
ALTER TABLE ocr_jobs ADD COLUMN IF NOT EXISTS uploader TEXT DEFAULT 'unknown';
ALTER TABLE ocr_jobs ADD COLUMN IF NOT EXISTS user_id TEXT NULL;

-- Create table for job notifications (for websocket)
CREATE TABLE IF NOT EXISTS ocr_notifications (
    id SERIAL PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES ocr_jobs(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Index for notification queries
CREATE INDEX IF NOT EXISTS idx_ocr_notifications_job_id ON ocr_notifications(job_id);
