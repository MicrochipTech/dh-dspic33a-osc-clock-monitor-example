// ADC module implementation for Board Potentiometer R14
// Configures ADC5 Channel 0 to sample the onboard potentiometer, triggered by SCCP2.

// ADC value is used for LED1-7 

#include <xc.h>
#include "adc.h"
#include "demo_app.h"

//#define FCY 200000000UL

// Boolean Flag used in Main()
volatile bool adc5_ch0_data_ready = false;

void adc_init(void)
{
    // The ADC is clocked via PLL1 Fout (320 MHz) - 320MHz is not required but it is the current example configuration 
    // The ADC module internally divides this clock by 4 to produce its core clock

    // Configure AD5 CH0 to use AD5AN0 which is connected to the onboard potentiometer, R14
    AD5CH0CON1bits.TRG1SRC = 0b100001;      // Trigger via SCCP2
    AD5CH0CON1bits.DIFF = 0;                // Use a single-ended input
    AD5CH0CON1bits.PINSEL = 0;              // Use AD5AN0 pin
    AD5CH0CON1bits.SAMC = 3;                // 6.5Tad = 81.25ns

    // Interrupt when data is ready in the AD5CH0DATA register
    AD5CH0CON1bits.IRQSEL = 1;

    // Enable ADC5 CH0 interrupt
    _AD5CH0IF = 0;              // Clear interrupt flag
    _AD5CH0IE = 1;              // Enable interrupt

    // Turn ADC on and wait for ADC ready bit to be set
    // This bit is set when the ADC is enabled and has completed its power up and self-calibration process
    AD5CONbits.ON = 1;
    while (AD5CONbits.ADRDY == 0) { }
}

// cppcheck-suppress misra-c2012-8.4 ; ISR prototype provided by device header
void __attribute__((interrupt)) _AD5CH0Interrupt(void)
{
    // Read ADC data directly into the global variable
    potentiometer_adc_counts = AD5CH0DATA;

    // Set flag for main loop to process. Flag used in demo_task function in demo_app.c
    adc5_ch0_data_ready = true;

    // Clear interrupt flag
    _AD5CH0IF = 0;
}
