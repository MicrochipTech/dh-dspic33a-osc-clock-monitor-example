// SCCP1 module implementation.
// Configures SCCP1 in PWM mode for RGB LED control.

#include <xc.h>
#include "sccp1.h"

void sccp1_init(void)
{
    // Configure CCP1 for PWM
    CCP1CON1bits.CLKSEL = 0;        // Peripheral bus clock (1:2 of CPU clock)
    CCP1CON1bits.MOD = 0b100;       // Dual Edge Compare (PWM)
    CCP1CON2bits.OCAEN = 1;         // CCP module controls OCx pin
    
    // Set Duty cycle to 5% @ 100kHz frequency
    CCP1PR = 999;
    CCP1RA = 0;
    CCP1RB = 50;
    
    // Turn module on
    CCP1CON1bits.ON = 1;
}
