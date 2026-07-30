# AgroIQ Competition Demo — Model Card

## Purpose

Demonstrate the AgroIQ software workflow for estimating plant-available phosphorus from colorimetric measurements and combining that result with universal soil-sensor context.

## Inputs

- RGB color values
- Reaction time
- Sample temperature
- pH, EC, moisture and soil temperature
- N/P/K sensor indicators
- Crop and field area

## Output

- Demo Olsen-P estimate
- Uncertainty estimate
- Phosphorus status class
- Transparent phosphorus fertilizer range
- Warnings and quality flags

## Scientific safeguards

- Sensor P never replaces or averages with colorimetric Olsen-P.
- N and K are qualitative screening indicators only.
- Fertilizer calculations are transparent and rule-based.

## Limitations

The published coefficients are illustrative and not the production calibration. The demo has not been field-validated and is not a certified laboratory method. Real use requires paired laboratory calibration, local soil validation, and agronomist confirmation.
