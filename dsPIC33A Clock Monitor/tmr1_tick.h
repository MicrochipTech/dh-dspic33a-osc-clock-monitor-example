// TMR1 system tick timer configuration.
// Provides millisecond and second timing for the application.

#ifndef TMRS_H
#define TMRS_H

// Initialize TMR1 as a system tick timer (generates periodic interrupts)
void tmr1_systick_init(void);

// Get elapsed time in milliseconds since timer initialization
uint32_t get_msec(void);

// Get elapsed time in seconds since timer initialization
uint32_t get_sec(void);

#endif