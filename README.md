VIRTUAL MOUSE CONTROL SYSTEM

A Webcam-Based Hand Gesture Mouse Control Application

PROJECT OVERVIEW

The Virtual Mouse Control System is a Python desktop application that enables users to control their computer mouse using hand gestures detected through a webcam.

The application combines computer vision, hand landmark detection, and mouse automation to provide a hands-free interaction experience. A graphical user interface provides Start and Stop controls to manage tracking.

KEY FEATURES

• Real-time hand tracking using MediaPipe.
• Webcam capture and image processing using OpenCV.
• Cursor movement controlled by index-finger position.
• Thumb and index-finger pinch for left-button interaction and dragging.
• Thumb and middle-finger pinch for right-click.
• Desktop graphical interface with Start and Stop controls.
• Background processing for camera and gesture tracking.
• Shutdown handling for mouse-button and camera cleanup.
• Automated tests for selected gesture and shutdown conditions.

HOW IT WORKS

1. Launch the application.
2. Press Start to begin webcam tracking.
3. OpenCV captures frames from the webcam.
4. MediaPipe identifies hand landmarks.
5. The application interprets supported gestures.
6. PyAutoGUI performs the corresponding mouse actions.
7. Press Stop to signal the tracking process to shut down.
8. The application performs cleanup before exiting.

GESTURE CONTROLS

Index-finger movement
Moves the mouse cursor.

Thumb and index-finger pinch
Performs the supported left-button interaction and dragging.

Thumb and middle-finger pinch
Triggers a right-click.

Gesture recognition depends on lighting, camera positioning, hand visibility, and the configured distance thresholds.

TECHNOLOGY STACK

Programming Language: Python 3.11

Computer Vision: OpenCV contrib 4.11.0.86

Hand Tracking: MediaPipe 0.10.21

Mouse Automation: PyAutoGUI 0.9.54

Graphical Interface: Tkinter

Background Processing: Python threading and events

Automated Testing: Python unittest

SYSTEM REQUIREMENTS

• Windows 10 or Windows 11
• Python 3.11
• A working webcam
• Camera access permission
• Internet access for dependency installation

The application has been tested locally using Python 3.11.9 on Windows. Other operating systems and configurations have not been verified.

INSTALLATION

Step 1. Download and extract the project files.

Step 2. Open PowerShell in the project directory.

Step 3. Create a virtual environment.

    py -3.11 -m venv .venv

Step 4. Activate the environment.

    .\.venv\Scripts\Activate.ps1

Step 5. Upgrade pip.

    python -m pip install --upgrade pip

Step 6. Install the required dependencies.

    python -m pip install -r requirements.txt

RUNNING THE APPLICATION

From the project directory, execute:

    python app.py

Allow camera access if Windows requests permission. When the application window opens, press Start to begin tracking. Press Stop to stop tracking, and close the application when finished.

RUNNING AUTOMATED TESTS

Run the test suite using:

    python -m unittest discover -v

Check Python syntax using:

    python -m py_compile app.py test_stop_mouse_patch.py test_gesture_conflict.py

VERIFICATION STATUS

The recorded automated test run passed all seven tests with no failures. Manual testing also confirmed cursor movement, left-button dragging, right-click, stopping, restarting, and clean application exit.

Automated tests cover selected code conditions. They do not guarantee identical behavior on every computer or webcam configuration.

TROUBLESHOOTING

Python is not available

Check the installed version with:

    py -3.11 --version

Dependency installation fails

Confirm the active Python environment and retry installation using requirements.txt.

Webcam does not open

Check Windows camera privacy settings, close applications that may already be using the webcam, and verify that the camera is functioning.

Hand tracking is unreliable

Improve lighting, keep the hand visible, avoid covering the fingertips, and maintain a comfortable distance from the camera.

Application does not start tracking

Run the application from PowerShell and inspect any error messages. Confirm that all dependencies are installed and that the webcam is accessible.

SAFETY CONSIDERATIONS

This application controls the real system mouse.

• Test in a safe environment.
• Save important work before starting.
• Keep the Stop control accessible.
• Stop tracking before interacting with sensitive dialogs or destructive actions.
• If the application becomes unresponsive, check the mouse state before continuing.

FUTURE IMPROVEMENTS

Potential enhancements include a live camera preview, adjustable gesture sensitivity, cursor smoothing, additional gestures, improved error reporting, broader platform support, and a desktop installer.

These are proposed improvements rather than existing features.

CONTRIBUTING

Contributions and suggestions are welcome. Test changes before submitting them, and avoid including virtual environments, local backups, or generated files in contributions.

LICENSE

A license has not yet been selected. Add an appropriate license before distributing the project as open-source software.

PROJECT SUMMARY

The Virtual Mouse Control System demonstrates how computer vision, hand tracking, desktop GUI development, and mouse automation can be combined into a practical Python application.

Developed using Python, OpenCV, MediaPipe, Tkinter, and PyAutoGUI.