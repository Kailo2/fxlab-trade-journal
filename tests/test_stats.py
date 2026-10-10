import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.stats import compute_stats, equity_curve_svg_points


class TestComputeStats(unittest.TestCase):
    def test_empty_list(self):
        s = compute_stats([])
        self.assertEqual(s.total_trades, 0)
        self.assertEqual(s.equity_curve, [0.0])
        self.assertIsNone(s.profit_factor)

    def test_all_wins(self):
        s = compute_stats([10, 20, 30])
        self.assertEqual(s.total_trades, 3)
        self.assertEqual(s.wins, 3)
        self.assertEqual(s.losses, 0)
        self.assertAlmostEqual(s.win_rate, 100.0)
        self.assertEqual(s.gross_loss, 0.0)
        self.assertIsNone(s.profit_factor)  # no losses -> undefined (reported as infinite upstream)
        self.assertAlmostEqual(s.net_pnl, 60.0)
        self.assertAlmostEqual(s.expectancy, 20.0)

    def test_mixed_wins_and_losses(self):
        pnls = [100, -50, 75, -25, 200]
        s = compute_stats(pnls)
        self.assertEqual(s.total_trades, 5)
        self.assertEqual(s.wins, 3)
        self.assertEqual(s.losses, 2)
        self.assertAlmostEqual(s.win_rate, 60.0)
        self.assertAlmostEqual(s.gross_profit, 375.0)
        self.assertAlmostEqual(s.gross_loss, 75.0)
        self.assertAlmostEqual(s.profit_factor, 5.0)
        self.assertAlmostEqual(s.net_pnl, 300.0)
        self.assertAlmostEqual(s.expectancy, 60.0)
        self.assertEqual(s.best_trade, 200)
        self.assertEqual(s.worst_trade, -50)

    def test_equity_curve_is_cumulative(self):
        s = compute_stats([10, -5, 20])
        self.assertEqual(s.equity_curve, [0.0, 10.0, 5.0, 25.0])

    def test_max_drawdown_basic(self):
        # equity: 0 -> 100 -> 60 -> 80  (peak 100, trough 60 -> DD = 40)
        s = compute_stats([100, -40, 20])
        self.assertAlmostEqual(s.max_drawdown, 40.0)

    def test_max_drawdown_zero_when_always_rising(self):
        s = compute_stats([10, 10, 10])
        self.assertAlmostEqual(s.max_drawdown, 0.0)

    def test_all_losses_profit_factor_zero_not_none(self):
        s = compute_stats([-10, -20])
        self.assertEqual(s.gross_profit, 0.0)
        self.assertAlmostEqual(s.profit_factor, 0.0)


class TestEquitySvgPoints(unittest.TestCase):
    def test_empty_or_single_point_returns_empty_string(self):
        self.assertEqual(equity_curve_svg_points([]), "")
        self.assertEqual(equity_curve_svg_points([0.0]), "")

    def test_two_points_produces_two_coordinate_pairs(self):
        pts = equity_curve_svg_points([0.0, 100.0], width=600, height=160)
        pairs = pts.split(" ")
        self.assertEqual(len(pairs), 2)
        for pair in pairs:
            x, y = pair.split(",")
            float(x), float(y)  # should not raise

    def test_flat_curve_does_not_divide_by_zero(self):
        pts = equity_curve_svg_points([5.0, 5.0, 5.0])
        self.assertNotEqual(pts, "")


if __name__ == "__main__":
    unittest.main()
