# overlay_renderer.py
# Lightweight OpenCV HUD overlay optimized for low CPU usage.
import cv2
import numpy as np

_FONT = cv2.FONT_HERSHEY_SIMPLEX
_BG = (20, 20, 20)
_TEXT_COLOR = (230, 230, 230)
_GOOD = (57, 180, 75)
_WARN = (0, 215, 255)

def _draw_transparent_rect(img, tl, br, color=(0,0,0), alpha=0.45):
    x1,y1 = tl; x2,y2 = br
    overlay = img.copy()
    cv2.rectangle(overlay, (x1,y1), (x2,y2), color, -1)
    cv2.addWeighted(overlay, alpha, img, 1-alpha, 0, img)

def _norm_to_px(norm_x, norm_y, w, h):
    return int(norm_x * w), int(norm_y * h)

def render_overlay(frame_bgr, landmarks, gesture_name, action_state, fps, debug=False):
    h, w = frame_bgr.shape[:2]
    pad_x, pad_y = 12, 12
    panel_w, panel_h = 320, 86
    _draw_transparent_rect(frame_bgr, (pad_x, pad_y), (pad_x + panel_w, pad_y + panel_h), color=_BG, alpha=0.55)

    fps_text = f"FPS: {fps:.1f}"
    cv2.putText(frame_bgr, fps_text, (pad_x + 12, pad_y + 26), _FONT, 0.7, _TEXT_COLOR, 2, cv2.LINE_AA)

    gtext = f"Gesture: {gesture_name or 'Idle'}"
    cv2.putText(frame_bgr, gtext, (pad_x + 12, pad_y + 52), _FONT, 0.7, _TEXT_COLOR, 2, cv2.LINE_AA)

    icon_x = pad_x + 12
    icon_y = pad_y + 72
    spacing = 82

    click_on = bool(action_state.get("click", False))
    color = _GOOD if click_on else (180,180,180)
    cv2.circle(frame_bgr, (icon_x, icon_y), 10, color, -1)
    cv2.putText(frame_bgr, "Click", (icon_x + 18, icon_y + 6), _FONT, 0.5, _TEXT_COLOR, 1, cv2.LINE_AA)

    drag_on = bool(action_state.get("drag", False))
    color = _GOOD if drag_on else (180,180,180)
    cv2.circle(frame_bgr, (icon_x + spacing, icon_y), 10, color, -1)
    cv2.putText(frame_bgr, "Drag", (icon_x + spacing + 18, icon_y + 6), _FONT, 0.5, _TEXT_COLOR, 1, cv2.LINE_AA)

    scroll_on = bool(action_state.get("scroll", False))
    color = _GOOD if scroll_on else (180,180,180)
    cv2.circle(frame_bgr, (icon_x + spacing*2, icon_y), 10, color, -1)
    cv2.putText(frame_bgr, "Scroll", (icon_x + spacing*2 + 18, icon_y + 6), _FONT, 0.5, _TEXT_COLOR, 1, cv2.LINE_AA)

    # Draw minimal landmarks (tips)
    if landmarks:
        key_points = [4, 8, 12, 16, 20]  # tips
        for idx in key_points:
            if idx < len(landmarks):
                x,y = landmarks[idx]
                px, py = _norm_to_px(x, y, w, h)
                cv2.circle(frame_bgr, (px, py), max(3, int(min(w,h)*0.006)), (0,255,0), -1)

    if debug:
        cv2.putText(frame_bgr, "DEBUG", (12, h - 12), _FONT, 0.5, _WARN, 1, cv2.LINE_AA)

    return frame_bgr
