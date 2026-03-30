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

        if data["status"] == "completed":
            return data["result"]
        elif data["status"] == "failed":
            print(f"Error: Screening failed — {data.get('error', 'unknown')}", file=sys.stderr)
            sys.exit(1)

        print(f"  [{(i+1)*2}s] {data['status']}...", file=sys.stderr)

    print("Error: Screening timed out after 30s", file=sys.stderr)
    sys.exit(1)


def format_report(result: dict, name: str) -> str:
    """Format screening result as readable report."""
    decision = result.get("decision", "UNKNOWN")
    risk = result.get("risk_level", "unknown").upper()

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
            lines.append(f"- 🚨 **{cat_name}: HIT**")
            for t in c.get("triggers", [])[:3]:
                if cat_key == "adverse_media":
                    lines.append(f"  - {t.get('count', 0)} articles, max severity: {t.get('max_severity', '?')}")
                elif cat_key == "pep":
                    for d in t.get("detail", [])[:2]:
                        if isinstance(d, dict):
                            lines.append(f"  - {d.get('position', '?')} ({d.get('jurisdiction', '?')})")
                elif cat_key == "sanctions":
                    for d in t.get("detail", [])[:3]:
                        if isinstance(d, dict):
                            lines.append(f"  - {d.get('list', '?')}")
                elif cat_key == "convicted":
                    lines.append(f"  - Criminal conviction on record")
        else:
            lines.append(f"- ✅ {cat_name}: Clear")

    lines.append(f"")
    lines.append(f"### Decision Reasoning")
    for reason in result.get("decision_reasons", [])[:5]:
        lines.append(f"- {reason}")

    lines.append(f"")
    lines.append(f"---")
    lines.append(f"*Screened via Width Risk & Compliance Database — width.info*")

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
