// Clock Monitor Demonstration implementation 
// Configures Clock Monitor for Frequency Drift Detection Measurement

#include <xc.h>
#include "clock_monitor.h"
#include <stdint.h>

#include "gpio.h"

uint32_t Freq_Result;
uint32_t Count_Read;
uint32_t LWT_Read;
uint32_t HWT_Read;

void clock_monitor_init(void)
{
   
    // Start from known state, Clock Monitor 2 is disabled
    CM2CONbits.ON = 0;

    CM2CONbits.WIDTH = 0;       // Select Frequency Measurement Mode
    CM2SELbits.WINSEL = 1;      // Select 8MHz FRC, Clock Generator 2 (FRC on by default at POR)
                                // CLKGEN2 is on by default. Initialization for CLKGEN2 is not required
    CM2SELbits.CNTSEL = 10;     // Select Clock Generator 11
    CM2CONbits.CNTDIV = 0;      // Divide-by-1 (no divide)
    
    // Set up window threshold limits, from Warning, to Fail to Saturation
    CM2WINPR = 2999;            // Set Accumulation time window (reference clock counts((2999+1) = 3000)    
                                // (Expect CM2BUF == 60000 monitor clocks)

    // Counts = ( Desired Threshold Frequency * (CM2WINPR  / Reference Clock Freq) )
    CM2LFAIL = 59400; 	        // Low Threshold fail, target CM2BUF -1%
    CM2LWARN = 59700;	        // 67000 Low Threshold warning, target CM2BUF -0.5%
    CM2HWARN = 60300;           // High Threshold warning, target CM2BUF +0.5%  
    CM2HFAIL = 60600;           // High Threshold fail, target CM2BUF +1%
    CM2SAT = 60900;             // Set Saturation count, +1.5%
   
    //CM2LWARN = 0x00000000;	// Example of how to Disable Low Warning Detection Threshold 
                                // Potentially application wants Fail Threshold Detection only
                                // This is one option to consider. There will be others.
    
    //CM2HWARN = 0xFFFFFFFF;	// Example, likewise for High Warning Detection

    // ensure event bits are clear
    CM2STATbits.LWT = 0;
    CM2STATbits.HWT = 0;
    CM2STATbits.LFT = 0;
    CM2STATbits.HFT = 0;

    // Enable Interrupts for Count Ready, Warnings, Fails and Saturation Events
    IFS0bits.CM2CNTIF = 0;      // Enable Clock Monitor 2 Count Ready interrupt
    IEC0bits.CM2CNTIE = 1;
    
    IFS0bits.CM2WARNIF = 0;     // Enable Clock Monitor 2 Warning interrupt
    IEC0bits.CM2WARNIE = 1;

    IFS0bits.CM2FAILIF = 0;     // Enable Clock Monitor 2 Failure interrupt
    IEC0bits.CM2FAILIE = 1;
    
    IFS0bits.CM2SATIF = 0;      // Enable Clock Monitor 2 Count Saturation interrupt
    IEC0bits.CM2SATIE = 1;
   
    // Used for testing 
    FRCTUNbits.TUN = 0b111100;  // Set FRCTUN = 60 (0x3C) For test, demo system tuned for CM2BUF = ~60000

    // Set initial state to Green (OK)
    RGB_R_PPS = RGB_PPS_NONE;
    RGB_G_PPS = RGB_PPS_PWM;
    RGB_B_PPS = RGB_PPS_NONE;

    // Enable Clock Monitor 2
    CM2CONbits.ON = 1;

    // Startup test
    // If test is never exited there may be a Reference clock issue (did not start)
    // If test is exited, then the Reference clock has started
    while (CM2STATbits.TRIG == 0){ 
        Nop();
            
        // If test is never exited there may be a Reference clock issue (did not start)
        // Set error flag and exit this loop for external processing 
        // TRIG bit is (R/W/HS) so exit routine can set this bit to exit routine
        // Normally would set a time limit to wait but for this example it is not included
    }
    Nop();                      // Reference Clock has started under normal system conditions
}


// ****************************************************************************
// ****************************************************************************
// Clock Monitor 2 Interrupt Handlers

    // Interrupt Handler - Clock Monitor 2 Count Ready event
    void __attribute__((interrupt)) _CM2CNTInterrupt(void)
    {
        Nop();                          // simple BP test
        if (CM2STATbits.BUFV == 1){     // Test if BUF[31:0] contains a valid captured count ready for use
            
            // Read CM2BUF
            Count_Read = CM2BUF;   

            // calculate frequency
            Freq_Result = (uint32_t)(((uint64_t)Count_Read * 8000000ULL) / ((uint32_t)CM2WINPR + 1));
           
            CM2STATbits.BUFV = 0;       // Clear Count Ready Flag   
        }
        else{
            // Set some error condition as application code should not be here
            Nop();                      // simple BP test
                                        // set error flag and exit
        }
        _CM2CNTIF = 0;                  // Clear Count Ready Interrupt flag
    }
    

    // Interrupt Handler - Clock Monitor 2 Count Warning Event
    void __attribute__((interrupt)) _CM2WARNInterrupt(void)
    {
        Nop();                          // simple BP test
        if (CM2STATbits.LWT == 1){
            RGB_R_PPS = RGB_PPS_NONE;            
            RGB_G_PPS = RGB_PPS_NONE;    
            RGB_B_PPS = RGB_PPS_PWM;    // enable BLUE led for Warning event
            
            // Do something here as it may be different from High Warning Threshold Detect
        
            // Read CM2BUF
            Count_Read = CM2BUF;
            
            // calculate frequency
            Freq_Result = (uint32_t)(((uint64_t)Count_Read * 8000000ULL) / ((uint32_t)CM2WINPR + 1));

            CM2STATbits.LWT = 0;        // Clear Low Warning Threshold Status bit
        }
        else if (CM2STATbits.HWT == 1){
            RGB_R_PPS = RGB_PPS_NONE;            
            RGB_G_PPS = RGB_PPS_NONE;    
            RGB_B_PPS = RGB_PPS_PWM;    // enable BLUE led for Warning event
             
            // Do something here as it may be different from Low Warning Threshold Detect
          
            // Read CM2BUF
            Count_Read = CM2BUF;
            
            // calculate frequency
            Freq_Result = (uint32_t)(((uint64_t)Count_Read * 8000000ULL) / ((uint32_t)CM2WINPR + 1));

            CM2STATbits.HWT = 0;        // High Warning Threshold Status bit
        } 
        else{
            // Set some error condition as application code should not be here
            Nop();                      // simple BP test
                                        // should set error flag and exit
        }
        _CM2WARNIF = 0;                 // Clear Warning Event Interrupt flag
    }


     // Interrupt Handler - Clock Monitor 2 Count Fail Event
    void __attribute__((interrupt)) _CM2FAILInterrupt(void)
    {
        Nop();                              // just used for a BP set
        if (CM2STATbits.LFT == 1){
            RGB_R_PPS = RGB_PPS_PWM;        // enable RED led for Failure event
            RGB_G_PPS = RGB_PPS_NONE;    
            RGB_B_PPS = RGB_PPS_NONE;

            // Do something here
            
            // Read CM2BUF
            Count_Read = CM2BUF;

            // calculate frequency
            Freq_Result = (uint32_t)(((uint64_t)Count_Read * 8000000ULL) / ((uint32_t)CM2WINPR + 1));

            // If CM2BUF value is less than CM2LFAIL value then both LWT and LFT flags may have been asserted
            // You can disable Low Warning Threshold detection by setting CM2LWARN = 0x000000000;	 
            CM2STATbits.LFT = 0;            // Clear Low Fail Threshold Event Flag
            CM2STATbits.LWT = 0;            // Clear Low Warning Threshold Event Flag
            
        }
        else if (CM2STATbits.HFT == 1){
            RGB_R_PPS = RGB_PPS_PWM;        // enable RED led for failure event
            RGB_G_PPS = RGB_PPS_NONE;    
            RGB_B_PPS = RGB_PPS_NONE;

            // Do something here
               
            // Read CM2BUF
            Count_Read = CM2BUF;

            // calculate frequency
            Freq_Result = (uint32_t)(((uint64_t)Count_Read * 8000000ULL) / ((uint32_t)CM2WINPR + 1));

            // If CM2BUF value is higher than CM2HFAIL (but < CM2SAT) then both HWT and HFT may have been asserted
            // You can disable High Warning Threshold detection by setting CM2HWARN = 0xFFFFFFFF;	 
            CM2STATbits.HWT = 0;            // Clear High Warning Threshold Event Flag
            CM2STATbits.HFT = 0;            // Clear High Fail Threshold Event Flag
        } 
        else{
            // Set some error condition as application code should not be here
            Nop();                          // simple BP test
                                            // should set error flag and exit
        }   
      
        _CM2FAILIF = 0;                     // Clear Fail Event Interrupt flag
        _CM2WARNIF = 0;                     // Clear WARN Event Interrupt flag

        // Normal application use must do something to rectify the Catastrophic Event or once 
        // the module is re-enabled the application will return back to this ISR
        // Re-enable Clock Monitor 2 -- as result of the fail event module was disabled
        
        CM2CONbits.ON = 1;
    }
    

    // Interrupt Handler - Clock Monitor 2 Count Saturation event
    void __attribute__((interrupt)) _CM2SATInterrupt(void)
    {
        Nop();                              // simple BP test
        if (CM2STATbits.SATD == 1){         // Test if counter saturated at SAT[31:0]
            RGB_R_PPS = RGB_PPS_PWM;        // enable RED led for failure event
            RGB_G_PPS = RGB_PPS_NONE;    
            RGB_B_PPS = RGB_PPS_NONE;

            // Read CM2BUF
            Count_Read = CM2BUF;

            // Calculation of Frequency may not be required for SATD == 1. CM2BUF != CM2SAT. 
            Freq_Result = (uint32_t)(((uint64_t)Count_Read * 8000000ULL) / ((uint32_t)CM2WINPR + 1));
                
            CM2STATbits.SATD = 0;           // Clear Saturation Event Flag
        }
        else{
            // Set some error condition as application code should not be here
            Nop();                          // simple BP test
                                            // should set error flag and exit
        }

        // No rearm code required as Saturation is not considered a Catastrophic Event
        _CM2SATIF = 0;                      // Clear Saturation Event Interrupt flag
    }