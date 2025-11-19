# system_control.py
import pyautogui
import time
import config
from utils import norm_dist

pyautogui.FAILSAFE = False  # optional: set True if you want a physical mouse corner safety

class SystemController:
    def __init__(self, cfg=None):
        self.cfg = cfg if cfg is not None else config
        self.action_state = {"click": False, "drag": False, "scroll": False}
        self._dragging = False
        self._last_gesture_time = 0.0

    def _safe_click(self):
        try:
            pyautogui.click(_pause=False)
        except Exception:
            pass

    def _safe_double_click(self):
        try:
            pyautogui.doubleClick(_pause=False)
        except Exception:
            pass

    def _safe_mouse_down(self):
        try:
            pyautogui.mouseDown(_pause=False)
        except Exception:
            pass

    def _safe_mouse_up(self):
        try:
            pyautogui.mouseUp(_pause=False)
        except Exception:
            pass

    def handle_gesture(self, gesture, hands_data, frame_shape):
        """
        gesture: string from recognizer
        hands_data: list, may be used to map coordinates
        frame_shape: frame.shape for mapping (h,w,_)
        """
        # default clear
        self.action_state["click"] = False
        # self.action_state["drag"] = False  # do not clear drag here, preserve if ongoing

        now = time.time()

        # PINCH / CLICK
        if gesture == "PINCH":
            # perform single click
            self._safe_click()
            self.action_state["click"] = True
            self._last_gesture_time = now

        elif gesture == "DOUBLE_CLICK":
            self._safe_double_click()
            self.action_state["click"] = True
            self._last_gesture_time = now

        elif gesture == "PINCH_HOLD" or gesture == "FIST":
            # start drag if not already
            if not self._dragging:
                self._safe_mouse_down()
                self._dragging = True
            self.action_state["drag"] = True
            self._last_gesture_time = now

            # while dragging, move mouse following index tip if available
            if hands_data and hands_data[0].get("lm_list"):
                lm = hands_data[0]["lm_list"]
                if len(lm) > 8:
                    ix, iy = lm[8]
                    # map normalized image coords to screen coords
                    screen_x = int(max(0, min(1.0, ix)) * pyautogui.size().width)
                    screen_y = int(max(0, min(1.0, iy)) * pyautogui.size().height)
                    try:
                        pyautogui.moveTo(screen_x, screen_y, _pause=False)
                    except Exception:
                        pass

        else:
            # No drag gesture: if we were dragging, release
            if self._dragging:
                self._safe_mouse_up()
                self._dragging = False
                self.action_state["drag"] = False

        # If no gesture for a while, ensure drag released (safety)
        if self._dragging and (now - self._last_gesture_time) > 1.2:
            self._safe_mouse_up()
            self._dragging = False
            self.action_state["drag"] = False
