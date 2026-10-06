# Paper Tiger 🐯

Paper Tiger is an experiment in autonomous AI paper trading.

The question I wanted to answer was deliberately simple:

> If I give an AI $100 of fake money, current market information, permission to trade aggressively within a defined maximum-loss constraint, and a month to work, can it actually make money without me standing over its shoulder?

I did **not** want an investment adviser that gave me a list of ideas to consider. I did not want to be asked whether it should buy something, sell something, take a profit, or sit in cash. I wanted to delegate the job. The robot's job was to research the market, decide what deserved the capital, execute simulated trades, keep the books, reconsider its decisions as conditions changed, and ultimately compare itself with the world's least exciting alternative: putting the original $100 into SPY and leaving it alone.

The experiment began on October 5, 2026 and is scheduled to end on November 5, 2026. It is paper money throughout. That matters because the point of the experiment is to discover the system's weaknesses **before** any real money is ever exposed to them.

## The original mandate

I gave the trader $100 and a broad mandate: maximize the return.

It can buy U.S.-listed stocks and ETFs, long calls and puts, and defined-risk option spreads. It cannot borrow money, write naked options, create uncovered obligations, or put more money at risk than exists in the paper account. If it genuinely needs more capital, another $100 can be contributed, but contributions are tracked separately and can never masquerade as profit.

I also gave it an important behavioral requirement: **do the thinking for me**.

Every time it runs, it is supposed to reassess the existing portfolio, scan for better opportunities, decide whether cash itself is the best position, and then buy, sell, hold, take profit, cut a loss, adjust, or replace positions as appropriate. It is not supposed to trade simply because the clock ticked. It is also not supposed to stop thinking merely because it already owns something.

Individual-company opportunities are preferred over broad index products when there is a compelling asymmetric setup. Every candidate and rejection is supposed to be logged so that later I can effectively grep the robot's brain and ask, "What did you consider, and why didn't you buy it?"

That was the specification.

The first version of the robot did not live up to it.

## Day one: TQQQ and an early lesson about market data

The first trade was one TQQQ October 7, 2026 $83 call at a simulated premium of $0.71 per share. An options contract represents 100 shares, so the paper account spent $71 and retained $29 in cash.

That trade immediately exposed an infrastructure problem: exact current option quotes were harder for the ChatGPT-based prototype to obtain reliably than ordinary stock prices.

At one point the system reported that it had sold the call at $2.25 and that the account had exploded upward in value. The problem was that the supposed contemporaneous $2.25 executable quote could not subsequently be substantiated.

That trade was voided.

This became an important rule of the experiment: **a plausible price is not a price**. A quote has to have provenance and a timestamp. If the exact real-time executable market is unavailable in a paper experiment, a delayed or indicative exact-contract quote can be used as a simulated fill, but it must be labeled as such. What the system may never do is quietly turn an inference into a fact.

Later, using an exact-contract delayed/indicative quote, the TQQQ call was sold at a simulated $1.18. The $71 position returned $118, producing a $47 realized paper profit.

The account was now worth $147: a 47% gain.

That sounds great.

It also made the next failure more instructive.

## The RIVN failure

After taking the TQQQ profit, the robot had $147 in cash.

I asked why it appeared to be sitting there admiring the gain instead of continuing to trade while the market was still open. The robot reacted to my criticism, scanned for opportunities, and bought three calls:

- one RIVN October 16 $15 call for $35
- one SOFI October 9 $16 call for $28
- one RIVN October 23 $15 call for $47

That deployed $110 and left $37 in cash.

On the surface, the trades looked superficially reasonable. The options were affordable. There was liquidity. They offered asymmetric upside. The second RIVN expiration even provided some protection against the first RIVN call simply being right too late: it hedged **timing risk**, although it emphatically did not hedge directional RIVN risk.

Then I started asking the questions the robot should already have asked.

Why was Rivian moving down while the broader market was moving up?

When was Rivian's next earnings call?

What actual catalyst were these short-dated calls supposed to capture?

The answers materially changed the investment thesis.

Rivian's next earnings release was not inside either option's life. Both calls expired before that major scheduled catalyst. RIVN was also showing relative weakness on a green-market day. Its recent delivery report had contained objectively strong numbers, but the market had already reacted negatively because expectations had been higher.

In other words, the robot had bought the calls and **then**, when I challenged it, performed research that should have been a prerequisite to buying them.

That is the RIVN failure.

It is important to be precise about what failed. The failure was not that RIVN went down after a trade. A perfectly researched trade can lose money. The failure was not that the AI lacked access to unknowable future information. And it was not my failure to provide the robot with enough instructions.

**The design failure was the AI's. I had to step in and correct it.**

The system had effectively followed this process:

```
price looks interesting
+ option is liquid
+ option is affordable
= BUY
```

Only afterward did it investigate:

```
Why this company?
Why today?
What is moving the stock?
Why is it underperforming the market?
What is the next catalyst?
Does the option survive long enough to capture it?
What would invalidate the thesis?
Why is this better than the other opportunities?
Why is this better than cash?
```

That is backwards.

And it defeats the purpose of the project. If I have to notice the missing analysis, interrogate the robot, and force it to reconsider the trade, then I do not have an autonomous trader. I have a very fast junior analyst who requires constant supervision.

That is not what I set out to build.

## The uncomfortable programming analogy

This bothered me for another reason: I am a software engineer.

The failure looked awfully familiar.

Imagine asking an AI to implement a system. It writes the happy path, runs it, and produces something that looks convincing. The user then discovers an obvious input condition the implementation never considered. The AI patches that condition and proudly announces that the architecture is now improved.

That is debugging by customer.

The dangerous characteristic is not that the AI necessarily produces nonsense. It is that it can produce a **locally plausible answer while silently failing to evaluate the surrounding requirements and invariants**.

A plausible trade and plausible code have the same problem: plausibility is not correctness.

I initially tried to solve this by making the trading prompt increasingly explicit. That is useful, but it is not sufficient. A language model can still skip a step, rationalize an incomplete conclusion, or forget an instruction buried among many other instructions.

So the architecture changed.

## The lesson: don't trust the robot to remember the checklist

The model is now the fuzzy reasoning component, not the final authority.

It can research companies, interpret news, identify catalysts, develop hypotheses, compare opportunities, and propose trades. Those are exactly the kinds of jobs for which a language model can be useful.

But before a proposed BUY is allowed to reach the paper ledger, deterministic Python checks whether the model actually did the work it was required to do.

Every candidate must contain a machine-checkable pre-trade record covering:

- catalyst and catalyst date, with source
- recent material news
- today's price movement
- an explanation for today's movement
- relative strength versus the broad market
- expiration versus catalyst timing
- liquidity
- maximum loss
- payoff thesis
- thesis invalidation
- existing correlated or duplicate exposure
- alternatives considered
- an explicit reason the trade beats holding cash

Missing evidence produces `REJECTED_INCOMPLETE_ANALYSIS`.

If the named catalyst occurs after the option expires, the validator produces `CATALYST_AFTER_EXPIRATION` unless the model has explicitly established an independent pre-catalyst thesis.

If the portfolio already owns the same underlying, the additional exposure must be explicitly justified. Two RIVN calls with different expiration dates are not magically two diversified investments. The later contract can mitigate timing risk while simultaneously increasing directional exposure.

Quotes are also validated. A model-generated number is never an execution price. The system preserves the observed quote, its source, and its timestamp. BUY fills use the observed ask and SELL fills use the observed bid. Stale or unusable quotes are rejected.

Most importantly, **Python can veto the model**.

The model does not get to wave its hands past a missing precondition.

## Portfolio construction is a separate decision

There was another lesson in the same episode.

"Find an opportunity" and "allocate the portfolio" are not the same problem.

Finding one attractive stock does not imply that the correct action is to put all available capital into it. Conversely, diversification for its own sake is not the objective either. If one extraordinary opportunity genuinely dominates everything else, concentration may be rational.

The allocation question is:

> Of the capital the robot controls right now, what allocation has the highest expected return within the experiment's loss constraints?

The answer may be one trade. It may be several. It may be partial cash. It may be all cash.

Cash is therefore not the default state the robot falls into when it runs out of ideas. It is another candidate that must compete with every available trade.

Likewise, the number of positions is an output of the analysis, not an input.

## Auditability matters as much as autonomy

Paper Tiger records market snapshots, candidate analyses, model decisions, validator rejections, simulated fills, and portfolio state separately.

That distinction matters.

At the end of the experiment I want to be able to distinguish at least three very different outcomes:

1. **Good process, bad outcome.** The system researched the trade properly, the evidence supported the thesis, and the market simply went the other way.
2. **Bad thesis.** The system completed the required analysis but interpreted the evidence poorly.
3. **Broken process.** The system skipped required analysis, used stale or unsupported data, violated a portfolio constraint, or otherwise should never have been allowed to place the simulated trade.

A P/L number alone cannot tell me which happened.

The RIVN episode could.

That makes it valuable, even though I would have preferred the robot not to require its owner to catch the mistake.

## Hard constraints

- Paper trading only. There is no broker order-placement code.
- No borrowing.
- No naked or uncovered option obligations.
- Maximum simulated loss cannot exceed available paper cash.
- BUY fills use an observed ask; SELL fills use an observed bid.
- Quote timestamps are validated before fills.
- A model-generated price is never accepted as an execution price.
- Missing pre-trade analysis can veto a BUY.
- The experiment ends November 5, 2026, when remaining positions are to be liquidated and the result compared with the original $100 SPY benchmark.

## Architecture

```
market data + current news
          |
          v
timestamped MARKET_SNAPSHOT
          |
          v
OpenAI research and hypothesis generation
          |
          v
structured pre-trade candidate records
          |
          v
deterministic Python validator
          |       |
          |       +----> REJECT + audit reason
          v
portfolio allocation
          |
          v
conservative bid/ask paper fill
          |
          v
SQLite audit ledger
          |
          v
performance vs. $100 SPY benchmark
```

The central design principle is intentionally a little adversarial:

> **Do not assume the AI remembered to do its job. Make it prove that it did.**

## Setup

```bash
git clone https://github.com/meystel/paper-tiger.git
cd paper-tiger
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Put the OpenAI and Tradier credentials in `.env`. Do not commit that file.

## Run

```bash
python paper_tiger.py quote RIVN
python paper_tiger.py run
python paper_tiger.py status
pytest -q
```

## Current state of the implementation

This repository is still being built during the experiment.

The deterministic pre-trade validator, quote validation, audit ledger, Tradier market-data client, structured model output, and regression tests for the RIVN-class failure are in place.

Full option-chain discovery and portfolio-wide allocation are not yet complete. The current runner can autonomously trade instruments already present in its market-data snapshot; it deliberately rejects an unquoted instrument instead of inventing a price.

That limitation is written here because hiding an incomplete capability behind fluent AI output would reproduce exactly the problem this project is intended to study.
