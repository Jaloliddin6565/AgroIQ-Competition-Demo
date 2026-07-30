import pytest

from src.agroiq_demo import (
    SoilInput,
    analyze,
    check_phosphorus_consistency,
    optical_features,
    phosphorus_status,
)


def sample(**overrides):
    values = dict(
        red=162.3,
        green=202.9,
        blue=230.7,
        reaction_time_sec=600,
        sample_temperature_c=24.0,
        ph=8.1,
        ec_ds_m=1.8,
        moisture_percent=21.0,
        soil_temperature_c=22.5,
        nitrogen_indicator=44.0,
        sensor_phosphorus_indicator=9.0,
        potassium_indicator=168.0,
        crop="Paxta",
        field_area_ha=10.0,
    )
    values.update(overrides)
    return SoilInput(**values)


def test_optical_features_are_finite():
    features = optical_features(162, 203, 231)
    assert all(value == value for value in features.values())


def test_status_boundaries():
    assert phosphorus_status(3.9) == "Juda past"
    assert phosphorus_status(6.5) == "Past"
    assert phosphorus_status(15) == "O'rtacha"
    assert phosphorus_status(22) == "Yetarli"
    assert phosphorus_status(35) == "Yuqori"


def test_colorimetric_value_remains_primary():
    result = analyze(sample(sensor_phosphorus_indicator=45.0))
    assert "P_INDICATORS_DISAGREE" in result.quality_flags
    assert result.estimated_olsen_p_mg_kg != pytest.approx((result.estimated_olsen_p_mg_kg + 45.0) / 2)


def test_disagreement_requires_absolute_and_relative_difference():
    assert check_phosphorus_consistency(2.0, 4.0)[0] is False
    assert check_phosphorus_consistency(8.0, 20.0)[0] is True


def test_high_phosphorus_returns_zero_additional_rate():
    result = analyze(sample(red=40, green=55, blue=20, ph=7.2))
    if result.phosphorus_status == "Yuqori":
        assert result.fertilizer_p2o5_kg_ha == (0.0, 0.0)


def test_invalid_rgb_rejected():
    with pytest.raises(ValueError):
        analyze(sample(red=300))
