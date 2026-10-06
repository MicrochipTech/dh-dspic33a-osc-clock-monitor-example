// Implements LED bar graph display based on potentiometer ADC readings.

#include <xc.h>
#include "adc.h"
#include "gpio.h"
#include "demo_app.h"
#include "sccp2.h"
#include "clock_monitor.h"

volatile uint32_t potentiometer_adc_counts;


// Update LED bar graph based on potentiometer ADC value
static void update_led_bargraph(void)
{
    uint32_t scaled_counts;

    // Scale the potentiometer ADC counts to have a value 0-7
    scaled_counts = (uint32_t) (potentiometer_adc_counts * 8U / 4095U);

    // LEDs act as a visual level meter based on ADC5CH0 data
    // Min value = LEDs OFF
    // More LEDs light up as potentiometer value increases
    if (scaled_counts >= 7U) {
        LED1_on();
    } else {
        LED1_off();
    }

    if (scaled_counts >= 6U) {
        LED2_on();
    } else {
        LED2_off();
    }

    if (scaled_counts >= 5U) {
        LED3_on();
    } else {
        LED3_off();
    }

    if (scaled_counts >= 4U) {
        LED4_on();
    } else {
        LED4_off();
    }

    if (scaled_counts >= 3U) {
        LED5_on();
    } else {
        LED5_off();
    }

    if (scaled_counts >= 2U) {
        LED6_on();
    } else {
        LED6_off();
    }

    if (scaled_counts >= 1U) {
        LED7_on();
    } else {
        LED7_off();
    }
}

void demo_init(void)
{
    adc_init();
    sccp2_init();
    clock_monitor_init();
}

void demo_task(void)
{
    // Check if ADC5 CH0 data is ready and process it
    if (adc5_ch0_data_ready) {
        adc5_ch0_data_ready = false;
        update_led_bargraph();
    }
}