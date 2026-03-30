# Width Risk & Compliance Database

Screen any person or company against **120W+ entities** — sanctions, PEP, criminal records, adverse media — powered by Asia's most comprehensive compliance database.

## Install

```bash
git clone https://github.com/Width-Risk-Comliance-Database/width-risk-compilance-skills.git
cd width-risk-compilance-skills
./install.sh
```

## Usage

Just tell your Agent what you need:

```
"帮我查一下赵长鹏"
"Screen Thaksin Shinawatra"
"Check if 杜均 is safe to onboard"
"Investigate MetaComp, a Singapore crypto company"
"这个人能不能开户：李林，火币创始人"
```

The Agent will:
1. Parse your intent (name, aliases, country, industry)
2. Call Width API for database checks (sanctions, PEP, criminal, adverse media)
3. Search the web for real-time news
4. Present a structured report with a link to full details

## What You Get

```
## Width Risk Screening — 赵长鹏

🚫 Decision: REJECT | Risk: SEVERE

### Database Checks
- ✅ Sanctions: Clear
- ✅ PEP: Clear
- 🚨 Criminal Records: HIT (1 triggers)
- 🚨 Adverse Media: HIT — 19 articles, max: SEVERE

### Full Report
https://kyc.trustin.bond/report/f7c46237-...
```

## Database Coverage

- **120W+ entities** — persons, companies, organizations, vessels
- **42W+ sanctions entries** — OFAC, EU, UN, UK + 116 lists
- **85W+ PEP records** — 255 jurisdictions worldwide
- **15W+ criminal/wanted** — INTERPOL, country-level wanted lists
- **3,000+ regulatory penalties** — China CSRC, PBOC, NFRA, SAFE, SAMR
- **Asia-deep** — CN, HK, SG, TH, JP, KR, PH, ID, VN, MY, AE

## Pricing

Free. No credit card.

| Tier | Limit | How |
|---|---|---|
| Free | 300/day | Auto on first use |
| Email | 500/day | Verify your email |
| Survey | 1,000/day | Answer 6 questions |

## Links

- **Website**: https://kyc.trustin.bond
- **API Docs**: https://kyc.trustin.bond/api-docs
- **Register**: https://kyc.trustin.bond/register
- **GitHub**: https://github.com/Width-Risk-Comliance-Database

## License

MIT
