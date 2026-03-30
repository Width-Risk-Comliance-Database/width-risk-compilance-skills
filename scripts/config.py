"""Width API configuration — stores API key locally."""
import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".width"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_API_URL = "http://kyc.trustin.bond"
SKILL_VERSION = "1.1.0"
VERSION_CHECK_URL = "https://raw.githubusercontent.com/Width-Risk-Comliance-Database/width-risk-compilance-skills/main/VERSION"


def get_config() -> dict:
    """Load config from ~/.width/config.json"""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(config: dict):
    """Save config to ~/.width/config.json"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_api_key() -> str | None:
    """Get API key from config."""
    return get_config().get("api_key")


def get_api_url() -> str:
    """Get API base URL."""
    return get_config().get("api_url", os.getenv("WIDTH_API_URL", DEFAULT_API_URL))
