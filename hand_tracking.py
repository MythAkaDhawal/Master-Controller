# hand_tracking.py
import mediapipe as mp
import cv2
import time
from utils import normalized_landmarks_to_list

class HandTracker:
    def __init__(self,
                 max_hands=1,
                 detection_con=0.6,
                 track_con=0.6,
                 smoothing_factor=0.75):
        self.max_hands = max_hands
        self.smoothing_factor = smoothing_factor

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )
        self.mp_draw = mp.solutions.drawing_utils

        # simple per-landmark smoothing storage
        self._prev_landmarks = None

    def _smooth(self, new_lm):
        if self._prev_landmarks is None:
            self._prev_landmarks = new_lm
            return new_lm
        alpha = self.smoothing_factor
        sm = []
        for (nx, ny), (px, py) in zip(new_lm, self._prev_landmarks):
            sx = alpha * px + (1 - alpha) * nx
            sy = alpha * py + (1 - alpha) * ny
            sm.append((sx, sy))
        self._prev_landmarks = sm
        return sm

    def find_hands(self, frame, draw=False):
        """
        Input: BGR frame (numpy)
        Output: (frame, hands_data)
        hands_data: list of dicts:
            {
                "lm_list": [(x,y), ...] normalized coords,
                "bbox": (x,y,w,h) in pixels,
                "handedness": "Left" or "Right"
            }
        """
        h, w = frame.shape[:2]
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        hands_out = []

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                lm_norm = normalized_landmarks_to_list(hand_landmarks.landmark)
                # smoothing
                lm_norm = self._smooth(lm_norm)
                # bounding box (pixel)
                xs = [int(x * w) for x, _ in lm_norm]
                ys = [int(y * h) for _, y in lm_norm]
                xmin, xmax = min(xs), max(xs)
                ymin, ymax = min(ys), max(ys)
                bbox = (xmin, ymin, xmax - xmin, ymax - ymin)

                handedness = None
                if results.multi_handedness and idx < len(results.multi_handedness):
                    handedness = results.multi_handedness[idx].classification[0].label

                hands_out.append({
                    "lm_list": lm_norm,
                    "bbox": bbox,
                    "handedness": handedness
                })

                if draw:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return frame, hands_out
