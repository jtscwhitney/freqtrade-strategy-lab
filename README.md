# freqtrade-strategy-lab

Greenfield **Freqtrade + FreqAI** strategy development. Same workflow as `freqtrade-scalper`: local Docker build from your `Freqtrade` fork/source tree, backtests, refinements, then push to GitHub.

## Prerequisites

1. **Freqtrade source** next to this repo (matches `docker-compose.yml` build context):

   ```
   Documents/
     Freqtrade/              ← build context
     freqtrade-scalper/
     freqtrade-strategy-lab/ ← this repo
   ```

2. **Docker** (optional: NVIDIA GPU for FreqAI training as in compose file).

## First-time setup

1. **Config (not committed — copy template):**

   ```powershell
   Copy-Item config\config-template.json config\config-dev.json
   ```

   Edit `config/config-dev.json`: exchange keys, `freqai.identifier` (change when you change features/models), JWT/password if needed.

2. **Run the bot (dry-run):**

   ```powershell
   docker compose up -d
   ```

   Web UI / API: `http://localhost:8080` (default credentials in template — change for anything beyond local lab).

3. **One-off CLI (backtest / hyperopt):**

   All `freqtrade` invocations should use the compose service (see `CLAUDE.md`). Example:

   ```powershell
   docker compose run --rm freqtrade backtesting --config /freqtrade/config/config-dev.json --strategy StarterStrategy_V01 --freqaimodel XGBoostRegressor --timerange 20230101-20240101 --cache none
   ```

## Layout

| Path | Purpose |
|------|---------|
| `config/config-template.json` | Committed template; copy to `config-dev.json` |
| `user_data/strategies/` | Strategy modules (e.g. `StarterStrategy_V01.py`) |
| `user_data/info/` | Design notes, deep dives |
| `.cursor/rules/` | Cursor project rules |
| `CLAUDE.md` | Claude Code / project conventions |
| `deploy/` | Optional deployment notes/scripts (fill in when needed) |

## GitHub

Create a new empty repository on GitHub, then:

```powershell
cd freqtrade-strategy-lab
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git branch -M main
git push -u origin main
```

## Decisions you may want to adjust

- **Folder / GitHub repo name:** This scaffold uses `freqtrade-strategy-lab`; rename the folder and remote if you prefer.
- **Ports:** Default API port is `8080`. Change in `config-dev.json` and `docker-compose.yml` if it clashes with scalper/Kinetic.
- **GPU:** The compose file requests an NVIDIA GPU; comment out `deploy.resources` if you run CPU-only builds.
