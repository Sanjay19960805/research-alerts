#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib import request, parse


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def normalize_universe(raw_universe: List[str]) -> List[str]:
    seen = set()
    items: List[str] = []
    for item in raw_universe:
        symbol = normalize_symbol(item)
        if symbol and symbol not in seen:
            seen.add(symbol)
            items.append(symbol)
    return items


def build_alert_text(symbol: str, config: Dict[str, Any]) -> str:
    disclaimer = config.get("telegram", {}).get("research_only_disclaimer", "research only")
    bear = config.get("telegram", {}).get("bear_counterpoint", "Bear counter-point: this can be a momentum trap if the setup is already priced in.")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"Phase 1 screening alert for {symbol}\n"
        f"Time: {timestamp}\n"
        f"Reason: screened against the configured Phase 1 thresholds.\n"
        f"{bear}\n"
        f"{disclaimer}\n"
        "This is not a trade recommendation and no order placement or capital deployment is involved."
    )


def telegram_send(message: str, config: Dict[str, Any]) -> bool:
    telegram_cfg = config.get("telegram", {})
    token = str(telegram_cfg.get("bot_token", "")).strip()
    chat_id = str(telegram_cfg.get("chat_id", "")).strip()

    if not token or not chat_id or token in {"[missing data]", "<set-your-token>"} or chat_id in {"[missing data]", "<set-your-chat-id>"}:
        print("Telegram send skipped: [missing data]")
        return False

    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": True,
    }).encode("utf-8")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    headers = {"Content-Type": "application/json"}
    req = request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("ok"):
                print(f"Telegram message sent successfully: {result.get('result', {}).get('message_id')}")
                return True
            print(f"Telegram API rejected the request: {result}")
            return False
    except Exception as exc:  # pragma: no cover - network and API errors are runtime conditions
        print(f"Telegram send failed: {exc}")
        return False


def screen_symbols(config: Dict[str, Any]) -> List[str]:
    screening = config.get("screening", {})
    universe = normalize_universe(screening.get("universe", []))

    # Phase 1 is a screening-only gate. There is no live market data source in this repo.
    # If a source is not configured, we cannot fabricate a value and must report [missing data].
    if not screening.get("source_configured", False):
        print("Market source not configured: [missing data]")
        return []

    shortlisted: List[str] = []
    for symbol in universe:
        # The actual screening logic can be inserted here when a data source is enabled.
        # For this repo, the default is intentionally conservative: no live data = no alert.
        if screening.get("default_shortlist", []) and symbol in screening.get("default_shortlist", []):
            shortlisted.append(symbol)
    return shortlisted


def run_phase_1(config_path: str, dry_run: bool) -> int:
    config = load_config(config_path)
    universe = normalize_universe(config.get("screening", {}).get("universe", []))

    print(f"Phase 1 start: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Configured universe: {', '.join(universe) if universe else '[missing data]'}")

    shortlisted = screen_symbols(config)
    if not shortlisted:
        print("No shortlisted symbols triggered in this run. [missing data]")
    else:
        print(f"Shortlisted symbols: {', '.join(shortlisted)}")

    if dry_run:
        print("Dry run mode enabled. Telegram send was skipped. No live message sent.")
        return 0

    if not shortlisted:
        print("No live alert was sent because there were no shortlisted symbols.")
        return 0

    for symbol in shortlisted:
        alert = build_alert_text(symbol, config)
        telegram_send(alert, config)

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 1 research-only stock screener and Telegram alert sender.")
    parser.add_argument("--config", default="config/config.json", help="Path to the JSON config file.")
    parser.add_argument("--dry-run", action="store_true", help="Print the run plan without sending a Telegram message.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        exit_code = run_phase_1(args.config, args.dry_run)
    except FileNotFoundError:
        print(f"Config file not found: {args.config}")
        print("Create config/config.json from the provided template before running the project.")
        exit_code = 1
    except json.JSONDecodeError:
        print(f"Config file is not valid JSON: {args.config}")
        exit_code = 1
    sys.exit(exit_code)


"""
This Phase 1 project intentionally avoids fabricated data. When live source configuration is absent,
all market values are reported as [missing data] and the workflow does not invent numbers.
"""
