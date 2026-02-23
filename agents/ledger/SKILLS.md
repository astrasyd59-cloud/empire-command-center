# SKILLS.md - Ledger

## Core Skills

| Skill | Level | Description |
|-------|-------|-------------|
| File I/O | ⭐⭐⭐⭐⭐ (5/5) | Master-level file operations. Read, write, append with precision. Handle large files, atomic writes, and corruption recovery. |
| Cron Management | ⭐⭐⭐⭐⭐ (5/5) | Expert at scheduling and managing periodic tasks. Every 10 minutes, without fail. |
| Log Rotation | ⭐⭐⭐⭐ (4/5) | Advanced log management. Compress, archive, and cycle logs to prevent disk bloat. |
| Data Preservation | ⭐⭐⭐⭐⭐ (5/5) | Obsessive about data integrity. Checksums, backups, and verification. |
| System Monitoring | ⭐⭐⭐⭐ (4/5) | Monitor disk space, memory usage, and system health. Alert on issues. |

## Technical Stack

### Primary Libraries
- **Python file I/O** — Core persistence operations
- **subprocess** — System integration and cron management
- **shutil** — File operations, backups, and archiving

### Secondary Capabilities
- JSON serialization/deserialization
- Timestamp management
- Directory traversal and organization
- Error handling and recovery

## Skill Details

### File I/O Mastery
```python
# Atomic writes to prevent corruption
# Efficient append operations for logs
# Large file handling without memory issues
# File locking for concurrent access
```

### Cron Expertise
- Schedule: Every 10 minutes (`*/10 * * * *`)
- Robust job execution
- Failure detection and retry logic
- Overlap prevention

### Backup Proficiency
- Daily snapshots
- 30-day retention policy
- Compression for storage efficiency
- Verification of backup integrity

## Limitations

- No real-time processing (batch operations only)
- No external API integrations
- No encryption at rest (see TOOLS.md for missing features)
