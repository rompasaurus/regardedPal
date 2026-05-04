# Dilder — Rolling Daily TODO

A living task list updated each week. Newest entries at the top.

---

## Week 3 — 2026-05-04 (Session Progress)

### Completed Today

- [x] Joystick PCB arrived from JLCPCB — unboxed, photographed, tested
- [x] Discovered COM/UP pin swap in EasyEDA-imported KiCad symbol — root cause traced, schematic fixed for Rev 2
- [x] Wired joystick breakout to Pico 2 W — GPIO mapping confirmed: L=GP2, D=GP3, UP=GP4, R=GP5, C=GP6
- [x] GPIO diagnostic added to firmware — prints raw pin states at startup and every 2s during runtime
- [x] Switched display driver from V3 to V4 (internal LUT, no custom waveform tables)
- [x] Rewrote V4 partial refresh driver 4 times (V1.0→V1.4) — final version uses two-pass diff-based partial refresh for ghost-free updates
- [x] Added firmware version system (`version.h`, v0.5.4) — all 20 programs print version + build timestamp at startup
- [x] Added "Clean Build & Deploy" button to DevTool Programs tab
- [x] Changed all display variant defaults from V3 to V4 (CMakeLists, Dockerfile, DevTool dropdown)
- [x] Mk2 translucent case photos converted, named, placed in website assets
- [x] Front page gallery updated with Mk2 translucent + joystick PCB photos
- [x] Blog post and design evolution entries for Mk2 translucent prototype
- [x] Created rolling TODO.md at project root

### Still Open from Handwritten List

> OCR'd from handwritten notes (see `website/docs/assets/images/hardware/handwritten-todo-list-week3-20260504.jpg`)

- [ ] Wire up and test speaker
- [ ] Put a speaker grill cutout for the case
- [ ] Research if wireless firmware deployment is possible to streamline deploy and testing pipeline
- [x] ~~Wednesday: wire up joystick mount~~ (done — wired and tested 2026-05-04)
- [ ] Add a chamfer and joystick retention square so that it fits around snugly the base of the joystick
- [ ] Determine a power on/off (leave power) mechanism
- [ ] With joystick implement menu and settings system
- [ ] Stand: create a landing page and progression synopsis; purge the stale folders and pointers; perhaps migrate to a V2 repo and project structure
- [ ] Compile a schematic for all the planned hardware; scour the web for best components and JLCPCB's basic components (add flash memory, high voltage level components)
- [ ] Estimate a board/print cost
- [ ] Run battery life benchmarks
- [ ] Estimate how thin this device could be with a dedicated board

### New Items from Today

- [ ] Fix KiCad joystick PCB Rev 2 — re-route with corrected COM/UP pin assignment, re-order from JLCPCB
- [ ] Verify all 5 joystick directions work with corrected wiring (swap COM/UP wires on current board as interim fix)
- [ ] Tune V4 two-pass partial refresh — blacks still slightly washed out with fast waveform, may need custom LUT or voltage adjustment
- [ ] Add pin-1 silkscreen dot to future PCB orders to prevent orientation ambiguity
- [ ] Investigate why V4 display's internal LUT produces weaker blacks than V3's custom LUT — may need to source V3 panels or create hybrid driver
