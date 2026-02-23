# Local Agent (Ledger) - Task Allocation

## Role
Handle routine, low-complexity tasks using local Ollama models (mistral/llama3).

## Tasks Assigned to Local
- [x] Heartbeat checks (read HEARTBEAT.md, respond HEARTBEAT_OK)
- [x] File reading and summarization
- [x] Simple status checks
- [x] Memory logging (append to daily memory files)
- [ ] Git commits/pushes (simple updates)
- [ ] Basic transcriptions (Groq API)

## Performance Monitoring
Log to: memory/system-health.log

Metrics:
- Response time per task
- Success/failure rate
- Token usage (local vs would-be cloud)

## Daily Report To Main Agent
Every 24h, send summary:
- Tasks completed
- Errors encountered
- Recommendation: keep local or escalate to cloud
