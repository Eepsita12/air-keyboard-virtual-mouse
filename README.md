🖱️ AI Virtual Mouse Using Hand Gestures

A real-time, contactless virtual mouse built using Python, MediaPipe, OpenCV, and PyAutoGUI.
The system uses webcam-based hand tracking to control cursor movement, clicking, scrolling, and drag-and-drop through intuitive gestures.

🚀 Features

Real-time cursor control
Index fingertip controls the mouse smoothly across the screen.

Left click
Short pinch gesture between thumb and index finger.

Drag & drop / text selection
Hold the thumb–index pinch for a short duration to activate dragging.
Move your hand while pinched to drag or select.
Release the pinch to drop.

Right click
Bring the index and middle fingers close together (with thumb down).

Scrolling
Thumb, index, and middle fingers close together activate scroll mode.
Move your hand up or down to scroll vertically.

Control toggle
Open palm enables tracking.
Closed fist temporarily pauses control, letting you rest your hand.

Always-on-top webcam window
The preview stays visible for easier gesture control.

🧠 Tech Stack

Python

MediaPipe Hands

OpenCV

PyAutoGUI

📁 Project Structure
virtual-mouse-hand-gesture/
│
├── virtual_mouse.py
├── requirements.txt
└── README.md

⚙️ Installation & Setup
1. Clone the repository
git clone https://github.com/<your-username>/virtual-mouse-hand-gesture.git
cd virtual-mouse-hand-gesture

2. Install dependencies
pip install -r requirements.txt

3. Run the project
python virtual_mouse.py

🎮 Gesture Controls (Summary)

Move index finger → Cursor movement

Thumb + index pinch (short) → Left click

Thumb + index pinch (hold) → Drag & drop

Index + middle pinch → Right click

Thumb + index + middle close + move up/down → Scroll

Open palm → Enable mouse control

Closed fist → Disable mouse control

📌 Notes

Works best in good lighting.

Keep your hand inside the webcam frame for accurate tracking.

Press q to quit the application.

🧑‍💻 Author

Eepsita Modi
B.Tech (Information Technology)
Passionate about AI, ML, Computer Vision, and Human–Computer Interaction.
