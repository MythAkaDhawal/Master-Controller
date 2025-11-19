# gesture_recognizer.py
from utils import norm_dist
import config
import time

class GestureRecognizer:
    def __init__(self, cfg=None):
        self.cfg = cfg if cfg is not None else config
        # state for double-click or hold
        self._last_pinch_time = 0.0
        self._pinch_down = False
        self._pinch_start = None

        self._last_gesture = "NONE"

    def recognize(self, hands_data):
        """
        Input: hands_data list as produced by HandTracker
        Output: (gesture_str, action_state_dict)
        gesture_str: short identifier, e.g., "PINCH","FIST","SWIPE_LEFT","NONE"
        action_state: dict with booleans, e.g., {"click":True,"drag":False,"scroll":False}
        """
        action_state = {"click": False, "drag": False, "scroll": False}
        if not hands_data:
            self._pinch_down = False
            self._pinch_start = None
            return "NONE", action_state

        hand = hands_data[0]
        lm = hand["lm_list"]

        # safety: need at least some landmarks
        if not lm or len(lm) < 9:
            return "NONE", action_state

        # pinch detection (index tip 8, thumb tip 4)
        pinch_dist = norm_dist(lm[8], lm[4])
        is_pinch_now = pinch_dist < self.cfg.PINCH_THRESHOLD

        # fist detection: average tip->wrist
        wrist = lm[0]
        tips = [lm[i] for i in (8,12,16,20)]
        avg_tip_dist = sum(norm_dist(t, wrist) for t in tips) / len(tips)
        is_fist_now = avg_tip_dist < self.cfg.FIST_THRESHOLD

        gesture = "NONE"

        # PINCH logic: click / double-click / hold
        now = time.time()
        if is_pinch_now:
            if not self._pinch_down:
                # pinch just started
                self._pinch_start = now
                # short click (on start)
                if now - self._last_pinch_time < self.cfg.DOUBLE_CLICK_MAX_GAP:
                    gesture = "DOUBLE_CLICK"
                    action_state["click"] = True
                else:
                    gesture = "PINCH"
                    action_state["click"] = True
                self._pinch_down = True
            else:
                # pinch still down: check hold
                if now - self._pinch_start > self.cfg.HOLD_TIME:
                    gesture = "PINCH_HOLD"
                    action_state["drag"] = True
        else:
            if self._pinch_down:
                # pinch released
                # record last pinch time for double click detection
                self._last_pinch_time = now
            self._pinch_down = False
            self._pinch_start = None

        # FIST logic overrides pinch/others: start drag
        if is_fist_now:
            gesture = "FIST"
            action_state["drag"] = True

        # Simple horizontal swipe detection: compare x of index tip vs bbox center speed
        # (very simple, may be extended)
        # Not implemented here to keep lightweight — report NONE if no special gesture
        if gesture == "NONE":
            gesture = "NONE"

        self._last_gesture = gesture
        return gesture, action_state
