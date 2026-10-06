// Implements LED bar graph display based on potentiometer ADC readings.

#ifndef DEMO_APP_H
#define	DEMO_APP_H

#include <stdint.h>


// Current ADC reading from potentiometer (updated by ADC interrupt)
extern volatile uint32_t potentiometer_adc_counts;

// Initialize measurement system (ADC)
void demo_init(void);

// Main task: checks ADC5 flags, processes data, and updates LEDs
void demo_task(void);

#endif	/* DEMO_APP_H */

