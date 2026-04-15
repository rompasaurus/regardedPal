# AeonLabs ESP32-S3 PCB Template

## Overview

A reusable PCB template for ESP32-S3 designs. Provides a minimal starting point with the ESP32-S3 module, basic power, and USB wired up — intended to be forked and customized for specific projects. Public domain (CC0) license makes it completely free to use in any way.

## Origin & Backstory

Created by **AeonSolutions** (Miguel Tomas), a prolific open-source hardware designer who publishes dozens of ESP32-based PCB templates for various use cases (sensors, data acquisition, smart devices). The template approach is interesting — rather than designing from scratch each time, you start with a proven base and add your specific peripherals. With ~19 stars, it's a niche but useful resource. The CC0 license is notable — it's a complete public domain dedication, meaning you can use it commercially without any attribution requirements.

## Relevance to Dilder

| Feature | AeonLabs Template | Dilder |
|---------|------------------|--------|
| MCU | ESP32-S3 | ESP32-S3-WROOM-1-N16R8 |
| Purpose | Starting template | Full device |
| Complexity | Minimal | Complete with peripherals |
| License | CC0 (public domain) | — |

## Key Takeaways for Dilder

- **Minimal ESP32-S3 baseline** — the absolute minimum wiring needed for an ESP32-S3 to function
- **Template approach** — useful concept if you plan to make variants of the Dilder board
- **CC0 license** — anything you copy from this design has zero legal constraints
- **Compare against Dilder's base** — verify your ESP32-S3 power and USB connections match this known-good starting point

## KiCad Files

```
KiCad/
├── ESP32_S3_PCB_TEMPLATE.kicad_pro
├── ESP32_S3_PCB_TEMPLATE.kicad_sch
└── ESP32_S3_PCB_TEMPLATE.kicad_pcb
```

## Links

- **Repository:** https://github.com/aeonSolutions/AeonLabs-pcb-template-esp32-s3
- **License:** CC0-1.0 (Public Domain)
- **Stars:** ~19
- **Author:** Miguel Tomas / AeonSolutions
