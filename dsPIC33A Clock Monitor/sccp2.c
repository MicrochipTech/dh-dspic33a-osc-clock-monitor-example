// SCCP2 module implementation.
// Configures SCCP2 in timer mode to trigger ADC sampling.

#include <xc.h>
#include "sccp2.h"

void sccp2_init(void)
{
    // Configure CCP2 as a simple timer
    CCP2CON1bits.CLKSEL = 0;        // Peripheral bus clock (1:2 of CPU clock)
    CCP2CON1bits.MOD = 0;           // Timer mode
    CCP2CON2bits.OCAEN = 1;         // CCP module controls OCx pin

    // Trigger ADC sampling at 100kHz frequency
    CCP2PR = 1000;
    
    // Turn module on
    CCP2CON1bits.ON = 1;
}
