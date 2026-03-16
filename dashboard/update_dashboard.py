#!/usr/bin/env python3
"""
Dashboard Update Script
Updates the daily dashboard with new entries for each day.
Usage: python update_dashboard.py
"""

from datetime import datetime, timedelta
import re
import os

def get_dashboard_path():
    """Get the absolute path to dashboard directory."""
    return os.path.join(os.path.dirname(__file__), 'index.html')

def get_today_links():
    """Generate today's links based on current date."""
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    formatted_date = today.strftime('%A, %B %-d, %Y')
    
    links = f'''
                    <div class="link-item">
                        <div class="link-icon">📊</div>
                        <div class="link-details">
                            <a href="https://astrasyd59-cloud.github.io/empire-command-center/daily5/{date_str}.html" class="link-title">Daily 5 + 1 + 1 Report</a>
                            <div class="link-desc">{formatted_date} market briefing</div>
                        </div>
                        <span class="link-arrow">→</span>
                    </div>
'''
    return links, formatted_date, date_str

def add_new_day():
    """Add a new day section to the dashboard."""
    dashboard_path = get_dashboard_path()
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    today_links, formatted_date, date_str = get_today_links()
    
    # Check if today already exists
    if f'📅 {formatted_date}' in content:
        print(f"⚠️  {formatted_date} already exists in dashboard")
        return
    
    # Create new day section
    new_day_section = f'''        <!-- {formatted_date.upper()} -->
        <div class="day-section">
            <div class="day-header">
                <span class="day-title">📅 {formatted_date}</span>
                <span class="day-badge">TODAY</span>
            </div>
            <div class="day-content">
                <div class="link-grid">
{today_links}
                </div>
                
                <div style="margin-top: 1.5rem;">
                    <h4 style="color: var(--accent-orange); margin-bottom: 0.75rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">Today's Tasks</h4>
                    <ul class="task-list">
                        <li class="task-item">
                            <div class="task-check"></div>
                            <span class="task-text">📚 Reading — 10 pages</span>
                        </li>
                        <li class="task-item">
                            <div class="task-check"></div>
                            <span class="task-text">🎯 Mission progress</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
'''
    
    # Find the position to insert (after the pinned note, before the first day section)
    insert_marker = '<!-- TODAY\'S SECTION -->'
    if insert_marker in content:
        # Replace TODAY marker with PAST badge for previous today
        content = content.replace('class="day-badge today"', 'class="day-badge"')
        content = content.replace(insert_marker, f'{insert_marker}\n{new_day_section}')
    else:
        # Insert after the pinned note
        pinned_end = '</div>\n        \n        <!-- '
        content = content.replace(pinned_end, f'{new_day_section}\n        <!-- ', 1)
    
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Added {formatted_date} to dashboard")

def add_adhoc_link(title, url, description=""):
    """Add an ad-hoc link to today's section."""
    dashboard_path = get_dashboard_path()
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    today = datetime.now().strftime('%A, %B %-d, %Y')
    
    # Find today's section
    today_marker = f'📅 {today}'
    if today_marker not in content:
        print(f"⚠️  {today} section not found. Run add_new_day() first.")
        return
    
    # Create new link item
    new_link = f'''                    <div class="link-item">
                        <div class="link-icon">🔗</div>
                        <div class="link-details">
                            <a href="{url}" class="link-title">{title}</a>
                            <div class="link-desc">{description}</div>
                        </div>
                        <span class="link-arrow">→</span>
                    </div>
'''
    
    # Insert after the link-grid div in today's section
    # This is a simple approach - find the first link-grid after today's header
    pattern = rf'(📅 {today}.*?<div class="link-grid">)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + '\n' + new_link + content[insert_pos:]
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Added link: {title}")
    else:
        print("⚠️  Could not find insertion point")

def add_voice_note(transcription, time_str=None):
    """Add a voice note transcription to today's section."""
    dashboard_path = get_dashboard_path()
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    today = datetime.now().strftime('%A, %B %-d, %Y')
    time_str = time_str or datetime.now().strftime('%I:%M %p')
    
    voice_note = f'''
                <div class="voice-note">
                    <div class="voice-label">🎙️ Voice Note — {time_str}</div>
                    <div class="voice-text">"{transcription}"</div>
                </div>
'''
    
    # Find today's section end and insert before it
    today_marker = f'📅 {today}'
    if today_marker in content:
        # Find the closing of today's day-content div
        pattern = rf'(📅 {today}.*?)(</div>\s*</div>\s*<!-- )'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Insert before the last two </div>
            insert_pos = match.start(2)
            content = content[:insert_pos] + voice_note + content[insert_pos:]
            
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Added voice note at {time_str}")
        else:
            print("⚠️  Could not find voice note insertion point")
    else:
        print(f"⚠️  {today} section not found")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'new-day':
            add_new_day()
        elif command == 'link' and len(sys.argv) >= 4:
            add_adhoc_link(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
        elif command == 'voice' and len(sys.argv) >= 3:
            time_str = sys.argv[3] if len(sys.argv) > 3 else None
            add_voice_note(sys.argv[2], time_str)
        else:
            print("Usage:")
            print("  python update_dashboard.py new-day")
            print("  python update_dashboard.py link 'Title' 'URL' 'Description'")
            print("  python update_dashboard.py voice 'Transcription' 'Time'")
    else:
        # Default: add new day
        add_new_day()
