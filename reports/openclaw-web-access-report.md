# 🌐 OpenClaw Web Access: Methods, Setup & Best Practices

> **Research Report** | Generated: 2026-02-19  
> **Scope**: Web access methods, browser automation, security considerations, and recommendations for Dibs's use case (React sites, wizards, etc.)

---

## 📋 Executive Summary

OpenClaw provides **three primary methods** for web access:

1. **`web_search`** - Fast API-based web search (Brave/Perplexity)
2. **`web_fetch`** - Static HTML extraction (Readability/Firecrawl)
3. **`browser`** - Full browser automation (Chrome DevTools Protocol + Playwright)

**For Dibs's use case (accessing React sites, wizards, dynamic content)**: The **`browser` tool with the Chrome extension relay** or **managed `openclaw` browser profile** is the **recommended approach**.

---

## 🔍 Web Access Methods Comparison

| Method | JS Execution | Auth/Login | Speed | Complexity | Best For |
|--------|-------------|------------|-------|------------|----------|
| **`web_search`** | ❌ No | ❌ No | ⚡ Fast | 🟢 Low | Quick lookups, research |
| **`web_fetch`** | ❌ No | ❌ No | ⚡ Fast | 🟢 Low | Static content, articles |
| **`browser` (managed)** | ✅ Yes | ✅ Yes | 🐢 Slower | 🟡 Medium | Dynamic sites, SPAs, forms |
| **`browser` (extension)** | ✅ Yes | ✅ Yes (inherits) | 🐢 Slower | 🟡 Medium | Sites where you're already logged in |
| **Firecrawl fallback** | ✅ Yes (service) | ⚠️ Limited | ⚡ Medium | 🟢 Low | Anti-bot sites |

---

## 📚 Detailed Method Analysis

### 1. `web_search` - API-Based Search

**What it does**: Searches the web via Brave Search API or Perplexity Sonar.

**Providers**:
- **Brave** (default): Fast, structured results (title, URL, snippet)
- **Perplexity**: AI-synthesized answers with citations

**Configuration**:
```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        provider: "brave", // or "perplexity"
        apiKey: "BRAVE_API_KEY_HERE",
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
    },
  },
}
```

**API Key Setup**:
1. Create account at [brave.com/search/api](https://brave.com/search/api/)
2. Choose **"Data for Search"** plan (NOT "Data for AI")
3. Store via: `openclaw configure --section web` or `BRAVE_API_KEY` env var

**Limitations**:
- ❌ No JavaScript execution
- ❌ No login/authentication
- ❌ Can't interact with dynamic content
- Returns only search results, not full page content

**When to use**: Research, finding documentation, quick fact-checking

---

### 2. `web_fetch` - Static Content Extraction

**What it does**: HTTP GET + extracts readable content (HTML → markdown/text).

**Extraction pipeline**:
1. **Readability** (local) - Main content extraction
2. **Firecrawl** (optional, if configured) - Anti-bot extraction
3. **Basic HTML cleanup** (fallback)

**Configuration**:
```json5
{
  tools: {
    web: {
      fetch: {
        enabled: true,
        maxChars: 50000,
        timeoutSeconds: 30,
        readability: true,
        firecrawl: {
          enabled: true,
          apiKey: "FIRECRAWL_API_KEY",
          baseUrl: "https://api.firecrawl.dev",
          onlyMainContent: true,
          maxAgeMs: 86400000, // 1 day cache
        },
      },
    },
  },
}
```

**Firecrawl Benefits**:
- Bot circumvention (`proxy: "auto"` with stealth mode)
- Caching for repeated requests
- Better success rate on protected sites

**Limitations**:
- ❌ No JavaScript execution (can't render React/Vue/Angular SPAs)
- ❌ No interaction (clicking, form submission)
- ❌ No session/login state
- Some sites block or return different content

**When to use**: Articles, documentation, static sites, blog posts

---

### 3. `browser` - Full Browser Automation ⭐

**What it does**: Controls a real Chromium browser (Chrome/Brave/Edge) via Chrome DevTools Protocol (CDP) + Playwright.

**Two Modes**:

#### A. **Managed Browser (`openclaw` profile)**
- Dedicated, isolated browser instance
- Named profile "openclaw" (orange accent)
- Separate user data directory
- Deterministic tab control
- No extension required

#### B. **Chrome Extension Relay (`chrome` profile)**
- Uses your existing Chrome installation
- Extension attaches to active tab via toolbar button
- Inherits your logged-in sessions
- Manual attach/detach (security feature)

**Setup - Managed Browser**:
```json5
{
  browser: {
    enabled: true,
    defaultProfile: "openclaw",
    executablePath: "/usr/bin/google-chrome-stable", // auto-detected if not set
    headless: false,  // set true for headless
    noSandbox: false, // set true for Docker/some Linux setups
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
    },
  },
}
```

**Setup - Chrome Extension**:
```bash
# 1. Install extension
openclaw browser extension install

# 2. Get path and load in Chrome
openclaw browser extension path
# → Load unpacked in chrome://extensions

# 3. Pin extension, click to attach
```

**Browser Capabilities**:

| Action | Description |
|--------|-------------|
| `status/start/stop` | Browser lifecycle |
| `tabs/open/focus/close` | Tab management |
| `snapshot` | Capture UI tree (AI or ARIA) |
| `screenshot` | Full-page or element capture |
| `navigate` | Go to URL |
| `act` | Click, type, press, hover, drag, select, fill |
| `evaluate` | Run JavaScript in page |
| `wait` | Wait for element, text, URL, load state |
| `cookies/storage` | Manage state |
| `upload/download` | File handling |
| `pdf` | Generate PDF |

**Snapshot Types**:
- **AI snapshot** (default): Numeric refs (`ref=12`), best for AI interaction
- **ARIA snapshot**: Accessibility tree, inspection only
- **Role snapshot**: Role refs (`ref=e12`), stable across similar pages

**Example Workflow**:
```javascript
// 1. Start browser
await browser({ action: "start" });

// 2. Navigate
await browser({ action: "navigate", targetUrl: "https://example.com" });

// 3. Get snapshot
const snapshot = await browser({ action: "snapshot" });
// Returns: "[ref=1] button: Submit"

// 4. Interact
await browser({
  action: "act",
  request: { kind: "click", ref: "1" }
});

// 5. Screenshot
await browser({ action: "screenshot" });
```

---

## 🛠️ Setup Guide for Dibs's Use Case

### Use Case Requirements
- ✅ Access React sites (JavaScript-heavy SPAs)
- ✅ Navigate wizards/multi-step forms
- ✅ Handle authentication when needed
- ✅ Interact with dynamic content

### Recommended Setup: Chrome Extension Relay

**Why extension relay for Dibs?**
- Inherits existing login sessions (no credential handling needed)
- Uses normal Chrome (familiar, bookmarks available)
- Manual control over which tabs agent can access
- Best for sites with existing accounts

**Step-by-Step Setup**:

```bash
# 1. Install extension
openclaw browser extension install

# 2. Get install path
openclaw browser extension path
# Example output: /home/astra/.openclaw/extensions/browser-relay

# 3. In Chrome:
#    - Go to chrome://extensions
#    - Enable "Developer mode"
#    - Click "Load unpacked"
#    - Select the path from step 2
#    - Pin the extension

# 4. Configure OpenClaw to use chrome profile
openclaw config set browser.defaultProfile "chrome"

# 5. Test
openclaw browser --browser-profile chrome status
```

**Usage Pattern**:
```bash
# When you want agent to control a tab:
# 1. Open the site in Chrome
# 2. Click the OpenClaw extension icon (badge shows ON)
# 3. Ask agent to interact with the page

# Example commands:
openclaw browser --browser-profile chrome snapshot
openclaw browser --browser-profile chrome act click --ref 12
```

### Alternative: Managed Browser Profile

**When to use managed instead**:
- You want complete isolation from personal browsing
- Running on a server/headless environment
- Need multiple simultaneous browser sessions
- Don't need personal login sessions

**Setup**:
```bash
# 1. Configure
openclaw config set browser.defaultProfile "openclaw"

# 2. Start browser
openclaw browser start

# 3. Navigate and login manually (first time)
openclaw browser open https://example.com

# 4. Then agent can control
openclaw browser snapshot
```

---

## 🔒 Security Considerations

### Browser Control Risks

| Risk | Mitigation |
|------|------------|
| **Account compromise** | Use dedicated browser profile; avoid attaching to personal banking/email tabs |
| **Prompt injection via web** | Untrusted web content can try to manipulate the agent |
| **Credential exposure** | Manual login only; never give credentials to the model |
| **Session hijacking** | Keep Gateway/node on tailnet-only; avoid public exposure |
| **Data exfiltration** | Use `allowHostControl: false` for sandboxed agents |

### Best Practices

```json5
{
  // Secure browser configuration
  browser: {
    enabled: true,
    defaultProfile: "openclaw", // Use isolated profile
    // Don't expose to LAN/public
  },
  
  // For sandboxed agents
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        browser: {
          allowHostControl: false, // Sandboxed agents can't touch host browser
        },
      },
    },
  },
  
  // Gateway security
  gateway: {
    bind: "loopback", // Never bind to 0.0.0.0
    auth: {
      mode: "token",
      token: "long-random-token",
    },
  },
}
```

### Tool Policy Recommendations

```json5
{
  tools: {
    // For high-security agents
    deny: ["browser", "web_fetch", "web_search"],
    
    // For trusted agents with web access
    allow: ["browser", "web_fetch", "web_search"],
    
    // Disable JavaScript evaluation if not needed
    browser: {
      evaluateEnabled: false,
    },
  },
}
```

---

## ⚠️ Limitations & Workarounds

### Browser Tool Limitations

| Limitation | Workaround |
|------------|------------|
| **Anti-bot detection** | Use Firecrawl, manual login, or stealth plugins |
| **2FA/MFA prompts** | Complete manually, then let agent continue |
| **CAPTCHAs** | Manual completion required (agent can't solve) |
| **File downloads** | Use `download` action; files go to temp directory |
| **Mobile-only sites** | Use `set device` to emulate mobile |
| **Ref stability** | Refs change on navigation; re-snapshot after page changes |

### Linux-Specific Issues

**Snap Chromium doesn't work** - Use Google Chrome instead:
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

# Then configure:
{
  browser: {
    executablePath: "/usr/bin/google-chrome-stable",
    headless: true,
    noSandbox: true,
  }
}
```

---

## 📊 Real-World Usage Patterns

### Pattern 1: Research Assistant
```javascript
// Search → Fetch → Summarize
const search = await web_search({ query: "React best practices 2025", count: 5 });
const article = await web_fetch({ url: search.results[0].url });
// Agent summarizes article
```

### Pattern 2: Form Automation
```javascript
// For Dibs's wizard scenario
await browser({ action: "navigate", targetUrl: "https://wizard.example.com" });
const snap = await browser({ action: "snapshot", refs: "aria" });
// Agent fills form step-by-step
await browser({
  action: "act",
  request: { kind: "fill", fields: [
    { ref: "3", type: "text", value: "John Doe" },
    { ref: "5", type: "select", value: "Option A" },
  ]}
});
await browser({ action: "act", request: { kind: "click", ref: "7" } }); // Next button
```

### Pattern 3: Monitoring/Dashboard
```javascript
// Periodic screenshot of React dashboard
await browser({ action: "navigate", targetUrl: "https://dashboard.example.com" });
await browser({ action: "wait", request: { selector: ".dashboard-loaded" } });
await browser({ action: "screenshot", fullPage: true });
```

---

## 🎯 Recommendation for Dibs

### Primary Recommendation: Chrome Extension Relay

**Setup**:
1. Install and load the OpenClaw Chrome extension
2. Set `browser.defaultProfile: "chrome"`
3. When needing agent help:
   - Navigate to the React site/wizard in Chrome
   - Click the extension icon to attach
   - Ask agent to interact

**Why this fits Dibs's needs**:
- ✅ Full JavaScript support for React SPAs
- ✅ Can navigate multi-step wizards
- ✅ Inherits login sessions (no credential sharing)
- ✅ Manual control over which tabs agent accesses
- ✅ Can handle dynamic content, modals, async loading

### Alternative: Hybrid Approach

```javascript
// Try web_fetch first (fast), fall back to browser if needed
try {
  const content = await web_fetch({ url: "https://example.com" });
  // Process static content
} catch (e) {
  // Site requires JS - use browser
  await browser({ action: "navigate", targetUrl: "https://example.com" });
  const snap = await browser({ action: "snapshot" });
  // Process dynamic content
}
```

---

## 📚 Additional Resources

### Documentation Links
- [Browser Tool Docs](https://openclaw.ai/tools/browser) - Complete browser automation reference
- [Chrome Extension Setup](https://openclaw.ai/tools/chrome-extension) - Extension installation guide
- [Web Tools](https://openclaw.ai/tools/web) - web_search and web_fetch details
- [Firecrawl Integration](https://openclaw.ai/tools/firecrawl) - Anti-bot extraction
- [Security Guide](https://openclaw.ai/gateway/security) - Security best practices

### CLI Quick Reference
```bash
# Browser control
openclaw browser status
openclaw browser start
openclaw browser open <url>
openclaw browser snapshot
openclaw browser screenshot --full-page
openclaw browser act click --ref 12

# Extension
openclaw browser extension install
openclaw browser extension path

# Configuration
openclaw config set browser.defaultProfile "chrome"
openclaw config set browser.profiles.openclaw.cdpPort 18800
```

---

## 🔧 Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| "Browser disabled" | Set `browser.enabled: true` and restart Gateway |
| "Failed to start Chrome CDP" | On Linux, use Google Chrome (not snap Chromium); set `noSandbox: true` |
| "No tab connected" (extension) | Click the extension icon to attach to a tab |
| "Playwright not available" | Install Playwright: `npx playwright install chromium` |
| Refs not working | Re-snapshot after navigation; refs are not stable across pages |
| White screen (canvas) | Check bind mode; use hostname not localhost for LAN/tailnet |

---

## ✅ Summary Checklist for Dibs

- [ ] Install OpenClaw Chrome extension (`openclaw browser extension install`)
- [ ] Load extension in Chrome (chrome://extensions → Developer mode → Load unpacked)
- [ ] Set `browser.defaultProfile: "chrome"` in config
- [ ] Pin extension toolbar button for easy access
- [ ] Test with: `openclaw browser --browser-profile chrome snapshot`
- [ ] For React sites: Navigate in Chrome → Click extension → Ask agent to interact
- [ ] Review security settings (bind: loopback, auth enabled)

---

*Report compiled by Chitra (Researcher Agent)*  
*Sources: OpenClaw documentation v{version}, local skill files, configuration examples*
