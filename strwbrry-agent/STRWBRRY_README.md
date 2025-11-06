# Strwbrry Vault AI Assistant

A lightweight multi-agent AI system for your Strwbrry Johnny Decimal vault, built with [laddr](https://github.com/AgnetLabs/laddr).

## 🎯 What This Does

**JD Classifier Agent**: Analyzes note content and suggests the best Johnny Decimal location in your vault structure.

- Understands your vault's organization (ethereal→concrete principle)
- Suggests specific XX.YY locations with reasoning
- Generates proper Strwbrry-compliant frontmatter
- Fast, lightweight, works without Docker

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install laddr
```

### 2. Configure Your API Key

Edit `.env` and add your OpenRouter API key:

```bash
OPENAI_API_KEY=your-actual-openrouter-key-here
```

Get a key at: https://openrouter.ai/keys

### 3. Test It

```bash
python test_classifier.py
```

This will run 5 test cases and show you how the agent categorizes different types of notes.

---

## 💡 Usage Examples

### Interactive Mode

```bash
python classify.py
```

Then enter your note description:

```
> I want to store my espresso brewing notes with grind settings

PRIMARY RECOMMENDATION: 25 - My Diet and Cooking
REASONING: Food/beverage preparation belongs in the Life area under Diet and Cooking

SUGGESTED FRONTMATTER:
---
UUID: a1b2c3d4-5678-90ab-cdef-1234567890ab
Date: 2025-11-06
Type: human
Title: Espresso Brewing Notes
---

SUGGESTED FILENAME: 25.77 - Espresso Brewing Technique.md
```

### Command Line Mode

```bash
python classify.py "Meeting notes from today's audio project"
```

### Python API

```python
from laddr import AgentRunner, LaddrConfig

runner = AgentRunner(env_config=LaddrConfig())
result = await runner.run(
    {"query": "Notes about my morning routine"},
    agent_name="jd_classifier"
)

print(result["result"])
```

---

## ⚙️ Configuration Options

### Using Claude Sonnet (Default)

```bash
# .env
LLM_BACKEND=openai
LLM_MODEL=anthropic/claude-3.5-sonnet
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=your-openrouter-key
```

### Using Local Ollama

```bash
# .env
LLM_BACKEND=openai
LLM_MODEL=llama3.2
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama  # Dummy key, Ollama doesn't require one
```

Make sure Ollama is running: `ollama serve`

### Using Other Models via OpenRouter

```bash
LLM_MODEL=anthropic/claude-3-haiku  # Faster, cheaper
LLM_MODEL=google/gemini-2.0-flash   # Google's model
LLM_MODEL=meta-llama/llama-3.3-70b  # Open source
```

---

## 🏗️ How It Works

### The Johnny Decimal Structure

The agent understands your vault's organization:

```
00-09: Meta (about the vault)
10-19: Living (day-to-day present)
20-29: Life (personal/health/relationships)
30-39: Lived (memories/past events)
40-49: Learn (education/courses)
50-59: Work (career/jobs)
60-69: Play (recreation/games)
70-79: Creation (making things)
80-89: System (technical/configs)
90-99: Archive (backups/inactive)
100: Inbox (unsorted)
```

### Custom Tools

The agent has access to these custom tools:

1. **get_jd_structure()** - Returns full vault organization
2. **find_jd_category()** - Looks up specific categories
3. **suggest_jd_location()** - Provides structured guidance
4. **generate_frontmatter()** - Creates proper YAML frontmatter

### The Decision Process

1. Agent reads your content description
2. Retrieves JD structure and guidance
3. Considers:
   - Is it personal or technical?
   - Is it present, past, or future-focused?
   - Is it about doing, creating, or documenting?
4. Suggests primary location with reasoning
5. Generates proper frontmatter and filename

---

## 🎓 Understanding the Vault Philosophy

### Ethereal → Concrete Principle

```
10-30s: Personal, subjective, changing
70-90s: Technical, objective, structured
```

### Temporal Flow

```
10s: Present (Living day-to-day)
30s: Past (Lived memories)
40s: Future (Learning for growth)
```

### Special Folders

- `XX.00` - Root/overview folders for each category
- `XX.99` - External/miscellaneous items

---

## 🔧 Advanced Usage

### Building More Agents

This is just ONE agent. You can add more:

**Inbox Processor** - Batch process inbox items
```python
# agents/inbox_processor.py
```

**Vault Linker** - Find related notes and suggest links
```python
# agents/vault_linker.py
```

**Journal Analyzer** - Extract patterns from daily journals
```python
# agents/journal_analyzer.py
```

### Multi-Agent Coordinator

Create a coordinator that delegates to specialists:

```python
# agents/vault_coordinator.py
coordinator = Agent(
    name="vault_coordinator",
    is_coordinator=True,
    available_agents=['jd_classifier', 'vault_linker', 'frontmatter_generator']
)
```

---

## 📊 Performance

**Lightweight Mode** (current setup):
- SQLite database (local file)
- Memory queue (no Redis needed)
- No Docker required
- ~2-5 seconds per classification

**Production Mode** (optional):
- PostgreSQL for tracing/history
- Redis for distributed queuing
- Docker Compose for scaling
- Multiple concurrent workers

---

## 🐛 Troubleshooting

### "Module 'laddr' not found"
```bash
pip install laddr
```

### "OPENAI_API_KEY not set"
Edit `.env` and add your OpenRouter key

### "Connection refused" with Ollama
```bash
ollama serve  # Start Ollama server
ollama pull llama3.2  # Download model
```

### Agent returns errors
Check `laddr.db` for trace logs:
```bash
sqlite3 laddr.db "SELECT * FROM traces ORDER BY created_at DESC LIMIT 5;"
```

---

## 🚀 Next Steps

### Immediate (What Works Now):
1. ✅ Classify individual notes
2. ✅ Generate proper frontmatter
3. ✅ Get JD location suggestions

### Short-term (Easy to Add):
1. Read actual markdown files from inbox
2. Batch process multiple files
3. Auto-generate full note templates

### Medium-term (Requires More Agents):
1. Link related notes automatically
2. Extract entities and build knowledge graph
3. Analyze journal patterns

### Long-term (The Vision):
1. Pattern Intelligence System (weekly insights)
2. Predictive failure detection
3. Behavioral validation (stated vs actual)
4. Hope→Action→Outcome tracking

---

## 🤔 Design Philosophy

**Why Start Simple?**

This implementation follows a pragmatic approach:
- ✅ Works TODAY (not "eventually")
- ✅ No complex infrastructure required
- ✅ Provides immediate value
- ✅ Foundation for growth

**The "Pattern Intelligence System" is amazing** (see the brainstorming docs) but it's a 3-6 month project. This JD Classifier proves the concept and gives you something useful NOW.

---

## 📝 Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_BACKEND` | `openai` | LLM provider |
| `LLM_MODEL` | `anthropic/claude-3.5-sonnet` | Model to use |
| `OPENAI_BASE_URL` | `https://openrouter.ai/api/v1` | API endpoint |
| `OPENAI_API_KEY` | *(required)* | Your API key |
| `DB_BACKEND` | `sqlite` | Database type |
| `QUEUE_BACKEND` | `memory` | Queue type |

### File Structure

```
strwbrry-agent/
├── agents/
│   └── jd_classifier.py       # JD classification agent
├── tools/
│   ├── vault_tools.py          # Custom vault tools
│   └── __init__.py
├── .env                        # Configuration (YOU EDIT THIS)
├── laddr.yml                   # Laddr project config
├── test_classifier.py          # Test suite
├── classify.py                 # Interactive CLI (create this)
└── STRWBRRY_README.md         # This file
```

---

## 💬 Questions?

**"Can I use this with my actual vault?"**
Yes! Just point it at your Documents/SPLN directory.

**"Will it modify my notes?"**
No! This agent only SUGGESTS locations. You decide what to do.

**"Can I use different LLMs?"**
Yes! Configure via .env (Sonnet, Haiku, Gemini, Llama, etc.)

**"How much does OpenRouter cost?"**
~$3 per million tokens for Sonnet. Very cheap for this use case.

**"Can I add more agents?"**
Absolutely! That's the whole point of laddr.

---

## 🎯 The Honest Truth

### What This IS:
- ✅ A working, useful tool RIGHT NOW
- ✅ Foundation for building more agents
- ✅ Proof that multi-agent systems can help your vault

### What This ISN'T:
- ❌ The full "Pattern Intelligence System" (that's 3-6 months)
- ❌ Automatic vault management (you're still in control)
- ❌ AI that "knows" your vault (it learns as you use it)

### Why This Approach:
**Build → Test → Learn → Iterate**

Start with something simple that works. Prove the value. Then expand.

---

**Built with:** [laddr](https://github.com/AgnetLabs/laddr) - Multi-Agent Framework for AI Systems

**For your:** Strwbrry Vault - A carefully crafted personal knowledge management system
