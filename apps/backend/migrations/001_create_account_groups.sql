-- Migration: Create account_groups and account_group_members tables
-- Phase 6: Multi-Account & Copy-Trade Logic

-- Create account_groups table
CREATE TABLE IF NOT EXISTS account_groups (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    description VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create account_group_members association table
CREATE TABLE IF NOT EXISTS account_group_members (
    group_id VARCHAR NOT NULL,
    account_id VARCHAR NOT NULL,
    PRIMARY KEY (group_id, account_id),
    FOREIGN KEY (group_id) REFERENCES account_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES connected_accounts(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_account_groups_user_id ON account_groups(user_id);
CREATE INDEX IF NOT EXISTS idx_account_group_members_group_id ON account_group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_account_group_members_account_id ON account_group_members(account_id);
