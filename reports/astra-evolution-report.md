# 🧠 Astra Evolution: Skills, LLMs & Future Growth

**Report Date:** February 19, 2026  
**Author:** Chitra (Research Sub-Agent)  
**Owner:** Dibs  
**Status:** 🟢 Ready for Review

---

## 📋 Executive Summary

This report provides a comprehensive analysis of the OpenClaw AI ecosystem and how Astra (the main agent) can evolve to deliver maximum value. The research covers five critical areas:

1. **Skills System** - OpenClaw's extensible capability framework
2. **LLM Provider Landscape** - Optimal model selection for different tasks
3. **Astra Upgrade Paths** - Strategies for agent evolution
4. **Multi-Agent Architecture** - When and how to deploy sub-agents
5. **Tool Integration** - Best practices for APIs and automation

### Key Recommendations for Dibs

| Priority | Recommendation | Impact |
|----------|----------------|--------|
| 🔴 High | Configure multi-agent routing for different contexts (work/personal/family) | Security + Organization |
| 🔴 High | Establish sub-agent defaults for cost-effective background tasks | Cost + Efficiency |
| 🟡 Medium | Curate workspace skills via ClawHub for specialized tasks | Capability Expansion |
| 🟡 Medium | Set up per-agent tool profiles for least-privilege access | Security |
| 🟢 Low | Document personal conventions in TOOLS.md | Consistency |

---

## 1️⃣ Skills System Deep Dive

### What Are Skills?

Skills are **AgentSkills-compatible** folders that teach Astra how to use tools effectively. Each skill contains:
- `SKILL.md` - YAML frontmatter + usage instructions
- Supporting files (configs, scripts, assets)

### Skills Loading Hierarchy

Skills are loaded from three locations with the following precedence:

```
<workspace>/skills (HIGHEST)
    ↓
~/.openclaw/skills (managed/local)
    ↓
bundled skills (LOWEST - shipped with install)
```

### Skill Gating & Requirements

Skills can declare requirements in metadata:

```yaml
---
name: gemini-image-gen
description: Generate images via Gemini
metadata:
  {
    "openclaw":
      {
        "requires": { 
          "bins": ["uv"],           # Required binaries on PATH
          "env": ["GEMINI_API_KEY"], # Required environment variables
          "config": ["browser.enabled"] # Required config paths
        },
        "primaryEnv": "GEMINI_API_KEY",
        "os": ["darwin", "linux"]   # Platform restrictions
      }
  }
---
```

### Key Skill Commands

| Command | Purpose |
|---------|---------|
| `clawhub install <skill>` | Install a skill from ClawHub registry |
| `clawhub update --all` | Update all installed skills |
| `clawhub sync --all` | Scan + publish local skills |
| `clawhub search "query"` | Search skills by keywords |

### Best Practices for Skills

1. **Security First**: Treat third-party skills as untrusted code - read before enabling
2. **Workspace Isolation**: Use workspace skills for agent-specific capabilities
3. **Shared Skills**: Place common skills in `~/.openclaw/skills` for multi-agent sharing
4. **Version Control**: Use `clawhub sync` to backup custom skills
5. **Auto-Refresh**: Skills are snapshotted per session; new sessions pick up changes

---

## 2️⃣ LLM Provider Comparison Matrix

### Provider Overview

| Provider | Best For | Auth Method | Cost Level | Speed |
|----------|----------|-------------|------------|-------|
| **Anthropic Claude** | Complex reasoning, coding, analysis | API Key / Token | $$$ | Medium |
| **OpenAI GPT** | General purpose, Codex for coding | API Key / OAuth | $$$ | Fast |
| **Moonshot Kimi** | Long context (256k), Chinese content | API Key | $$ | Fast |
| **Kimi Coding** | Code-specific tasks | API Key | $$ | Fast |
| **Google Gemini** | Multimodal, vision tasks | API Key / OAuth | $$ | Fast |
| **Groq** | Ultra-low latency inference | API Key | $ | Very Fast |
| **MiniMax** | Cost-effective sub-agents | API Key | $ | Fast |
| **Ollama** | Local/privacy-first inference | None (local) | Free | Hardware-dependent |
| **Venice AI** | Privacy-focused, uncensored | API Key | $$ | Fast |

### Detailed Provider Analysis

#### 🏆 Anthropic Claude (Recommended for Primary Agent)

**Models:**
- `anthropic/claude-opus-4-6` - Best overall reasoning
- `anthropic/claude-sonnet-4-5` - Balanced speed/capability
- `anthropic/claude-haiku-3-5` - Fast, lightweight

**Strengths:**
- Exceptional code understanding and generation
- Long context handling
- Strong reasoning and analysis
- Excellent instruction following

**Best For:**
- Primary agent for complex tasks
- Code review and architecture decisions
- Multi-step reasoning problems

**Config:**
```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-sonnet-4-5" }
    }
  }
}
```

---

#### ⚡ Moonshot Kimi / Kimi Coding

**Models:**
- `moonshot/kimi-k2.5` - General purpose
- `moonshot/kimi-k2-thinking` - Reasoning mode
- `kimi-coding/k2p5` - Code-optimized

**Strengths:**
- 256K context window (excellent for large codebases)
- Strong Chinese language support
- Fast inference
- Cost-effective

**Best For:**
- Large document analysis
- Chinese content processing
- Cost-effective coding assistance

**Config:**
```json5
{
  env: { MOONSHOT_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "moonshot/kimi-k2.5" }
    }
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "kimi-k2.5",
            name: "Kimi K2.5",
            contextWindow: 256000,
            maxTokens: 8192
          }
        ]
      }
    }
  }
}
```

---

#### 🚀 OpenAI

**Models:**
- `openai/gpt-5.1-codex` - Code-optimized
- `openai/gpt-5.2` - General purpose
- `openai/gpt-5.3-codex` - Advanced coding

**Strengths:**
- Broad capability spectrum
- Strong tool use
- Codex integration for VS Code workflows

**Best For:**
- General purpose tasks
- VS Code integration
- Tool-heavy workflows

---

#### 💨 Groq (Speed Champion)

**Strengths:**
- Sub-100ms latency
- Cost-effective
- Good for simple tasks

**Best For:**
- Real-time applications
- High-volume, simple queries
- Sub-agents for quick tasks

---

#### 🏠 Ollama (Local/Privacy)

**Strengths:**
- Zero API costs
- Complete data privacy
- No internet required

**Limitations:**
- Hardware-dependent performance
- Requires local GPU for good performance

**Best For:**
- Sensitive data processing
- Offline environments
- Cost minimization

---

### Model Selection Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│                    What do you need?                         │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌──────────┐       ┌──────────┐       ┌──────────┐
    │ Complex  │       │ Fast &   │       │ Local/   │
    │ Reasoning│       │ Cheap    │       │ Private  │
    └────┬─────┘       └────┬─────┘       └────┬─────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────┐ ┌──────────────┐  ┌──────────────┐
│ Claude Opus 4-6 │ │ Kimi K2.5    │  │ Ollama       │
│ or Kimi Coding  │ │ or MiniMax   │  │ Local Models │
└─────────────────┘ └──────────────┘  └──────────────┘
```

---

## 3️⃣ Astra Upgrade Paths

### Evolution Strategies

Astra can evolve along multiple dimensions:

| Dimension | Current State | Upgrade Options |
|-----------|---------------|-----------------|
| **Capabilities** | Bundled skills | + ClawHub skills + Custom skills |
| **Intelligence** | Single model | Multi-model routing by task |
| **Scope** | Single agent | Multi-agent specialization |
| **Memory** | Session-only | Persistent memory + long-term |
| **Integration** | Basic tools | Rich API ecosystem |

### Recommended Upgrade Sequence

```
Phase 1: Foundation (Current)
├── Configure optimal primary model
├── Establish workspace conventions
└── Set up basic skills from ClawHub

Phase 2: Specialization
├── Create task-specific sub-agent defaults
├── Install domain-specific skills
└── Configure tool profiles

Phase 3: Multi-Agent
├── Split contexts (work/personal/family)
├── Configure agent bindings
└── Set up cross-agent workflows

Phase 4: Advanced
├── Custom skill development
├── Automation pipelines
└── Integration with external APIs
```

### Workspace File Evolution

| File | Purpose | Evolution Strategy |
|------|---------|-------------------|
| `SOUL.md` | Persona, tone, boundaries | Refine as personality preferences emerge |
| `AGENTS.md` | Operating instructions | Add patterns discovered through use |
| `USER.md` | User profile, preferences | Expand with learned preferences |
| `TOOLS.md` | Tool conventions | Document successful patterns |
| `BOOTSTRAP.md` | First-run ritual | Delete after completion |
| `HEARTBEAT.md` | Background task triggers | Add recurring automation |

---

## 4️⃣ Multi-Agent Scenarios

### When to Spawn Sub-Agents

| Scenario | Use Sub-Agent? | Rationale |
|----------|----------------|-----------|
| Research task while continuing chat | ✅ Yes | Parallel processing |
| Long-running analysis | ✅ Yes | Non-blocking main agent |
| Multiple independent tasks | ✅ Yes | Parallel execution |
| Simple Q&A | ❌ No | Direct response is faster |
| Context-dependent follow-ups | ❌ No | Needs main agent context |

### Sub-Agent Configuration

```json5
{
  agents: {
    defaults: {
      // Use cheaper model for sub-agents
      subagents: {
        model: "minimax/MiniMax-M2.1",
        thinking: "low",
        maxConcurrent: 4,
        archiveAfterMinutes: 30
      }
    }
  },
  tools: {
    subagents: {
      tools: {
        // Restrict sub-agent capabilities
        deny: ["browser", "gateway", "cron"]
      }
    }
  }
}
```

### Multi-Agent Routing Examples

#### Example 1: Work vs Personal Split

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        default: true,
        name: "Personal Assistant",
        workspace: "~/.openclaw/workspace",
        model: "anthropic/claude-sonnet-4-5"
      },
      {
        id: "work",
        name: "Work Agent",
        workspace: "~/.openclaw/workspace-work",
        model: "anthropic/claude-opus-4-6",
        sandbox: {
          mode: "all",
          scope: "agent"
        },
        tools: {
          allow: ["group:fs", "exec", "message"],
          deny: ["browser", "gateway"]
        }
      }
    ]
  },
  bindings: [
    { agentId: "personal", match: { channel: "telegram", accountId: "personal" } },
    { agentId: "work", match: { channel: "telegram", accountId: "work" } }
  ]
}
```

#### Example 2: Channel-Based Routing

```json5
{
  agents: {
    list: [
      {
        id: "chat",
        name: "Everyday",
        model: "anthropic/claude-sonnet-4-5"
      },
      {
        id: "deep",
        name: "Deep Work",
        model: "anthropic/claude-opus-4-6"
      }
    ]
  },
  bindings: [
    { agentId: "chat", match: { channel: "whatsapp" } },
    { agentId: "deep", match: { channel: "telegram" } }
  ]
}
```

#### Example 3: Family Agent (Restricted)

```json5
{
  agents: {
    list: [
      {
        id: "family",
        name: "Family Bot",
        workspace: "~/.openclaw/workspace-family",
        groupChat: {
          mentionPatterns: ["@family", "@familybot"]
        },
        sandbox: {
          mode: "all",
          scope: "agent"
        },
        tools: {
          allow: ["read", "exec", "message"],
          deny: ["write", "edit", "browser", "cron", "gateway"]
        }
      }
    ]
  },
  bindings: [
    {
      agentId: "family",
      match: {
        channel: "whatsapp",
        peer: { kind: "group", id: "GROUP_ID@g.us" }
      }
    }
  ]
}
```

### Sub-Agent Management Commands

| Command | Purpose |
|---------|---------|
| `/subagents list` | Show active/completed sub-agents |
| `/subagents stop <id>` | Stop a running sub-agent |
| `/subagents log <id>` | View sub-agent transcript |
| `/subagents send <id> <msg>` | Message a running sub-agent |

---

## 5️⃣ Tool Integration Patterns

### Tool Categories

| Category | Tools | Use Cases |
|----------|-------|-----------|
| **File System** | `read`, `write`, `edit`, `apply_patch` | Code editing, document management |
| **Runtime** | `exec`, `process` | Command execution, background tasks |
| **Web** | `web_search`, `web_fetch`, `browser` | Research, data extraction |
| **UI** | `browser`, `canvas` | Visual interaction, screenshots |
| **Messaging** | `message` | Cross-channel communication |
| **Sessions** | `sessions_list`, `sessions_spawn` | Multi-agent coordination |
| **Automation** | `cron`, `gateway` | Scheduling, system control |
| **Nodes** | `nodes` | Mobile/remote device control |

### Tool Profiles

Profiles provide base allowlists:

| Profile | Allowed Tools |
|---------|---------------|
| `minimal` | `session_status` only |
| `coding` | File system + Runtime + Sessions |
| `messaging` | Messaging + basic session tools |
| `full` | All tools (default) |

### Security Best Practices

1. **Tool Gating by Provider**
```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" }
    }
  }
}
```

2. **Sandboxing**
```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",      // Always sandbox
        scope: "agent"    // Per-agent containers
      }
    }
  }
}
```

3. **Elevated Mode Controls**
```json5
{
  tools: {
    elevated: {
      enabled: true,
      ask: "on-miss"  // Ask for unknown commands
    }
  }
}
```

### API Integration Patterns

#### Pattern 1: Direct API Calls via `exec`
```bash
# REST API call
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     https://api.example.com/data
```

#### Pattern 2: Skill-Based Integration
Create a skill with:
- `SKILL.md` documenting API usage
- Config file for endpoints
- Helper scripts for common operations

#### Pattern 3: Webhook Automation
```json5
{
  automation: {
    webhooks: {
      enabled: true,
      routes: [
        {
          path: "/github-webhook",
          handler: "scripts/handle-github.js"
        }
      ]
    }
  }
}
```

---

## 📊 Progress Tracking

### Current Configuration Audit

| Component | Status | Notes |
|-----------|--------|-------|
| Primary Model | ⬜ Unknown | Need to verify current default |
| Skills Installed | ⬜ Unknown | Run `clawhub list` to audit |
| Multi-Agent Setup | ⬜ Not Configured | Consider for work/personal split |
| Sub-Agent Defaults | ⬜ Not Configured | Set cheaper model for background tasks |
| Sandbox Mode | ⬜ Unknown | Verify security posture |
| Tool Profiles | ⬜ Not Configured | Implement least-privilege |

### Implementation Checklist

- [ ] Audit current model configuration
- [ ] List installed skills (`clawhub list`)
- [ ] Define agent personas (work/personal/family)
- [ ] Configure sub-agent defaults with cost-effective model
- [ ] Set up tool profiles for security
- [ ] Document personal conventions in `TOOLS.md`
- [ ] Create custom skills for repetitive tasks
- [ ] Configure automation (cron/heartbeat)

---

## 🔮 Future Roadmap

### Short Term (1-2 Months)

| Initiative | Effort | Impact |
|------------|--------|--------|
| Multi-agent setup | Medium | High |
| Sub-agent optimization | Low | Medium |
| Skills curation | Medium | Medium |
| Tool profile hardening | Low | High |

### Medium Term (3-6 Months)

| Initiative | Effort | Impact |
|------------|--------|--------|
| Custom skill development | High | High |
| Advanced automation pipelines | Medium | High |
| Integration with external services | Medium | Medium |
| Performance monitoring | Low | Medium |

### Long Term (6+ Months)

| Initiative | Effort | Impact |
|------------|--------|--------|
| AI-native workflow design | High | Very High |
| Cross-agent memory sharing | Medium | High |
| Predictive task automation | High | Very High |
| Custom model fine-tuning | Very High | Medium |

---

## ❓ Questions for Dibs

To optimize Astra's evolution, please consider:

1. **Usage Patterns**
   - What tasks do you use Astra for most frequently?
   - Are there tasks that feel slow or expensive?

2. **Context Separation**
   - Do you want separate agents for work vs personal?
   - Should family members have isolated access?

3. **Privacy & Security**
   - Are there sensitive tasks that should be sandboxed?
   - Which tools should require explicit approval?

4. **Integration Needs**
   - What external services would you like Astra to connect to?
   - Are there repetitive workflows worth automating?

5. **Budget Considerations**
   - What's your target monthly AI spend?
   - Should sub-agents use cheaper models by default?

---

## 📚 Source Citations

| Section | Primary Sources |
|---------|-----------------|
| Skills System | OpenClaw docs: `/tools/skills.md`, `/tools/clawhub.md` |
| LLM Providers | OpenClaw docs: `/providers/index.md`, `/providers/moonshot.md`, `/concepts/model-providers.md` |
| Multi-Agent | OpenClaw docs: `/concepts/multi-agent.md`, `/tools/subagents.md` |
| Tool Integration | OpenClaw docs: `/tools/index.md`, `/gateway/background-process.md`, `/concepts/agent.md` |
| Official Docs | https://docs.openclaw.ai |
| Skill Registry | https://clawhub.ai |

---

## 📝 Action Items

### Immediate (This Week)

| # | Action | Owner | Due |
|---|--------|-------|-----|
| 1 | Review and approve this report | Dibs | 2026-02-21 |
| 2 | Run configuration audit (`openclaw status`, `clawhub list`) | Dibs/Astra | 2026-02-22 |
| 3 | Answer "Questions for Dibs" section | Dibs | 2026-02-23 |

### Short Term (Next 2 Weeks)

| # | Action | Owner | Due |
|---|--------|-------|-----|
| 4 | Implement sub-agent cost optimization | Astra | 2026-03-05 |
| 5 | Curate initial skill set from ClawHub | Astra | 2026-03-05 |
| 6 | Document personal conventions in TOOLS.md | Astra | 2026-03-05 |

### Medium Term (Next Month)

| # | Action | Owner | Due |
|---|--------|-------|-----|
| 7 | Design multi-agent architecture | Astra/Dibs | 2026-03-19 |
| 8 | Implement tool profiles | Astra | 2026-03-19 |
| 9 | Create first custom skill | Astra | 2026-03-19 |

---

## 🏁 Conclusion

Astra is built on a powerful, extensible architecture. The key to evolution is:

1. **Strategic model selection** - Match models to tasks
2. **Skill curation** - Build capability incrementally
3. **Multi-agent design** - Isolate contexts appropriately
4. **Security-first tooling** - Least privilege, sandboxed execution
5. **Continuous refinement** - Document patterns, iterate on setup

With these foundations, Astra can grow from a helpful assistant into a truly personalized AI collaborator.

---

*Report generated by Chitra, Research Sub-Agent*  
*For: Astra Main Agent → Dibs*  
*Date: February 19, 2026*
