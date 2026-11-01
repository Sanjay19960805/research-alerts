# research-alerts

Research-only stock screening and Telegram alerting project.

Important guardrails
- No orders are placed.
- No broker integration is implemented.
- No capital deployment occurs in this system.
- No fabricated data is used. If a value is unavailable, the code prints `[missing data]` and stops without inventing a number.
- All thresholds, universe lists, schedule times, and API keys live in one config file: `config/config.json`.
- Every Telegram alert includes a bear counter-point and a research-only disclaimer.
- Token cost awareness is built into the project so each run can report an exact estimate.

What Phase 2 does
- Reads the config from `config/config.json`.
- Supports a real data provider (for example: Finnhub).
- Resolves a combined or mode-based universe.
- Applies screener thresholds.
- Produces a shortlist after the screening gate.
- Sends a Telegram message only for shortlisted names.
- Tracks approximate token cost for the run.

Files in this repo
- `main.py` — Phase 2 runner and alert sender
- `data_provider.py` — live market-data adapter
- `screening.py` — shortlist generation
- `costing.py` — token cost tracking
- `config/config.json` — one-file source for thresholds, schedule, universe, and Telegram details
- `scripts/run_phase2.sh` — one-command local runner
- `README.md` — project guide

How to run Phase 2
1. Edit `config/config.json`.
2. Set your data provider API key.
3. Update the `default_shortlist` and/or `us_universe` and `india_universe` lists.
4. Run:

```bash
python3 main.py --config config/config.json --dry-run
```

If you want the one-command local runner:

```bash
bash scripts/run_phase2.sh
```

Config file details
The file `config/config.json` is the single control point for:
- stock universe
- threshold values
- schedule windows
- data provider settings
- Telegram bot token and chat ID
- research-only and bear messaging strings
- token cost settings

Do not hardcode secrets in code. Put them in the config file instead.

Telemetry and cost tracking
The project is designed to avoid waste. Only shortlisted names go to the detailed analysis phase. The cost model is simple and transparent:

- cost = (input_tokens / 1000 * input_rate_per_1k) + (output_tokens / 1000 * output_rate_per_1k)

This keeps monitoring predictable and easy to audit.

Telegram alert rules
Every Telegram message must include:
- a bear counter-point
- a research-only disclaimer
- no trade execution language

The code enforces this through the alert builder in `main.py`.

Operational note
This repo intentionally does not include broker SDK code or capital-deployment logic. It is a research-only workflow that matches the constraints you specified.

To verify the code in this environment, run the dry-run command above. If the config file is present but no live provider is configured, the run reports `[missing data]` instead of inventing data.

Phase plan
- Phase 1: screener + Telegram alerting only
- Phase 2: market-data adapter + shortlist logic + token cost tracking
- Phase 3: scheduling and cron/service automation
- Phase 4: richer sign-off flow and operational monitoring
