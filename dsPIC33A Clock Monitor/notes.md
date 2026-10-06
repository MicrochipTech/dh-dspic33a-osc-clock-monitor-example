# dsPIC33A Clock Monitor Notes

This project demonstrates the Clock Monitor 2 (CM2) peripheral in frequency measurement mode. CM2
compares a monitored clock against a reference clock and flags drift outside a set range.

A small peripheral demo runs alongside CM2: system clock setup, buttons, LEDs, and a
potentiometer-driven LED bar graph. The demo targets the dsPIC33A Curiosity Platform Development
Board, with a dsPIC33AK512MPS512 GP DIM. Refer to [main.c](main.c#L4).

[Clock_Monitor_Flowchart.png](Clock_Monitor_Flowchart.png) (source:
[Clock_Monitor_Flowchart.drawio](Clock_Monitor_Flowchart.drawio)) shows the control flow.
[_tools/build_flowchart.py](_tools/build_flowchart.py) generates both files.

**RGB LED and push buttons:** the RGB LED shows the last CM2 event by color -- green, blue, or red.
Refer to [RGB LED (tri-color status indicator)](#rgb-led-tri-color-status-indicator). Push buttons S1,
S2, and S3 trigger drift live by writing `FRCTUNbits.TUN`. Refer to
[Triggering drift live](#triggering-drift-live-s1-s2-and-s3).

## Index

- [System clock setup](clock.c#L180-L210) -- PLL1, PLL2, CLKGEN1 (System Clock), CLKGEN6 (ADC Clock),
  CLKGEN2 (CM2 Reference Clock), CLKGEN11 (CM2 Monitored Clock)
- [Clock Monitor 2 init](clock_monitor.c#L15-L86) -- frequency measurement setup and startup wait
- [Clock Monitor 2 thresholds](clock_monitor.c#L31-L36)
- [Clock Monitor 2 interrupt handlers](clock_monitor.c#L94-L242)
- [main](main.c#L24-L48) -- [`system_init()`](main.c#L16-L22) order, then the main loop with its own
  [`CM2STATbits.TRIG` check](main.c#L38-L46)
- [Push-button drift triggers S1, S2, S3](gpio.c#L91-L182)

---

## System Clock Setup

> Source: [clock.c](clock.c#L180-L210), [clock.h](clock.h)

At power-up, the device runs on the internal 8MHz FRC. [`clock_init()`](clock.c#L180-L210) enables the
primary oscillator (POSC), configures two PLLs, and then configures the clock generators. PLL1 feeds
CLKGEN1 and CLKGEN6. PLL2 feeds CLKGEN11. CLKGEN2 runs from the FRC and needs no init call, because the
FRC is the default clock source at Power-On-Reset.

| Block        | Full name                                       | Source                        | Output                          |
|--------------|-------------------------------------------------|-------------------------------|---------------------------------|
| **PLL1**     | Phase-Locked Loop 1                             | POSC (8MHz external clock)    | Fout 320MHz / VCODIV Out 200MHz |
| **PLL2**     | Phase-Locked Loop 2                             | POSC (8MHz external clock)    | Fout 160MHz / VCODIV Out 200MHz |
| **CLKGEN1**  | Clock Generator 1 -- System/CPU Clock           | PLL1 VCODIV Out               | **200MHz**                      |
| **CLKGEN6**  | Clock Generator 6 -- ADC Module Clock           | PLL1 Fout                     | **320MHz**                      |
| **CLKGEN2**  | Clock Generator 2 -- CM2 Reference/Window Clock | FRC (8MHz), on by default     | **8MHz**                        |
| **CLKGEN11** | Clock Generator 11 -- CM2 Monitored Clock       | PLL2 Fout                     | **160MHz**                      |

The two VCODIV outputs both equal 200MHz, from different VCO frequencies and dividers (PLL1: 1600MHz
VCO / 8; PLL2: 800MHz VCO / 4). PLL1's VCODIV Out feeds CLKGEN1. PLL2's VCODIV Out has no consumer in
this project. CLKGEN11 uses PLL2's Fout (160MHz).

`clock_init()` calls, in order: [`pll1_init()`](clock.c#L13-L56), [`pll2_init()`](clock.c#L60-L103),
[`clkgen1_init()`](clock.c#L107-L133), [`clkgen6_init()`](clock.c#L136-L157),
[`clkgen11_init()`](clock.c#L161-L178). It runs before `clock_monitor_init()`, which
[`demo_init()`](demo_app.c#L67-L72) calls after `system_init()`. All clock generators therefore run
before CM2 is configured.

PLL1, CLKGEN1, and CLKGEN6 support the general demo: CPU clock and ADC sampling. PLL2, CLKGEN2, and
CLKGEN11 support CM2.

`clkgen1_init()` sets no `ON` bit, because CLKGEN1 is always on. `clkgen6_init()` and `clkgen11_init()`
each set their own `ON` bit. `pll1_init()`, `pll2_init()`, and `clkgen1_init()` each configure a backup
source (`BOSC`) and a fail-safe clock monitor (`FSCMEN`).

---

## Clock Monitor 2 -- Frequency Drift Detection

> Source: [clock_monitor.c](clock_monitor.c#L15-L242), [clock_monitor.h](clock_monitor.h)

CM2 operates in Frequency Measurement Mode (`CM2CONbits.WIDTH = 0`). CM2 counts edges of a monitored
clock over a fixed window, set by a reference clock. At the end of each window, CM2 stores the count in
`CM2BUF` and compares it against the thresholds.
[`clock_monitor_init()`](clock_monitor.c#L15-L86) disables CM2, configures it, enables it, and then
waits for the reference clock to start.

```
Reference clock (Clock Generator 2, via CM2SELbits.WINSEL = 1) --> WINPR-count window (3000 ref counts, nominally 375us)
                                                              |
                                                              v
Monitored clock (CLKGEN11 @ 160MHz, via PLL2 Fout)      --> counted for the window duration --> CM2BUF
                                                                                                 |
                                                                          compared against HWARN/LWARN/HFAIL/LFAIL/SAT
```

### [Window and monitored clock selection](clock_monitor.c#L19-L28)

- `CM2CONbits.ON = 0` -- disables CM2 before any CM2 configuration write.
- `CM2CONbits.WIDTH = 0` -- selects Frequency Measurement Mode.
- `CM2SELbits.WINSEL = 1` -- selects Clock Generator 2 as the reference/window clock.
- `CM2SELbits.CNTSEL = 10` -- selects Clock Generator 11 (160MHz) as the monitored clock.
- `CM2CONbits.CNTDIV = 0` -- divides the monitored clock by 1.
- `CM2WINPR = 2999` -- sets the window to `CM2WINPR + 1` = 3000 reference clock counts (375us at
  8MHz).
- `FRCTUNbits.TUN = 0b111100` -- sets the FRC trim to 60 (`0x3C`), the healthy baseline. Push button S2
  writes this value back at run time.

[`clock_monitor_init()`](clock_monitor.c#L74-L85) ends with a startup wait: `while
(CM2STATbits.TRIG == 0){ Nop(); }`. This loop blocks `clock_monitor_init()`, and so `demo_init()` and
`main()`, until the reference clock produces its first edge and sets `TRIG`. `main()`'s own
[`CM2STATbits.TRIG` check](main.c#L38-L46) therefore passes on its first evaluation. Neither loop has
a timeout.

### [Drift thresholds](clock_monitor.c#L31-L36)

All thresholds use the unit of `CM2BUF`: monitored-clock counts per window. The nominal count is 60000.

| Register    | Value | Offset from nominal | Meaning                                   |
|-------------|-------|---------------------|-------------------------------------------|
| `CM2LFAIL`  | 59400 | -1%                 | Low **failure** threshold                 |
| `CM2LWARN`  | 59700 | -0.5%               | Low **warning** threshold                 |
| *(nominal)* | 60000 | 0%                  | Expected count for a healthy clock        |
| `CM2HWARN`  | 60300 | +0.5%               | High **warning** threshold                |
| `CM2HFAIL`  | 60600 | +1%                 | High **failure** threshold                |
| `CM2SAT`    | 60900 | +1.5%               | Saturation count                          |

The nominal count is the 160MHz / 8MHz = 20 ratio times the 3000-count window. The S1 and S3
`FRCTUNbits.TUN` values each target one row of this table.

Two commented-out lines after the thresholds show how to disable a Warning threshold: `CM2LWARN = 0` and
`CM2HWARN = 0xFFFFFFFF`. Fail and Saturation detection stay active. This demo leaves both lines
disabled.

`clock_monitor_init()` also clears the `CM2STAT` bits `LWT`, `HWT`, `LFT`, and `HFT`. A stale bit from a
previous run then cannot look like a new event. Before it enables CM2, it sets the RGB LED to green.

### Interrupts

`clock_monitor_init()` clears and enables four CM2 interrupt sources. Each handler starts with a
`Nop()` as a debugger breakpoint anchor. Each handler reads `CM2BUF` into `Count_Read`, recomputes
`Freq_Result`, and clears its own `CM2STAT` bit and interrupt flag. The Warning, Failure, and
Saturation handlers also set the RGB LED (see
[RGB LED (tri-color status indicator)](#rgb-led-tri-color-status-indicator)).

- [`_CM2CNTInterrupt`](clock_monitor.c#L94-L113) (`CM2CNTIE`) -- **Count Ready**: fires once per
  completed window, inside `if (CM2STATbits.BUFV == 1)`. Clears `BUFV`. Does not change the RGB LED.
- [`_CM2WARNInterrupt`](clock_monitor.c#L117-L156) (`CM2WARNIE`) -- **Warning**: fires when `CM2BUF`
  crosses `CM2HWARN` or `CM2LWARN`. Clears `LWT` or `HWT`, whichever is set.
- [`_CM2FAILInterrupt`](clock_monitor.c#L160-L214) (`CM2FAILIE`) -- **Failure**: fires when `CM2BUF`
  crosses `CM2HFAIL` or `CM2LFAIL`. Clears `LFT`+`LWT`, or `HFT`+`HWT`, because a Fail event also
  crosses its matching Warn threshold unless that threshold is disabled. Clears both `_CM2FAILIF` and
  `_CM2WARNIF`. A Failure event disables CM2 in hardware. This handler re-enables it
  (`CM2CONbits.ON = 1`) as its last step.
- [`_CM2SATInterrupt`](clock_monitor.c#L218-L242) (`CM2SATIE`) -- **Saturation**: fires when the count
  clamps at `CM2SAT`, inside `if (CM2STATbits.SATD == 1)`. Clears `SATD`. This handler does not
  re-enable CM2, because Saturation is not a catastrophic event.

No handler restores the baseline `FRCTUNbits.TUN` value. Only S2 does that.

Each handler computes `Freq_Result` from its `Count_Read` snapshot in the same way, for example in
[`_CM2CNTInterrupt`](clock_monitor.c#L100-L103):
```c
Count_Read = CM2BUF;
...
Freq_Result = (uint32_t)(((uint64_t)Count_Read * 8000000ULL) / ((uint32_t)CM2WINPR + 1));
```
The math uses integers, so no `double` math runs in the interrupt handler. `8000000ULL` is the nominal
8MHz reference clock. The divisor `CM2WINPR + 1` is the window length, 3000 counts. The result is
`Count_Read * 8MHz / 3000`.

`Count_Read` ([clock_monitor.c:11](clock_monitor.c#L11)) is a file-scope global with no `extern`.
[`Freq_Result`](clock_monitor.h#L5) is `extern`, so other files can read the latest measurement.

### RGB LED (tri-color status indicator)

[`gpio_pins_init()`](gpio.c#L12-L61) routes SCCP1's PWM output to the red channel at boot.
[`clock_monitor_init()`](clock_monitor.c#L66-L69) then routes it to green, and clears red and blue,
before it enables CM2. Each of the Warning, Failure, and Saturation handlers routes the PWM output to
one channel and clears the other two:

| Event                          | Handler              | RGB channel |
|--------------------------------|----------------------|-------------|
| Warning (`LWT` or `HWT`)       | `_CM2WARNInterrupt`  | Blue        |
| Failure (`LFT` or `HFT`)       | `_CM2FAILInterrupt`  | Red         |
| Saturation (`SATD`)            | `_CM2SATInterrupt`   | Red         |

Failure and Saturation both show red, so red alone does not distinguish them.

The LED shows the most recent event. The Count Ready handler does not reset it. The LED therefore stays
blue or red after the clock recovers, until a new event occurs or S2 sets it to green.

### Triggering drift live (S1, S2, and S3)

> Source: [gpio.c](gpio.c#L91-L182)

Each push button has its own external-interrupt handler. The handler writes `FRCTUNbits.TUN`, which
trims the FRC that drives CM2's reference clock, CLKGEN2. Each handler also updates a `static uint32_t
debounce_tick` from `get_msec()` and `DEBOUNCE_MS` (50ms). This is bookkeeping only. The
`FRCTUNbits.TUN` write runs unconditionally, so the handler rewrites the trim on every bounce.

S1 and S3 pick the `FRCTUNbits.TUN` value from the potentiometer position at the moment of the press.
Each handler reads `AD5CH0DATA` directly. It does not use the ADC interrupt flag (`adc5_ch0_data_ready`)
or the `potentiometer_adc_counts` global that the LED bar graph uses. S2 ignores the potentiometer.

- [`_INT1Interrupt`](gpio.c#L91-L124) (S1): lowers the FRC trim. The FRC slows, the window lengthens,
  and `CM2BUF` rises.

  | `AD5CH0DATA` | `FRCTUNbits.TUN`        | Event                                          |
  |--------------|-------------------------|------------------------------------------------|
  | `< 0x0800`   | `0b110110` (54, `0x36`) | HWARN -- `CM2HWARN < CM2BUF < CM2HFAIL`        |
  | `< 0x0A00`   | `0b110001` (49, `0x31`) | HFAIL -- `CM2BUF > CM2HFAIL`                   |
  | `>= 0x0A00`  | `0b101100` (44, `0x2C`) | SATD -- saturation event before count captured |

  These three bands cover the full `AD5CH0DATA` range.
- [`_INT2Interrupt`](gpio.c#L127-L150) (S2): writes `FRCTUNbits.TUN = 0b111100` (60, `0x3C`), the
  baseline value. It also sets the RGB LED to green. S2 is the "reset to healthy" button.
- [`_INT3Interrupt`](gpio.c#L153-L182) (S3): raises the FRC trim. The FRC speeds up, the window
  shortens, and `CM2BUF` falls.

  | `AD5CH0DATA` | `FRCTUNbits.TUN`       | Event                                   |
  |--------------|------------------------|-----------------------------------------|
  | `< 0x0400`   | `0b000010` (2, `0x02`) | LWARN -- `CM2LWARN > CM2BUF > CM2LFAIL` |
  | `< 0x0600`   | `0b000110` (6, `0x06`) | LFAIL -- `CM2BUF < CM2LFAIL`            |

  At or above `0x0600`, `FRCTUNbits.TUN` keeps its current value.

S1 and S3 do not touch the RGB LED. The LED changes only after CM2 reports the event. A drift event does
not clear itself. The trim stays at the triggered value until S2 writes the baseline, or a later S1 or
S3 press selects a different band.

---

## Supporting peripherals (not specific to clock monitoring)

The rest of the project (`gpio.c`, `adc.c`, `sccp1.c`, `sccp2.c`, `tmr1_tick.c`, `demo_app.c`) builds
the demo app that runs alongside CM2. `config_bits.c` holds the device `#pragma config` fuse settings,
independent of any one peripheral.

- `gpio.c` / `tmr1_tick.c` / `sccp1.c` -- LEDs, switches, the millisecond tick, and RGB PWM.
  - `sccp1_init()` configures SCCP1 as a 100kHz PWM source at 5% duty. The PWM feeds the RGB LED
    through the channel that the `RGB_x_PPS` routing selects.
  - [`tmr1_systick_init()`](tmr1_tick.c#L14-L28) configures TMR1 for a 1ms tick: `TCS = 0` (system
    clock), `TCKPS = 0b0` (1:1 prescale), and `PR1 = 100000`. TMR1 counts at `SYS_CLK_HZ / 2`
    (100MHz).
  - [`_T1Interrupt`](tmr1_tick.c#L42-L53) fires once per `PR1` period. It increments `tick_ms` every
    time and `tick_s` every 1000th time.
  - [`get_msec()`](tmr1_tick.c#L30-L33) and [`get_sec()`](tmr1_tick.c#L35-L38) return these values.
    `gpio.c` uses `get_msec()` for button debounce bookkeeping. `main.c` uses it for the LED0 heartbeat
    blink (500ms).
- `adc.c` / `sccp2.c` -- SCCP2 triggers ADC5 CH0 sampling of the potentiometer at 100kHz.
  `_AD5CH0Interrupt` copies `AD5CH0DATA` to `potentiometer_adc_counts` and sets
  `adc5_ch0_data_ready`. [`update_led_bargraph()`](demo_app.c#L14-L65) then drives LED1 through LED7
  from `potentiometer_adc_counts`, scaled to 0-7. This path is independent of CM2.
