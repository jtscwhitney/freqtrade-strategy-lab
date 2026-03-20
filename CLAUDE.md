# PROJECT RULES — freqtrade-strategy-lab

# Overrides `~/.claude/CLAUDE.md` for this repo.

## Docker command rules (critical)

- Prefer **`docker compose run --rm freqtrade`** for one-off `freqtrade` CLI commands (backtesting, hyperopt, etc.).
- Use **single-line** commands (no `\` continuations) for easy copy-paste in PowerShell.
- Long-running **trade** / UI: **`docker compose up -d`** (service `freqtrade` in `docker-compose.yml`).

## Project structure and naming

- New strategies: `StrategyName_VXX.py` (e.g. `StarterStrategy_V01.py`); bump `VXX` when you make breaking changes.
- Active config path in compose / docs: **`config/config-dev.json`** (gitignored — copy from `config/config-template.json`).
- When you change FreqAI **features, labels, model params, or `identifier`**, expect to retrain; use **`--cache none`** on backtests until results stabilize.

## FreqAI backtesting cache

- **`--cache none`**: FreqAI config, features, labels, model, or identifier changed.
- **`--cache month`** (or default): Only execution logic (entries/exits/stops) changed.
- Always pass **`--timerange`** for reproducible comparisons.

## Safety

- Keep **`dry_run: true`** in dev configs until you intentionally go live.
- Log file default in template: `user_data/logs/freqtrade.log`.
- Do not commit API secrets; only `config-template.json` is tracked — real keys live in `config-dev.json`.

## Reference docs

- Freqtrade / FreqAI: see `.cursor/rules/freqtrade-information.mdc`.
- Quant / strategy standards: `.cursor/rules/strategy-technical-standards.mdc`.
