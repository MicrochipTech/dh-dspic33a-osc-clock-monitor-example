// TMR1 system tick timer implementation.
// Provides millisecond and second timing using TMR1 periodic interrupts.

#include <xc.h>
#include "clock.h"
#include "tmr1_tick.h"

static volatile uint32_t tick_ms = 0;
static volatile uint32_t tick_s = 0;

// cppcheck-suppress misra-c2012-8.9 ; shared between ISR and get functions at file scope
static volatile uint32_t tick_counter = 0;

void tmr1_systick_init(void)
{
    T1CONbits.TCS = 0;              // use system clock
    T1CONbits.TCKPS = 0b0;          // 1:1 prescale

    TMR1 = 0;
    double pr1_val = 10e6 / (2.0 * 10e9 / (double)SYS_CLK_HZ);
    PR1 = (uint32_t)pr1_val;        // everything in ns
    
    _T1IP = 5;
    
    _T1IF = 0;
    _T1IE = 1;
    T1CONbits.ON = 1;
}

uint32_t get_msec(void)
{
    return tick_ms;
}

uint32_t get_sec(void)
{
    return tick_s;
}


// cppcheck-suppress misra-c2012-8.4 ; ISR prototype provided by device header
void __attribute__((interrupt)) _T1Interrupt(void)
{
    tick_ms++;
    tick_counter++;

    if (tick_counter >= 1000U) {
        tick_counter = 0;
        tick_s++;
    }

    _T1IF = 0;
}
