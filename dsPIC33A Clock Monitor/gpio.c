// GPIO implementation.
// Configures GPIO pins for LEDs, switches, and handles push button interrupts for FRC tuning aid

#include <xc.h>
#include "adc.h"

#include "gpio.h"
#include "tmr1_tick.h"

volatile uint32_t reset_clocks = 0;

static void gpio_pins_init(void)
{
    // Configure RGB LED pins
    RGB_R_off();
    RGB_G_off();
    RGB_B_off();
    RGB_R_set_digital_output();
    RGB_G_set_digital_output();
    RGB_B_set_digital_output();
    RGB_R_PPS = RGB_PPS_PWM;
    RGB_G_PPS = RGB_PPS_NONE;
    RGB_B_PPS = RGB_PPS_NONE;
    
    // Configure user LEDs 0-8
    LED0_set_digital_output();
    LED1_set_digital_output();
    LED2_set_digital_output();
    LED3_set_digital_output();
    LED4_set_digital_output();
    LED5_set_digital_output();
    LED6_set_digital_output();
    LED7_set_digital_output();
    LED0_off();
    LED1_off();
    LED2_off();
    LED3_off();
    LED4_off();
    LED5_off();
    LED6_off();
    LED7_off();

    // Configure switch inputs
    S1_set_digital_input();
    S2_set_digital_input();
    S3_set_digital_input();
    
    // Switch S2 and S3 are on pins which also have analog functions
    // Analog functions have priority over digital functions, hence, we must disable analog function for the pin
    // Note: S1 doesn't need analog disable (no ANSEL register)
    S2_analog_disable();
    S3_analog_disable();
    
    
    // Configure PPS for switch inputs
    // PPS is configured to assign INT1-3 external interrupts to SW1-3 respectively
    _INT1R = S1_RPINR;
    _INT2R = S2_RPINR;
    _INT3R = S3_RPINR;

}

void gpio_init(void)
{
    // Configure all the pins
    gpio_pins_init();

    // Configure and enable External Interrupts 1-3
    // Push buttons are active low
    // INTxEP = Edge detect polarity select. 0: positive edge; 1: negative edge
    _INT1EP = 1;
    _INT2EP = 1;
    _INT3EP = 1;
    
    // Clear flags before enabling interrupts
    _INT1IF = 0;
    _INT2IF = 0;
    _INT3IF = 0;

    // Set Interrupt Priority level to 5
    _INT2IP = 0b101;
   
    // Enable the external interrupts
    _INT1IE = 1;
    _INT2IE = 1;
    _INT3IE = 1;
    
}

// cppcheck-suppress misra-c2012-8.4 ; ISR prototype provided by device header
void __attribute__((interrupt)) _INT1Interrupt(void)
{
    // _INT1Interrupt() entered when S1 is pressed

    static uint32_t debounce_tick = 0;
    uint32_t now_tick = get_msec();
    
    if ((now_tick - debounce_tick) >= DEBOUNCE_MS) {
                
        debounce_tick = now_tick;
    }
    
    Nop();                             // just used for a simple BP set

    // Decrease FRC (make Reference Clock Slower compared to baseline)
    // This can be viewed as a Faster Monitor Clock
    // Switch S1 enables entry to FRCTUN -- to decrease FRC frequency  
    // Depending on ADC results (LEDs illuminated) determines whether an LWARN, LFAIL or SATD event occurs
        
    // LED7, LED6 and LED5 are on (3 LEDS are on)
    if ( AD5CH0DATA < 0x0800 ) {
        FRCTUNbits.TUN = 0b110110;   // 54(0x36), HWARN Event = (CM2HWARN < CM2BUF < CM2HFAIL)
    }
    // LED7, LED6, LED5 and LED4 are on (4 LEDS are on)
    else if (AD5CH0DATA < 0x0A00) {
        FRCTUNbits.TUN = 0b110001;   // 49(0x31), HFAIL Event = (CM2BUF > CM2HFAIL)
    }
    // LED7, LED6, LED5, LED4, LED3 and LED2 (5-6 LEDS are on)
    else if (AD5CH0DATA >= 0x0A00) {
        FRCTUNbits.TUN = 0b101100;   // 44(0x2C), SATD Event – Saturation event before Count captured
    }

    _INT1IF = 0;
}

// cppcheck-suppress misra-c2012-8.4 ; ISR prototype provided by device header
void __attribute__((interrupt)) _INT2Interrupt(void)
{
    // _INT2Interrupt() entered when S2 is pressed

    static uint32_t debounce_tick = 0;
    uint32_t now_tick = get_msec();
   
    if ((now_tick - debounce_tick) >= DEBOUNCE_MS) {
               
        debounce_tick = now_tick;
    }
    
    Nop();                      // just used for a simple BP set

    // Reset 8MHz FRC, demo system tuned for CM2BUF = ~60000   
    FRCTUNbits.TUN = 0b111100;  // 60 (0x3C) - Reset to code initialize state

    // Reset to normal condition
    RGB_R_PPS = RGB_PPS_NONE;
    RGB_G_PPS = RGB_PPS_PWM;    // set RGB to Green (normal state)
    RGB_B_PPS = RGB_PPS_NONE;

    _INT2IF = 0;
}

// cppcheck-suppress misra-c2012-8.4 ; ISR prototype provided by device header
void __attribute__((interrupt)) _INT3Interrupt(void)
{
    // _INT3Interrupt() entered when S3 is pressed

    static uint32_t debounce_tick = 0;
    uint32_t now_tick = get_msec();
   
    if ((now_tick - debounce_tick) >= DEBOUNCE_MS) {
                
        debounce_tick = now_tick;
    }
      
    Nop();                             // just used for a simple BP set

    // Increase FRC (make Reference Clock Faster compared to baseline)
    // This can also be viewed as a Slower Monitor Clock
    // Switch S3 enables entry to FRCTUN ++ to increase FRC frequency  
    // Depending on ADC results (LEDs illuminated) determines whether an LWARN or LFAIL event occurs
    
    // LED7 is on (ONLY) - Adjust R14 for the LED condition
    if ( AD5CH0DATA < 0x0400 ){
        FRCTUNbits.TUN = 0b000010;     // 02(0x02), LWARN Event = (CM2LWARN  > CM2BUF > CM2LFAIL)
    }
    // LED7 and LED6 are on (BOTH) - Adjust R14 for the LED condition
    else if (AD5CH0DATA < 0x0600) {
        FRCTUNbits.TUN = 0b000110;     // 06(0x06), LFAIL Event = (CM2BUF < CM2LFAIL)
    }
    
    _INT3IF = 0;
}