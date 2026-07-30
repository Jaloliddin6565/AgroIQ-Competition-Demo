# AgroIQ — Competition Code Demo

This public repository contains a **sanitized, runnable subset** of the AgroIQ software architecture prepared for evaluation in the President AI Award competition.

AgroIQ combines:

1. a portable colorimetric analyzer for estimating plant-available phosphorus;
2. a universal soil sensor providing pH, EC, moisture, temperature and N/P/K screening indicators;
3. an explainable data-fusion and fertilization recommendation layer.

## Scientific separation

The demo enforces the same core scientific rule as the MVP:

- the colorimetric Olsen-P estimate is the **primary quantitative phosphorus source**;
- the universal sensor P value is stored only as a **screening indicator**;
- the two phosphorus values are never averaged;
- N and K remain qualitative screening indicators until laboratory calibration is completed.

## Included in this repository

- optical feature extraction from RGB measurements;
- a transparent demonstration estimator for Olsen-P;
- soil-condition interpretation for pH, EC, moisture and temperature;
- consistency checking between colorimetric Olsen-P and sensor P;
- transparent phosphorus fertilizer calculation;
- demo scenarios and automated tests.

## Intentionally excluded

The following proprietary or not-yet-validated materials are not published:

- reagent and cartridge formulations;
- PCB, CAD and industrial design files;
- real farmer and field datasets;
- final local calibration coefficients;
- production model weights;
- full commercial recommendation rules;
- private API credentials and device-specific register maps.

## Run the demo

```bash
python demo.py
```

Run tests:

```bash
python -m pip install -r requirements.txt
pytest
```

## Repository structure

```text
AgroIQ-Competition-Demo/
├── demo.py
├── src/
│   └── agroiq_demo.py
├── config/
│   └── demo_thresholds.json
├── data/
│   └── demo_samples.csv
├── tests/
│   └── test_demo.py
├── MODEL_CARD.md
├── NOTICE.md
├── LICENSE.md
└── requirements.txt
```

## Important limitation

This repository is a competition demonstration, not a certified laboratory system. The optical coefficients and agronomic thresholds are illustrative demo values. Real field use requires paired device–laboratory calibration, local soil validation and confirmation by a qualified agronomist.

## Main project

- Project: **AgroIQ — AI-powered multisensor soil diagnostics and precision fertilization platform**
- Category: **AI in green economy and agricultural technologies**
- Full MVP repository is maintained separately by the AgroIQ team.
