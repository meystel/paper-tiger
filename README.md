# Paper Tiger 🐯

Autonomous **paper-only** trading experiment. Tradier supplies market data; OpenAI researches and proposes opportunities; deterministic Python validates every proposed BUY before any simulated fill is recorded.

## What changed after the RIVN failure

The model is not trusted to remember the investment checklist. A proposed BUY must carry a complete pre-trade record:

- catalyst and date, with source
- recent material news
- today's move and an explanation for it
- relative strength vs. the broad market
- expiration/catalyst timing
- liquidity
- maximum loss
- payoff thesis and invalidation
- correlated/duplicate exposure
- alternatives considered
- explicit reason the trade beats cash

Missing evidence produces `REJECTED_INCOMPLETE_ANALYSIS`. A catalyst after option expiration produces `CATALYST_AFTER_EXPIRATION` unless the proposal explicitly establishes a separate pre-catalyst thesis. Same-underlying exposure must be explicitly justified. Quotes are rejected when stale or not two-sided.

The audit database records market snapshots, model decisions, validator rejections, and simulated actions separately, so a bad thesis can be distinguished from a broken decision process.

## Hard constraints

- Paper trading only. There is no broker order-placement code.
- No borrowing.
- No naked/uncovered option obligations.
- Maximum simulated loss cannot exceed available paper cash.
- BUY fills use the observed ask; SELL fills use the observed bid.
- Tradier quote timestamps are validated before fills.
- A model-generated price is never accepted as an execution price.

## Setup

```bash
git clone https://github.com/meystel/paper-tiger.git
cd paper-tiger
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Put your keys in `.env`. Do not commit that file.

For current Tradier production market data, use the production base URL already shown in `.env.example`. Tradier's sandbox is intentionally delayed; this project performs its own paper accounting and therefore does not need to submit broker orders.

## Run

```bash
python paper_tiger.py quote RIVN
python paper_tiger.py run
python paper_tiger.py status
pytest -q
```

## Architecture

```
Tradier market data
        |
        v
timestamped MARKET_SNAPSHOT
        |
        v
OpenAI + web research
        |
        v
structured candidate records
        |
        v
deterministic validator  <--- can veto the model
        |
        v
conservative bid/ask paper fill
        |
        v
SQLite audit ledger
```

## Current limitation

The current runner can autonomously trade instruments already present in its market-data snapshot. Full option-chain discovery/selection and portfolio-wide allocation are the next implementation layer; the validator deliberately rejects an unquoted option instead of fabricating a price. This limitation is explicit rather than hidden behind model reasoning.
