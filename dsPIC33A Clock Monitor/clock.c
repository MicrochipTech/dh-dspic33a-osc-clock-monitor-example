// Clock configuration implementation.
// Configures PLLs (PLL1, PLL2) and clock generators (CLKGEN1, CLKGEN6, and CLKGEN11) for system operation.

#include <xc.h>
#include "clock.h"

// Current system/CPU clock in Hz
// Since the device boots with FRC clock, initial value is FRC frequency
uint32_t SYS_CLK_HZ = 8000000UL;


// Configure PLL1, to be used CPU Clock Generator 1 (200MHz) and ADC Module Clock Generator (320MHz)
static void pll1_init(void)
{
    // Enable the PLL
    PLL1CONbits.ON = 1;
    
    // Configure backup oscillator in case of a failure
    PLL1CONbits.BOSC = CLK_SRC_BFRC;
    PLL1CONbits.FSCMEN = 1;
    
    // Configure PLL values
    // PLLPRE   = 1   : Do not divide PLL input clock
    // PLLFBDIV = 200 : VCO frequency = 8MHz * 200 = 1600MHz (input selected below)
    // POSTDIV1 = 5   : Divide VCO out by 5
    // POSTDIV2 = 1   : Divide VCO out further by 1
    // INTDIV   = 4   : Divide Internal VCO of 1600MHz / 8 for 200MHz (CLKGEN1 ready input)
    // These settings yield PLL1 Fout = 320MHz, and PLL1 VCO Out = 200MHz
    
    // Update POSTDIV1/2 and INTDIV output dividers
    PLL1DIVbits.POSTDIV1 = 5;   // POSTDIV1 should always be greater than POSTDIV2
    PLL1DIVbits.POSTDIV2 = 1;
    PLL1CONbits.FOUTSWEN = 1;           
    while (PLL1CONbits.FOUTSWEN == 1) { }
    
    // Update input divider and feedback divider
    PLL1DIVbits.PLLPRE   = 1;
    PLL1DIVbits.PLLFBDIV = 200;
    PLL1CONbits.PLLSWEN = 1;
    while (PLL1CONbits.PLLSWEN == 1) { }
    
    // Update VCO Output divider bits
    VCO1DIVbits.INTDIV = 4;     // Divide raw VCO output by 8 (4 * 2)
    PLL1CONbits.DIVSWEN = 1;
    while (PLL1CONbits.DIVSWEN == 1) { }

    // Update PLL clock source
    // Select Primary Oscillator
    PLL1CONbits.NOSC = CLK_SRC_POSC;
    PLL1CONbits.OSWEN = 1;
    while (PLL1CONbits.OSWEN == 1) { }
    
    // Wait for PLL ready
    while (PLL1CONbits.CLKRDY == 0) { }
    while (OSCCTRLbits.PLL1RDY == 0) { }
}

// Configure PLL2, to be used for Clock Monitor Frequency Drift Detection Measurement example
// PLL2_FOUT use as source for Clock Generator 11
static void pll2_init(void)
{
    // Enable the PLL
    PLL2CONbits.ON = 1;
    
    // Configure backup oscillator in case of a failure
    PLL2CONbits.BOSC = CLK_SRC_BFRC;
    PLL2CONbits.FSCMEN = 1;
    
    // Configure PLL values
    // PLLPRE   = 1   : Do not divide PLL input clock
    // PLLFBDIV = 100 : VCO frequency = 8MHz * 100 = 800MHz
    // POSTDIV1 = 5   : Divide VCO out by 5 ((800MHz / 5) = 160MHz)
    // POSTDIV2 = 1   : Do not divide VCO out further 
    // INTDIV   = 2   : Divide Raw Internal VCO of 800MHz /4 for 200MHz (2*2 = 4)
    // These settings yield PLL2 Fout = 160MHz, PLL2 VCO Out = 200MHz

    // Update POSTDIV1/2 output dividers
    PLL2DIVbits.POSTDIV1 = 5;   // POSTDIV1 should always be greater than POSTDIV2
    PLL2DIVbits.POSTDIV2 = 1;
    PLL2CONbits.FOUTSWEN = 1;
    while (PLL2CONbits.FOUTSWEN == 1) { }

    // Update input divider and feedback divider
    PLL2DIVbits.PLLPRE   = 1;
    PLL2DIVbits.PLLFBDIV = 100;
    PLL2CONbits.PLLSWEN  = 1;
    while (PLL2CONbits.PLLSWEN == 1) { } 
    
    // Update VCO Output divider bits
    VCO2DIVbits.INTDIV  = 2;     // Divide raw VCO output by (2*2) = 4 
    PLL2CONbits.DIVSWEN = 1;
    while (PLL2CONbits.DIVSWEN == 1) { }

    // Update PLL clock source
    // Select POSC
    PLL2CONbits.NOSC = CLK_SRC_POSC;
    PLL2CONbits.OSWEN = 1;
    while (PLL2CONbits.OSWEN == 1) { }
    
    // Wait for PLL2 ready
    while (PLL2CONbits.CLKRDY  == 0) { }
    while (OSCCTRLbits.PLL2RDY == 0) { }
}


// Configure Clock Generator 1 for the System Clock
static void clkgen1_init(void)
{
    // The maximum supported System Clock (core CPU) is 200MHz
    // Note that CLKGEN1 is *always on*. Hence, we do not need to set the CLKxCON.ON bit
    
    // Configure backup source in case of a failure
    CLK1CONbits.BOSC = CLK_SRC_FRC;
    CLK1CONbits.FSCMEN = 1;
    
    // Set integer and fractional divide ratios ((PLL1 VCODIV Out = 200MHz / 1) = 200MHz
    CLK1DIVbits.INTDIV = 0;     // Integer divider is not used (1:1 clock)
    CLK1DIVbits.FRACDIV = 0;    // Fractional divider is not used
    
    // Update the dividers
    CLK1CONbits.DIVSWEN = 1;
    while (CLK1CONbits.DIVSWEN == 1) { }
    
    // Select CLKGEN source as PLL1 VCO Divider Out
    CLK1CONbits.NOSC = CLK_SRC_PLL1_VCODIV_OUT;
    CLK1CONbits.OSWEN = 1;
    while (CLK1CONbits.OSWEN == 1) { }

    // This setup yields the system clock as
    // 200MHz / 4 = 200MHz
    SYS_CLK_HZ = 200000000UL;
    
}

// Configure Clock Generator 6 for the ADC
void clkgen6_init(void)
{
    // The ADC module supports a maximum input clock of 320MHz.
    // We will supply the ADC with PLL1 Fout that we have already configured to be 320MHz.
    // This input clock is internally divided in the ADC module to generate its required 80MHz clock.
       
    // Turn on CLKGEN6
    CLK6CONbits.ON = 1;
    
    // Set integer and fractional divide ratios
    CLK6DIVbits.INTDIV = 0;     // Integer divider is not used (1:1 clock)
    CLK6DIVbits.FRACDIV = 0;    // Fractional divider is not used
    
    // Update the dividers
    CLK6CONbits.DIVSWEN = 1;
    while (CLK6CONbits.DIVSWEN == 1) { }
    
    // Select CLKGEN source as PLL1 Fout
    CLK6CONbits.NOSC = CLK_SRC_PLL1_FOUT;
    CLK6CONbits.OSWEN = 1;
    while (CLK6CONbits.OSWEN == 1) { }
}

// Clock Generator for Clock Monitor example - MONITOR CLOCK @ 160MHz
// Configure Clock Generator 11 for Clock Monitor Example - Frequency Drift Detection
void clkgen11_init(void)
{
    // Turn on CLKGEN11
    CLK11CONbits.ON = 1;
    
    // Set integer and fractional divide ratios
    CLK11DIVbits.INTDIV = 0;     // Integer divider is not used (1:1 clock)
    CLK11DIVbits.FRACDIV = 0;    // Fractional divider is not used
    
    // Update the dividers
    CLK11CONbits.DIVSWEN = 1;
    while (CLK11CONbits.DIVSWEN == 1) { }
    
    // Select CLKGEN source as PLL2 Fout
    CLK11CONbits.NOSC = CLK_SRC_PLL2_FOUT;  // 160MHz PLL2 FOut
    CLK11CONbits.OSWEN = 1;
    while (CLK11CONbits.OSWEN == 1) { }
}

void clock_init(void)
{
    // Note that device starts up with FRC as the system clock source
    // We can then switch to our desired clock source
    
    // Setup for primary oscillator
    // The dsPIC33AK512MPS512 GP DIM has an onboard 8MHz MEMS clock source
    OSCCFGbits.POSCMD = POSC_TYPE_EXTERNAL_CLOCK;
    OSCCTRLbits.POSCEN = 1;
    
    // Configure PLLs to generate the following frequencies
    // PLL1 Fout = 320MHz, and PLL1 VCO Out = 200MHz
    // PLL2 Fout = 160MHz, PLL2 VCO Out = 200MHz
    // The values presented here are the recommended clocking scheme to allow for all peripherals to be able to derive their
    // max supported clock speeds from the two PLLs
    pll1_init();
    pll2_init();

    // Configure CLKGENs
    // System clock @ 200MHz, via PLL1 VCO divide by 8
    // ADC clock    @ 320MHz, via PLL1 Fout
    clkgen1_init();     // Clock Generator for CPU @ 200MHz (Core Clock)
    SYS_CLK_HZ = 200000000UL;

    clkgen6_init();     // Clock Generator for ADC Module @ 320MHz

    // Clock Generator for Clock Monitor Frequency Drift Measurement example
    // Note: Clock Generator is always on with output of FRC @ 8MHz
    clkgen11_init();    // Clock Generator for Monitor Clock @ 160MHz

}
