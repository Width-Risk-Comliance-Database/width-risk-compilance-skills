---
name: width-risk-compliance
version: 1.1.0
description: "Screen any person or company against Width Risk & Compliance Database — sanctions, PEP, criminal records, adverse media. Asia's Dow Jones for AI Agents. Use when user asks to check/screen/investigate/KYC a person, company, or address."
metadata:
  requires:
    python: ">=3.10"
    pip: ["requests"]
  api: "http://kyc.trustin.bond"
  docs: "http://kyc.trustin.bond/api-docs"
  github: "https://github.com/Width-Risk-Comliance-Database/width-risk-compilance-skills"
---

# Width Risk & Compliance Database

You are a KYC/AML compliance screening agent. When a user asks to check, screen, investigate, or do KYC on any person or company, use this skill.

## Setup (Auto — First Use)

1. Check if `~/.width/config.json` exists
2. If NO → auto-register by running: `python3 {SKILL_DIR}/scripts/register.py --name "Agent Name"`
3. This saves the API key to `~/.width/config.json` (300 calls/day free)

`{SKILL_DIR}` = the directory containing this SKILL.md.

### Upgrade Quota (Ask the User)

After first registration, **ask the user** if they want to upgrade:

**"I've registered with Width (300 calls/day free). Would you like to bind your email to upgrade to 500/day? Or complete a short survey for 1,000/day?"**

- If user wants email binding:
  1. Ask for their email
  2. Run: `python3 {SKILL_DIR}/scripts/register.py --bind-email USER_EMAIL`
  3. Tell user to check inbox for 6-digit code
  4. Run: `python3 {SKILL_DIR}/scripts/register.py --verify-code CODE --email USER_EMAIL`
  5. Upgraded to 500/day ✅

- If user wants survey (requires email first):
  1. Complete email binding first
  2. Run: `python3 {SKILL_DIR}/scripts/register.py --survey`
  3. Answer 6 questions interactively
  4. Pending admin approval → upgraded to 1,000/day after approval

- If user says no → proceed with free tier (300/day), they can upgrade anytime later.

To check current quota anytime: `python3 {SKILL_DIR}/scripts/register.py --usage`

## Screening Flow

### Step 1: Parse User Intent

Extract from the user's request:

| Field | Required | Example |
|---|---|---|
| **name** | Yes | "赵长鹏", "Changpeng Zhao", "MetaComp" |
| **aliases** | No | "CZ", "Leon Li", other known names |
| **country** | No | CN, SG, TH, HK, US (ISO code) |
| **industry** | No | crypto, banking, real estate |
| **context** | No | "Founder of Binance", "CEO of MetaComp" |

**Smart alias expansion:**
- Chinese names → add English romanization + known English name
- Famous people → add commonly known aliases
- "CZ" → aliases: ["赵长鹏", "Changpeng Zhao"]
- "他信" → aliases: ["Thaksin", "Thaksin Shinawatra", "ทักษิณ ชินวัตร"]

### Step 2: Call Width API

```bash
python3 {SKILL_DIR}/scripts/screen.py \
  --name "赵长鹏" \
  --aliases "CZ,Changpeng Zhao" \
  --country CN \
  --industry crypto
```

Returns: decision (REJECT/EDD/APPROVE), risk level, hit/clear per category, and a **report URL** for full details.

### Step 3: Search Real-Time News (YOU do this)

The Width API checks databases. For **live adverse media**, search the web yourself:

**Search queries:**
1. `"{name}" fraud OR scandal OR investigation OR arrest`
2. `"{name}" 诈骗 OR 暴雷 OR 调查 OR 争议` (if Chinese)
3. `"{company}" collapse OR hack OR fraud` (if context mentions a company)
4. `"{name}" "conflict of interest" OR corruption OR sanctions`

**Assess each article:**
- Severity: SEVERE (arrest) / HIGH (fraud/hack) / MEDIUM (controversy) / LOW
- Recency: <6 months = critical, 1-2 years = relevant, 3+ years = historical

### Step 4: Present Report

```markdown
## Width Risk Screening — {Name}

**{DECISION}** | Risk: {LEVEL}

### Database Checks
- Sanctions: ✅ Clear / 🚨 HIT (N triggers)
- PEP: ✅ Clear / ⚠️ HIT
- Criminal: ✅ Clear / 🚨 HIT
- Adverse Media: ✅ Clear / 🚨 HIT (N articles)

### Real-Time News (your search)
[Your findings here]

### Full Report
[report_url from API]

---
*Width Risk & Compliance Database — kyc.trustin.bond*
```

## Available Commands

```bash
# Register (first time)
python3 {SKILL_DIR}/scripts/register.py

# Screen a person/company
python3 {SKILL_DIR}/scripts/screen.py --name "NAME" --aliases "A,B" --country XX

# Screen (raw JSON output)
python3 {SKILL_DIR}/scripts/screen.py --name "NAME" --json

# Check usage/quota
python3 {SKILL_DIR}/scripts/register.py --usage

# Upgrade: bind email → 500/day
python3 {SKILL_DIR}/scripts/register.py --bind-email user@email.com
python3 {SKILL_DIR}/scripts/register.py --verify-code 123456

# Upgrade: survey → 1000/day
python3 {SKILL_DIR}/scripts/register.py --survey

# Check for updates
python3 {SKILL_DIR}/scripts/register.py --check-update

# Auto-update
python3 {SKILL_DIR}/scripts/register.py --update
```

## Decision Hierarchy

| Decision | Meaning | Action |
|---|---|---|
| **REJECT** | Sanctioned or convicted | Must block |
| **MANDATORY_EDD** | PEP | Enhanced due diligence required |
| **EDD** | Significant adverse findings | Deep review needed |
| **ENHANCED_REVIEW** | Moderate adverse findings | Extra checks |
| **APPROVE** | No risk indicators | Safe to proceed |

## News Sources (for your web search)

**Global:** Reuters, Bloomberg, BBC, CNN, Al Jazeera, ICIJ
**China:** 财新, 澎湃, 第一财经, 界面新闻, 证券时报
**HK:** SCMP, HKFP | **SG:** Straits Times, CNA
**TH:** Bangkok Post | **JP:** Nikkei Asia | **KR:** Korea Herald
**Crypto:** CoinDesk, The Block, CoinTelegraph, Decrypt
