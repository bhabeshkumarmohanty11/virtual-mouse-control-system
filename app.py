#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Virtual Mouse Pro
Control the mouse using hand landmarks detected by a webcam.

Install:
    python -m pip install opencv-python mediapipe pyautogui

Run:
    python virtual_mouse_final.py

Safety:
- PyAutoGUI's fail-safe remains enabled (move cursor to top-left to abort).
- All mouse actions and camera cleanup happen in the worker thread.
- Stopping the app requests shutdown; the worker releases any held mouse button.
"""

import math
import threading
import tkinter as tk
from tkinter import messagebox

import cv2
import mediapipe as mp
import pyautogui


# Keep PyAutoGUI's fail-safe enabled. Reduce its default delay for smoother
# cursor movement; set this to 0.05 if you prefer extra pacing.
pyautogui.PAUSE = 0.0

# Configuration
CAMERA_INDEX = 0
MAX_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7
SMOOTHING = 7.0
GESTURE_THRESHOLD_RATIO = 0.075  # Relative to the smaller frame dimension.
CLICK_COOLDOWN_SECONDS = 0.6

# Thread coordination
stop_event = threading.Event()
worker_thread = None
state_lock = threading.Lock()
dragging = False

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def get_distance(p1, p2):
    """Return Euclidean distance between two 2D points."""
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def set_dragging(value):
    """Update the dragging state safely."""
    global dragging
    with state_lock:
        dragging = value


def is_dragging():
    """Read the dragging state safely."""
    with state_lock:
        return dragging


def run_virtual_mouse():
    """Capture webcam frames and translate hand gestures into mouse actions."""
    global worker_thread

    cap = None
    hands = None
    left_button_held = False
    cursor_initialized = False
    prev_x, prev_y = 0.0, 0.0
    right_click_down = False
    last_action_time = 0.0

    try:
        screen_w, screen_h = pyautogui.size()
        cap = cv2.VideoCapture(CAMERA_INDEX)

        if not cap.isOpened():
            raise RuntimeError(
                f"Could not open webcam (camera index {CAMERA_INDEX}). "
                "Close other camera applications or check camera permissions."
            )

        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )

        while not stop_event.is_set():
            success, img = cap.read()
            if not success or img is None:
                raise RuntimeError(
                    "Could not read a frame from the webcam. "
                    "Check the camera connection and permissions."
                )

            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)
            frame_h, frame_w = img.shape[:2]
            status_text = "No Hand"

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                mp_drawing.draw_landmarks(
                    img, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )
                landmarks = hand_landmarks.landmark

                # Fingertip positions in camera-frame pixels.
                ix, iy = int(landmarks[8].x * frame_w), int(landmarks[8].y * frame_h)
                tx, ty = int(landmarks[4].x * frame_w), int(landmarks[4].y * frame_h)
                mx, my = int(landmarks[12].x * frame_w), int(landmarks[12].y * frame_h)

                # Initialize directly at the first detected fingertip; smooth
                # only subsequent frames. A separate flag avoids using (0, 0)
                # as a special marker, since that can be a valid coordinate.
                if not cursor_initialized:
                    cur_x, cur_y = float(ix), float(iy)
                    cursor_initialized = True
                else:
                    cur_x = prev_x + (ix - prev_x) / SMOOTHING
                    cur_y = prev_y + (iy - prev_y) / SMOOTHING

                screen_x = (cur_x / max(frame_w - 1, 1)) * (screen_w - 1)
                screen_y = (cur_y / max(frame_h - 1, 1)) * (screen_h - 1)
                screen_x = max(0, min(screen_w - 1, screen_x))
                screen_y = max(0, min(screen_h - 1, screen_y))
                pyautogui.moveTo(int(screen_x), int(screen_y))
                prev_x, prev_y = cur_x, cur_y
                status_text = "Moving"

                # Scale gesture thresholds with the frame resolution.
                threshold = min(frame_w, frame_h) * GESTURE_THRESHOLD_RATIO
                pinch_distance = get_distance((ix, iy), (tx, ty))
                right_click_distance = get_distance((mx, my), (tx, ty))
                now = __import__("time").monotonic()

                # Left pinch: hold left mouse button for dragging.
                if pinch_distance < threshold:
                    if not left_button_held and now - last_action_time >= CLICK_COOLDOWN_SECONDS:
                        pyautogui.mouseDown(button="left")
                        left_button_held = True
                        set_dragging(True)
                        last_action_time = now
                        status_text = "Dragging"
                elif left_button_held:
                    pyautogui.mouseUp(button="left")
                    left_button_held = False
                    set_dragging(False)
                    last_action_time = now
                    status_text = "Released"

                # Right click is mutually exclusive with an active left drag.
                # If the right gesture is already held during a drag, remember
                # that state so it cannot fire immediately when the drag ends.
                if left_button_held:
                    right_click_down = right_click_distance < threshold
                elif right_click_distance < threshold:
                    if (
                        not right_click_down
                        and now - last_action_time >= CLICK_COOLDOWN_SECONDS
                    ):
                        pyautogui.click(button="right")
                        right_click_down = True
                        last_action_time = now
                        status_text = "Right Click"
                else:
                    right_click_down = False

                cv2.circle(img, (ix, iy), 8, (0, 255, 255), -1)

            else:
                # Reset cursor smoothing after hand loss so reappearance
                # initializes at the new location instead of gliding from stale data.
                cursor_initialized = False

                # Safety: release a held drag if the hand disappears.
                if left_button_held:
                    pyautogui.mouseUp(button="left")
                    left_button_held = False
                    set_dragging(False)
                    last_action_time = __import__("time").monotonic()
                    status_text = "Drag Released"

                right_click_down = False

            cv2.putText(
                img,
                f"Status: {status_text}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 100),
                2,
            )
            cv2.imshow("Virtual Mouse Pro", img)

            # ESC in the camera window requests shutdown.
            if cv2.waitKey(1) & 0xFF == 27:
                stop_event.set()
                break

    except Exception as exc:
        # Report errors on the Tk main thread rather than touching Tk from
        # the worker thread.
        root.after(0, lambda error=str(exc): show_worker_error(error))
    finally:
        # Always release the left mouse button if the worker exits mid-drag.
        if left_button_held:
            try:
                pyautogui.mouseUp(button="left")
            except Exception:
                pass
        set_dragging(False)

        if hands is not None:
            try:
                hands.close()
            except Exception:
                pass

        if cap is not None:
            try:
                cap.release()
            except Exception:
                pass

        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

        stop_event.set()
        root.after(0, on_worker_finished)


def show_worker_error(message):
    """Show a worker error safely from the Tk main thread."""
    if root.winfo_exists():
        messagebox.showerror("Virtual Mouse Error", message, parent=root)


def on_worker_finished():
    """Restore GUI state after the worker finishes."""
    global worker_thread
    worker_thread = None
    start_btn.config(state=tk.NORMAL)
    stop_btn.config(state=tk.DISABLED)


def start_mouse():
    """Start the camera worker if it is not already running."""
    global worker_thread

    if worker_thread is not None and worker_thread.is_alive():
        messagebox.showinfo(
            "Already Running", "The virtual mouse is already running.", parent=root
        )
        return

    stop_event.clear()
    start_btn.config(state=tk.DISABLED)
    stop_btn.config(state=tk.NORMAL)

    worker_thread = threading.Thread(target=run_virtual_mouse, daemon=True)
    worker_thread.start()


def stop_mouse():
    """Request worker shutdown; the worker owns camera and mouse cleanup."""
    stop_event.set()
    stop_btn.config(state=tk.DISABLED)


def close_app():
    """Request shutdown before closing the Tk window."""
    stop_event.set()
    if worker_thread is not None and worker_thread.is_alive():
        # Keep the GUI alive briefly so the worker can clean up safely.
        root.after(100, wait_for_worker_then_close)
    else:
        root.destroy()


def wait_for_worker_then_close():
    """Wait asynchronously for the camera worker to finish cleanup."""
    if worker_thread is not None and worker_thread.is_alive():
        root.after(100, wait_for_worker_then_close)
    else:
        root.destroy()


# Tkinter GUI
root = tk.Tk()
root.title("Virtual Mouse Controller")
root.geometry("460x370")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", close_app)

title = tk.Label(root, text="🖱 Virtual Mouse Pro", font=("Arial", 16, "bold"))
title.pack(pady=12)

instructions = (
    "How to use:\n"
    "• Raise your hand in front of the webcam.\n"
    "• Move index finger = move cursor.\n"
    "• Pinch index + thumb = drag / left-button hold.\n"
    "• Pinch middle finger + thumb = right-click.\n"
    "• Press ESC in the camera window or click Stop to stop."
)
info_label = tk.Label(root, text=instructions, justify="left", font=("Arial", 10))
info_label.pack(pady=10)

start_btn = tk.Button(
    root,
    text="Start Virtual Mouse",
    font=("Arial", 12),
    bg="green",
    fg="white",
    width=20,
    command=start_mouse,
)
start_btn.pack(pady=8)

stop_btn = tk.Button(
    root,
    text="Stop Virtual Mouse",
    font=("Arial", 12),
    bg="red",
    fg="white",
    width=20,
    command=stop_mouse,
    state=tk.DISABLED,
)
stop_btn.pack(pady=8)

root.mainloop()
