#!/usr/bin/env python3
from typing import Any, Dict, List


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


def screen_symbols(symbols: List[str], market_data: Dict[str, Dict[str, Any]], thresholds: Dict[str, Any]) -> List[str]:
    shortlisted: List[str] = []
    for symbol in symbols:
        payload = market_data.get(symbol, {})
        if payload.get("error"):
            continue

        price = payload.get("price")
        volume = payload.get("volume")
        market_cap = payload.get("market_cap")

        if price is None:
            continue

        if market_cap is not None and market_cap < thresholds.get("min_market_cap_usd", 0):
            continue

        if volume is not None and volume < thresholds.get("min_volume", 0):
            continue

        day_change_pct = payload.get("day_change_pct")
        if day_change_pct is not None and day_change_pct < thresholds.get("min_price_change_pct_1d", 0.0):
            continue

        shortlisted.append(symbol)

    return shortlisted
