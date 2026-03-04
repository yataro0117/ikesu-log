"""KPI unit tests - 既知データで計算値を検証"""
import pytest
import math


def test_est_count_basic():
    """推定尾数 = 初期尾数 - 累積死亡"""
    initial = 1000
    mortality = 45
    harvest = 0
    est = initial - mortality - harvest
    assert est == 955


def test_est_biomass():
    """推定バイオマス = 推定尾数 × 推定平均体重(g) / 1000"""
    est_count = 955
    avg_weight_g = 620.0
    biomass_kg = est_count * avg_weight_g / 1000.0
    assert abs(biomass_kg - 592.1) < 0.1


def test_fcr_basic():
    """簡易FCR = 期間給餌量(kg) / 期間増体量(kg)"""
    feed_kg = 500.0
    n = 950
    w1_g = 500.0
    w2_g = 620.0
    growth_kg = (w2_g - w1_g) * n / 1000.0  # 114kg
    fcr = feed_kg / growth_kg
    assert abs(fcr - 4.386) < 0.01


def test_mortality_rate_7d():
    """死亡率(7日) = 期間死亡数 / 期首推定尾数 * 100"""
    dead_7d = 12
    start_count = 1000
    rate = dead_7d / start_count * 100
    assert abs(rate - 1.2) < 0.01


def test_sgr():
    """SGR = (ln(W2) - ln(W1)) / days * 100"""
    w1 = 500.0
    w2 = 620.0
    days = 14
    sgr = (math.log(w2) - math.log(w1)) / days * 100
    # SGR(500→620g, 14日) = (ln(620)-ln(500))/14*100 ≈ 1.537
    assert abs(sgr - 1.537) < 0.01


def test_days_to_target():
    """出荷見込み日 = ln(target/current) / (sgr/100)"""
    current_weight = 620.0
    target_weight = 5000.0
    sgr_per_day = 1.499 / 100  # SGR/100
    days = (math.log(target_weight) - math.log(current_weight)) / sgr_per_day
    assert 100 < days < 200  # 合理的な範囲


def test_est_count_with_move():
    """移動を含む推定尾数計算"""
    initial = 3000
    moved_out = 1000
    mortality = 30
    est = initial - moved_out - mortality
    assert est == 1970
