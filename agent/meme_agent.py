#!/usr/bin/env python3
"""
Meme coin trend agent for Solana.

Pulls trending Solana liquidity pools from the free GeckoTerminal API
(no API key required) and prints a ranked report with momentum and
risk signals to help you spot what's currently fomo-ing.

This is a research/reporting tool only. It does not place trades and
makes no financial guarantees -- meme coins are extremely volatile and
you can lose everything you put in. Always do your own research.

Usage:
    python3 meme_agent.py [--pages N] [--top N] [--min-liquidity USD]
"""

import argparse
import math
import re
import sys
import urllib.error
import urllib.request
import json

API_URL = "https://api.geckoterminal.com/api/v2/networks/solana/trending_pools"
USER_AGENT = "meme-trend-agent/1.0"

# Base tokens that aren't meme coins -- majors, wrapped assets, and
# stablecoins that otherwise show up in the generic trending-pools feed.
NON_MEME_SYMBOLS = {
    "SOL", "WSOL", "USDC", "USDT", "USDH", "PYUSD",
    "BTC", "WBTC", "ETH", "WETH",
}

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")


def sanitize(text):
    """Strip terminal control characters from externally-supplied text."""
    return _CONTROL_CHARS_RE.sub("", text)


def fetch_page(page):
    url = f"{API_URL}?page={page}"
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)


def fetch_trending_pools(pages):
    pools = []
    for page in range(1, pages + 1):
        try:
            payload = fetch_page(page)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            print(f"warning: failed to fetch page {page}: {exc}", file=sys.stderr)
            continue
        pools.extend(payload.get("data", []))
    return pools


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def momentum_score(attrs):
    change = attrs.get("price_change_percentage", {})
    h1 = to_float(change.get("h1"))
    h6 = to_float(change.get("h6"))
    volume_h24 = to_float(attrs.get("volume_usd", {}).get("h24"))
    liquidity = to_float(attrs.get("reserve_in_usd"))
    if liquidity <= 0:
        return float("-inf")
    # weight recent price action highest, use volume/liquidity turnover as a tiebreaker
    turnover = volume_h24 / liquidity
    return (h1 * 2) + h6 + min(turnover, 10)


def risk_flags(attrs):
    flags = []
    liquidity = to_float(attrs.get("reserve_in_usd"))
    fdv = to_float(attrs.get("fdv_usd"))
    h24_change = to_float(attrs.get("price_change_percentage", {}).get("h24"))
    txns_h24 = attrs.get("transactions", {}).get("h24", {})
    sells = txns_h24.get("sells", 0) or 0
    buys = txns_h24.get("buys", 0) or 0

    if liquidity < 10_000:
        flags.append("very low liquidity")
    if fdv and liquidity and fdv / liquidity > 50:
        flags.append("high FDV vs liquidity")
    if h24_change <= -30:
        flags.append("dumping (24h)")
    if buys + sells > 0 and sells > buys * 1.5:
        flags.append("sell pressure")
    return flags


def format_usd(value):
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:.2f}"


def format_price(price):
    if price <= 0:
        return "$0.00"
    if price >= 0.01:
        return f"${price:.4f}"
    # Sub-cent meme coin prices can be many orders of magnitude smaller than
    # a fixed decimal count can show; scale precision to keep ~4 significant
    # digits instead of rounding tiny prices down to zero.
    magnitude = math.floor(math.log10(price))
    decimals = min(-magnitude + 3, 18)
    return f"${price:.{decimals}f}"


def is_meme_pool(attrs):
    base_symbol = attrs.get("name", "").split(" / ")[0].strip().upper()
    return base_symbol not in NON_MEME_SYMBOLS


def print_report(pools, top, min_liquidity):
    scored = []
    for pool in pools:
        attrs = pool.get("attributes", {})
        if not is_meme_pool(attrs):
            continue
        liquidity = to_float(attrs.get("reserve_in_usd"))
        if liquidity < min_liquidity:
            continue
        scored.append((momentum_score(attrs), pool, attrs))

    scored.sort(key=lambda item: item[0], reverse=True)
    scored = scored[:top]

    if not scored:
        print("No pools matched the filters. Try lowering --min-liquidity.")
        return

    print(f"{'#':<3} {'Pair':<22} {'Price':<14} {'1h':>8} {'6h':>8} {'24h':>8} {'Vol 24h':>10} {'Liquidity':>10}  Flags")
    print("-" * 110)
    for rank, (score, pool, attrs) in enumerate(scored, start=1):
        name = sanitize(attrs.get("name", "?"))[:22]
        price = to_float(attrs.get("base_token_price_usd"))
        change = attrs.get("price_change_percentage", {})
        h1 = to_float(change.get("h1"))
        h6 = to_float(change.get("h6"))
        h24 = to_float(change.get("h24"))
        volume_h24 = to_float(attrs.get("volume_usd", {}).get("h24"))
        liquidity = to_float(attrs.get("reserve_in_usd"))
        flags = ", ".join(risk_flags(attrs)) or "-"

        price_str = format_price(price)
        print(
            f"{rank:<3} {name:<22} {price_str:<14} {h1:>7.1f}% {h6:>7.1f}% {h24:>7.1f}% "
            f"{format_usd(volume_h24):>10} {format_usd(liquidity):>10}  {flags}"
        )

    print("\nNot financial advice. Meme coins are highly volatile and illiquid;")
    print("only risk what you can afford to lose, and verify contracts yourself.")


def main():
    parser = argparse.ArgumentParser(description="Report trending Solana meme coins.")
    parser.add_argument("--pages", type=int, default=2, help="How many pages of trending pools to fetch (20 per page). Default: 2")
    parser.add_argument("--top", type=int, default=15, help="How many results to show. Default: 15")
    parser.add_argument("--min-liquidity", type=float, default=5000, help="Filter out pools below this USD liquidity. Default: 5000")
    args = parser.parse_args()

    pools = fetch_trending_pools(args.pages)
    if not pools:
        print("No data returned from GeckoTerminal. Check your network connection.", file=sys.stderr)
        sys.exit(1)

    print_report(pools, args.top, args.min_liquidity)


if __name__ == "__main__":
    main()
