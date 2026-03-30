# Width Risk & Compliance Database — AI Agent Skill

Screen any person or company against **1.2M+ entities** — sanctions, PEP, criminal records, adverse media — in under 2 seconds. Then use your Agent's web search to find real-time news.

## Quick Start

### 1. Install

**Claude Code:**
```bash
# Copy to your skills directory
cp -r width-risk-compliance-skills ~/.claude/skills/width-risk-compliance
```

**Or clone anywhere:**
```bash
git clone https://github.com/Width-Risk-Comliance-Database/width-risk-compilance-skills.git
```

### 2. Register (Auto on First Use)

```bash
cd width-risk-compliance-skills
python3 scripts/register.py
# → ✅ Registered! API Key: e6602814-... (300/day free)
```

### 3. Screen Someone

```bash
python3 scripts/screen.py --name "赵长鹏" --aliases "CZ,Changpeng Zhao" --country CN
```

Output:
```
## Width Risk Screening — 赵长鹏

**🚫 Decision: REJECT** | Risk: SEVERE

### Database Checks
- ✅ Sanctions: Clear
- ✅ PEP: Clear
- 🚨 **Criminal Records: HIT**
  - Criminal conviction on record
- 🚨 **Adverse Media: HIT**
  - 19 articles, max severity: SEVERE

### Decision Reasoning
- CONVICTED: 'Changpeng Zhao' has a criminal conviction on record
- ADVERSE MEDIA: 19 article(s), max_severity=SEVERE
```

## Upgrade Your Quota

| Tier | Limit | How |
|---|---|---|
| Free | 300/day | Auto on register |
| Email | 500/day | `python3 scripts/register.py --bind-email you@email.com` |
| Survey | 1,000/day | `python3 scripts/register.py --survey` |

```bash
# Check your usage
python3 scripts/register.py --usage

# Bind email (sends verification code)
python3 scripts/register.py --bind-email you@email.com
python3 scripts/register.py --verify-code 123456

# Complete survey
python3 scripts/register.py --survey
```

## How It Works

```
You (Agent) ─── "screen 杜均" ──→ Skill parses intent
                                    │
                                    ├─ Extract: name, aliases, country, industry, context
                                    │
                                    ├─ Call Width API (/v1/screening)
                                    │   └─ Returns: sanctions, PEP, criminal, adverse media
                                    │
                                    └─ Agent searches web for real-time news
                                        └─ Using news source list from SKILL.md
                                    │
                                    └─ Combined report presented to user
```

**Width API handles:** Database screening (1.2M entities, 420K sanctions, 856K PEP)
**Your Agent handles:** Real-time news search (using its own WebSearch capability)

## Database Coverage

- **120W+ entities** — persons, companies, organizations, vessels
- **42W+ sanctions entries** — OFAC, EU, UN, UK + 116 more lists
- **85W+ PEP records** — 255 jurisdictions worldwide
- **15W+ criminal/wanted** — INTERPOL, country-level wanted lists
- **3,000+ Chinese regulatory penalties** — CSRC, PBOC, NFRA, SAFE, SAMR
- **Asia-deep coverage** — CN, HK, SG, TH, JP, KR, PH, ID, VN, MY, AE

## Files

```
SKILL.md              — Skill definition (how your Agent uses this)
scripts/
  config.py           — API key storage (~/.width/config.json)
  register.py         — Register, bind email, survey, check usage
  screen.py           — Submit screening, poll result, format report
README.md             — This file
```

## License

MIT
