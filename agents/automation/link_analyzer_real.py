#!/usr/bin/env python3
"""
REAL LINK ANALYSIS - Content Extraction + Analysis
Downloads content, extracts text, analyzes with Groq
"""
import os
import re
import json
import requests
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_LINK_DB_ID = os.getenv("NOTION_LINK_ANALYSIS_DB_ID", "30d8b652-b7df-819f-8506-f330141e9670")

def extract_domain(url):
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    except:
        return "unknown"

def download_content(url):
    """
    Download and extract content based on URL type
    Returns: (content_type, extracted_text, title)
    """
    domain = extract_domain(url)
    
    # YouTube videos
    if 'youtube.com' in domain or 'youtu.be' in domain:
        return extract_youtube_info(url)
    
    # PDF files
    if url.endswith('.pdf') or '/pdf' in url.lower():
        return download_and_extract_pdf(url)
    
    # Regular web pages
    return scrape_webpage(url)

def extract_youtube_info(url):
    """Get YouTube title and transcript if available"""
    try:
        # Try to get title via oEmbed
        video_id = None
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0]
        elif 'v=' in url:
            video_id = url.split('v=')[-1].split('&')[0]
        
        if video_id:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            resp = requests.get(oembed_url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                title = data.get('title', 'YouTube Video')
                return ('youtube', f"Title: {title}\n\n[Video content - transcript extraction requires additional setup]", title)
    except:
        pass
    return ('youtube', '[Could not extract YouTube content]', 'YouTube Video')

def download_and_extract_pdf(url):
    """Download PDF and extract text"""
    try:
        # Download PDF
        resp = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code != 200:
            return ('pdf', f'[Could not download PDF: {resp.status_code}]', 'PDF Document')
        
        # Save temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(resp.content)
            tmp_path = tmp.name
        
        # Try to extract text using pdftotext if available
        try:
            result = subprocess.run(
                ['pdftotext', tmp_path, '-'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout:
                text = result.stdout[:15000]  # Limit to 15k chars
                os.unlink(tmp_path)
                return ('pdf', text, 'PDF Document')
        except:
            pass
        
        # Fallback: try PyPDF2
        try:
            import PyPDF2
            with open(tmp_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages[:10]:  # First 10 pages
                    text += page.extract_text() + "\n"
                os.unlink(tmp_path)
                return ('pdf', text[:15000], 'PDF Document')
        except:
            pass
        
        os.unlink(tmp_path)
        return ('pdf', '[PDF downloaded but text extraction failed]', 'PDF Document')
        
    except Exception as e:
        return ('pdf', f'[PDF extraction error: {str(e)}]', 'PDF Document')

def scrape_webpage(url):
    """Scrape article content from webpage"""
    try:
        resp = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        if resp.status_code != 200:
            return ('web', f'[Could not fetch page: {resp.status_code}]', 'Web Page')
        
        html = resp.text
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip()[:200] if title_match else 'Web Page'
        
        # Try to extract main content (article, main, etc.)
        # Remove scripts and styles
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Try article tag first
        article_match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL | re.IGNORECASE)
        if article_match:
            text = article_match.group(1)
        else:
            # Try main tag
            main_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL | re.IGNORECASE)
            if main_match:
                text = main_match.group(1)
            else:
                # Try content div
                text = html
        
        # Strip HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return ('web', text[:15000], title)
        
    except Exception as e:
        return ('web', f'[Scraping error: {str(e)}]', 'Web Page')

def analyze_with_groq_real(content, title, url, content_type):
    """
    Send ACTUAL content to Groq for analysis
    """
    if not GROQ_API_KEY:
        return None
    
    # Truncate content if too long
    content_preview = content[:8000] if len(content) > 8000 else content
    
    prompt = f"""Analyze this {content_type.upper()} content for Dibs, a 28-year-old crypto trading operations manager looking to improve his life and career.

SOURCE: {title}
URL: {url}

CONTENT:
{content_preview}

Provide a structured analysis:
1. SUMMARY: What's this about? Be specific. (2-3 sentences)
2. KEY IDEAS: What are the main concepts/takeaways? (3-5 specific bullet points)
3. ACTIONABLE INSIGHTS: What could Dibs actually implement? Be specific.
4. PROS: Why should he do this? (concrete benefits)
5. CONS/CONSIDERATIONS: What are the risks, costs, or downsides? Be honest.
6. PRIORITY STEPS: Ordered list of first 3 concrete steps to take

IMPORTANT: Base your analysis ONLY on the content provided. If the content is insufficient, say so. Do NOT make up information.

Format as JSON:
{{
    "summary": "...",
    "ideas": ["...", "...", "..."],
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
                "model": "llama-3.3-70b-versatile",  # Current Groq model
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 2000
            },
            timeout=60
        )
        
        if resp.status_code == 200:
            content_resp = resp.json()['choices'][0]['message']['content']
            # Extract JSON
            json_match = re.search(r'\{.*\}', content_resp, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        else:
            print(f"Groq error: {resp.status_code} - {resp.text[:200]}")
            
    except Exception as e:
        print(f"Groq analysis error: {e}")
    
    return None

def analyze_link_real(url, chat_id=None):
    """
    FULL PIPELINE with real content extraction
    """
    print(f"\n{'='*60}")
    print(f"🔍 REAL LINK ANALYSIS")
    print(f"URL: {url}")
    print(f"{'='*60}\n")
    
    # Step 1: Download and extract content
    print("📥 Step 1: Downloading content...")
    content_type, content, title = download_content(url)
    print(f"   ✅ Type: {content_type}")
    print(f"   ✅ Title: {title[:60]}...")
    print(f"   ✅ Content length: {len(content)} chars")
    
    # Check if we got real content
    if len(content) < 100 or '[Could not' in content or '[PDF' in content:
        print(f"   ⚠️ Warning: Limited content extracted")
        print(f"   Content preview: {content[:200]}...")
    
    # Step 2: Analyze with Groq
    print("\n🧠 Step 2: Analyzing with Groq...")
    analysis = analyze_with_groq_real(content, title, url, content_type)
    
    if not analysis:
        print("   ❌ Groq analysis failed")
        # Return honest failure
        return {
            'success': False,
            'error': 'Could not analyze content',
            'title': title,
            'content_type': content_type,
            'content_sample': content[:500]
        }
    
    print("   ✅ Analysis complete")
    print(f"\n📋 SUMMARY:")
    print(f"   {analysis.get('summary', 'N/A')[:150]}...")
    
    # Step 3: Return results
    return {
        'success': True,
        'title': title,
        'url': url,
        'content_type': content_type,
        'analysis': analysis,
        'content_length': len(content),
        'analyzed_at': datetime.now().isoformat()
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        chat_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = analyze_link_real(url, chat_id)
        print("\n" + "="*60)
        print("RESULT:")
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: python3 link_analyzer_real.py <url> [chat_id]")
        print("\nThis script performs REAL content extraction and analysis.")
        print("It downloads PDFs, scrapes web pages, and sends actual content to Groq.")
