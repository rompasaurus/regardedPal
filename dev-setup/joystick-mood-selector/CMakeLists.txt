cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(joystick_mood_selector C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

# Display variant: pass -DDISPLAY_VARIANT=V2|V3|V3a|V4 to cmake.
# Default is V4 (current hardware — SSD1680 internal LUT).
if(NOT DEFINED DISPLAY_VARIANT)
    set(DISPLAY_VARIANT "V4")
endif()

if(DISPLAY_VARIANT STREQUAL "V2")
    set(EPD_SOURCE lib/e-Paper/EPD_2in13_V2.c)
    set(EPD_DEFINE DISPLAY_V2)
    message(STATUS "Display variant: V2 (SSD1675B)")
elseif(DISPLAY_VARIANT STREQUAL "V3a")
    set(EPD_SOURCE lib/e-Paper/EPD_2in13_V3a.c)
    set(EPD_DEFINE DISPLAY_V3A)
    message(STATUS "Display variant: V3a (revision A)")
elseif(DISPLAY_VARIANT STREQUAL "V4")
    set(EPD_SOURCE lib/e-Paper/EPD_2in13_V4.c)
    set(EPD_DEFINE DISPLAY_V4)
    message(STATUS "Display variant: V4 (internal LUT)")
else()
    set(EPD_SOURCE lib/e-Paper/EPD_2in13_V3.c)
    set(EPD_DEFINE "")
    message(STATUS "Display variant: V3 (standard)")
endif()

add_executable(joystick_mood_selector
    main.c
    lib/Config/DEV_Config.c
    ${EPD_SOURCE}
)

if(EPD_DEFINE)
    target_compile_definitions(joystick_mood_selector PRIVATE ${EPD_DEFINE}=1)
endif()

target_include_directories(joystick_mood_selector PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/lib
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/Config
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/e-Paper
)

target_link_libraries(joystick_mood_selector
    pico_stdlib
    hardware_spi
    hardware_gpio
    hardware_adc
    m
)


# hardware_rtc only exists on RP2040 — RP2350 uses software fallback in rtc_compat.h
if(PICO_PLATFORM STREQUAL "rp2040")
    target_link_libraries(joystick_mood_selector hardware_rtc)
endif()
pico_enable_stdio_usb(joystick_mood_selector 1)
pico_enable_stdio_uart(joystick_mood_selector 0)

pico_add_extra_outputs(joystick_mood_selector)
