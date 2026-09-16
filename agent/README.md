# Meme Coin Trend Agent

A small CLI agent that reports currently trending Solana meme coins, using
the free [GeckoTerminal](https://www.geckoterminal.com/) API (no API key
needed).

It ranks trending pools by short-term momentum (1h/6h price change plus
volume turnover) and flags basic risk signals (low liquidity, high FDV vs.
liquidity, heavy sell pressure, 24h dumps).

## Usage

```bash
python3 agent/meme_agent.py
```

Options:

- `--pages N` — pages of trending pools to fetch, 20 pools/page (default: 2)
- `--top N` — number of results to show (default: 15)
- `--min-liquidity USD` — filter out pools below this liquidity (default: 5000)

Example:

```bash
python3 agent/meme_agent.py --pages 3 --top 20 --min-liquidity 20000
```

## Disclaimer

This is a research/reporting tool only — it does not place trades, hold
funds, or give financial advice. Meme coins are extremely volatile and
illiquid; you can lose your entire investment. Always verify token
contracts yourself and only risk what you can afford to lose.
