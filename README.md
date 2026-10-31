# research-alerts

Research-only stock screening and Telegram alerting project. This repo is intentionally scoped to Phase 1 only: screening and alerts, without order placement, broker integration, or capital deployment.

Important guardrails
- No orders are placed.
- No broker integration is implemented.
- No capital deployment occurs in this system.
- No fabricated data is used. If a value is unavailable, the code prints `[missing data]` and stops without inventing a number.
- All thresholds, universe lists, schedule times, and API keys live in one config file: `config/config.json`.
- Every Telegram alert includes a bear counter-point and a research-only disclaimer.
- Token cost awareness is built into the project, but the exact run cost is only known after you configure the model and its pricing.

What Phase 1 does
- Reads the config from `config/config.json`.
- Defines a universe of stocks.
- Applies screener thresholds.
- Produces a shortlist after the screening gate.
- Sends a Telegram message only when a shortlisted stock passes and a Telegram bot is configured.
- Uses a dry-run mode so you can test execution without sending real alerts.

Universe included in the default config
- NVDA
- SK HYNIX
- TSM
- ASML
- CRWD
- AVGO

Files in this repo
- `main.py` — Phase 1 runner and alert sender
- `config/config.json` — one-file source for thresholds, schedule, universe, and Telegram details
- `scripts/run_phase1.sh` — one-command local runner
- `README.md` — project guide

How to run Phase 1
1. Edit `config/config.json`.
2. Set the intended `universe`, thresholds, and Telegram bot details.
3. Run:

```bash
python3 main.py --config config/config.json --dry-run
```

This works without a real Telegram bot token and confirms the project can start cleanly.

If you want the one-command local runner:

```bash
bash scripts/run_phase1.sh
```

Config file details
The file `config/config.json` is the single control point for:
- stock universe
- threshold values
- schedule windows
- Telegram bot token and chat ID
- research-only and bear messaging strings
- token cost placeholders

Do not hardcode secrets in code. Put them in the config file instead.

README phase plan
- Phase 1: screener + Telegram alerting only
- Phase 2: deeper research analysis for shortlisted names only
- Phase 3: scheduling and cron or service automation
- Phase 4: richer sign-off flow and operational monitoring

Token cost estimate
The project is designed to avoid waste. Only shortlisted names go to the detailed analysis phase. The rough per-run token cost is not a fixed number in this repo because the exact model and usage are not configured yet.

The practical formula is:
- cost = (input_tokens + output_tokens) × model_rate_per_1k_tokens

Because the exact model and pricing are not set here, the repo keeps the estimate as `[missing data]` until you configure your model and usage profile.

Telegram alert rules
Every Telegram message must include:
- a bear counter-point
- a research-only disclaimer
- no trade execution language

The code enforces this through the alert builder in `main.py`.

How to tune the project
- change `screening.universe` to your watchlist
- change `screening.thresholds.*` to your desired rules
- change `screening.schedule.run_minutes` to your preferred schedule
- set `telegram.bot_token` and `telegram.chat_id` only in `config/config.json`
- keep the rest of the code generic and config-driven

Operational note
This repo intentionally does not include a broker SDK or any capital-deployment code. It is a research-only workflow, which matches the constraints you specified.

To verify the code in this environment, run the dry-run command above. If the config file is present but no Telegram token is configured, the run reports `[missing data]` instead of inventing data or pretending a live alert succeeded.
