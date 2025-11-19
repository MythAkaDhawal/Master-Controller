# main.py
import cv2
import time
import pyautogui
import config
from utils import FPS, normalized_landmarks_to_list
from hand_tracking import HandTracker
from gesture_recognizer import GestureRecognizer
from system_control import SystemController
from overlay_renderer import render_overlay

# Setup
pyautogui.FAILSAFE = False

def main():
    fps_counter = FPS()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)

    tracker = HandTracker(
        max_hands=config.MAX_HANDS,
        detection_con=config.DETECTION_CONFIDENCE,
        track_con=config.TRACKING_CONFIDENCE,
        smoothing_factor=config.LANDMARK_SMOOTHING_FACTOR
    )
    recognizer = GestureRecognizer(config)
    controller = SystemController(config)

    print("Hand Gesture Control System activated. Press 'q' or ESC to quit.")

    last_loop = time.time()
    while True:
        t0 = time.time()
        success, frame = cap.read()
        if not success:
            time.sleep(0.01)
            continue

        frame = cv2.flip(frame, 1)  # mirror
        # 1. Find hands
        frame, hands_data = tracker.find_hands(frame, draw=config.DRAW_LANDMARKS)

        # 2. Recognize gesture
        gesture, action_state = recognizer.recognize(hands_data)

        if config.DEBUG and gesture != "NONE":
            print(f"[DEBUG] Gesture: {gesture} | Action: {action_state}")

        # 3. Handle gesture -> system actions
        controller.handle_gesture(gesture, hands_data, frame.shape)

        # merge controller.action_state (controller may have updated drag state)
        # give rendering the union of recognizer and controller states
        display_action_state = controller.action_state.copy()
        for k, v in action_state.items():
            display_action_state[k] = display_action_state.get(k, False) or v

        # 4. FPS
        fps_counter.update()
        fps_val = fps_counter.get_fps()

        # 5. Overlay & show
        display = frame.copy()
        display = render_overlay(display, hands_data[0]["lm_list"] if hands_data else None,
                                 gesture if gesture else "Idle", display_action_state, fps_val, debug=config.DEBUG)
        fps_counter.display_fps(display, pos=(10, 30))  # redundant but safe

        cv2.imshow("Gesture Control", display)

        # Cap FPS to config.MAX_FPS
        elapsed = time.time() - t0
        min_frame_time = 1.0 / config.MAX_FPS
        if elapsed < min_frame_time:
            time.sleep(min_frame_time - elapsed)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("System deactivated.")

if __name__ == "__main__":
    main()
