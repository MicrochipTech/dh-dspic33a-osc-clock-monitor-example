// Clock configuration for the microcontroller.
// Configures PLLs and clock generators for system operation.

#ifndef CLOCK_H
#define	CLOCK_H

// Primary oscillator (POSC) configuration options
typedef enum {
    POSC_TYPE_EXTERNAL_CLOCK = 0U,  // External clock input (used in this lab)
    POSC_TYPE_MS_OSC         = 1U,  // Medium-speed crystal oscillator
    POSC_TYPE_HS_OSC         = 2U,  // High-speed crystal oscillator
    POSC_TYPE_OFF            = 3U,  // Primary oscillator disabled
} OSC_POSCMD_t;

// Available clock sources for PLLs and clock generators
typedef enum {
    CLK_SRC_RESERVED         = 0U,
    CLK_SRC_FRC              = 1U,  // Fast RC oscillator (8MHz, default at startup)
    CLK_SRC_BFRC             = 2U,  // Backup Fast RC oscillator
    CLK_SRC_POSC             = 3U,  // Primary oscillator (8MHz external clock)
    CLK_SRC_LPRC             = 4U,  // Low-power RC oscillator (32kHz)
    CLK_SRC_PLL1_FOUT        = 5U,  // PLL1 final output (320MHz in this lab)
    CLK_SRC_PLL2_FOUT        = 6U,  // PLL2 final output
    CLK_SRC_PLL1_VCODIV_OUT  = 7U,  // PLL1 VCO divided output (1600MHz in this lab)
    CLK_SRC_PLL2_VCODIV_OUT  = 8U,  // PLL2 VCO divided output
    CLK_SRC_REFI1            = 9U,  // Reference clock input 1
    CLK_SRC_REFI2            = 10U, // Reference clock input 2
    CLK_SRC_RESERVED_LAST    = 11U,
} CLK_SRC_t;

// Current system/CPU clock frequency in Hz (updated by clock_init)
extern uint32_t SYS_CLK_HZ;

// Initialize system clocks, PLLs, and clock generators
void clock_init(void);

#endif	/* CLOCK_H */

