-- Migration: Create audit_logs table
-- Phase 7: Safety, Trust & UX

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR PRIMARY KEY,
    account_id VARCHAR,
    group_id VARCHAR,
    user_id VARCHAR NOT NULL,
    event_type VARCHAR NOT NULL,
    event_data JSONB DEFAULT '{}',
    rule_name VARCHAR,
    previous_status VARCHAR,
    current_status VARCHAR,
    message VARCHAR,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (account_id) REFERENCES connected_accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES account_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_account_id ON audit_logs(account_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_group_id ON audit_logs(group_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_rule_name ON audit_logs(rule_name);
