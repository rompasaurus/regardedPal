cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(moodselector_sound C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

# Display variant: pass -DDISPLAY_VARIANT=V2|V3|V3a|V4 to cmake.
# Default is V4 (current hardware — SSD1680 internal LUT).
if(NOT DEFINED DISPLAY_VARIANT)
    set(DISPLAY_VARIANT "V4")
endif()

if(DISPLAY_VARIANT STREQUAL "V4")
    set(EPD_SOURCE lib/e-Paper/EPD_2in13_V4.c)
    set(EPD_DEFINE DISPLAY_V4)
    message(STATUS "Display variant: V4 (internal LUT)")
else()
    set(EPD_SOURCE lib/e-Paper/EPD_2in13_V3.c)
    set(EPD_DEFINE "")
    message(STATUS "Display variant: V3 (standard)")
endif()

add_executable(moodselector_sound
    main.c
    lib/Config/DEV_Config.c
    ${EPD_SOURCE}
)

if(EPD_DEFINE)
    target_compile_definitions(moodselector_sound PRIVATE ${EPD_DEFINE}=1)
endif()

target_include_directories(moodselector_sound PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/lib
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/Config
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/e-Paper
)

target_link_libraries(moodselector_sound
    pico_stdlib
    hardware_spi
    hardware_gpio
    hardware_adc
    hardware_pwm
    m
)

pico_enable_stdio_usb(moodselector_sound 1)
pico_enable_stdio_uart(moodselector_sound 0)

pico_add_extra_outputs(moodselector_sound)
