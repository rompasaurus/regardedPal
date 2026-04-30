---
date: 2026-04-30
authors:
  - rompasaurus
categories:
  - Hardware
tags:
  - freecad
  - joystick
  - piezo
  - accelerometer
  - 3d-printing
  - parametric
---

# Joystick Anchor Pad, Piezo Speaker, and MPU-6500 Accelerometer

Major revision to the FreeCAD parametric macro: the joystick mounting system was redesigned with a precision anchor pad, a 20 mm piezo speaker got a retaining ring in the base plate, and an MPU-6500 6-axis IMU module now has its own recessed pocket between the battery rails.

<!-- more -->

## Joystick PCB Alignment Fix

The joystick PCB was placed at `enc_y/2 + 0.67` (23.67 mm) instead of `enc_y/2` (23.0 mm), which double-applied the SW1 Y offset. The cover hole, pocket, and cradle pit already shift by `joy_pcb_y_offset` to land on the switch stick -- so the PCB itself should sit at the true bounding-box center. After the fix, the actuator stick lands within 0.01 mm of the cover hole center.

## Joystick Anchor Pad (replaces JoyWell + Cut_JoyBody)

The old approach used a 22.6 mm well sleeve around the PCB plus a separate square body cutout. The new design replaces both with a single **14 x 14 mm anchor pad** with a **12 x 12 mm square inner hole**, extending 6.85 mm from the cover face plate down to exactly the PCB top surface. This acts as a precision locating collar for the K1-1506SN-01 switch body without intersecting the board.

Removed features:

- `Cut_JoyBody` -- square body cutout (anchor pad inner hole replaces it)
- `JoyWell_Outer` / `JoyWell_Inner` -- sleeve molding (anchor pad replaces it)
- `Cut_JoyPCBPocket` -- face plate pocket (no longer needed)
- `PicoRetentionBlock` -- overlapped with IMU pocket

## Cradle Pit Tightened

The joystick PCB pit in the cradle shrank from **23.0 mm to 20.0 mm** -- the board is 19.6 x 19.6 mm, so the old pit had 1.7 mm of gap per side. Now it's 0.2 mm per side for a snug slide-fit. The pit Y center also moved from 23.67 to 23.0 to match the corrected PCB placement.

## Piezo Speaker -- FT-20T / YOUMILE JK-YM-297A

A **20 mm piezo disc** (brass plate 20 mm x 0.20 mm + ceramic element 15 mm x 0.22 mm) sits in a circular retaining ring on the base plate pocket floor, dead center between the battery rails.

- **Ring ID:** 20.2 mm (0.1 mm clearance per side for slide-fit)
- **Ring wall:** 1.0 mm thick, 1.5 mm tall
- **Ring OD:** 22.2 mm (fits in the 23 mm Y gap between rail supports)
- **Position:** (47.25, 23.0) -- centered in X and Y on the base plate

The disc slides or glues into the ring with the ceramic element facing up into the device cavity.

## MPU-6500 Accelerometer -- GY-6500 Module

A **25 x 15 mm IMU breakout** (MPU-6500, 6-axis gyro + accelerometer, I2C/SPI) gets a rectangular retaining pocket on the base plate, same Y center as the piezo, shifted toward -X.

- **Pocket:** 25.4 x 15.4 mm inner cavity, 1.0 mm thick retaining wall, 1.5 mm tall
- **Position:** center at (21.65, 23.0) -- 2 mm gap from the piezo ring's -X edge
- **Module:** 25 x 15 x 1.0 mm PCB + MPU-6500 QFN (3 x 3 x 0.9 mm) + passives

Neither the IMU nor the piezo disc interfere with the Pico W's 2.4 GHz WiFi -- both are passive/low-frequency components housed in plastic retaining walls.

## TP4056 USB-C Connector Removed

The separate `TP4056_USBC` silver connector visualization was removed from the peripherals. The `TP4056_Module` (PCB + IC lump) remains.

## Summary of Changes

| Feature | Before | After |
|---------|--------|-------|
| Joystick PCB Y | 23.67 (double offset) | 23.0 (bbox center) |
| Joystick body support | JoyWell + Cut_JoyBody | 14x14 anchor pad |
| Cradle pit XY | 23.0 mm | 20.0 mm |
| Piezo speaker | -- | 20 mm disc in retaining ring |
| IMU accelerometer | -- | GY-6500 in recessed pocket |
| TP4056 USB-C viz | present | removed |
| PicoRetentionBlock | present | removed |

Source: `hardware-design/freecad-mk2/dilder_rev2_mk2.FCMacro`
