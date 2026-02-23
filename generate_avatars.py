#!/usr/bin/env python3
"""
Pixel - AI Image Generation Specialist
Generate 5 Astra avatar concepts using DALL-E 3 (using urllib - no external deps)
"""

import os
import json
import time
import urllib.request
import ssl

# Avatar definitions
avatars = [
    {
        "name": "astra-avatar-1.png",
        "title": "Minimalist Blade",
        "prompt": "Minimalist line-art dagger icon, clean geometric dagger silhouette, smooth purple (#2E1A47) to pink (#D4A5A5) gradient fill, flat vector style, centered composition, luxury tech aesthetic, digital art, app icon format, solid background, crisp edges, professional design"
    },
    {
        "name": "astra-avatar-2.png",
        "title": "Celestial Weapon",
        "prompt": "Abstract glowing crystal dagger, geometric facets, neon cyan (#00D4FF) and gold (#FFD700) glow effects, dark navy blue (#0A0E27) background, futuristic sacred geometry patterns, ethereal weapon, digital art, sci-fi fantasy aesthetic, app icon, centered, luminous"
    },
    {
        "name": "astra-avatar-3.png",
        "title": "Feminine + Sharp",
        "prompt": "Minimalist feminine silhouette portrait, elegant woman's profile with flowing hair that transforms into abstract blade shapes, warm coral (#E8A87C) to cream (#FDF6F0) gradient, empowering elegant pose, boho-luxe aesthetic, soft and sharp contrast, digital art, app icon, centered composition"
    },
    {
        "name": "astra-avatar-4.png",
        "title": "Hindu Mandala",
        "prompt": "Minimalist circular mandala design with subtle dagger at the center, intricate geometric patterns inspired by Hindu sacred art, gold (#D4AF37) and bronze (#CD7F32) accents on deep navy background (#0F172A), spiritual modern aesthetic, perfectly circular format ideal for avatars, sacred geometry, balanced symmetry, digital art, clean and elegant"
    },
    {
        "name": "astra-avatar-5.png",
        "title": "Gen Z Chill",
        "prompt": "Stylized kawaii dagger emoji, soft pastel lavender (#C8B6FF) to mint (#B8E0D2) to pink (#FFC8DD) gradient, Y2K aesthetic, cute sparkles and stars around, playful and fun, rounded soft edges, kawaii illustration style, digital art, app icon, centered, trendy gen z vibe"
    }
]

output_dir = "/home/astra/.openclaw/workspace/avatars"
results = []

print("🎨 Pixel - Astra Avatar Generator")
print("=" * 50)
print(f"Output directory: {output_dir}")
print()

# Check API key
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    # Try to get from openclaw auth
    import subprocess
    try:
        result = subprocess.run(["openclaw", "auth", "get", "openai"], 
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            api_key = result.stdout.strip()
            print("✅ API Key retrieved from openclaw auth")
    except Exception as e:
        print(f"Could not get auth: {e}")

if not api_key:
    print("❌ ERROR: OPENAI_API_KEY not found in environment or auth!")
    exit(1)

print(f"✅ API Key available (length: {len(api_key)} chars)")
print()

def generate_image(prompt, api_key):
    """Generate image using OpenAI DALL-E 3 API via urllib"""
    url = "https://api.openai.com/v1/images/generations"
    
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "size": "1024x1024",
        "quality": "standard",
        "n": 1
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    # Create SSL context that doesn't verify certs (for compatibility)
    ssl_context = ssl.create_default_context()
    
    with urllib.request.urlopen(req, context=ssl_context, timeout=120) as response:
        return json.loads(response.read().decode('utf-8'))

def download_image(url, filepath):
    """Download image from URL"""
    ssl_context = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    with urllib.request.urlopen(req, context=ssl_context, timeout=60) as response:
        with open(filepath, 'wb') as f:
            f.write(response.read())
    return True

# Generate each avatar
for i, avatar in enumerate(avatars, 1):
    print(f"[{i}/5] Generating: {avatar['title']}")
    print(f"      File: {avatar['name']}")
    
    try:
        response = generate_image(avatar['prompt'], api_key)
        
        image_url = response['data'][0]['url']
        revised_prompt = response['data'][0].get('revised_prompt', 'N/A')
        
        # Download the image
        file_path = os.path.join(output_dir, avatar['name'])
        download_image(image_url, file_path)
        
        print(f"      ✅ Saved to: {file_path}")
        results.append({
            "avatar": avatar,
            "success": True,
            "path": file_path,
            "revised_prompt": revised_prompt
        })
        
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"      ❌ HTTP Error {e.code}: {error_body}")
        results.append({
            "avatar": avatar,
            "success": False,
            "error": f"HTTP {e.code}: {error_body}"
        })
    except Exception as e:
        print(f"      ❌ Error: {e}")
        results.append({
            "avatar": avatar,
            "success": False,
            "error": str(e)
        })
    
    print()
    time.sleep(2)  # Rate limiting between requests

# Print summary
print("=" * 50)
print("📊 GENERATION SUMMARY")
print("=" * 50)

for r in results:
    status = "✅" if r['success'] else "❌"
    print(f"{status} {r['avatar']['name']}: {r['avatar']['title']}")
    if r['success']:
        print(f"   Path: {r['path']}")
        print(f"   Revised prompt: {r['revised_prompt'][:120]}...")
    else:
        print(f"   Error: {r.get('error', 'Unknown')}")
    print()

# Count successes
successes = sum(1 for r in results if r['success'])
print(f"Total: {successes}/{len(avatars)} images generated successfully")
print()

if successes == len(avatars):
    print("🎉 ALL AVATARS GENERATED SUCCESSFULLY!")
else:
    print(f"⚠️  {len(avatars) - successes} avatar(s) failed to generate")
