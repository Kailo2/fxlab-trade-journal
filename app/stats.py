"""
stats.py — pure trading-statistics functions over a list of realized P&L
values (floats, one per closed trade, in account currency). No Flask or
database dependency, so these are trivial to unit-test directly.
"""
from dataclasses import dataclass


@dataclass
class JournalStats:
    total_trades: int
    wins: int
    losses: int
    win_rate: float          # 0..100
    gross_profit: float
    gross_loss: float        # stored as a positive number
    profit_factor: float | None   # gross_profit / gross_loss, None if no losses
    expectancy: float        # average P&L per trade
    net_pnl: float
    best_trade: float
    worst_trade: float
    max_drawdown: float      # largest peak-to-trough drop in equity curve
    equity_curve: list       # cumulative P&L after each trade, starting at 0


def compute_stats(pnls: list) -> JournalStats:
    if not pnls:
        return JournalStats(
            total_trades=0, wins=0, losses=0, win_rate=0.0,
            gross_profit=0.0, gross_loss=0.0, profit_factor=None,
            expectancy=0.0, net_pnl=0.0, best_trade=0.0, worst_trade=0.0,
            max_drawdown=0.0, equity_curve=[0.0],
        )

    wins_list = [p for p in pnls if p > 0]
    losses_list = [p for p in pnls if p < 0]

    gross_profit = sum(wins_list)
    gross_loss = abs(sum(losses_list))
    total = len(pnls)
    win_rate = (len(wins_list) / total) * 100
    net_pnl = sum(pnls)
    expectancy = net_pnl / total
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else None

    equity = [0.0]
    running = 0.0
    for p in pnls:
        running += p
        equity.append(running)

    peak = equity[0]
    max_dd = 0.0
    for v in equity:
        if v > peak:
            peak = v
        dd = peak - v
        if dd > max_dd:
            max_dd = dd

    return JournalStats(
        total_trades=total,
        wins=len(wins_list),
        losses=len(losses_list),
        win_rate=win_rate,
        gross_profit=gross_profit,
        gross_loss=gross_loss,
        profit_factor=profit_factor,
        expectancy=expectancy,
        net_pnl=net_pnl,
        best_trade=max(pnls),
        worst_trade=min(pnls),
        max_drawdown=max_dd,
        equity_curve=equity,
    )


def equity_curve_svg_points(equity: list, width: int = 600, height: int = 160, padding: int = 10) -> str:
    """
    Turn an equity curve (list of floats) into an SVG <polyline> `points`
    attribute string, scaled to fit width x height. Pure function, no SVG
    library dependency -- keeps the whole app dependency-free beyond Flask.
    """
    if len(equity) < 2:
        return ""
    lo, hi = min(equity), max(equity)
    span = (hi - lo) or 1.0
    n = len(equity)
    usable_w = width - 2 * padding
    usable_h = height - 2 * padding

    points = []
    for i, v in enumerate(equity):
        x = padding + (i / (n - 1)) * usable_w
        # SVG y grows downward, so invert
        y = padding + (1 - (v - lo) / span) * usable_h
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)
