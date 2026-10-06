// Clock Monitor example application and a little more.
// Demonstrates Clock Monitor Module configured for Frequency Drift Detection Measurement.

// Demonstration Code is built and tested on dsPIC33A Curiosity Platform Development Board using dsPIC33AK512MPS512 GP DIM

#include <xc.h>
#include <stdint.h>

#include "clock.h"
#include "gpio.h"
#include "tmr1_tick.h"
#include "sccp1.h"
#include "demo_app.h"

// Initialize system peripherals
static void system_init(void)
{
    clock_init();
    gpio_init();
    tmr1_systick_init();
    sccp1_init();
}

int main(void)
{
    uint32_t ms = 0;

    system_init();       // Initialize system peripherals
    demo_init();
   
    while (1) {
        if (get_msec() > (ms + 500U)) {  
            ms = get_msec();
            LED0_toggle();
        }
        demo_task();
       
        // Runtime Clock Monitor for Reference Clock
        // TRIG == 0 may mean a Reference clock issue (stopped toggling)
        while (CM2STATbits.TRIG == 0){ 
        
        Nop();
            
        // This test meets a different purpose vs. start-up test and checks if the reference clock is working
        // System failure or Clock Monitor module is disabled. Application level handling required.
        }
    }
}
