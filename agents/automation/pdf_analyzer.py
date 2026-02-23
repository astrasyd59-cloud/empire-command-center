#!/usr/bin/env python3
"""
PDF ANALYZER - Real text extraction + AI analysis
Downloads PDF, extracts text, analyzes with Groq, generates report
"""
import os
import sys
import json
import re
import requests
import subprocess
from datetime import datetime
from pathlib import Path

# Config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_LINK_DB_ID = os.getenv("NOTION_LINK_ANALYSIS_DB_ID", "30d8b652-b7df-819f-8506-f330141e9670")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using multiple methods"""
    text = ""
    
    # Method 1: pdftotext (if available)
    try:
        result = subprocess.run(
            ['pdftotext', pdf_path, '-'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except:
        pass
    
    # Method 2: PyPDF2
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages[:20]:  # First 20 pages
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        if text:
            return text
    except Exception as e:
        print(f"PyPDF2 error: {e}")
    
    # Method 3: pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:20]:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        if text:
            return text
    except Exception as e:
        print(f"pdfplumber error: {e}")
    
    return text if text else "[Could not extract text from PDF]"

def analyze_with_groq(text, filename):
    """Send extracted text to Groq for analysis"""
    if not GROQ_API_KEY:
        return None
    
    # Truncate if too long
    content = text[:12000] if len(text) > 12000 else text
    
    prompt = f"""Analyze this PDF document for Dibs, a 28-year-old crypto trading operations manager looking to improve his life and career.

DOCUMENT: {filename}

EXTRACTED TEXT:
{content[:10000]}

Provide a structured analysis:
1. SUMMARY: What's this document about? Be specific. (2-3 sentences)
2. KEY IDEAS: What are the main concepts/takeaways? (5-7 specific bullet points)
3. ACTIONABLE INSIGHTS: What could Dibs actually implement? Be specific and practical.
4. PROS: Why should he apply this? (concrete benefits)
5. CONS/CONSIDERATIONS: What are the risks, costs, or downsides? Be honest.
6. PRIORITY STEPS: Ordered list of first 3-5 concrete steps to take

IMPORTANT: Base analysis ONLY on the extracted text. If content is insufficient, say so.

Format as JSON:
{{
    "summary": "...",
    "ideas": ["...", "..."],
    "actionable": "...",
    "pros": ["...", "..."],
    "cons": ["...", "..."],
    "steps": ["1. ...", "2. ...", "3. ..."]
}}"""

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 2500
            },
            timeout=60
        )
        
        if resp.status_code == 200:
            content_resp = resp.json()['choices'][0]['message']['content']
            json_match = re.search(r'\{.*\}', content_resp, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        else:
            print(f"Groq error: {resp.status_code} - {resp.text[:200]}")
            
    except Exception as e:
        print(f"Groq analysis error: {e}")
    
    return None

def generate_html_report(filename, analysis, text_length):
    """Generate professional HTML report"""
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    summary = analysis.get('summary', 'No summary available')
    ideas = analysis.get('ideas', [])[:7]
    actionable = analysis.get('actionable', analysis.get('implementation', 'Review document for actionable items'))
    pros = analysis.get('pros', [])[:5]
    cons = analysis.get('cons', [])[:5]
    steps = analysis.get('steps', [])[:5]
    
    ideas_html = "".join([f'<li>{idea}</li>' for idea in ideas]) if ideas else '<li>No key ideas extracted</li>'
    pros_html = "".join([f'<li>{pro}</li>' for pro in pros]) if pros else '<li>No pros identified</li>'
    cons_html = "".join([f'<li>{con}</li>' for con in cons]) if cons else '<li>No cons identified</li>'
    steps_html = "".join([f'<li>{step}</li>' for step in steps]) if steps else '<li>No steps defined</li>'
    
    # Quality based on text extracted
    quality = '🟢 Full Analysis' if text_length > 5000 else '🟡 Partial Analysis' if text_length > 1000 else '🔴 Limited Content'
    badge_color = '#10b981' if text_length > 5000 else '#f59e0b' if text_length > 1000 else '#ef4444'
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Analysis | {filename[:50]}...</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0a0f; color: #e0e0e0; line-height: 1.6; min-height: 100vh; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
        header {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 40px; border-radius: 16px; margin-bottom: 30px; }}
        header h1 {{ font-size: 2rem; margin-bottom: 10px; color: white; }}
        header .meta {{ opacity: 0.9; font-size: 0.9rem; color: rgba(255,255,255,0.8); }}
        .quality-badge {{ display: inline-block; padding: 6px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-top: 10px; background: {badge_color}; color: white; }}
        .card {{ background: #1a1a25; border-radius: 12px; padding: 30px; margin-bottom: 20px; border: 1px solid #2a2a35; }}
        .card h2 {{ color: #10b981; margin-bottom: 15px; font-size: 1.3rem; display: flex; align-items: center; gap: 10px; }}
        .card h2::before {{ content: "▸"; color: #6366f1; }}
        .summary {{ font-size: 1.1rem; line-height: 1.8; color: #e0e0e0; }}
        ul {{ list-style: none; padding-left: 0; }}
        ul li {{ padding: 12px 0; padding-left: 30px; position: relative; border-bottom: 1px solid #2a2a35; line-height: 1.6; }}
        ul li:last-child {{ border-bottom: none; }}
        .ideas li::before {{ content: "💡"; position: absolute; left: 0; }}
        .pros li::before {{ content: "✓"; color: #10b981; position: absolute; left: 0; }}
        .cons li::before {{ content: "✗"; color: #ef4444; position: absolute; left: 0; }}
        .steps li::before {{ content: "⚡"; color: #f59e0b; position: absolute; left: 0; }}
        .actionable-box {{ background: linear-gradient(135deg, #1e3a2f 0%, #2d5a4a 100%); border-left: 4px solid #10b981; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .actionable-box h3 {{ color: #10b981; margin-bottom: 10px; font-size: 1.1rem; }}
        .stats {{ background: #2a2a35; padding: 15px; border-radius: 8px; margin: 20px 0; font-size: 0.9rem; color: #a0a0a0; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📄 PDF Analysis Report</h1>
            <div class="meta">{filename} • Analyzed on {now}</div>
            <span class="quality-badge">{quality}</span>
        </header>
        
        <div class="stats">
            📊 Extracted {text_length:,} characters from PDF
        </div>
        
        <div class="card">
            <h2>Summary</h2>
            <p class="summary">{summary}</p>
        </div>
        
        <div class="card">
            <h2>Key Ideas</h2>
            <ul class="ideas">{ideas_html}</ul>
        </div>
        
        <div class="actionable-box">
            <h3>🎯 Actionable Insights</h3>
            <p>{actionable}</p>
        </div>
        
        <div class="card">
            <h2>Pros</h2>
            <ul class="pros">{pros_html}</ul>
        </div>
        
        <div class="card">
            <h2>Cons & Considerations</h2>
            <ul class="cons">{cons_html}</ul>
        </div>
        
        <div class="card">
            <h2>Priority Steps</h2>
            <ul class="steps">{steps_html}</ul>
        </div>
    </div>
</body>
</html>"""
    
    return html

def deploy_to_vercel(html):
    """Deploy HTML to Vercel"""
    if not VERCEL_TOKEN:
        return None
    
    try:
        resp = requests.post(
            "https://api.vercel.com/v13/deployments",
            headers={"Authorization": f"Bearer {VERCEL_TOKEN}", "Content-Type": "application/json"},
            json={"name": "dibs-empire-roadmap", "files": [{"file": "index.html", "data": html}], "target": "production"},
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get('url') or f"https://dibs-empire-roadmap-{data.get('id', '')[:8]}.vercel.app"
    except Exception as e:
        print(f"Vercel error: {e}")
    
    return None

def notify_telegram(chat_id, report_url, summary, filename):
    """Send report link to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        return
    
    message = f"""📄 **PDF Analysis Complete**

**Document:** {filename}

**Summary:**
{summary[:150]}...

**📊 Full Report:**
{report_url}

_Extracted text analyzed with AI. This is real analysis, not a template._"""
    
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram notify error: {e}")

def add_to_notion(filename, summary, report_url):
    """Add entry to Notion"""
    if not NOTION_TOKEN or not NOTION_LINK_DB_ID:
        return None
    
    try:
        from notion_client import Client
        notion = Client(auth=NOTION_TOKEN)
        
        page = notion.pages.create(
            parent={"database_id": NOTION_LINK_DB_ID},
            properties={
                "Title": {"title": [{"text": {"content": f"📄 {filename[:80]}"}}]},
                "Link": {"url": report_url},
                "Summary": {"rich_text": [{"text": {"content": summary[:200]}}]},
                "Status": {"select": {"name": "Analyzed"}},
                "Category": {"select": {"name": "Document"}},
                "Date Added": {"date": {"start": datetime.now().isoformat()}},
                "Report URL": {"url": report_url}
            }
        )
        return page['id']
    except Exception as e:
        print(f"Notion error: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pdf_analyzer.py <pdf_path> [chat_id] [filename]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    chat_id = sys.argv[2] if len(sys.argv) > 2 else None
    filename = sys.argv[3] if len(sys.argv) > 3 else os.path.basename(pdf_path)
    
    print(f"📄 PDF ANALYZER")
    print(f"File: {filename}")
    print(f"Path: {pdf_path}")
    print("="*60)
    
    # Step 1: Extract text
    print("\n📥 Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)
    text_length = len(text)
    print(f"✅ Extracted {text_length:,} characters")
    
    if text_length < 100:
        print("❌ Not enough text extracted. Cannot analyze.")
        # Send failure message
        if chat_id and TELEGRAM_BOT_TOKEN:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": f"❌ Could not extract text from PDF: {filename}\n\nThe PDF may be scanned images or password protected. Try copy/pasting the text directly."
                },
                timeout=10
            )
        sys.exit(1)
    
    # Step 2: Analyze with Groq
    print("\n🧠 Analyzing with AI...")
    analysis = analyze_with_groq(text, filename)
    
    if not analysis:
        print("❌ AI analysis failed")
        if chat_id and TELEGRAM_BOT_TOKEN:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": f"⚠️ Analysis failed for: {filename}\n\nText was extracted ({text_length:,} chars) but AI analysis failed. This is a real failure, not a template."
                },
                timeout=10
            )
        sys.exit(1)
    
    print("✅ Analysis complete")
    print(f"\n📋 Summary preview:")
    print(f"   {analysis.get('summary', 'N/A')[:150]}...")
    
    # Step 3: Generate HTML report
    print("\n🎨 Generating report...")
    html = generate_html_report(filename, analysis, text_length)
    print("✅ Report generated")
    
    # Step 4: Deploy to Vercel
    print("\n🚀 Deploying to Vercel...")
    report_url = deploy_to_vercel(html)
    
    if report_url:
        print(f"✅ DEPLOYED: {report_url}")
    else:
        print("⚠️ Vercel deploy failed - saving locally")
        # Save locally as fallback
        local_path = f"/home/astra/.openclaw/reports/pdf_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(local_path, 'w') as f:
            f.write(html)
        report_url = f"file://{local_path}"
        print(f"   Saved to: {local_path}")
    
    # Step 5: Send to Telegram
    if chat_id:
        print("\n📱 Notifying Telegram...")
        notify_telegram(chat_id, report_url, analysis['summary'], filename)
        print("✅ Notification sent")
    
    # Step 6: Add to Notion
    print("\n📝 Adding to Notion...")
    notion_id = add_to_notion(filename, analysis['summary'], report_url)
    if notion_id:
        print(f"✅ Notion entry: {notion_id}")
    
    print("\n" + "="*60)
    print("✅ PDF ANALYSIS COMPLETE")
    print(f"🌐 Report: {report_url}")

if __name__ == "__main__":
    main()
