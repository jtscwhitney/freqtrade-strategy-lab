# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa
"""
EnhancedCointPairsStrategy_V02 @ **1h** — same logic as V02 (β-churn, config `cointpairs`), shorter bars.

Higher bar count for startup to approximate the same calendar warm-up as 4h×500.
Orphan window scaled so wall-clock ~1 day (24×1h) vs 6×4h.
"""
from EnhancedCointPairsStrategy_V02 import EnhancedCointPairsStrategy_V02


class EnhancedCointPairsStrategy_V02_1h(EnhancedCointPairsStrategy_V02):
    timeframe = "1h"
    inf_tf = "1h"
    startup_candle_count = 1500
    ORPHAN_MAX_CANDLES = 24
