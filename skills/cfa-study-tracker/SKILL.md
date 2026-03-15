---
name: cfa-study-tracker
description: Tracks Dibs's CFA Level I study progress across 10 topics. Records quiz scores, time spent, and mastery levels. Generates progress reports and identifies weak areas needing focus. Integrates with Daily 5 quiz system.
user-invocable: true
---

# CFA Study Tracker Skill

## Purpose

Dibs is studying for CFA Level I. This skill tracks:

- 10 curriculum topics (Ethics → Portfolio Management)
- Quiz scores and accuracy trends
- Time spent per topic
- Mastery levels (Not Started → In Progress → Proficient → Mastered)
- Weak areas needing review

---

## CFA Level I Topics (10)

| # | Topic | Weight | Status |
|---|-------|--------|--------|
| 1 | Ethical & Professional Standards | 15-20% | 🔄 Rotating |
| 2 | Quantitative Methods | 8-12% | 🔄 Rotating |
| 3 | Economics | 8-12% | 🔄 Rotating |
| 4 | Financial Reporting & Analysis | 13-17% | 🔄 Rotating |
| 5 | Corporate Issuers | 8-12% | 🔄 Rotating |
| 6 | Equity Investments | 10-12% | 🔄 Rotating |
| 7 | Fixed Income | 10-12% | 🔄 Rotating |
| 8 | Derivatives | 5-8% | 🔄 Rotating |
| 9 | Alternative Investments | 5-8% | 🔄 Rotating |
| 10 | Portfolio Management | 5-8% | 🔄 Rotating |

---

## Quick Commands

### Log quiz results
```bash
python3 ~/.openclaw/workspace/skills/cfa-study-tracker/scripts/log_quiz.py \
  --topic "Equity Investments" \
  --questions 5 \
  --correct 4 \
  --time-minutes 8 \
  --source "Daily 5 Batch 10"
```

### Update topic status
```bash
python3 ~/.openclaw/workspace/skills/cfa-study-tracker/scripts/update_topic.py \
  --topic "Quantitative Methods" \
  --status "Proficient" \
  --hours-studied 12
```

### View progress dashboard
```bash
python3 ~/.openclaw/workspace/skills/cfa-study-tracker/scripts/dashboard.py
```

### Identify weak areas
```bash
python3 ~/.openclaw/workspace/skills/cfa-study-tracker/scripts/weak_areas.py
```

### Generate weekly study report
```bash
python3 ~/.openclaw/workspace/skills/cfa-study-tracker/scripts/weekly_report.py
```

---

## Data Structure

### Topic Progress
```json
{
  "topic": "Equity Investments",
  "topic_number": 6,
  "exam_weight": "10-12%",
  "status": "In Progress",
  "hours_studied": 8.5,
  "quizzes_taken": 3,
  "total_questions": 15,
  "correct_answers": 11,
  "accuracy_percent": 73.3,
  "mastery_level": 2,
  "last_studied": "2026-03-15",
  "formulas_mastered": ["GGM", "P/E ratio", "DCF"],
  "formulas_struggling": ["Multi-stage DDM", "EV/EBITDA"]
}
```

### Quiz Log Entry
```json
{
  "quiz_id": 42,
  "date": "2026-03-15",
  "topic": "Equity Investments",
  "source": "Daily 5 Batch 10",
  "questions": 5,
  "correct": 4,
  "accuracy": 80.0,
  "time_minutes": 8,
  "wrong_questions": [
    {
      "concept": "Multi-stage dividend discount model",
      "user_answer": "B",
      "correct_answer": "C"
    }
  ]
}
```

---

## Mastery Levels

| Level | Name | Criteria |
|-------|------|----------|
| 0 | Not Started | No study time logged |
| 1 | In Progress | < 5 hours OR accuracy < 70% |
| 2 | Developing | 5-10 hours AND accuracy 70-80% |
| 3 | Proficient | 10-15 hours AND accuracy 80-90% |
| 4 | Mastered | 15+ hours AND accuracy > 90% |

---

## Astra's Protocol

### After Daily 5 quiz

Extract quiz data from Daily 5 report and log it:
```
Daily 5 Batch [N] — [Topic]
Questions: 5
Correct: [X]
Wrong: [concepts]
```

### Weekly Check-in (Sundays)

Generate dashboard showing:
- Topics at each mastery level
- Average accuracy per topic
- Total study hours this week
- Recommended focus areas

### When Dibs mentions CFA study

Ask:
1. Which topic?
2. How long did you study?
3. Any formulas or concepts giving trouble?

Update topic progress immediately.

---

## Storage

**Location:** `~/.openclaw/workspace/cfa/`

```
cfa/
├── topics/
│   ├── 01_ethics.json
│   ├── 02_quant.json
│   ├── ...
│   └── 10_portfolio_mgmt.json
├── quizzes/
│   ├── 2026-03-15_quiz_001.json
│   └── ...
├── dashboard.html
└── progress.csv
```

---

## Integration with Daily 5

Daily 5 includes CFA content:
- Rotating topic each day (sequential through 10)
- 5-question quiz per report
- Formula spotlights
- Worked examples

This skill tracks:
- Quiz scores from Daily 5
- Time spent per topic
- Mastery progression

---

## Study Recommendations

### If accuracy < 70% on a topic
- Re-read curriculum summary
- Do additional practice questions
- Review wrong answers carefully

### If accuracy 70-80%
- Continue regular practice
- Focus on weak sub-topics
- Drill formulas

### If accuracy > 80%
- Maintain with periodic review
- Move focus to weaker topics
- Practice exam conditions

---

## Progress Tracking

**Current:** Rotating through topics via Daily 5 (Batch 10 = Equity Investments)
**Goal:** All topics at Proficient or Mastered before exam
**Timeline:** TBD based on exam date

---

*Skill version: 1.0 | Created: March 15, 2026*
