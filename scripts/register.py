#!/usr/bin/env python3
"""Register for a Width API key, bind email, or complete survey.

Usage:
    python3 scripts/register.py                          # Register (free, 300/day)
    python3 scripts/register.py --bind-email you@x.com   # Send verification code
    python3 scripts/register.py --verify-code 123456      # Verify and upgrade to 500/day
    python3 scripts/register.py --survey                  # Complete survey for 1000/day
    python3 scripts/register.py --usage                   # Check current usage
"""
import argparse
import json
import sys
import requests

from config import get_config, save_config, get_api_key, get_api_url


def register(name: str):
    """Register a new API key."""
    url = get_api_url()
    r = requests.post(f"{url}/v1/register", json={"name": name}, timeout=10)
    if r.status_code != 200:
        print(f"Error: {r.json().get('detail', r.text)}")
        sys.exit(1)

    data = r.json()
    save_config({"api_key": data["api_key"], "api_url": url, "name": name, "tier": data["tier"]})

    print(f"✅ Registered successfully!")
    print(f"   API Key:  {data['api_key']}")
    print(f"   Tier:     {data['tier']}")
    print(f"   Limit:    {data['daily_limit']}/day")
    print(f"   Saved to: ~/.width/config.json")
    return data


def bind_email(email: str):
    """Send verification code to email."""
    key = get_api_key()
    if not key:
        print("No API key found. Run `python3 scripts/register.py` first.")
        sys.exit(1)

    url = get_api_url()
    r = requests.post(f"{url}/v1/account/send-code",
                      json={"email": email},
                      headers={"X-API-Key": key}, timeout=10)
    if r.status_code != 200:
        print(f"Error: {r.json().get('detail', r.text)}")
        sys.exit(1)

    print(f"✅ Verification code sent to {email}")
    print(f"   Check your inbox and run:")
    print(f"   python3 scripts/register.py --verify-code CODE")


def verify_code(email: str, code: str):
    """Verify code and bind email → upgrade to 500/day."""
    key = get_api_key()
    url = get_api_url()
    r = requests.post(f"{url}/v1/account/verify-code",
                      json={"email": email, "code": code},
                      headers={"X-API-Key": key}, timeout=10)
    if r.status_code != 200:
        print(f"Error: {r.json().get('detail', r.text)}")
        sys.exit(1)

    data = r.json()
    if data.get("upgraded"):
        config = get_config()
        config["tier"] = data["tier"]
        config["email"] = email
        save_config(config)
        print(f"✅ Email verified! Upgraded to {data['tier']} tier ({data['daily_limit']}/day)")
    else:
        print(f"Failed: {data.get('reason', 'Unknown')}")


def do_survey():
    """Interactive survey for 1000/day upgrade."""
    key = get_api_key()
    url = get_api_url()

    # Get questions
    r = requests.get(f"{url}/v1/account/survey/questions", headers={"X-API-Key": key}, timeout=10)
    questions = r.json()["questions"]

    print("📋 Width Survey — answer these questions to unlock 1,000 requests/day")
    print("   ⚠️  Quality answers required. Low-effort responses will be rejected.\n")

    answers = {}
    for q in questions:
        print(f"  {q['question']}")
        print(f"  {q['question_cn']}")
        if q.get("options"):
            for i, opt in enumerate(q["options"], 1):
                print(f"    {i}. {opt}")
            while True:
                choice = input("  → ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(q["options"]):
                    answers[q["id"]] = q["options"][int(choice) - 1]
                    break
                elif choice in q["options"]:
                    answers[q["id"]] = choice
                    break
                print("  Invalid choice, try again.")
        else:
            answers[q["id"]] = input("  → ").strip()
        print()

    # Submit
    r = requests.post(f"{url}/v1/account/survey",
                      json={"answers": answers},
                      headers={"X-API-Key": key}, timeout=10)
    data = r.json()
    if data.get("submitted"):
        config = get_config()
        config["survey_status"] = "pending"
        save_config(config)
        print("✅ Survey submitted! Pending admin review.")
        print("   You'll be upgraded to 1,000/day once approved.")
    else:
        print(f"Failed: {data.get('reason', 'Unknown')}")


def check_usage():
    """Check current usage and quota."""
    key = get_api_key()
    if not key:
        print("No API key found. Run `python3 scripts/register.py` first.")
        sys.exit(1)

    url = get_api_url()
    r = requests.get(f"{url}/v1/account/usage", headers={"X-API-Key": key}, timeout=10)
    data = r.json()
    print(f"  API Key:   {key[:8]}...")
    print(f"  Tier:      {data['tier']}")
    print(f"  Email:     {data['email'] or '(none)'}")
    print(f"  Used:      {data['used_today']}/{data['daily_limit']}")
    print(f"  Remaining: {data['remaining']}")
    print(f"  Status:    {data['status']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Width Risk & Compliance — API Key Management")
    parser.add_argument("--name", default="Claude Code Agent", help="Agent name for registration")
    parser.add_argument("--bind-email", metavar="EMAIL", help="Send verification code to this email")
    parser.add_argument("--verify-code", metavar="CODE", help="Verify email with 6-digit code")
    parser.add_argument("--email", help="Email for verify-code (reads from config if bound)")
    parser.add_argument("--survey", action="store_true", help="Complete survey for 1000/day")
    parser.add_argument("--usage", action="store_true", help="Check current usage")
    args = parser.parse_args()

    if args.usage:
        check_usage()
    elif args.bind_email:
        bind_email(args.bind_email)
    elif args.verify_code:
        email = args.email or get_config().get("email", "")
        if not email:
            email = input("Email: ").strip()
        verify_code(email, args.verify_code)
    elif args.survey:
        do_survey()
    elif not get_api_key():
        register(args.name)
    else:
        print(f"Already registered. Key: {get_api_key()[:8]}...")
        check_usage()
