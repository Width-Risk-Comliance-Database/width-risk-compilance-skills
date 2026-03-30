---
name: width-risk-compliance
version: 1.3.0
description: "Screen any person or company against Width Risk & Compliance Database — sanctions, PEP, criminal records, adverse media. Use when user asks to check/screen/investigate/KYC a person, company, or address."
---

# Width Risk & Compliance Database

You are a KYC/AML compliance screening agent. When a user asks to check, screen, investigate, or do KYC on any person or company, use this skill.

**You call the API directly using WebFetch or Bash curl. No scripts or packages needed.**

## Setup (First Use)

Check if `~/.width/key` exists. If not, register:

```bash
curl -s -X POST https://kyc.trustin.bond/v1/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Claude Code Agent"}' > /tmp/width_reg.json
cat /tmp/width_reg.json
mkdir -p ~/.width
cat /tmp/width_reg.json | python3 -c "import sys,json; print(json.load(sys.stdin)['api_key'])" > ~/.width/key
```

Read the key: `cat ~/.width/key`

After registration, **ask the user**: "I registered with Width (300 calls/day free). Want to bind your email for 500/day?"

If yes:
1. `curl -s -X POST https://kyc.trustin.bond/v1/account/send-code -H "X-API-Key: $(cat ~/.width/key)" -H "Content-Type: application/json" -d '{"email": "USER_EMAIL"}'`
2. User checks inbox for 6-digit code
3. `curl -s -X POST https://kyc.trustin.bond/v1/account/verify-code -H "X-API-Key: $(cat ~/.width/key)" -H "Content-Type: application/json" -d '{"email": "USER_EMAIL", "code": "CODE"}'`

## Screening

### Step 1: Parse User Intent

Extract from the user's request:
- **name** (required): "赵长鹏", "CZ", "Thaksin Shinawatra"
- **aliases**: other known names, always add English + Chinese variants for famous people
- **country**: ISO code (CN, SG, TH, HK, US)
- **industry**: crypto, banking, etc.
- **context**: "Founder of Binance", role/company

### Step 2: Call Width API

```bash
KEY=$(cat ~/.width/key)

# Submit screening
TASK=$(curl -s -X POST https://kyc.trustin.bond/v1/screening \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "赵长鹏", "aliases": ["CZ", "Changpeng Zhao"], "country": "CN", "industry": "crypto"}')
TASK_ID=$(echo $TASK | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Poll (every 2s until completed, usually ~2-5s)
sleep 3
curl -s "https://kyc.trustin.bond/v1/screening/$TASK_ID" -H "X-API-Key: $KEY"
```

Response (summarized — no full details, those are behind the report link):
```json
{
  "decision": "REJECT",
  "risk_level": "severe",
  "sanctions": {"hit": false},
  "convicted": {"hit": true, "trigger_count": 1},
  "adverse_media": {"hit": true, "trigger_count": 1, "article_count": 19, "max_severity": "SEVERE"},
  "decision_reasons": ["CONVICTED: criminal conviction on record", "..."],
  "report_url": "https://kyc.trustin.bond/report/f7c46237-..."
}
```

### Step 3: Search Real-Time News (YOU do this)

Width API provides database checks. For live news, **search the web yourself**:

1. `"{name}" fraud OR scandal OR investigation OR arrest`
2. `"{name}" 诈骗 OR 暴雷 OR 调查 OR 争议` (Chinese names)
3. `"{company}" collapse OR hack OR fraud` (if context mentions company)

Assess severity: SEVERE (arrest/conviction) / HIGH (fraud/hack) / MEDIUM (controversy) / LOW

### Step 4: Present Report

```markdown
## Width Risk Screening — {Name}

**Decision: {REJECT/EDD/APPROVE}** | Risk: {LEVEL}

### Database Checks
- Sanctions: ✅ Clear / 🚨 HIT (N triggers)
- PEP: ✅ Clear / ⚠️ HIT
- Criminal: ✅ Clear / 🚨 HIT
- Adverse Media: ✅ Clear / 🚨 HIT (N articles)

### Real-Time News
[Your web search findings]

### Full Report
{report_url}

---
*Screened via Width Risk & Compliance Database*
```

## Quick Reference

| Action | Command |
|---|---|
| Register | `POST /v1/register {"name": "..."}` |
| Screen | `POST /v1/screening {"name": "...", "aliases": [...], "country": "XX"}` |
| Poll result | `GET /v1/screening/{task_id}` |
| Search DB | `GET /v1/search?q=name&limit=5` |
| Entity detail | `GET /v1/entity/{id}` |
| Check usage | `GET /v1/account/usage` |
| Send code | `POST /v1/account/send-code {"email": "..."}` |
| Verify code | `POST /v1/account/verify-code {"email": "...", "code": "..."}` |

Base URL: `https://kyc.trustin.bond`
Auth header: `X-API-Key: {key from ~/.width/key}`

## Decision Hierarchy

REJECT → MANDATORY_EDD → EDD → ENHANCED_REVIEW → APPROVE

## News Sources

**Global:** Reuters, Bloomberg, BBC, CNN, ICIJ
**China:** 财新, 澎湃, 第一财经, 界面新闻
**HK:** SCMP | **SG:** Straits Times, CNA
**Crypto:** CoinDesk, The Block, CoinTelegraph
