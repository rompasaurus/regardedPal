cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(moodselector_sound_wifi C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

# Display variant
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

# WiFi credentials — pass via cmake or edit wifi_config.h
if(DEFINED WIFI_SSID)
    add_compile_definitions(WIFI_SSID="${WIFI_SSID}")
endif()
if(DEFINED WIFI_PASS)
    add_compile_definitions(WIFI_PASS="${WIFI_PASS}")
endif()

add_executable(moodselector_sound_wifi
    main.c
    lib/Config/DEV_Config.c
    ${EPD_SOURCE}
)

if(EPD_DEFINE)
    target_compile_definitions(moodselector_sound_wifi PRIVATE ${EPD_DEFINE}=1)
endif()

target_include_directories(moodselector_sound_wifi PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/lib
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/Config
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/e-Paper
)

target_link_libraries(moodselector_sound_wifi
    pico_stdlib
    hardware_spi
    hardware_gpio
    hardware_adc
    hardware_pwm
    hardware_rtc
    pico_cyw43_arch_lwip_poll
    m
)

pico_enable_stdio_usb(moodselector_sound_wifi 1)
pico_enable_stdio_uart(moodselector_sound_wifi 0)

pico_add_extra_outputs(moodselector_sound_wifi)
