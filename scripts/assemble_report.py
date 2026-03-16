import json
import sqlite3
import sys
import re
from datetime import datetime
from pathlib import Path

# ── PATHS ──────────────────────────────────────────────────────
BASE = Path("/home/astra/.openclaw/workspace")
TEMPLATE = BASE / "daily5/TEMPLATE_v2.html"
OUTPUT = BASE / f"daily5/{datetime.now().strftime('%Y-%m-%d')}.html"
DB_PATH = BASE / "agents/automation/bot_stats.db"
DATA_FILE = BASE / "daily5/today_data.json"

# ── STAGE 2 TIMEOUT GUARD ─────────────────────────────────────
# If today_data.json is missing or > 90 min old, flag stale data
if not DATA_FILE.exists():
    print("[WARN] today_data.json missing — report will use fallback placeholders", file=sys.stderr)
    # Continue with minimal data structure
    d = {
        "date": datetime.now().strftime('%B %d, %Y'),
        "date_short": datetime.now().strftime('%b %d'),
        "date_iso": datetime.now().strftime('%Y-%m-%d'),
        "time_et": "5:55 AM",
        "day_num": 0,
        "tickers_str": "N/A",
        "batch_label": "Fallback",
        "cfa_topic": "N/A",
        "macro": {},
        "progress": {"stocks_done": 0, "sp_pct": 0, "cfa_done": 0, "cfa_pct": 0},
    }
else:
    age_minutes = (datetime.now().timestamp() - DATA_FILE.stat().st_mtime) / 60
    if age_minutes > 90:
        print(f"[WARN] Data is {age_minutes:.0f} min old — may be stale", file=sys.stderr)
    
    with open(DATA_FILE) as f:
        d = json.load(f)

# Check all required keys exist, insert fallback if missing
required = {
    "stock_cards_html": '<div class="asset-card"><div class="asset-body"><p style="color:var(--red);font-family:var(--font-mono);font-size:0.8rem;">⚠️ Stock data unavailable — Stage 2 timeout. Check logs.</p></div></div>',
    "crypto_card_html": '<div class="asset-card crypto-card"><div class="asset-body"><p style="color:var(--red);font-family:var(--font-mono);font-size:0.8rem;">⚠️ Crypto data unavailable — Stage 2 timeout.</p></div></div>',
    "forex_card_html": '<div class="asset-card forex-card"><div class="asset-body"><p style="color:var(--red);font-family:var(--font-mono);font-size:0.8rem;">⚠️ Forex data unavailable — Stage 2 timeout.</p></div></div>',
    "setup_rows_html": '<tr><td colspan="7" style="color:var(--red);font-family:var(--font-mono);">⚠️ Trading setups unavailable</td></tr>',
    "options_card_html": '<div class="options-card"><p style="color:var(--red);font-family:var(--font-mono);font-size:0.8rem;">⚠️ Options section unavailable — Stage 2 timeout.</p></div>',
    "quiz_html": '<div class="quiz-question"><p style="color:var(--red);font-family:var(--font-mono);">⚠️ Quiz unavailable — pre-generation failed.</p></div>',
    "glossary_html": '<div class="term-entry"><p style="color:var(--red);font-family:var(--font-mono);">⚠️ Glossary unavailable — pre-generation failed.</p></div>',
}

missing = [k for k in required if not d.get(k)]
if missing:
    print(f"[WARN] Missing blocks: {missing} — inserting fallback sections", file=sys.stderr)
    for k in missing:
        d[k] = required[k]

# ── LOAD TEMPLATE ──────────────────────────────────────────────
html = TEMPLATE.read_text(encoding="utf-8")

# ── REPLACE ALL PLACEHOLDERS ───────────────────────────────────
replacements = {
    # Header
    "{{DATE}}": d["date"],
    "{{DATE_SHORT}}": d["date_short"],
    "{{TIME}}": d["time_et"],
    "{{DAY_NUM}}": str(d["day_num"]),
    "{{TICKERS}}": d["tickers_str"],
    "{{BATCH}}": d["batch_label"],
    
    # Macro
    "{{SPX}}": d["macro"]["spx"]["val"],
    "{{SPX_DIR}}": d["macro"]["spx"]["dir"],
    "{{SPX_CHG}}": d["macro"]["spx"]["chg"],
    "{{VIX}}": d["macro"]["vix"]["val"],
    "{{VIX_DIR}}": d["macro"]["vix"]["dir"],
    "{{VIX_CHG}}": d["macro"]["vix"]["chg"],
    "{{YIELD10}}": d["macro"]["yield10"]["val"],
    "{{YIELD_DIR}}": d["macro"]["yield10"]["dir"],
    "{{YIELD_CHG}}": d["macro"]["yield10"]["chg"],
    "{{FED_FUNDS}}": d["macro"]["fed_funds"],
    "{{DXY}}": d["macro"]["dxy"]["val"],
    "{{DXY_DIR}}": d["macro"]["dxy"]["dir"],
    "{{DXY_CHG}}": d["macro"]["dxy"]["chg"],
    "{{GOLD}}": d["macro"]["gold"]["val"],
    "{{GOLD_DIR}}": d["macro"]["gold"]["dir"],
    "{{GOLD_CHG}}": d["macro"]["gold"]["chg"],
    
    # Progress
    "{{STOCKS_DONE}}": str(d["progress"]["stocks_done"]),
    "{{SP_PCT}}": str(d["progress"]["sp_pct"]),
    "{{CFA_DONE}}": str(d["progress"]["cfa_done"]),
    "{{CFA_PCT}}": str(d["progress"]["cfa_pct"]),
    "{{CFA_CURRENT_TOPIC}}": d["cfa_topic"],
    
    # Crypto / Forex section labels
    "{{CRYPTO_TICKER}}": d["crypto"]["ticker"],
    "{{FOREX_PAIR}}": d["forex"]["pair"],
    
    # Stock blocks
    "{{STOCK_CARDS}}": d["stock_cards_html"],
    
    # Crypto card
    "{{CRYPTO_CARD}}": d["crypto_card_html"],
    
    # Forex card
    "{{FOREX_CARD}}": d["forex_card_html"],
    
    # Trading setups table rows
    "{{TRADING_TABLE_ROWS}}": d["setup_rows_html"],
    
    # Options section
    "{{OPTIONS_CARD}}": d["options_card_html"],
    
    # Quiz
    "{{QUIZ_QUESTIONS}}": d["quiz_html"],
    
    # Glossary
    "{{GLOSSARY_TERMS}}": d["glossary_html"],
}

for token, value in replacements.items():
    html = html.replace(token, str(value))

# ── VALIDATE — NO UNREPLACED TOKENS ────────────────────────────
remaining = re.findall(r'\{\{[^}]+\}\}', html)
if remaining:
    print(f"[WARN] Unreplaced tokens: {remaining}", file=sys.stderr)

# ── WRITE OUTPUT ───────────────────────────────────────────────
OUTPUT.write_text(html, encoding="utf-8")
print(f"[OK] Report written: {OUTPUT}")
print(f"[OK] Size: {OUTPUT.stat().st_size // 1024}KB")

# ── LOG TO DB ──────────────────────────────────────────────────
con = sqlite3.connect(DB_PATH)
con.execute("""
    INSERT INTO daily_reports (report_date, html_path, status, generated_at)
    VALUES (?, ?, 'success', ?)
    ON CONFLICT(report_date) DO UPDATE SET
        html_path = excluded.html_path,
        status = 'success',
        generated_at = excluded.generated_at
""", (d["date_iso"], str(OUTPUT), datetime.now().isoformat()))
con.commit()
con.close()

print("[OK] Database updated")
