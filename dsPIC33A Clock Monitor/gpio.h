// GPIO pin definitions and control macros.
// Provides macros for controlling LEDs, and switches. 

#ifndef GPIO_H
#define	GPIO_H

// General GPIO definitions
#define DEBOUNCE_MS                         50U  

#define GPIO_OUTPUT                         0
#define GPIO_INPUT                          1

#define GPIO_DIGITAL                        0
#define GPIO_ANALOG                         1

// RGB LED control macros
#define RGB_PPS_PWM                         _RPOUT_OCM1
#define RGB_PPS_NONE                        0

#define RGB_R_DIR                           _TRISD9
#define RGB_R_LAT                           _LATD9
#define RGB_R_PPS                           _RP58R
#define RGB_R_set_digital_output()          (RGB_R_DIR=GPIO_OUTPUT)
#define RGB_R_on()                          (RGB_R_LAT=1)
#define RGB_R_off()                         (RGB_R_LAT=0)
#define RGB_R_toggle()                      (RGB_R_LAT^=1)

#define RGB_G_DIR                           _TRISD0
#define RGB_G_LAT                           _LATD0
#define RGB_G_PPS                           _RP49R
#define RGB_G_set_digital_output()          (RGB_G_DIR=GPIO_OUTPUT)
#define RGB_G_on()                          (RGB_G_LAT=1)
#define RGB_G_off()                         (RGB_G_LAT=0)
#define RGB_G_toggle()                      (RGB_G_LAT^=1)

#define RGB_B_DIR                           _TRISD2
#define RGB_B_LAT                           _LATD2
#define RGB_B_PPS                           _RP51R
#define RGB_B_set_digital_output()          (RGB_B_DIR=GPIO_OUTPUT)
#define RGB_B_on()                          (RGB_B_LAT=1)
#define RGB_B_off()                         (RGB_B_LAT=0)
#define RGB_B_toggle()                      (RGB_B_LAT^=1)

// User LED control macros (LED0-LED7)
#define LED0_DIR                            _TRISC8
#define LED0_LAT                            _LATC8
#define LED0_set_digital_output()           (LED0_DIR=GPIO_OUTPUT)
#define LED0_on()                           (LED0_LAT=1)
#define LED0_off()                          (LED0_LAT=0)
#define LED0_toggle()                       (LED0_LAT^=1)

#define LED1_DIR                            _TRISC9
#define LED1_LAT                            _LATC9
#define LED1_set_digital_output()           (LED1_DIR=GPIO_OUTPUT)
#define LED1_on()                           (LED1_LAT=1)
#define LED1_off()                          (LED1_LAT=0)
#define LED1_toggle()                       (LED1_LAT^=1)

#define LED2_DIR                            _TRISC10
#define LED2_LAT                            _LATC10
#define LED2_set_digital_output()           (LED2_DIR=GPIO_OUTPUT)
#define LED2_on()                           (LED2_LAT=1)
#define LED2_off()                          (LED2_LAT=0)
#define LED2_toggle()                       (LED2_LAT^=1)

#define LED3_DIR                            _TRISC11
#define LED3_LAT                            _LATC11
#define LED3_set_digital_output()           (LED3_DIR=GPIO_OUTPUT)
#define LED3_on()                           (LED3_LAT=1)
#define LED3_off()                          (LED3_LAT=0)
#define LED3_toggle()                       (LED3_LAT^=1)

#define LED4_DIR                            _TRISC12
#define LED4_LAT                            _LATC12
#define LED4_set_digital_output()           (LED4_DIR=GPIO_OUTPUT)
#define LED4_on()                           (LED4_LAT=1)
#define LED4_off()                          (LED4_LAT=0)
#define LED4_toggle()                       (LED4_LAT^=1)

#define LED5_DIR                            _TRISC13
#define LED5_LAT                            _LATC13
#define LED5_set_digital_output()           (LED5_DIR=GPIO_OUTPUT)
#define LED5_on()                           (LED5_LAT=1)
#define LED5_off()                          (LED5_LAT=0)
#define LED5_toggle()                       (LED5_LAT^=1)

#define LED6_DIR                            _TRISC14
#define LED6_LAT                            _LATC14
#define LED6_set_digital_output()           (LED6_DIR=GPIO_OUTPUT)
#define LED6_on()                           (LED6_LAT=1)
#define LED6_off()                          (LED6_LAT=0)
#define LED6_toggle()                       (LED6_LAT^=1)

#define LED7_DIR                            _TRISC15
#define LED7_LAT                            _LATC15
#define LED7_set_digital_output()           (LED7_DIR=GPIO_OUTPUT)
#define LED7_on()                           (LED7_LAT=1)
#define LED7_off()                          (LED7_LAT=0)
#define LED7_toggle()                       (LED7_LAT^=1)

// Push button switch input macros (S1-S3)
#define S1_DIR                              _TRISF3
#define S1_RPINR                            84
#define S1_set_digital_input()              (S1_DIR=GPIO_INPUT)

#define S2_ANSEL                            (_ANSELF0)
#define S2_DIR                              _TRISF0
#define S2_RPINR                            81
#define S2_set_digital_input()              (S2_DIR=GPIO_INPUT)
#define S2_analog_disable()                 (S2_ANSEL=GPIO_DIGITAL)

#define S3_ANSEL                            _ANSELB2
#define S3_DIR                              _TRISB2
#define S3_RPINR                            19
#define S3_set_digital_input()              (S3_DIR=GPIO_INPUT)
#define S3_analog_disable()                 (S3_ANSEL=GPIO_DIGITAL)

// Initialize all GPIO pins (LEDs, switches) and external interrupts
void gpio_init(void);

#endif	/* GPIO_H */

