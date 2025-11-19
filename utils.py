# utils.py
import time
import cv2
import numpy as np

class FPS:
    def __init__(self, smooth=0.9):
        self._last = time.time()
        self._fps = 0.0
        self._smooth = smooth

    def update(self):
        now = time.time()
        dt = now - self._last if now - self._last > 0 else 1e-6
        inst = 1.0 / dt
        # exponential smoothing
        self._fps = (self._smooth * self._fps) + (1 - self._smooth) * inst
        self._last = now

    def get_fps(self):
        return self._fps

    def display_fps(self, frame, pos=(10, 30)):
        text = f"FPS: {self._fps:.1f}"
        cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (230,230,230), 2, cv2.LINE_AA)

def norm_dist(a, b):
    return ((a[0]-b[0])**2 + (a[1]-b[1])**2) ** 0.5

def normalized_landmarks_to_list(landmarks):
    """
    Accepts mediapipe landmarks object and returns list of (x,y) normalized tuples.
    If input is already list/tuple, returns it unchanged.
    """
    if landmarks is None:
        return None
    try:
        # landmarks: sequence of landmark objects with .x .y
        return [(lm.x, lm.y) for lm in landmarks]
    except Exception:
        # maybe already normalized list
        return landmarks
