<a name="readme-top"></a>

<div align="center">

  <h3 align="center">Gesture-Based Air Keyboard & Virtual Mouse</h3>

  <p align="center">
    A real-time Human–Computer Interaction (HCI) system that enables keyboard typing
    and mouse control using hand gestures captured via webcam.
  </p>

</div>

---

## About The Project

This project is a **real-time computer vision–based interaction system** built to explore  
**gesture recognition**, **hand tracking**, and **natural human–computer interaction**.

The system allows users to type text and control mouse actions (move, click, drag, scroll)
using only hand gestures in front of a webcam — without any physical keyboard or mouse.

The core focus of the project is computer vision, gesture-based input design,  
real-time system stability, and practical HCI engineering, rather than UI frameworks
or web deployment.

---

## Core Interaction Flow

1. Capture live video input from webcam  
2. Detect and track hand landmarks using MediaPipe  
3. Interpret finger configurations as gestures  
4. Switch interaction modes (Keyboard / Mouse)  
5. Execute system-level keyboard and mouse actions  
6. Provide real-time visual feedback on screen  

All interactions happen **locally and in real time**.

---

## GitHub Link

https://github.com/Eepsita12/air-keyboard-virtual-mouse

---

## Built With

### Core Technologies
* [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

* [![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)

* [![MediaPipe](https://img.shields.io/badge/MediaPipe-0F9D58?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/mediapipe)

* [![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)

* [![PyAutoGUI](https://img.shields.io/badge/PyAutoGUI-FF6F00?style=for-the-badge&logo=python&logoColor=white)](https://pyautogui.readthedocs.io/)


---

## Gesture Controls

### Mode Switching
| Gesture | Action |
|------|------|
| Open Palm | Switch to Mouse Mode |
| Peace Sign ✌️ | Switch to Keyboard Mode |

### Keyboard Mode
| Gesture | Action |
|------|------|
| Hover + Pinch (Thumb + Index) | Key press |
| Backspace Key | Delete last character |
| Space Key | Insert space |

### Mouse Mode
| Gesture | Action |
|------|------|
| Index finger movement | Move cursor |
| Quick pinch (Thumb + Index) | Left click |
| Pinch & hold | Drag & drop |
| Index + Middle pinch | Right click |
| Scroll gesture (Middle + Thumb) | Scroll up/down |

---

## System Architecture

```

Webcam Input
|
v
Hand Landmark Detection (MediaPipe)
|
v
Gesture Interpretation Logic
|
v
Mode Controller (Keyboard / Mouse)
|
v
OS-Level Actions (PyAutoGUI)
|
v
Visual Feedback (OpenCV Overlay)

````

---

## Architectural Principles

- No external servers or APIs
- No web UI or deployment dependency
- All processing happens locally
- Real-time performance prioritized
- Explicit separation of:
  - Gesture detection
  - Interaction logic
  - System actions
- Configurable thresholds for tuning stability

This mirrors how real-world HCI prototypes and assistive interaction systems
are engineered.

---

## Key Engineering Decisions

### 1. Landmark Smoothing
Raw MediaPipe landmarks naturally jitter frame-to-frame.  
Temporal smoothing is applied to fingertip positions to ensure:

- Stable cursor movement
- Reliable key selection
- Reduced accidental clicks

---

### 2. Dead-Zone & Interpolation
To prevent cursor jumps:

- Camera input is clipped using a normalized margin
- Finger movement is interpolated to screen dimensions
- Movement is smoothed before applying OS-level actions

---

### 3. Controlled Gesture Activation
All gestures use:
- Distance thresholds
- Frame-based debouncing
- Hold-duration logic

This prevents:
- Accidental triggers
- Rapid repeated clicks
- Gesture misfires in noisy conditions

---

## Configuration & Tunability

All interaction parameters are centralized in a **User Config section**:

- Pinch thresholds
- Drag hold time
- Mouse smoothing factor
- Scroll sensitivity
- Keyboard character limit

This allows easy tuning without modifying core logic.

---

## How to Run

### 1. Install dependencies
```bash
pip install opencv-python mediapipe pyautogui numpy
````

### 2. Run the application

```bash
python air_keyboard_virtual_mouse.py
```

### Requirements

* Webcam
* Well-lit environment
* Desktop OS (Windows / macOS / Linux)

---

## Project Status

| Feature               | Status     |
| --------------------- | ---------- |
| Hand Tracking         | ✅ Complete |
| Gesture Recognition   | ✅ Complete |
| Air Keyboard          | ✅ Complete |
| Virtual Mouse         | ✅ Complete |
| Click / Drag / Scroll | ✅ Complete |
| Mode Switching        | ✅ Complete |
| Stability & Smoothing | ✅ Complete |

---

## Future Enhancements

* Predictive text suggestions
* Multi-language keyboard layouts
* Gesture customization UI
* Accessibility-focused interaction modes
* Multi-hand support

---

## Author

**Eepsita Modi**

---

## Thank You

This project was built as a practical exploration of
**computer vision**, **gesture-based interfaces**, and **human–computer interaction**.

Feel free to explore, experiment, and build on top of it ✨
