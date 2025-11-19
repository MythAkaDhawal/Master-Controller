# config.py
CAM_WIDTH = 640
CAM_HEIGHT = 480
MAX_HANDS = 1
DETECTION_CONFIDENCE = 0.6
TRACKING_CONFIDENCE = 0.6
LANDMARK_SMOOTHING_FACTOR = 0.75  # EMA smoothing inside tracker

DRAW_LANDMARKS = False
DEBUG = False

# Gesture thresholds (normalized coords)
PINCH_THRESHOLD = 0.045   # index-tip <-> thumb-tip distance -> pinch
FIST_THRESHOLD = 0.22    # avg tip->wrist distance -> fist

# Behavior / timing
HOLD_TIME = 0.35         # seconds for hold/drag
DOUBLE_CLICK_MAX_GAP = 0.35

# Performance
MAX_FPS = 25.0
SMOOTHING = 0.75         # cursor EMA in main/controller
