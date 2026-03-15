---
name: interview-prep
description: Stores company research, interview prep notes, and tracks interview stages. Helps Dibs prepare for operations/trading roles with company-specific intel, common questions, and follow-up reminders.
user-invocable: true
---

# Interview Prep Skill

## Purpose

Dibs is actively job hunting — targeting operations/trading roles at $200k+. This skill tracks:

- Company research (funding, team, culture, tech stack)
- Interview stages and notes
- Common questions by role type
- Follow-up reminders
- Salary benchmarks and negotiation notes

---

## Integration with Job Pipeline

This skill works alongside `job-pipeline` (GitHub Issues tracker):

- **job-pipeline:** Tracks application stage (Applied → Interview → Offer)
- **interview-prep:** Stores detailed research and prep notes

Use both when preparing for interviews.

---

## Quick Commands

### Research a company
```bash
python3 ~/.openclaw/workspace/skills/interview-prep/scripts/research_company.py \
  --company "Keyrock" \
  --role "Operations Manager" \
  --url "https://keyrock.com"
```

### Log interview notes
```bash
python3 ~/.openclaw/workspace/skills/interview-prep/scripts/log_interview.py \
  --company "Keyrock" \
  --round "Phone Screen" \
  --interviewer "Sarah Chen, Head of Operations" \
  --questions "Tell me about yourself, Why Keyrock, Explain a trade lifecycle" \
  --notes "Strong focus on risk management, team is 15 people, they use Ripple Prime"
```

### Get interview prep checklist
```bash
python3 ~/.openclaw/workspace/skills/interview-prep/scripts/prep_checklist.py \
  --company "Keyrock"
```

### View upcoming interviews
```bash
python3 ~/.openclaw/workspace/skills/interview-prep/scripts/upcoming.py
```

### Salary benchmark lookup
```bash
python3 ~/.openclaw/workspace/skills/interview-prep/scripts/salary_benchmark.py \
  --role "Operations Manager" \
  --location "Sydney"
```

---

## Company Research Template

```json
{
  "company": "Keyrock",
  "role": "Operations Manager",
  "application_url": "https://jobs.ashbyhq.com/Keyrock/...",
  "job_pipeline_issue": 42,
  
  "company_intel": {
    "founded": "2017",
    "funding": "$72M Series B (2022)",
    "headcount": "150-200",
    "headquarters": "Brussels, Belgium",
    "sydney_office": "Yes (Barangaroo)",
    "business": "Crypto market making and liquidity provision",
    "clients": "Ripple, Binance, Coinbase, institutional traders"
  },
  
  "tech_stack": {
    "trading_platform": "Proprietary",
    "prime_broker": "Ripple Prime",
    "custody": "Fireblocks, Copper",
    "languages": "Python, Rust, Go",
    "infrastructure": "AWS, Kubernetes"
  },
  
  "team_intel": {
    "hiring_manager": "Sarah Chen, Head of Operations",
    "linkedin_profiles": ["linkedin.com/in/sarahchen-ops"],
    "team_size": "Operations team ~12 people",
    "culture_notes": "Fast-paced, crypto-native, risk-focused"
  },
  
  "interview_stages": [
    {
      "round": "Phone Screen",
      "date": "2026-03-20",
      "interviewer": "Sarah Chen",
      "questions_asked": [...],
      "notes": "...",
      "next_steps": "Technical interview scheduled"
    }
  ],
  
  "common_questions": [
    "Walk me through a trade lifecycle",
    "How do you handle trade breaks?",
    "Explain your experience with prime brokers",
    "How would you improve our onboarding process?"
  ],
  
  "salary_benchmark": {
    "role_range": "$180k-220k AUD base",
    "bonus": "20-40%",
    "total_comp": "$220k-300k AUD",
    "source": "Glassdoor, Levels.fyi, recruiter intel"
  },
  
  "prepared_answers": {
    "why_this_company": "Keyrock is the largest crypto market maker in Europe...",
    "strengths": "Process optimization, risk management, Python automation",
    "weaknesses": "Working on delegation — tend to own too much"
  },
  
  "questions_to_ask": [
    "What's the biggest operations challenge right now?",
    "How does the team handle weekend/evening coverage?",
    "What does success look like in 90 days?"
  ],
  
  "follow_ups": [
    {
      "date": "2026-03-22",
      "action": "Send thank-you email to Sarah",
      "status": "pending"
    }
  ]
}
```

---

## Role-Specific Question Banks

### Operations Manager
1. Walk me through a trade from execution to settlement
2. How do you handle trade breaks and discrepancies?
3. Describe your experience with prime brokers (Ripple Prime, Copper, etc.)
4. How would you improve our onboarding/KYC process?
5. Tell me about a time you caught an error before it became a problem
6. How do you prioritize when multiple issues hit at once?
7. What's your experience with automation? (Python, SQL, etc.)
8. How do you handle weekend/evening coverage?
9. Explain counterparty risk and how to mitigate it
10. What's your approach to process documentation?

### Trading/Dealer Roles
1. Explain bid-ask spread and market impact
2. How do you size positions based on volatility?
3. Walk me through your risk management framework
4. What's your view on the current crypto market?
5. How do you handle fast-moving markets and slippage?
6. Explain options Greeks and how you use them
7. What's your experience with algorithmic execution?
8. How do you stay informed on market-moving news?
9. Tell me about your best and worst trades
10. What's your edge as a trader?

---

## Astra's Protocol

### When Dibs schedules an interview

1. Research the company immediately
2. Pull role-specific questions
3. Generate prep checklist
4. Set follow-up reminders

### After the interview

Ask:
1. How did it go? (1-10)
2. What questions did they ask?
3. Any red flags or concerns?
4. Next steps and timeline?

Then: Log everything. Update job-pipeline issue.

### Weekly Job Hunt Check (Wed/Fri)

Combine with job-pipeline status:
```
💼 Job Hunt Check-in — [DAY]

Active Applications: [N]
Interviews This Week: [N]
Upcoming Interviews: [list with prep status]
Follow-ups Due: [list]

Actions:
• Send thank-you for [interview]
• Prep for [upcoming interview] — research attached
• Apply to 2 new roles
```

---

## Storage

**Location:** `~/.openclaw/workspace/interviews/`

```
interviews/
├── companies/
│   ├── keyrock-operations-manager.json
│   ├── wintermute-trading-desk.json
│   └── ...
├── question_banks/
│   ├── operations-manager.md
│   ├── trading-desk.md
│   └── crypto-operations.md
├── salary_data/
│   ├── sydney-2026.json
│   └── singapore-2026.json
└── templates/
    ├── thank-you-email.txt
    ├── follow-up-email.txt
    └── negotiation-script.txt
```

---

## Salary Benchmarks (Sydney 2026)

| Role | Base | Bonus | Total |
|------|------|-------|-------|
| Operations Manager (Crypto) | $150k-200k | 20-40% | $180k-280k |
| Senior Operations | $180k-240k | 30-50% | $230k-360k |
| Trading/Dealer | $200k-280k | 50-100% | $300k-560k |
| Quantitative Analyst | $180k-250k | 40-80% | $250k-450k |

*Sources: Glassdoor, Levels.fyi, recruiter intel, industry contacts*

---

## Negotiation Notes

### Dibs's Position
- Current: $150k (dying firm)
- Target: $200k+ with bonus
- Walk-away: $180k base minimum
- Must-have: Career path to trading
- Nice-to-have: WFH flexibility

### Negotiation Script
```
"I'm excited about this opportunity. Based on my 5 years in crypto operations 
and my technical skills in Python and prime brokerage, I was expecting a base 
in the $200-220k range. Is there flexibility there?"
```

---

*Skill version: 1.0 | Created: March 15, 2026*
