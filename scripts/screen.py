#!/usr/bin/env python3
"""Screen a person or company via Width Risk & Compliance Database.

Usage:
    python3 scripts/screen.py --name "赵长鹏" --aliases "CZ,Changpeng Zhao" --country CN
    python3 scripts/screen.py --name "Thaksin Shinawatra" --country TH
    python3 scripts/screen.py --name "MetaComp" --country SG --industry crypto

Output: JSON screening result to stdout.
"""
import argparse
import json
import sys
import time
import requests

from config import get_api_key, get_api_url


def screen(name: str, aliases: list = None, country: str = None,
           industry: str = None, context: str = None) -> dict:
    """Submit screening and poll for result."""
    key = get_api_key()
    if not key:
        print("Error: No API key. Run `python3 scripts/register.py` first.", file=sys.stderr)
        sys.exit(1)

    url = get_api_url()
    headers = {"X-API-Key": key, "Content-Type": "application/json"}

    # Submit
    body = {"name": name}
    if aliases:
        body["aliases"] = aliases
    if country:
        body["country"] = country
    if industry:
        body["industry"] = industry
    if context:
        body["context"] = context

    r = requests.post(f"{url}/v1/screening", json=body, headers=headers, timeout=15)
    if r.status_code == 429:
        print("Error: Daily quota exceeded. Upgrade your tier.", file=sys.stderr)
        sys.exit(1)
    if r.status_code == 401:
        print("Error: Invalid API key. Run `python3 scripts/register.py` to re-register.", file=sys.stderr)
        sys.exit(1)
    if r.status_code != 200:
        print(f"Error: {r.status_code} — {r.text}", file=sys.stderr)
        sys.exit(1)

    task = r.json()
    task_id = task["id"]

    # Poll for result (max 30s — API mode is fast, ~2s)
    for i in range(15):
        time.sleep(2)
        r = requests.get(f"{url}/v1/screening/{task_id}", headers=headers, timeout=10)
        data = r.json()

        if data.get("status") == "completed" or data.get("decision"):
            return data  # API returns flat summary with decision/report_url
        elif data.get("status") == "failed":
            print(f"Error: Screening failed — {data.get('error', 'unknown')}", file=sys.stderr)
            sys.exit(1)

        print(f"  [{(i+1)*2}s] {data['status']}...", file=sys.stderr)

    print("Error: Screening timed out after 30s", file=sys.stderr)
    sys.exit(1)


def format_report(result: dict, name: str) -> str:
    """Format screening result as readable report (works with summarized API response)."""
    decision = result.get("decision", "UNKNOWN")
    risk = result.get("risk_level", "unknown").upper()
    report_url = result.get("report_url", "")

    icons = {"REJECT": "🚫", "MANDATORY_EDD": "⚠️", "EDD": "⚠️", "ENHANCED_REVIEW": "🔍", "APPROVE": "✅"}

    lines = []
    lines.append(f"## Width Risk Screening — {name}")
    lines.append(f"")
    lines.append(f"**{icons.get(decision, '❓')} Decision: {decision}** | Risk: {risk}")
    lines.append(f"")
    lines.append(f"### Database Checks")

    for cat_name, cat_key in [("Sanctions", "sanctions"), ("PEP", "pep"), ("Criminal Records", "convicted"), ("Adverse Media", "adverse_media")]:
        c = result.get(cat_key, {})
        if c.get("hit"):
            extra = ""
            if c.get("trigger_count"):
                extra += f" ({c['trigger_count']} triggers)"
            if c.get("article_count"):
                extra += f" — {c['article_count']} articles, max: {c.get('max_severity', '?')}"
            lines.append(f"- 🚨 **{cat_name}: HIT**{extra}")
        else:
            lines.append(f"- ✅ {cat_name}: Clear")

    lines.append(f"")
    lines.append(f"### Decision Reasoning")
    for reason in result.get("decision_reasons", [])[:5]:
        lines.append(f"- {reason}")

    if report_url:
        lines.append(f"")
        lines.append(f"### Full Report")
        lines.append(f"View complete details: {report_url}")

    lines.append(f"")
    lines.append(f"---")
    lines.append(f"*Screened via Width Risk & Compliance Database — kyc.trustin.bond*")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Width Risk Screening")
    parser.add_argument("--name", required=True, help="Person or company name")
    parser.add_argument("--aliases", help="Comma-separated aliases")
    parser.add_argument("--country", help="ISO country code (CN, SG, TH, etc.)")
    parser.add_argument("--industry", help="Industry (crypto, banking, etc.)")
    parser.add_argument("--context", help="Background context")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of report")
    args = parser.parse_args()

    aliases = [a.strip() for a in args.aliases.split(",")] if args.aliases else None

    result = screen(args.name, aliases=aliases, country=args.country,
                    industry=args.industry, context=args.context)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_report(result, args.name))
