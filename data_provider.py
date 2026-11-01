#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib import request

from costing import summarize_cost
from data_provider import fetch_market_data
from screening import normalize_universe, screen_symbols


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_universe(config: Dict[str, Any]) -> List[str]:
    screening_cfg = config.get("screening", {})
    mode = (screening_cfg.get("mode") or "combined").lower()

    if mode == "us_only":
        return normalize_universe(screening_cfg.get("us_universe", []))
    if mode == "india_only":
        return normalize_universe(screening_cfg.get("india_universe", []))

    us_symbols = normalize_universe(screening_cfg.get("us_universe", []))
    india_symbols = normalize_universe(screening_cfg.get("india_universe", []))
    default_symbols = normalize_universe(screening_cfg.get("default_shortlist", []))

    if default_symbols:
        return default_symbols
    return us_symbols + india_symbols


def build_alert_text(symbol: str, config: Dict[str, Any]) -> str:
    disclaimer = config.get("telegram", {}).get("research_only_disclaimer", "research only")
    bear = config.get("telegram", {}).get("bear_counterpoint", "Bear counter-point: this can be a momentum trap if the move is already priced in.")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"Phase 2 screening alert for {symbol}\n"
        f"Time: {timestamp}\n"
        f"Reason: screened against the configured Phase 2 threshold set.\n"
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
    except Exception as exc:
        print(f"Telegram send failed: {exc}")
        return False


def run_phase_2(config_path: str, dry_run: bool) -> int:
    config = load_config(config_path)
    screening_cfg = config.get("screening", {})
    provider_cfg = config.get("data_provider", {})
    token_cfg = config.get("token_cost", {})

    if not screening_cfg.get("source_configured", False):
        print("Market source not configured: [missing data]")
        return 0

    universe = resolve_universe(config)
    if not universe:
        print("No configured universe in config/config.json")
        return 0

    print(f"Phase 2 start: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Universe count: {len(universe)}")
    print(f"Universe: {', '.join(universe)}")

    market_data = fetch_market_data(universe, provider_cfg)
    shortlisted = screen_symbols(universe, market_data, screening_cfg.get("thresholds", {}))

    if not shortlisted:
        print("No shortlisted symbols after screening.")
        return 0

    print(f"Qualified symbols: {', '.join(shortlisted)}")

    input_tokens = 1200
    output_tokens = 400
    cost_summary = summarize_cost(token_cfg, input_tokens, output_tokens)
    print(f"Estimated token cost: ${cost_summary['total_cost']:.4f} USD")

    if dry_run:
        print("Dry run mode enabled. Telegram send was skipped.")
        return 0

    for symbol in shortlisted:
        alert = build_alert_text(symbol, config)
        telegram_send(alert, config)

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 2 research-only stock screener with market data and Telegram alerts.")
    parser.add_argument("--config", default="config/config.json", help="Path to the JSON config file.")
    parser.add_argument("--dry-run", action="store_true", help="Print the run plan without sending a Telegram message.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        exit_code = run_phase_2(args.config, args.dry_run)
    except FileNotFoundError:
        print(f"Config file not found: {args.config}")
        exit_code = 1
    except json.JSONDecodeError:
        print(f"Config file is not valid JSON: {args.config}")
        exit_code = 1
    sys.exit(exit_code)
