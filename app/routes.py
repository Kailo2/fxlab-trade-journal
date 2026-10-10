from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash

from . import db
from .stats import compute_stats, equity_curve_svg_points

bp = Blueprint("journal", __name__)


@bp.route("/")
def index():
    conn = db.get_db()
    trades = db.list_trades(conn)
    pnls = db.closed_pnls(conn)
    stats = compute_stats(pnls)
    svg_points = equity_curve_svg_points(stats.equity_curve)
    return render_template("index.html", trades=trades, stats=stats, svg_points=svg_points)


@bp.route("/trades/new", methods=["GET", "POST"])
def new_trade():
    if request.method == "POST":
        error = None
        form = request.form

        symbol = form.get("symbol", "").strip().upper()
        direction = form.get("direction", "")
        entry_price = form.get("entry_price", "")
        exit_price = form.get("exit_price", "")
        lots = form.get("lots", "")
        pnl = form.get("pnl", "")
        opened_at = form.get("opened_at", "")
        closed_at = form.get("closed_at", "")
        notes = form.get("notes", "").strip()

        if not symbol:
            error = "نماد الزامی است."
        elif direction not in ("long", "short"):
            error = "جهت معامله باید long یا short باشد."
        elif not opened_at:
            error = "تاریخ باز شدن معامله الزامی است."
        else:
            try:
                entry_price = float(entry_price)
                lots = float(lots)
                exit_price = float(exit_price) if exit_price else None
                pnl = float(pnl) if pnl else None
            except ValueError:
                error = "قیمت ورود، خروج، حجم و سود/زیان باید عدد باشند."

        if error is not None:
            flash(error)
        else:
            trade = {
                "symbol": symbol,
                "direction": direction,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "lots": lots,
                "pnl": pnl,
                "opened_at": opened_at,
                "closed_at": closed_at or None,
                "notes": notes or None,
            }
            conn = db.get_db()
            db.insert_trade(conn, trade)
            return redirect(url_for("journal.index"))

    return render_template("new_trade.html")


@bp.route("/trades/<int:trade_id>/delete", methods=["POST"])
def delete_trade(trade_id):
    conn = db.get_db()
    db.delete_trade(conn, trade_id)
    return redirect(url_for("journal.index"))
