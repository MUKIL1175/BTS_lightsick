# members.py - official/fan-known BTS member colors + pattern type per member

PATTERN_SOLID = 0
PATTERN_PULSE = 1
PATTERN_SPARKLE = 2
PATTERN_CHASE = 3
PATTERN_WAVE = 4

# (name, (r,g,b), pattern)
MEMBERS = [
    ("RM",       (0x9B, 0x59, 0xB6), PATTERN_WAVE),     # purple
    ("Jin",      (0xFF, 0xC0, 0xCB), PATTERN_PULSE),    # pink
    ("Suga",     (0xB0, 0xB0, 0xB0), PATTERN_SPARKLE),  # grey
    ("J-Hope",   (0xFF, 0xD7, 0x00), PATTERN_CHASE),    # yellow/gold
    ("Jimin",    (0xFF, 0x69, 0x9C), PATTERN_PULSE),    # pink/magenta
    ("V",        (0x4B, 0x32, 0x21), PATTERN_WAVE),     # brown/burgundy
    ("Jungkook", (0x00, 0x9B, 0xDE), PATTERN_CHASE),    # sky blue
]

MEMBER_COUNT = len(MEMBERS)

IDLE_COLOR = (0x6A, 0x0D, 0xAD)
