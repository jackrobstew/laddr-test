# Strwbrry Vault Advisory Council

A multi-agent AI system that provides **insights and recommendations** for your Strwbrry vault through multiple specialized advisors with distinct personalities.

## 🎯 Core Philosophy

**Agents NEVER modify your vault.** They are read-only advisors who:
- 🔍 **Analyze** your vault from different perspectives
- 💡 **Provide insights** you might miss
- 🎯 **Give exact recommendations** with supporting evidence
- 🚫 **Never make changes** - you stay in control

## 👥 The Advisory Council

### **The Skeptic** - Truth Teller
**Personality**: Direct, evidence-based, uncomfortably honest
**Specialty**: Finds misalignments between what you SAY and what you DO
**Output**: Points out stated vs actual priorities, abandoned hopes, contradictions

**Example Insight:**
> "You wrote in 20-Personal Identity that relationships are your foundation. Reality: 27-Relationships updated 2x this month, 51-Audio Engineering updated 34x. Either update your stated values to match reality, OR block 2hrs/week for relationships and treat it like work. You can't have both stories. Pick one."

---

### **The Pattern Seeker** - Cycle Detective
**Personality**: Curious, analytical, fascinated by patterns
**Specialty**: Finds recurring cycles, correlations, and rhythms in your behavior
**Output**: Identifies patterns, makes predictions, reveals hidden connections

**Example Insight:**
> "Pattern Detected: 'Work Season Cycle' - Every 4-6 weeks you enter an intense work period, creative projects go dormant, then you rebalance. Current: Week 3 of work season. Prediction: Natural rebalancing will start around Nov 13. Stop fighting this cycle - it's how you work. Pre-plan the rebalancing period."

---

### **The Guardian** - Early Warning System
**Personality**: Protective, forward-looking, concerned but not alarmist
**Specialty**: Detects warning signs of burnout/imbalance BEFORE they happen
**Output**: Risk assessments, timeline predictions, preventive recommendations

**Example Insight:**
> "Risk Level: MODERATE. Leading indicators: Work activity +40%, creative projects going dormant (matches historical stress precursor), sleep mentions decreasing. Predicted timeline: 5-7 days until creative outlet absence → increased stress. Recommendation: 15min daily creative play as pressure valve. This isn't about time management - it's about preventing predictable burnout."

---

## 🚀 Quick Start

### 1. Install

```bash
cd strwbrry-agent
pip install laddr
```

### 2. Configure

First, set up your environment file:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your settings
nano .env  # or use your preferred editor
```

**Required settings in `.env`:**

```bash
# Your OpenRouter API key
OPENAI_API_KEY=sk-or-v1-your-key-here

# Path to your Strwbrry vault
VAULT_PATH=/path/to/Documents/SPLN
```

**Get an OpenRouter key:** https://openrouter.ai/keys (free credits available)

**Note:** `.env` is gitignored for security - your API keys stay local!

### 3. Run Advisory Council

```bash
python get_insights.py
```

This will:
1. Run all three advisors in parallel
2. Synthesize their perspectives
3. Provide a comprehensive report

### 4. Consult Individual Advisors

```bash
python get_insights.py skeptic
python get_insights.py pattern_seeker
python get_insights.py guardian
```

---

## 📊 What You Get

### **Full Council Report** includes:

1. **Executive Summary** - Main insights across all advisors
2. **The Skeptic's Perspective** - Stated vs actual priorities
3. **The Pattern Seeker's Findings** - Cycles and correlations
4. **The Guardian's Warning** - Risk assessment and predictions
5. **Council Synthesis** - Areas of agreement, root issues, consensus
6. **Priority Recommendations** - Top 3 actions with supporting evidence
7. **Closing Reflection** - Connection to your Strwbrry philosophy

---

## ⚙️ Configuration

### Using Claude Sonnet (Default - Recommended)

```bash
# .env
LLM_BACKEND=openai
LLM_MODEL=anthropic/claude-3.5-sonnet
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=your-openrouter-key
```

**Cost:** ~$3 per 1M tokens (very affordable for this use case)

### Using Local Ollama (Free, Private)

```bash
# .env
LLM_BACKEND=openai
LLM_MODEL=llama3.2
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama  # Dummy key
```

Make sure Ollama is running:
```bash
ollama serve
ollama pull llama3.2
```

### Other Models via OpenRouter

```bash
LLM_MODEL=anthropic/claude-3-haiku  # Faster, cheaper
LLM_MODEL=google/gemini-2.0-flash   # Google
LLM_MODEL=meta-llama/llama-3.3-70b  # Open source
```

---

## 🛠️ How It Works

### Architecture

```
get_insights.py
    ↓
Vault Advisor (Coordinator)
    ↓
┌─────────────┬──────────────────┬─────────────┐
│   Skeptic   │  Pattern Seeker  │   Guardian  │
│ (parallel)  │    (parallel)    │ (parallel)  │
└─────────────┴──────────────────┴─────────────┘
    ↓
Synthesis & Report
```

### Custom Tools (Read-Only)

All advisors have access to these vault analysis tools:

- `check_vault_connection()` - Verify vault access
- `count_updates_by_area(days)` - Where attention is going
- `read_vault_area(area)` - Read specific JD areas
- `read_recent_journals(days)` - Analyze journal entries
- `search_vault_content(query)` - Find specific content
- `analyze_strwbrry_folder()` - Read hopes/implementations
- `compare_areas(area1, area2)` - Compare activity levels

**All tools are READ-ONLY**. No modifications possible.

### Lightweight Mode (Default)

- SQLite database (local file)
- Memory queue (no Redis)
- No Docker required
- Perfect for personal use

---

## 🎓 Use Cases

### Weekly Check-In

```bash
# Every Sunday
python get_insights.py > weekly_insights.md
```

Get a weekly advisory report to inform your planning.

### Before Major Decisions

Consult the council before:
- Starting new projects
- Committing to goals
- Major life changes

### When Feeling "Off"

```bash
python get_insights.py guardian
```

The Guardian can often predict what's wrong before you consciously realize it.

---

## 🔬 Advanced Usage

### Custom Advisory Agent

Create your own advisor with a unique perspective:

```python
# agents/growth_advocate.py

growth_advocate = Agent(
    name="growth_advocate",
    role="The Growth Advocate - Action Catalyst",
    goal="Push user toward action on stated hopes and learning goals",
    backstory="""You're The Growth Advocate. Encouraging, action-oriented, optimistic...""",
    llm=openai(...),
    tools=[...],
    instructions="""..."""
)
```

Add to `laddr.yml`:
```yaml
agents:
  - vault_advisor
  - skeptic
  - pattern_seeker
  - guardian
  - growth_advocate  # Your new advisor
```

---

## ⚠️ Limitations & Known Issues

### **Current Limitations:**

1. **Folder Path Assumptions**
   - Tools attempt multiple naming variations but may not find all vault structures
   - Works best with Johnny Decimal naming (e.g., "10-19 - Living")

2. **Analysis Time**
   - Full council report: 3-10 minutes
   - No real-time progress updates during analysis
   - Single advisor: 1-3 minutes

3. **Preview Sizes**
   - Journal previews: 2000 characters (increased from 500)
   - May miss context in very long journal entries
   - Search context: 100 chars each side of match

4. **File Limits**
   - Search scans max 500 files (configurable)
   - Large vaults (>1000 notes) may have incomplete analysis
   - Vault area reading limited to 20 files by default

5. **Pattern Detection**
   - Patterns require manual validation
   - No historical tracking across runs (yet)
   - Confidence scores not implemented

6. **Language Support**
   - English-centric agent personalities
   - UTF-8 encoding assumed (with latin-1 fallback)

### **What This System Cannot Do:**

- ❌ **Modify your vault** (by design - read-only)
- ❌ **Track changes over time** (each run is independent)
- ❌ **Validate predictions** (no feedback loop yet)
- ❌ **Handle non-markdown files** (PDFs, images, etc.)
- ❌ **Real-time monitoring** (on-demand analysis only)
- ❌ **Cross-vault analysis** (single vault only)

### **Performance Notes:**

- First run is slower (no caching)
- SQLite database grows with usage (~1MB per 100 runs)
- Memory usage: ~100-500MB during analysis
- OpenRouter API costs: ~$0.10-0.50 per full council report

---

## 🐛 Troubleshooting

### "Vault not found"

Set `VAULT_PATH` in `.env`:
```bash
export VAULT_PATH=/path/to/Documents/SPLN
```

### "OPENAI_API_KEY not set"

Edit `.env` and add your OpenRouter key.

### "Module 'laddr' not found"

```bash
pip install laddr
```

---

## 📈 What's Next

### Current (v1.0) ✅
- 3 advisory agents with distinct personalities
- Read-only vault analysis
- Multi-agent coordinator
- Synthesis and recommendations

### Near-term Ideas
- **The Philosopher** - Connects to values and meaning
- **The Systems Optimizer** - Process improvement suggestions
- **The Growth Advocate** - Pushes toward action on hopes
- Historical tracking (compare reports over time)

---

## 🤔 Philosophy

### Why This Approach?

**Multi-perspective insight > Single AI assistant**

One AI is limited by its single perspective. Multiple agents with distinct personalities provide:
- Diverse viewpoints (catch blind spots)
- Personality diversity (insights more compelling)
- Specialization (depth in each area)
- Emergent intelligence (synthesis > sum of parts)

**Read-only = Trust**

Agents that modify your vault are risky. Read-only advisors are:
- Safe (can't break anything)
- Trustworthy (no hidden changes)
- Empowering (you make decisions)
- Aligned with "Simple Truths Restore Willpower"

**Evidence-based recommendations**

Every insight backed by vault data:
- Not generic advice
- Specific to YOUR patterns
- Actionable recommendations
- Testable predictions

### Connection to Strwbrry

This system embodies core Strwbrry principles:

1. **Simple Truths Restore Willpower**
   - Advisors reveal simple truths from complex data
   - Truths → awareness → willpower → action

2. **Self-awareness is not enough**
   - System doesn't just describe, it RECOMMENDS
   - Specific, actionable next steps

3. **Pattern recognition**
   - Humans can't track 100+ correlations
   - AI spots patterns we miss
   - Patterns → predictions → prevention

---

## 🎯 Bottom Line

### This System:
- ✅ Multiple AI advisors with distinct personalities
- ✅ Read-only analysis (never modifies vault)
- ✅ Evidence-based insights and recommendations
- ✅ Works locally, privately, affordably
- ✅ Extensible (add your own advisors)

### This is NOT:
- ❌ Automation (you make decisions)
- ❌ Full "Pattern Intelligence System" (that's months of work)
- ❌ Replacement for thinking (augments it)

### Why Start Here:
- Works TODAY (not eventually)
- Proves value immediately
- Foundation for more agents
- Safe, read-only, trustworthy

---

**Built with:** [laddr](https://github.com/AgnetLabs/laddr) - Multi-Agent Framework

**For your:** Strwbrry Vault - "Simple Truths Restore Willpower"

**Philosophy:** Multiple perspectives reveal truth. Truth enables action. Action creates change.
