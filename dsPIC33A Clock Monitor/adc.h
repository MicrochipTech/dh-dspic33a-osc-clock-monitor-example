// ADC (Analog-to-Digital Converter) module configuration.
// Configures ADC5 Channel 0 for potentiometer sampling triggered by SCCP2.

#ifndef ADC_H
#define ADC_H

#include <stdbool.h>

// ADC trigger source definitions
#define ADC_TRIGGER_SCCP2       0b100001    // SCCP2 trigger

// Flag indicating new ADC data is ready to be processed
extern volatile bool adc5_ch0_data_ready;

// Initialize ADC5 Channel 0 for potentiometer sampling
void adc_init(void);


#endif /* ADC_H */