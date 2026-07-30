"""Sanitized AgroIQ competition demonstration logic.

This module intentionally excludes proprietary cartridge chemistry, production model
weights, device register maps, and commercial recommendation rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import colorsys
import math


@dataclass(frozen=True)
class SoilInput:
    red: float
    green: float
    blue: float
    reaction_time_sec: float
    sample_temperature_c: float
    ph: float
    ec_ds_m: float
    moisture_percent: float
    soil_temperature_c: float
    nitrogen_indicator: float
    sensor_phosphorus_indicator: float
    potassium_indicator: float
    crop: str
    field_area_ha: float


@dataclass(frozen=True)
class AnalysisResult:
    estimated_olsen_p_mg_kg: float
    uncertainty_mg_kg: float
    phosphorus_status: str
    fertilizer_p2o5_kg_ha: tuple[float, float]
    fertilizer_product_kg_ha: tuple[float, float]
    warnings: tuple[str, ...]
    quality_flags: tuple[str, ...]
    explanation: tuple[str, ...]


def validate_input(data: SoilInput) -> None:
    for name, value in (("red", data.red), ("green", data.green), ("blue", data.blue)):
        if not 0 <= value <= 255:
            raise ValueError(f"{name} must be between 0 and 255")
    if not 3.0 <= data.ph <= 11.0:
        raise ValueError("ph must be between 3.0 and 11.0")
    if data.ec_ds_m < 0:
        raise ValueError("ec_ds_m cannot be negative")
    if not 0 <= data.moisture_percent <= 100:
        raise ValueError("moisture_percent must be between 0 and 100")
    if data.field_area_ha <= 0:
        raise ValueError("field_area_ha must be positive")


def optical_features(red: float, green: float, blue: float) -> dict[str, float]:
    """Create a small, transparent subset of optical features used in the MVP."""
    eps = 1e-9
    total = red + green + blue + eps
    r_n, g_n, b_n = red / total, green / total, blue / total
    h, s, v = colorsys.rgb_to_hsv(red / 255.0, green / 255.0, blue / 255.0)
    absorbance_blue = -math.log10(max(blue / 255.0, eps))
    return {
        "r_norm": r_n,
        "g_norm": g_n,
        "b_norm": b_n,
        "blue_red_ratio": blue / (red + eps),
        "blue_green_ratio": blue / (green + eps),
        "hue": h,
        "saturation": s,
        "brightness": v,
        "absorbance_blue": absorbance_blue,
    }


def estimate_olsen_p(data: SoilInput) -> tuple[float, float]:
    """Illustrative optical calibration for competition demonstration only.

    The coefficients are deliberately simplified and are not production calibration
    parameters. Real use requires paired colorimetric and laboratory Olsen-P data.
    """
    f = optical_features(data.red, data.green, data.blue)
    temperature_factor = 1.0 + 0.006 * (data.sample_temperature_c - 25.0)
    time_factor = min(max(data.reaction_time_sec / 600.0, 0.75), 1.25)
    estimate = (
        2.5
        + 16.0 * f["absorbance_blue"]
        + 5.0 * f["blue_red_ratio"]
        + 2.0 * f["saturation"]
    ) * temperature_factor * time_factor
    estimate = round(max(0.0, min(60.0, estimate)), 1)
    uncertainty = round(0.8 + 0.09 * estimate, 1)
    return estimate, uncertainty


def phosphorus_status(value: float) -> str:
    if value < 4:
        return "Juda past"
    if value < 10:
        return "Past"
    if value < 18:
        return "O'rtacha"
    if value < 30:
        return "Yetarli"
    return "Yuqori"


def interpret_soil(data: SoilInput) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    flags: list[str] = []
    if data.ph >= 8.0:
        warnings.append("Ishqoriy tuproqda fosfor o'zlashtirilishi cheklanishi mumkin.")
        flags.append("PH_HIGH")
    if data.ec_ds_m >= 4.0:
        warnings.append("Yuqori EC sho'rlanish xavfini ko'rsatadi.")
        flags.append("EC_HIGH")
    if data.moisture_percent < 12:
        warnings.append("Past namlik oziqa elementlari o'zlashtirilishini cheklashi mumkin.")
        flags.append("MOISTURE_LOW")
    return warnings, flags


def check_phosphorus_consistency(
    olsen_p: float, sensor_p_indicator: float
) -> tuple[bool, str | None]:
    absolute_difference = abs(olsen_p - sensor_p_indicator)
    relative_difference = absolute_difference / max(olsen_p, 1.0)
    disagrees = absolute_difference > 6.0 and relative_difference > 0.60
    if disagrees:
        return True, (
            "Fosfor bo'yicha qurilmalar o'rtasida tafovut aniqlandi. "
            "Kolorimetrik Olsen-P tavsiyada asosiy manba sifatida ishlatildi."
        )
    return False, None


def phosphorus_recommendation(
    crop: str, status: str, ph: float, fertilizer_p2o5_fraction: float = 0.46
) -> tuple[tuple[float, float], tuple[float, float]]:
    base_ranges: dict[str, dict[str, tuple[float, float]]] = {
        "Paxta": {
            "Juda past": (70, 90),
            "Past": (55, 75),
            "O'rtacha": (35, 50),
            "Yetarli": (15, 30),
            "Yuqori": (0, 0),
        },
        "Bug'doy": {
            "Juda past": (60, 80),
            "Past": (45, 65),
            "O'rtacha": (30, 45),
            "Yetarli": (10, 25),
            "Yuqori": (0, 0),
        },
    }
    crop_rules = base_ranges.get(crop, base_ranges["Paxta"])
    low, high = crop_rules[status]
    ph_factor = 1.10 if ph >= 8.0 and high > 0 else 1.0
    p2o5_range = (round(low * ph_factor, 1), round(high * ph_factor, 1))
    product_range = (
        round(p2o5_range[0] / fertilizer_p2o5_fraction, 1),
        round(p2o5_range[1] / fertilizer_p2o5_fraction, 1),
    )
    return p2o5_range, product_range


def analyze(data: SoilInput) -> AnalysisResult:
    validate_input(data)
    olsen_p, uncertainty = estimate_olsen_p(data)
    status = phosphorus_status(olsen_p)
    warnings, flags = interpret_soil(data)

    disagreement, message = check_phosphorus_consistency(
        olsen_p, data.sensor_phosphorus_indicator
    )
    if disagreement:
        flags.append("P_INDICATORS_DISAGREE")
        if message:
            warnings.append(message)

    p2o5_range, product_range = phosphorus_recommendation(data.crop, status, data.ph)

    explanation = [
        f"Kolorimetrik model Olsen-P ni {olsen_p} mg/kg deb baholadi.",
        f"Fosfor holati: {status}.",
        "Universal sensor P qiymati alohida skrining indikatori sifatida saqlandi.",
        "N va K indikatorlari laboratoriya kalibrlashisiz miqdoriy me'yor uchun ishlatilmadi.",
    ]

    if status == "Yuqori":
        warnings.append("Qo'shimcha fosforli o'g'it iqtisodiy va ekologik jihatdan asoslanmasligi mumkin.")

    return AnalysisResult(
        estimated_olsen_p_mg_kg=olsen_p,
        uncertainty_mg_kg=uncertainty,
        phosphorus_status=status,
        fertilizer_p2o5_kg_ha=p2o5_range,
        fertilizer_product_kg_ha=product_range,
        warnings=tuple(warnings),
        quality_flags=tuple(flags),
        explanation=tuple(explanation),
    )


def result_to_dict(result: AnalysisResult) -> dict[str, Any]:
    return {
        "estimated_olsen_p_mg_kg": result.estimated_olsen_p_mg_kg,
        "uncertainty_mg_kg": result.uncertainty_mg_kg,
        "phosphorus_status": result.phosphorus_status,
        "fertilizer_p2o5_kg_ha": result.fertilizer_p2o5_kg_ha,
        "fertilizer_product_kg_ha": result.fertilizer_product_kg_ha,
        "warnings": result.warnings,
        "quality_flags": result.quality_flags,
        "explanation": result.explanation,
    }
