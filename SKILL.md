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

Width API provides database checks. For live news, **search the web yourself in the person's local language**:

**Always search in English:**
- `"{name}" fraud OR scandal OR investigation OR arrest OR sanctions`

**Then search in their local language based on country:**

| Country | Search Terms | Priority Media |
|---|---|---|
| 🇨🇳 CN | `"{名字}" 诈骗 OR 暴雷 OR 调查 OR 争议 OR 制裁 OR 洗钱 OR 跑路` | 财新 Caixin, 澎湃 The Paper, 第一财经, 界面新闻, 证券时报 |
| 🇭🇰 HK | Same as CN + `"{name}" HKMA OR SFC OR ICAC` | SCMP, HKFP, The Standard |
| 🇸🇬 SG | `"{name}" MAS OR fraud OR charged` | Straits Times, CNA, Business Times |
| 🇹🇭 TH | `"{ชื่อ}" ฉ้อโกง OR ฟอกเงิน OR สอบสวน OR อายัด OR ป.ป.ง.` | Bangkok Post, The Nation, Thai PBS, กรุงเทพธุรกิจ |
| 🇮🇩 ID | `"{nama}" penipuan OR korupsi OR pencucian uang OR OJK OR PPATK` | Kompas, Tempo, Detik, Bisnis Indonesia |
| 🇻🇳 VN | `"{tên}" lừa đảo OR rửa tiền OR điều tra OR vi phạm` | VnExpress, Thanh Niên, Tuổi Trẻ |
| 🇵🇭 PH | `"{name}" fraud OR AMLC OR Sandiganbayan OR graft` | Philippine Star, Inquirer, Rappler |
| 🇲🇾 MY | `"{nama}" penipuan OR rasuah OR BNM OR SC Malaysia` | The Star, New Straits Times, Malay Mail |
| 🇯🇵 JP | `"{名前}" 詐欺 OR 逮捕 OR 行政処分 OR マネーロンダリング OR 金融庁` | 日経 Nikkei, Japan Times, NHK, 朝日新聞 |
| 🇰🇷 KR | `"{이름}" 사기 OR 체포 OR 수사 OR 제재 OR 금감원` | Korea Herald, 매일경제, 조선일보, 한국경제 |
| 🇦🇪 AE | `"{name}" DFSA OR ADGM OR fraud` | The National, Arabian Business, Gulf News |
| 🇮🇳 IN | `"{name}" SEBI OR ED OR RBI OR fraud OR arrest` | Economic Times, LiveMint, NDTV |

**If context mentions a company, also search:**
- `"{company}" collapse OR hack OR fraud OR depeg OR bankruptcy`

**Assess each finding:**
- **SEVERE**: arrest, conviction, prison sentence
- **HIGH**: fraud charges, hack/exploit, investigation, sanctions
- **MEDIUM**: regulatory fine, controversy, conflict of interest
- **LOW**: minor dispute, historical (3+ years old)

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
