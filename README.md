{
  "project": {
    "name": "research-alerts",
    "phase": "2",
    "description": "Research-only stock screener with live market data and cost tracking."
  },
  "data_provider": {
    "provider": "finnhub",
    "api_key": "your_finnhub_api_key_here",
    "market": "us"
  },
  "screening": {
    "source_configured": true,
    "mode": "combined",
    "us_universe": [
      "NVDA",
      "AAPL",
      "MSFT",
      "AMZN",
      "GOOGL"
    ],
    "india_universe": [
      "RELIANCE.NS",
      "TCS.NS",
      "INFY.NS",
      "HDFCBANK.NS"
    ],
    "default_shortlist": [
      "NVDA",
      "AAPL",
      "MSFT"
    ],
    "thresholds": {
      "min_market_cap_usd": 5000000000,
      "min_volume": 1000000,
      "min_price_change_pct_1d": 0.0,
      "min_price_change_pct_5d": 0.0,
      "min_relative_strength_14d": 0.0,
      "research_only": true
    },
    "schedule": {
      "timezone": "UTC",
      "run_minutes": ["09:00", "13:00", "17:00"]
    }
  },
  "telegram": {
    "bot_token": "9270828467:AAHCmITI9u_r3KZIXRdG8tunAYsjEMg0Mbw",
    "chat_id": "1138246643",
    "research_only_disclaimer": "research only",
    "bear_counterpoint": "Bear counter-point: this can be a momentum trap if the move is already priced in."
  },
  "token_cost": {
    "model": "gpt-4o-mini",
    "input_rate_per_1k": 0.15,
    "output_rate_per_1k": 0.60
  }
}
