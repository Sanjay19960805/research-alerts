#!/usr/bin/env python3
import json
from typing import Any, Dict, List
from urllib import request


def fetch_finnhub_quote(symbol: str, api_key: str) -> Dict[str, Any]:
    cleaned_symbol = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
    url = f"https://finnhub.io/api/v1/quote?symbol={cleaned_symbol}&token={api_key}"
    try:
        with request.urlopen(url, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return {
                "symbol": symbol,
                "price": payload.get("c"),
                "previous_close": payload.get("pc"),
                "day_change": payload.get("d"),
                "day_change_pct": payload.get("dp"),
                "volume": payload.get("v"),
                "market_cap": None,
                "error": None,
            }
    except Exception as exc:
        return {
            "symbol": symbol,
            "price": None,
            "previous_close": None,
            "day_change": None,
            "day_change_pct": None,
            "volume": None,
            "market_cap": None,
            "error": str(exc),
        }


def fetch_market_data(symbols: List[str], provider_cfg: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    provider = (provider_cfg.get("provider") or "finnhub").lower()
    api_key = str(provider_cfg.get("api_key", "")).strip()

    if not api_key:
        return {
            symbol: {"symbol": symbol, "price": None, "volume": None, "market_cap": None, "error": "missing api key"}
            for symbol in symbols
        }

    market_data: Dict[str, Dict[str, Any]] = {}
    for symbol in symbols:
        if provider == "finnhub":
            market_data[symbol] = fetch_finnhub_quote(symbol, api_key)
        else:
            market_data[symbol] = {
                "symbol": symbol,
                "price": None,
                "volume": None,
                "market_cap": None,
                "error": f"unsupported provider {provider}",
            }
    return market_data
