#!/bin/bash
# PostgreSQL Setup Script for Phase 1.3
# Run this on the NUC to create user, database, and tables

set -e

echo "=== OpenClaw PostgreSQL Setup ==="
echo ""

# Configuration
DB_USER="astra_user"
DB_NAME="openclaw_db"
DB_PASSWORD="AstraSecure2026!"  # Change this after setup

echo "Creating user: $DB_USER"
echo "Creating database: $DB_NAME"
echo ""

# Create user and database
sudo -u postgres psql << EOF
-- Create user with password
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Create database owned by user
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Allow user to create schemas
ALTER USER $DB_USER CREATEDB;
EOF

echo "✓ User and database created"
echo ""
echo "=== Testing connection ==="

# Test the connection
export PGPASSWORD="$DB_PASSWORD"
psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT current_user, current_database();"

echo ""
echo "✓ Phase 1.3 Complete!"
echo ""
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Password: $DB_PASSWORD"
echo ""
echo "⚠️  IMPORTANT: Change the password after setup!"
echo "   Command: ALTER USER astra_user WITH PASSWORD 'your-new-password';"
