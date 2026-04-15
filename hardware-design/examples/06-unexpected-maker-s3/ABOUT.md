# Unexpected Maker ESP32-S3 Boards

## Overview

A collection of ESP32-S3 development boards and carrier boards from Unexpected Maker, a well-known maker in the ESP32 community. Includes designs for TinyS3, ProS3, FeatherS3, NanoS3, OMGS3, and EdgeS3D — plus KiCad carrier board designs that show how to build custom hardware around these modules. The carrier boards are the most useful reference.

## Origin & Backstory

**Unexpected Maker** (Seon Rozenblum, based in Australia) is one of the most prolific ESP32 board designers in the maker community. His boards are sold through Adafruit, SparkFun, and Pimoroni. The designs prioritize compact form factors, USB-C, and battery support. The KiCad carrier board files in this repo are particularly interesting because they show how to integrate an ESP32-S3 module into a larger system — exactly what the Dilder project is doing. The project has ~275 stars and an active community.

## Relevance to Dilder

| Feature | UM Boards | Dilder |
|---------|----------|--------|
| MCU | Various ESP32-S3 modules | ESP32-S3-WROOM-1-N16R8 |
| USB | USB-C | USB-C |
| Power | Battery support on some | LiPo + TP4056 |
| Form factor | Tiny dev boards + carriers | Custom handheld |

## Key Takeaways for Dilder

- **Carrier board design patterns** — NanoS3 and OMGS3 carriers show how to route signals from an ESP32-S3 module to external peripherals
- **Compact layout techniques** — Unexpected Maker is known for incredibly dense, well-routed boards
- **USB-C implementation** — proven USB-C connector wiring for ESP32-S3
- **Multiple board designs to compare** — see different approaches to the same problem

## KiCad Files

```
kicad/
├── NanoS3 Carrier/
│   ├── NanoS3_Carrier.kicad_sch
│   └── NanoS3_Carrier.kicad_pcb
└── OMGS3 Carrier/
    ├── OMGS3_Carrier_R1.kicad_pro
    ├── OMGS3_Carrier_R1.kicad_sch
    └── OMGS3_Carrier_R1.kicad_pcb
series_d/KiCAD/
└── EdgeS3D_Carrier_P1/
    ├── EdgeS3D_Carrier_P1.kicad_pro
    ├── EdgeS3D_Carrier_P1.kicad_sch
    └── EdgeS3D_Carrier_P1.kicad_pcb
```

## Links

- **Repository:** https://github.com/UnexpectedMaker/esp32s3
- **License:** Community-oriented (not formally specified)
- **Stars:** ~275
- **Store:** https://unexpectedmaker.com
