-- Manifest Scrapper Database Schema
-- Run this in Supabase SQL Editor to create all tables

-- Create custom types/enums
CREATE TYPE product_status AS ENUM (
    'pending',
    'scraping',
    'collected',
    'ready_to_post',
    'posting',
    'posted',
    'sold',
    'failed'
);

CREATE TYPE job_type AS ENUM (
    'scrape',
    'post'
);

CREATE TYPE job_status AS ENUM (
    'pending',
    'running',
    'completed',
    'failed'
);

-- Products table - Main product data
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL UNIQUE,
    title TEXT,
    price TEXT,
    description TEXT,
    status product_status NOT NULL DEFAULT 'pending',
    missing_fields TEXT[] DEFAULT ARRAY[]::TEXT[],
    folder_path TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE,
    posted_at TIMESTAMP WITH TIME ZONE,
    sold_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Jobs table - Track scraping and posting jobs
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    job_type job_type NOT NULL,
    status job_status NOT NULL DEFAULT 'pending',
    result JSONB,
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Product images table - Store image file paths
CREATE TABLE product_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    image_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Posting history table - Track Facebook posting attempts
CREATE TABLE posting_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    marketplace_url TEXT,
    status TEXT NOT NULL,
    error TEXT,
    posted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_url ON products(url);
CREATE INDEX idx_products_created_at ON products(created_at);
CREATE INDEX idx_jobs_product_id ON jobs(product_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_product_images_product_id ON product_images(product_id);
CREATE INDEX idx_posting_history_product_id ON posting_history(product_id);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to auto-update updated_at on products
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add some helpful comments
COMMENT ON TABLE products IS 'Main product data with status tracking';
COMMENT ON TABLE jobs IS 'Scraping and posting job history';
COMMENT ON TABLE product_images IS 'Image file paths for products';
COMMENT ON TABLE posting_history IS 'Facebook Marketplace posting history';
