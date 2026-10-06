# Generates the Clock Monitor firmware flow chart as matching .png and .drawio
# files, laid out on a single-column PORTRAIT page (8.5in wide, height auto-
# fit to content) with 0.5in margins on all sides.
#
# Visual format follows a "function box + filename" reference style: each
# process box shows a bold call name, its source filename, and a plain
# description line per sub-call; autonomous/interrupt-driven activity is
# grouped in dashed-border containers; the main while(1) loop is a solid
# container. Decision diamonds sit on a left-biased centerline (DCX) so a
# self-loop / bypass label always has a clear right-hand lane to sit in.
#
# One coordinate system drives both outputs: 1 unit == 1/100 inch. Page
# height is computed from the actual content height, so this script must
# finish laying everything out (populating PRIMS) before it knows PAGE_H.
# draw.io's default page grid uses the same 100-units-per-inch convention,
# so the .drawio geometry is a 1:1 copy of the PNG layout.

import math
import xml.etree.ElementTree as ET
from xml.dom import minidom
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- geometry --
PAGE_W = 850           # 8.5in wide; PAGE_H is computed after layout (below)
SCALE = 3              # PNG render scale for print resolution (300 dpi at 8.5in wide)

MARGIN = 50                       # 0.5 in on every side
CONTENT_X = MARGIN                # 50
CONTENT_R = PAGE_W - MARGIN        # 800
CONTENT_W = CONTENT_R - CONTENT_X  # 750

FONT_DIR = r"C:\Windows\Fonts"
def font(path, size):
    return ImageFont.truetype(path, int(size * SCALE))

F_MONO  = lambda s=12: font(f"{FONT_DIR}\\consola.ttf", s)
F_MONOB = lambda s=12: font(f"{FONT_DIR}\\consolab.ttf", s)
F_SANS  = lambda s=10: font(f"{FONT_DIR}\\segoeui.ttf", s)
F_SANSI = lambda s=10: font(f"{FONT_DIR}\\segoeuii.ttf", s)
F_SANSB = lambda s=10: font(f"{FONT_DIR}\\segoeuib.ttf", s)
FONT_FN = {"title": F_MONOB, "mono": F_MONO, "monob": F_MONOB, "sans": F_SANS, "sansi": F_SANSI, "sansb": F_SANSB}

def get_font(spec):
    kind, size = spec
    return FONT_FN[kind](size)

def text_w(s, fspec):
    return get_font(fspec).getlength(s) / SCALE

# ink / lines
INK    = (22, 35, 46)
MUTED  = (91, 107, 120)
PAPER  = (247, 249, 251)
LINE   = (51, 71, 90)
ACCENT = (35, 92, 133)
NOMINAL= (27, 128, 82)
WARN   = (5, 56, 209)
FAIL   = (198, 22, 16)
SAT    = (198, 22, 16)
BUTTON = (150, 110, 20)
INIT   = (124, 58, 149)
CM2HW  = (71, 85, 105)

# light pastel fills
BG_START   = (232, 239, 246)
BG_MAIN    = (223, 236, 247)
BG_BRANCH  = (222, 241, 238)
BG_DECISION= (236, 231, 247)
BG_SUB     = (236, 238, 240)
BG_NOMINAL = (224, 244, 233)
BG_WARN    = (210, 220, 249)
BG_FAIL    = (249, 212, 210)
BG_SAT     = (249, 212, 210)
BG_BUTTON  = (253, 244, 219)
BG_INIT    = (237, 225, 246)
BG_CM2HW   = (226, 232, 240)
BG_GRAY    = (233, 236, 239)

DRAWIO_HEX = {
    INK: "#16232E", MUTED: "#5B6B78", LINE: "#33475A", ACCENT: "#235C85",
    NOMINAL: "#1B8052", WARN: "#0538D1", FAIL: "#C61610", SAT: "#C61610", BUTTON: "#966414", INIT: "#7C3A95", CM2HW: "#475569",
    PAPER: "#F7F9FB",
    BG_START: "#E8EFF6", BG_MAIN: "#DFECF7", BG_BRANCH: "#DEF1EE", BG_DECISION: "#ECE7F7",
    BG_SUB: "#ECEEF0", BG_NOMINAL: "#E0F4E9", BG_WARN: "#D2DCF9", BG_FAIL: "#F9D4D2", BG_SAT: "#F9D4D2",
    BG_BUTTON: "#FDF4DB", BG_GRAY: "#E9ECEF", BG_INIT: "#EDE1F6", BG_CM2HW: "#E2E8F0",
}

# Collected drawing primitives, shared by both renderers.
PRIMS = []
def P(kind, **kw):
    PRIMS.append((kind, kw))

def rect(x, y, w, h, dashed=False, color=LINE, sw=1.3, fill=None):
    P("rect", x=x, y=y, w=w, h=h, dashed=dashed, color=color, sw=sw, fill=fill)

def diamond(cx, cy, rx, ry, color=LINE, sw=1.3, fill=None):
    P("diamond", cx=cx, cy=cy, rx=rx, ry=ry, color=color, sw=sw, fill=fill)

def ellipse(cx, cy, rx, ry, color=LINE, sw=1.3, fill=None):
    P("ellipse", cx=cx, cy=cy, rx=rx, ry=ry, color=color, sw=sw, fill=fill)

def line(pts, color=INK, sw=1.3, arrow=True, dashed=False):
    P("line", pts=pts, color=color, sw=sw, arrow=arrow, dashed=dashed)

def dot(cx, cy, r=3.2, color=INK):
    P("dot", cx=cx, cy=cy, r=r, color=color)

def text(x, y, s, f, color=INK, anchor="la", rot=0):
    P("text", x=x, y=y, s=s, f=f, color=color, anchor=anchor, rot=rot)

def bar(x, y, w, h, color):
    P("rect", x=x, y=y, w=w, h=h, dashed=False, color=color, sw=0, fill=color)

def header_line(x, y, bold_part, plain_part, bold_f, plain_f, color=INK, mcolor=MUTED, anchor="la"):
    text(x, y, bold_part, bold_f, color=color, anchor=anchor)
    bw = text_w(bold_part, bold_f)
    text(x + bw, y, plain_part, plain_f, color=mcolor, anchor=anchor)
    return bw

# ==========================================================================
# BOX HELPERS
# ==========================================================================
ROW_H = 32          # bold call-line + plain description line, per row
HEAD_H = 28         # box header band (function name -- file.c)
PAD_BOTTOM = 14

def func_box(x, y, w, func_name, filename, rows, fill, extra_note=None):
    """rows: list of (call_name, call_file, desc) triples."""
    n = len(rows)
    extra_h = 18 if extra_note else 0
    h = HEAD_H + n * ROW_H + extra_h + PAD_BOTTOM
    rect(x, y, w, h, fill=fill)
    header_line(x + 16, y + 9, func_name, "  \u2014  " + filename, ("monob", 13.5), ("sans", 11), color=INK, mcolor=MUTED)
    ry = y + HEAD_H + 4
    for call_name, call_file, desc in rows:
        header_line(x + 16, ry, call_name, "  \u2014  " + call_file, ("mono", 10.6), ("sans", 9.3), color=INK, mcolor=MUTED)
        text(x + 16, ry + 14, desc, ("sans", 9.7), color=MUTED)
        ry += ROW_H
    if extra_note:
        text(x + 16, ry + 3, extra_note, ("sans", 9.4), color=MUTED)
    return h

def simple_box(x, y, w, func_name, filename, desc_lines, fill):
    h = HEAD_H + len(desc_lines) * 16 + PAD_BOTTOM
    rect(x, y, w, h, fill=fill)
    header_line(x + 16, y + 9, func_name, "  \u2014  " + filename, ("monob", 13.5), ("sans", 11), color=INK, mcolor=MUTED)
    ry = y + HEAD_H + 6
    for ln in desc_lines:
        text(x + 16, ry, ln, ("sans", 10), color=MUTED)
        ry += 16
    return h

def dashed_container_title(x, y, w, title):
    text(x + w / 2, y + 9, title, ("monob", 13), color=INK, anchor="ma")

def section_title(y, s):
    text(CONTENT_X, y, s, ("monob", 14.5), color=ACCENT)
    return y + 19

# ==========================================================================
# HEADER
# ==========================================================================
text(CONTENT_X, 62, "CLOCK MONITOR \u2014 CONTROL FLOW", ("title", 22), color=INK)
text(CONTENT_X, 86, "dsPIC33AK512MPS512 GP DIM \u00b7 CM2 Frequency-Drift Detection", ("sans", 12.5), color=MUTED)

# Left column: containers/backdrops. Right column: ISR severity colors --
# grouped here so the key lines up with the FRC Test-Injection cards and the
# CM2 Interrupt Service Routines box, both drawn on the right side below.
legend_left_a  = [("Background HW", CM2HW, BG_CM2HW)]
legend_left_b  = [("Push-button ISR (FRC Test Injection)", BUTTON, BG_BUTTON)]
legend_right_a = [("CNT ready (Green RGB)", NOMINAL, BG_NOMINAL), ("Warning (Blue RGB)", WARN, BG_WARN)]
legend_right_b = [("Fail (Red RGB)", FAIL, BG_FAIL), ("Saturation (Red RGB)", SAT, BG_SAT)]
LEGEND_TOP = 108
LEGEND_ROW_H = 20
LEGEND_COL_X = [CONTENT_X, CONTENT_X + 160, CONTENT_X + 440, CONTENT_X + 440 + 160]
legend_cols = (legend_left_a, legend_left_b, legend_right_a, legend_right_b)
LEGEND_ROWS_MAX = max(len(col_items) for col_items in legend_cols)
for col_items, lx in zip(legend_cols, LEGEND_COL_X):
    col_offset = (LEGEND_ROWS_MAX - len(col_items)) * LEGEND_ROW_H / 2
    for r, (label, col, bgcol) in enumerate(col_items):
        ly = LEGEND_TOP + col_offset + r * LEGEND_ROW_H
        rect(lx, ly, 13, 13, color=col, sw=1.1, fill=bgcol)
        text(lx + 18, ly, label, ("sans", 11), color=INK)

RULE_Y = LEGEND_TOP + LEGEND_ROWS_MAX * LEGEND_ROW_H + 8
line([(CONTENT_X, RULE_Y), (CONTENT_R, RULE_Y)], color=LINE, sw=1, arrow=False)
y = RULE_Y + 16

# ==========================================================================
# STARTUP CHAIN
# ==========================================================================

# Standard process-block width -- narrower than CONTENT_W so single-column
# boxes don't carry a lot of unused interior whitespace; DCX is the shared
# vertical centerline used everywhere below (chain boxes and loop diamonds
# alike), leaving a right-hand lane past BLOCK_X+BLOCK_W free for bypass
# lines and self-loop labels.
BLOCK_W = 400
BLOCK_X = CONTENT_X
DCX = BLOCK_X + BLOCK_W / 2   # 250

# System Start boxes (system_init/demo_init/LED0_toggle) run narrower than
# the shared BLOCK_W, centered on DCX -- MAIN LOOP and CM2 Hardware below
# keep the full BLOCK_W.
STARTUP_BOX_W = 340
STARTUP_BOX_X = DCX - STARTUP_BOX_W / 2

ellipse(DCX, y + 15, 88, 15, fill=BG_START)
text(DCX, y + 15, "System Start", ("monob", 13), anchor="mm")
y += 30
line([(DCX, y), (DCX, y + 12)])
y += 12

# col_top/col_bottom bracket the system_init..LED0_toggle chain so the
# push-button column (below) can be drawn beside it at exactly this height,
# instead of below it -- freeing a full-width band of page height and
# giving the button cards a taller, less cramped column to grow into.
col_top = y

h = func_box(STARTUP_BOX_X, y, STARTUP_BOX_W, "system_init()", "main.c", [
    ("clock_init()", "clock.c", "PLL1 200 MHz core \u00b7 PLL2 160 MHz monitor clock (CLKGEN1/6/11)"),
    ("gpio_init()", "gpio.c", "LEDs, RGB, switches S1-S3, ext. INT1-3 PPS routing"),
    ("tmr1_systick_init()", "tmr1_tick.c", "1 ms system tick, source for get_msec()"),
    ("sccp1_init()", "sccp1.c", "RGB status LED PWM (CCP1, 100 kHz)"),
], BG_INIT)
y += h
line([(DCX, y), (DCX, y + 12)])
y += 12

h = func_box(STARTUP_BOX_X, y, STARTUP_BOX_W, "demo_init()", "demo_app.c", [
    ("adc_init()", "adc.c", "ADC5 CH0 potentiometer (R14), SCCP2-triggered, IRQ sets flag"),
    ("sccp2_init()", "sccp2.c", "100 kHz ADC sample-trigger timer (CCP2)"),
    ("clock_monitor_init()", "clock_monitor.c", "Configure CM2 thresholds \u00b7 enable IRQs \u00b7 run startup test (below)"),
], BG_INIT)
y += h
line([(DCX, y), (DCX, y + 12)])
y += 12

h = simple_box(STARTUP_BOX_X, y, STARTUP_BOX_W, "LED0_toggle()", "main.c", [
    "Heartbeat LED, toggled every 500 ms",
    "Runs in while (1) alongside the runtime CM2 check",
], BG_GRAY)
y += h
col_bottom = y

# Push-button FRC test-injection ISRs -- these three fire independently
# (whichever button is pressed). Placed beside the STARTUP chain (rather
# than in a full-width band below it) so each card gets a taller column
# and can run larger type; column height matches the chain exactly so
# both containers' borders line up top and bottom.
BTN_GAP = 20
BTN_X = BLOCK_X + BLOCK_W + BTN_GAP    # 470
BTN_W = CONTENT_R - BTN_X               # 330
BTN_H2 = col_bottom - col_top
CARD_W = BTN_W - 32                     # 298
CARD_GAP = 16
BRANCH_LINE_H = 13
CARD_TOP_PAD, CARD_TITLE_H, CARD_MID_GAP, CARD_BOT_PAD = 8, 18, 6, 8

rect(BTN_X, col_top, BTN_W, BTN_H2, dashed=True, sw=1.2, color=BUTTON)
text(BTN_X + BTN_W / 2, col_top + 9, "FRC Test-Injection Push Buttons", ("monob", 13), color=INK, anchor="ma")
text(BTN_X + BTN_W / 2, col_top + 27, "gpio.c ISRs", ("sans", 10), color=MUTED, anchor="ma")

# Pointer from the "Push-button ISR" legend swatch down to this box, routed
# through the empty BTN_GAP corridor so it clears the STARTUP chain column.
_btn_off = (LEGEND_ROWS_MAX - len(legend_left_b)) * LEGEND_ROW_H / 2
_sw_cx = LEGEND_COL_X[1] + 6.5
_sw_by = LEGEND_TOP + _btn_off + 13
_corridor_x = BLOCK_X + BLOCK_W + BTN_GAP / 2
_box_cx = BTN_X + BTN_W / 2
line([(_sw_cx, _sw_by), (_sw_cx, _sw_by + 17), (_corridor_x, _sw_by + 17),
      (_corridor_x, col_top - 8), (_box_cx, col_top - 8), (_box_cx, col_top)],
     color=BUTTON, sw=1.2, dashed=True)

by = col_top + 40

def branch_card(title, rows):
    """rows: list of (line_text, color) -- one line per if/elif branch,
    or a single line for an unconditional handler."""
    global by
    h = CARD_TOP_PAD + CARD_TITLE_H + CARD_MID_GAP + len(rows) * BRANCH_LINE_H + CARD_BOT_PAD
    rect(BTN_X + 16, by, CARD_W, h, color=BUTTON, sw=1.2, fill=BG_BUTTON)
    text(BTN_X + 16 + CARD_W / 2, by + CARD_TOP_PAD + CARD_TITLE_H / 2, title, ("monob", 12.2), color=INK, anchor="mm")
    ry = by + CARD_TOP_PAD + CARD_TITLE_H + CARD_MID_GAP
    for row_text, row_color in rows:
        text(BTN_X + 30, ry, row_text, ("mono", 9.2), color=row_color, anchor="la")
        ry += BRANCH_LINE_H
    by += h + CARD_GAP

branch_card("S1  (_INT1Interrupt)  \u2192  FRC slower", [
    ("if   AD5CH0DATA < 0x0800  \u2192 TUN=0b110110  HWARN", WARN),
    ("elif AD5CH0DATA < 0x0A00  \u2192 TUN=0b110001  HFAIL", FAIL),
    ("elif AD5CH0DATA > 0x0A00  \u2192 TUN=0b101100  SATD", SAT),
])
branch_card("S2  (_INT2Interrupt)  \u2192  FRC reset", [
    ("(unconditional) \u2192 TUN=0b111100  nominal, CM2BUF\u224860000", NOMINAL),
])
branch_card("S3  (_INT3Interrupt)  \u2192  FRC faster", [
    ("if   AD5CH0DATA < 0x0400  \u2192 TUN=0b000010  LWARN", WARN),
    ("elif AD5CH0DATA < 0x0600  \u2192 TUN=0b000110  LFAIL", FAIL),
])

by += 6
text(BTN_X + 16, by, "50 ms debounce tick recorded, non-gating; first true", ("sans", 9.6), color=MUTED)
by += 15
text(BTN_X + 16, by, "branch wins; AD5CH0DATA == 0x0A00 leaves FRCTUN as-is", ("sans", 9.6), color=MUTED)
by += 19
text(BTN_X + 16, by, "Used to demo Warning/Fail/Saturation events", ("sans", 9.6), color=MUTED)
by += 15
text(BTN_X + 16, by, "without external hardware", ("sans", 9.6), color=MUTED)

y = col_bottom + 46

# ==========================================================================
# MAIN LOOP -- full width, centered on the page; comes right after STARTUP.
# Loop entry is gated by the Startup Test diamond down in CM2 CLOCK MONITOR
# (below) -- shown with a curved return arrow, routed through the left
# page margin, rather than a physical arrow feeding down from above.
# ==========================================================================

# BOX_W/BOX_X alias the STARTUP-chain BLOCK_W/BLOCK_X so the loop diamonds
# and their action boxes share the same centerline (DCX) and left edge as
# everything above -- with a right-hand lane past BOX_X+BOX_W free for the
# "No" bypass lines and the loop-back "next iteration" arrow.
BOX_W, BOX_X = BLOCK_W, BLOCK_X
BYPASS_X = BOX_X + BOX_W + 30    # 480
RETURN_LANE_X = CONTENT_R - 20   # 780

# Process boxes (ms=get_msec()/LED0_toggle(), demo_task()) are narrower than
# the full STARTUP-chain width -- centered on DCX, independent of BOX_W/BOX_X.
PROC_BOX_W = 320
PROC_BOX_X = DCX - PROC_BOX_W / 2

def loop_diamond(cy, rx, ry, lines, mono_size=10.6):
    diamond(DCX, cy, rx, ry, fill=BG_DECISION)
    n = len(lines)
    for i, ln in enumerate(lines):
        ty = cy + (i - (n - 1) / 2) * 13
        text(DCX, ty, ln, ("mono", mono_size), anchor="mm")
    return cy - ry, cy + ry

LOOP_TOP = y
text(CONTENT_X + CONTENT_W / 2, LOOP_TOP + 16, "MAIN LOOP \u2014 while (1) { \u2026 }  \u2014  main.c", ("monob", 12.5), color=ACCENT, anchor="ma")

entry_y = LOOP_TOP + 40
dot(DCX, entry_y)
text(DCX + 12, entry_y - 4, "entry \u2014 gated by Startup Test, below", ("sansi", 9), color=MUTED)

# F1 -- heartbeat LED
cy1 = entry_y + 42
line([(DCX, entry_y), (DCX, cy1 - 22)])
top1, bot1 = loop_diamond(cy1, 100, 22, ["get_msec() >", "ms + 500 ?"])

box1_top = bot1 + 16
line([(DCX, bot1), (DCX, box1_top)], sw=1.2)
text(DCX + 8, bot1 + 4, "Yes", ("sans", 10), color=MUTED)
box1_h = 34
rect(PROC_BOX_X, box1_top, PROC_BOX_W, box1_h, fill=BG_BRANCH)
text(DCX, box1_top + box1_h / 2 - 7, "ms = get_msec();", ("mono", 11), anchor="mm")
text(DCX, box1_top + box1_h / 2 + 7, "LED0_toggle();", ("mono", 11), anchor="mm")
box1_bottom = box1_top + box1_h

merge1_y = box1_bottom + 16
line([(DCX, box1_bottom), (DCX, merge1_y)], sw=1.2, arrow=False)
line([(DCX + 100, cy1), (BYPASS_X, cy1), (BYPASS_X, merge1_y), (DCX, merge1_y)], sw=1.2, arrow=False)
text(DCX + 108, cy1 - 4, "No", ("sans", 10), color=MUTED)
dot(DCX, merge1_y)
y = merge1_y + 16
line([(DCX, merge1_y), (DCX, y)], sw=1.3)

# F2 -- demo_task(): ADC bar-graph
cy2 = y + 24
top2, bot2 = loop_diamond(cy2, 100, 24, ["adc5_ch0_data", "_ready ?"])

box2_top = bot2 + 16
line([(DCX, bot2), (DCX, box2_top)], sw=1.2)
text(DCX + 8, bot2 + 4, "Yes", ("sans", 10), color=MUTED)
box2_h = 64
rect(PROC_BOX_X, box2_top, PROC_BOX_W, box2_h, fill=BG_BRANCH)
text(DCX, box2_top + box2_h / 2 - 16, "demo_task()  \u2014  demo_app.c", ("monob", 10.6), anchor="mm")
text(DCX, box2_top + box2_h / 2, "clear adc5_ch0_data_ready; update_led_bargraph()", ("sans", 9.6), color=MUTED, anchor="mm")
text(DCX, box2_top + box2_h / 2 + 16, "scale potentiometer_adc_counts (0\u20134095) \u2192 LED1\u2026LED7 level", ("sans", 9.4), color=MUTED, anchor="mm")
box2_bottom = box2_top + box2_h

merge2_y = box2_bottom + 16
line([(DCX, box2_bottom), (DCX, merge2_y)], sw=1.2, arrow=False)
line([(DCX + 100, cy2), (BYPASS_X, cy2), (BYPASS_X, merge2_y), (DCX, merge2_y)], sw=1.2, arrow=False)
text(DCX + 108, cy2 - 4, "No", ("sans", 10), color=MUTED)
dot(DCX, merge2_y)
y = merge2_y + 34
line([(DCX, merge2_y), (DCX, y)], sw=1.3)

# F3 -- runtime clock-monitor check
F3_RX, F3_RY = 112, 24
cy3 = y + F3_RY
top3, bot3 = loop_diamond(cy3, F3_RX, F3_RY, ["Runtime check:", "CM2STAT.TRIG == 0 ?"], mono_size=10.2)

loop3_y = top3 - 18
line([(DCX + F3_RX, cy3), (DCX + F3_RX + 24, cy3), (DCX + F3_RX + 24, loop3_y), (DCX, loop3_y), (DCX, top3)], sw=1.2, color=FAIL)
text(DCX + F3_RX + 32, loop3_y - 6, "Yes \u2014 wait (Nop());", ("sans", 9.6), color=FAIL)
text(DCX + F3_RX + 32, loop3_y + 10, "ref-clock fault \u2014 app must handle", ("sans", 9.6), color=FAIL)

turn_y = bot3 + 18
text(DCX - 14, bot3 + 9, "No", ("sans", 10), color=MUTED, anchor="ra")
reentry_y = top1
line([(DCX, bot3), (DCX, turn_y), (RETURN_LANE_X, turn_y), (RETURN_LANE_X, reentry_y), (DCX, reentry_y)], sw=1.2)
dot(DCX, reentry_y)
text(RETURN_LANE_X - 6, turn_y - 12, "next iteration", ("sans", 9), color=MUTED, anchor="ra")

LOOP_BOTTOM = turn_y + 16
rect(CONTENT_X, LOOP_TOP, CONTENT_W, LOOP_BOTTOM - LOOP_TOP, sw=1.4)

# ==========================================================================
# CM2 CLOCK MONITOR -- hardware pipeline + startup test (left column) and
# the four CM2 Interrupt Service Routines (right column), side by side,
# below the Main Loop. The Startup Test's "Yes" exit returns control to the
# Main Loop above via a curved arrow routed through the left page margin,
# since clock_monitor_init() (and its one-time startup test) runs before
# the loop begins even though it is drawn below it.
# ==========================================================================
y = LOOP_BOTTOM + 34
y = section_title(y, "CM2 CLOCK MONITOR \u2014 clock_monitor.c \u00b7 main.c")
CM2_TOP = y

RIGHT_GAP = 20
RIGHT_X = BLOCK_X + BLOCK_W + RIGHT_GAP    # 470
RIGHT_W = CONTENT_R - RIGHT_X               # 330
CARD_W2 = RIGHT_W - 32                      # 298

# ---- precompute LEFT content height: hardware pipeline + startup test ----
hw_row_h, hw_gap = 40, 10
HW_TITLE_H = 30
HW_NOTES_H = 40
HW_H = HW_TITLE_H + 4 * hw_row_h + 3 * hw_gap + HW_NOTES_H   # 260

E_RX, E_RY = 100, 26
CONNECT = 40
CAPTION_H = 8 + 2 * 14 + 10
DIAMOND_BLOCK_H = CONNECT + 2 * E_RY + CAPTION_H   # 40+52+46 = 138
LEFT_CONTENT_H = HW_H + 16 + DIAMOND_BLOCK_H        # 414

# ---- precompute RIGHT content height: ISR header + 4 (shrunk) cards ----
HEADER2_H = 52
CARD_H2, CARD_GAP2 = 66, 14
NOTES2_H = 15 + 2 * 14 + 15
RIGHT_CONTENT_H = HEADER2_H + 4 * CARD_H2 + 3 * CARD_GAP2 + NOTES2_H   # 416

CM2_H = max(LEFT_CONTENT_H, RIGHT_CONTENT_H) + 36
LEFT_PAD = max(18, (CM2_H - LEFT_CONTENT_H) / 2)
RIGHT_PAD = max(18, (CM2_H - RIGHT_CONTENT_H) / 2)
CM2_BOTTOM = CM2_TOP + CM2_H

rect(BLOCK_X, CM2_TOP, BLOCK_W, CM2_H, dashed=True, sw=1.2, color=CM2HW)
rect(RIGHT_X, CM2_TOP, RIGHT_W, CM2_H, dashed=True, sw=1.2, color=LINE)

# -------------------- LEFT: hardware pipeline --------------------
HW_TOP = CM2_TOP + LEFT_PAD
dashed_container_title(BLOCK_X, HW_TOP, BLOCK_W, "CM2 Hardware (runs autonomously once enabled)")
hy = HW_TOP + 30
hw_boxes = [
    ("Reference Clock", "CLKGEN2", "FRC, nominal 8 MHz (FRCTUNbits.TUN = 0b111100)"),
    ("CM2 Counter", "clock_monitor.c", "Counts CLKGEN11 (PLL2, 160MHz) edges; window CM2WINPR = 2999 (3000 cycles)"),
    ("Threshold Compare", "clock_monitor.c", "LFAIL 59400 < LWARN 59700 < HWARN 60300 < HFAIL 60600 < SAT 60900"),
    ("Status + Trigger", "CM2STAT", "Sets TRIG/BUFV/LWT/HWT/LFT/HFT/SATD \u2192 fires CM2CNT/WARN/FAIL/SAT IRQ"),
]
hw_box_w = BLOCK_W - 32
for i, (name, fn, desc) in enumerate(hw_boxes):
    rect(BLOCK_X + 16, hy, hw_box_w, hw_row_h, color=CM2HW, sw=1.1, fill=BG_CM2HW)
    header_line(BLOCK_X + 28, hy + 7, name, "  \u2014  " + fn, ("monob", 10.6), ("sans", 9.2), color=INK, mcolor=MUTED)
    text(BLOCK_X + 28, hy + 22, desc, ("sans", 9.3), color=MUTED)
    if i < len(hw_boxes) - 1:
        line([(BLOCK_X + 16 + hw_box_w / 2, hy + hw_row_h), (BLOCK_X + 16 + hw_box_w / 2, hy + hw_row_h + hw_gap)], sw=1.1, color=CM2HW)
    hy += hw_row_h + hw_gap
text(BLOCK_X + 16, HW_TOP + HW_H - 32, "\u2192 CM2STAT.TRIG feeds the Startup Test below \u2014", ("sansi", 9), color=MUTED)
text(BLOCK_X + 16, HW_TOP + HW_H - 18, "CM2xIF flags fire the ISRs at right", ("sansi", 9), color=MUTED)

# -------------------- LEFT: startup test diamond --------------------
dtop = HW_TOP + HW_H + 16
line([(DCX, dtop), (DCX, dtop + CONNECT)])
e_cy = dtop + CONNECT + E_RY
diamond(DCX, e_cy, E_RX, E_RY, fill=BG_DECISION)
text(DCX, e_cy - 7, "CM2STAT.TRIG", ("mono", 10.6), anchor="mm")
text(DCX, e_cy + 8, "== 1 ?", ("mono", 10.6), anchor="mm")

loop_y = e_cy - E_RY - 10
line([(DCX + E_RX, e_cy), (DCX + E_RX + 24, e_cy), (DCX + E_RX + 24, loop_y), (DCX, loop_y), (DCX, e_cy - E_RY)], sw=1.2)
ann_x = DCX + E_RX + 32
text(ann_x, loop_y - 19, "No \u2014 wait", ("sans", 9.6), color=MUTED)
text(ann_x, loop_y - 6, "(Nop());", ("sans", 9.6), color=MUTED)
text(ann_x, loop_y + 7, "possible", ("sans", 9.6), color=MUTED)
text(ann_x, loop_y + 20, "ref-clock fault", ("sans", 9.6), color=MUTED)

e_bottom = e_cy + E_RY
text(BLOCK_X + 16, e_bottom + 8, "Yes \u2014 clock running (clock_monitor_init(), before the loop)", ("sans", 9.4), color=MUTED)
text(BLOCK_X + 16, e_bottom + 22, "\u2192 enters Main Loop above, via return arrow at left", ("sans", 9.4), color=MUTED)

# curved return arrow -- Startup Test "Yes" exit, down, left into the page
# margin, up past everything above, right into the Main Loop entry dot.
MARGIN_X = 28
arrow_down_y = e_bottom + 44
line([(DCX, e_bottom), (DCX, arrow_down_y)], sw=1.3, color=ACCENT, arrow=False)
line([(DCX, arrow_down_y), (MARGIN_X, arrow_down_y), (MARGIN_X, entry_y), (DCX, entry_y)], sw=1.3, color=ACCENT)

# -------------------- RIGHT: CM2 Interrupt Service Routines --------------
isr_cards2 = [
    (NOMINAL, BG_NOMINAL, "_CM2CNTInterrupt()  \u2192  Count Ready",
     ["BUFV==1: Freq_Result = CM2BUF\u00b78MHz/(CM2WINPR+1);", "clear BUFV; clear CM2CNTIF"]),
    (WARN, BG_WARN, "_CM2WARNInterrupt()  \u2192  Low/High Warning",
     ["LWT/HWT: recompute Freq_Result, clear flag;", "FRCTUN unchanged \u2014 press S2 to reset"]),
    (FAIL, BG_FAIL, "_CM2FAILInterrupt()  \u2192  Low/High Fail",
     ["LFT/HFT: clear flags, re-enable CM2CONbits.ON;", "FRCTUN unchanged \u2014 press S2 to reset"]),
    (SAT, BG_SAT, "_CM2SATInterrupt()  \u2192  Saturation",
     ["SATD==1: recompute Freq_Result, clear SATD;", "FRCTUN unchanged, no re-arm needed"]),
]

hy2 = CM2_TOP + RIGHT_PAD
text(RIGHT_X + RIGHT_W / 2, hy2, "CM2 Interrupt Service Routines", ("monob", 13), color=INK, anchor="ma")
text(RIGHT_X + RIGHT_W / 2, hy2 + 18, "clock_monitor.c", ("sans", 10), color=MUTED, anchor="ma")
text(RIGHT_X + RIGHT_W / 2, hy2 + 33, "(fired asynchronously by the hardware)", ("sansi", 9.6), color=MUTED, anchor="ma")

cy2 = hy2 + HEADER2_H
for accent, bg, title, detail_lines in isr_cards2:
    rect(RIGHT_X + 16, cy2, CARD_W2, CARD_H2, color=accent, sw=1.2, fill=bg)
    ccx, ccy = RIGHT_X + 16 + CARD_W2 / 2, cy2 + CARD_H2 / 2
    text(ccx, ccy - 15, title, ("monob", 10.8), color=INK, anchor="mm")
    text(ccx, ccy + 3, detail_lines[0], ("sans", 9.4), color=MUTED, anchor="mm")
    text(ccx, ccy + 16, detail_lines[1], ("sans", 9.4), color=MUTED, anchor="mm")
    cy2 += CARD_H2 + CARD_GAP2

note_y2 = cy2 - CARD_GAP2 + 15
text(RIGHT_X + 16, note_y2, "All four ISRs run at IPL set by the interrupt controller \u2014", ("sans", 9.6), color=MUTED)
text(RIGHT_X + 16, note_y2 + 14, "none call back into main.c or demo_app.c", ("sans", 9.6), color=MUTED)

y = CM2_BOTTOM + 20

# ==========================================================================
# FOOTER
# ==========================================================================
FOOT_Y = y + 14
line([(CONTENT_X, FOOT_Y), (CONTENT_R, FOOT_Y)], color=LINE, sw=1, arrow=False)
text(CONTENT_X, FOOT_Y + 13, "Source: main.c \u00b7 demo_app.c \u00b7 clock_monitor.c \u00b7 gpio.c \u00b7 adc.c", ("sans", 9.2), color=MUTED)
text(CONTENT_X, FOOT_Y + 27, "dsPIC33A Curiosity Platform, dsPIC33AK512MPS512 GP DIM", ("sans", 9.2), color=MUTED)

PAGE_H = FOOT_Y + 27 + 12 + MARGIN

# ==========================================================================
# RENDER — PNG (Pillow)
# ==========================================================================
img = Image.new("RGB", (int(PAGE_W * SCALE), int(PAGE_H * SCALE)), PAPER)
d = ImageDraw.Draw(img)

def s(v):
    return v * SCALE

def dashed_line_pts(spts, color, sw):
    dash, gap = 6 * SCALE, 4 * SCALE
    for (ex0, ey0), (ex1, ey1) in zip(spts[:-1], spts[1:]):
        length = ((ex1 - ex0) ** 2 + (ey1 - ey0) ** 2) ** 0.5
        if not length:
            continue
        steps = max(1, int(length // (dash + gap)))
        for i in range(steps + 1):
            t0 = i * (dash + gap) / length
            if t0 >= 1:
                break
            t1 = min(1.0, t0 + dash / length)
            d.line([(ex0 + (ex1 - ex0) * t0, ey0 + (ey1 - ey0) * t0),
                    (ex0 + (ex1 - ex0) * t1, ey0 + (ey1 - ey0) * t1)], fill=color, width=max(1, int(sw * SCALE)))

def dashed_rect(box, color, sw):
    x0, y0, x1, y1 = box
    dashed_line_pts([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], color, sw)

for kind, kw in PRIMS:
    if kind == "rect":
        x, y, w, h, dashed, color, sw, fill = kw["x"], kw["y"], kw["w"], kw["h"], kw["dashed"], kw["color"], kw["sw"], kw["fill"]
        box = [s(x), s(y), s(x + w), s(y + h)]
        if fill and sw == 0:
            d.rectangle(box, fill=fill)
        elif dashed:
            if fill:
                d.rectangle(box, fill=fill)
            dashed_rect(box, color, sw)
        else:
            if fill:
                d.rectangle(box, fill=fill)
            d.rectangle(box, outline=color, width=max(1, int(sw * SCALE)))
    elif kind == "diamond":
        cx, cy, rx, ry, color, sw, fill = kw["cx"], kw["cy"], kw["rx"], kw["ry"], kw["color"], kw["sw"], kw["fill"]
        pts = [(s(cx), s(cy - ry)), (s(cx + rx), s(cy)), (s(cx), s(cy + ry)), (s(cx - rx), s(cy))]
        d.polygon(pts, fill=fill, outline=color, width=max(1, int(sw * SCALE)))
    elif kind == "ellipse":
        cx, cy, rx, ry, color, sw, fill = kw["cx"], kw["cy"], kw["rx"], kw["ry"], kw["color"], kw["sw"], kw["fill"]
        d.ellipse([s(cx - rx), s(cy - ry), s(cx + rx), s(cy + ry)], fill=fill, outline=color, width=max(1, int(sw * SCALE)))
    elif kind == "line":
        pts, color, sw, arrow, dashed = kw["pts"], kw["color"], kw["sw"], kw["arrow"], kw["dashed"]
        spts = [(s(x), s(y)) for x, y in pts]
        if dashed:
            dashed_line_pts(spts, color, sw)
        else:
            d.line(spts, fill=color, width=max(1, int(sw * SCALE)), joint="curve")
        if arrow:
            (x0, y0), (x1, y1) = spts[-2], spts[-1]
            ang = math.atan2(y1 - y0, x1 - x0)
            al, aa = 9 * SCALE, 0.45
            p1 = (x1 - al * math.cos(ang - aa), y1 - al * math.sin(ang - aa))
            p2 = (x1 - al * math.cos(ang + aa), y1 - al * math.sin(ang + aa))
            d.polygon([(x1, y1), p1, p2], fill=color)
    elif kind == "dot":
        cx, cy, r, color = kw["cx"], kw["cy"], kw["r"], kw["color"]
        d.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], fill=color)
    elif kind == "text":
        x, y, txt, f, color, anchor, rot = kw["x"], kw["y"], kw["s"], kw["f"], kw["color"], kw["anchor"], kw["rot"]
        fnt = get_font(f)
        if rot:
            tmp = Image.new("RGBA", (s(280), s(26)), (0, 0, 0, 0))
            td = ImageDraw.Draw(tmp)
            td.text((0, 0), txt, font=fnt, fill=color, anchor="lm")
            tmp = tmp.rotate(-rot, expand=True, resample=Image.BICUBIC)
            img.paste(tmp, (int(s(x) - tmp.width / 2), int(s(y) - tmp.height / 2)), tmp)
        else:
            pil_anchor = {"la": "la", "ma": "ma", "ra": "ra", "mm": "mm"}[anchor]
            d.text((s(x), s(y)), txt, font=fnt, fill=color, anchor=pil_anchor)

out_png = r"C:\dsPIC33A VSCode Examples\Clock Monitor\dsPIC33A Clock Monitor\Clock_Monitor_Flowchart.png"
img.save(out_png, dpi=(300, 300))
print("PNG written:", out_png)

# ==========================================================================
# RENDER — draw.io (mxGraph XML)
# ==========================================================================
mxfile = ET.Element("mxfile", host="app.diagrams.net")
diagram = ET.SubElement(mxfile, "diagram", name="Clock Monitor Control Flow", id="clockmon1")
model = ET.SubElement(diagram, "mxGraphModel", {
    "dx": "800", "dy": "600", "grid": "1", "gridSize": "10", "guides": "1",
    "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
    "pageScale": "1", "pageWidth": str(PAGE_W), "pageHeight": str(PAGE_H),
    "math": "0", "shadow": "0",
})
root = ET.SubElement(model, "root")
ET.SubElement(root, "mxCell", id="0")
ET.SubElement(root, "mxCell", id="1", parent="0")

_id = [1]
def next_id():
    _id[0] += 1
    return f"n{_id[0]}"

def hexc(rgb):
    return DRAWIO_HEX.get(rgb, "#%02X%02X%02X" % rgb)

def add_vertex(x, y, w, h, style, value=""):
    cell = ET.SubElement(root, "mxCell", id=next_id(), value=value, style=style, vertex="1", parent="1")
    ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"})
    return cell

def add_edge(points, style):
    cell = ET.SubElement(root, "mxCell", id=next_id(), value="", style=style, edge="1", parent="1")
    geo = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    ET.SubElement(geo, "mxPoint", {"x": str(points[0][0]), "y": str(points[0][1]), "as": "sourcePoint"})
    ET.SubElement(geo, "mxPoint", {"x": str(points[-1][0]), "y": str(points[-1][1]), "as": "targetPoint"})
    if len(points) > 2:
        arr = ET.SubElement(geo, "Array", {"as": "points"})
        for px, py in points[1:-1]:
            ET.SubElement(arr, "mxPoint", {"x": str(px), "y": str(py)})
    return cell

def add_text(x, y, w, h, value, color, align="left", italic=False, bold=False, size=11):
    fs = "fontStyle=%d;" % ((1 if bold else 0) + (2 if italic else 0))
    style = f"text;html=1;align={align};verticalAlign=middle;fontColor={hexc(color)};fontSize={size};{fs}"
    add_vertex(x, y, w, h, style, value.replace("&", "&amp;").replace("<", "&lt;"))

FONT_PX = {"title": 15, "mono": 10, "monob": 10, "sans": 9, "sansi": 9, "sansb": 9}
for kind, kw in PRIMS:
    if kind == "rect":
        x, y, w, h, dashed, color, sw, fill = kw["x"], kw["y"], kw["w"], kw["h"], kw["dashed"], kw["color"], kw["sw"], kw["fill"]
        if fill and sw == 0:
            add_vertex(x, y, w, h, f"rounded=0;whiteSpace=wrap;html=1;fillColor={hexc(fill)};strokeColor=none;")
        else:
            dash = "dashed=1;dashPattern=6 4;" if dashed else ""
            fc = hexc(fill) if fill else "none"
            add_vertex(x, y, w, h, f"rounded=0;whiteSpace=wrap;html=1;fillColor={fc};strokeColor={hexc(color)};strokeWidth={sw};{dash}")
    elif kind == "diamond":
        cx, cy, rx, ry, color, sw, fill = kw["cx"], kw["cy"], kw["rx"], kw["ry"], kw["color"], kw["sw"], kw["fill"]
        fc = hexc(fill) if fill else "none"
        add_vertex(cx - rx, cy - ry, 2 * rx, 2 * ry, f"rhombus;whiteSpace=wrap;html=1;fillColor={fc};strokeColor={hexc(color)};strokeWidth={sw};")
    elif kind == "ellipse":
        cx, cy, rx, ry, color, sw, fill = kw["cx"], kw["cy"], kw["rx"], kw["ry"], kw["color"], kw["sw"], kw["fill"]
        fc = hexc(fill) if fill else "none"
        add_vertex(cx - rx, cy - ry, 2 * rx, 2 * ry, f"ellipse;whiteSpace=wrap;html=1;fillColor={fc};strokeColor={hexc(color)};strokeWidth={sw};")
    elif kind == "line":
        pts, color, sw, arrow, dashed = kw["pts"], kw["color"], kw["sw"], kw["arrow"], kw["dashed"]
        end = "classic" if arrow else "none"
        dash = "dashed=1;dashPattern=6 4;" if dashed else ""
        add_edge(pts, f"edgeStyle=none;html=1;rounded=0;endArrow={end};startArrow=none;strokeColor={hexc(color)};strokeWidth={sw};{dash}")
    elif kind == "dot":
        cx, cy, r, color = kw["cx"], kw["cy"], kw["r"], kw["color"]
        add_vertex(cx - r, cy - r, 2 * r, 2 * r, f"ellipse;whiteSpace=wrap;html=1;fillColor={hexc(color)};strokeColor=none;")
    elif kind == "text":
        x, y, txt, f, color, anchor, rot = kw["x"], kw["y"], kw["s"], kw["f"], kw["color"], kw["anchor"], kw["rot"]
        fkind, fsize = f
        align = {"la": "left", "ma": "center", "ra": "right", "mm": "center"}[anchor]
        w, h = 460, 16
        if anchor in ("la", "ma"):
            tx = x if anchor == "la" else x - w / 2
        elif anchor == "ra":
            tx = x - w
        else:
            tx = x - w / 2
        ty = y - h / 2 if anchor == "mm" else y - 2
        add_text(tx, ty, w, h, txt, color, align=align, italic=(fkind in ("sansi",)),
                  bold=(fkind in ("monob", "title")), size=FONT_PX.get(fkind, 9))

xml_bytes = ET.tostring(mxfile, encoding="utf-8")
pretty = minidom.parseString(xml_bytes).toprettyxml(indent="  ")
out_drawio = r"C:\dsPIC33A VSCode Examples\Clock Monitor\dsPIC33A Clock Monitor\Clock_Monitor_Flowchart.drawio"
with open(out_drawio, "w", encoding="utf-8") as f:
    f.write(pretty)
print("drawio written:", out_drawio)
