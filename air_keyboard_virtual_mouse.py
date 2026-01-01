import cv2
import numpy as np
import mediapipe as mp
import math
import pyautogui
import time

pyautogui.FAILSAFE = False


letters=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["<-","SPC"]
key_rows=4
key_cols=7
typed_text= ""

# ================= USER CONFIG =================

PINCH_START_THRESHOLD = 0.04
PINCH_END_THRESHOLD   = 0.06

DRAG_HOLD_TIME = 0.18

MOUSE_SMOOTHING = 0.35
FRAME_MARGIN_NORM = 0.15

SCROLL_SENSITIVITY = 3000
SCROLL_THRESHOLD   = 0.06

MAX_CHARS = 25

# ===============================================



def smooth_point(prev, curr, alpha=0.7):
    if prev is None:
        return curr
    x = int(prev[0] * alpha + curr[0] * (1 - alpha))
    y = int(prev[1] * alpha + curr[1] * (1 - alpha))
    return (x, y)


def build_keys(frame_width,frame_height):
    keys=[]
    key_height=70 ## height of each key in pixels
    total_keyboard_height=key_height*key_rows
    bottom_margin=60 # extra empty space at bottom
    y_start=frame_height-total_keyboard_height-bottom_margin

    side_margin=60 # pixels empty on left and right
    usable_width=frame_width - 2*side_margin
    key_width=usable_width//key_cols
    for index,char in enumerate(letters):
        row=index//key_cols
        col=index % key_cols

        x1 = side_margin+ col * key_width
        y1 = y_start + row * key_height
        x2 = x1 + key_width
        y2 = y1 + key_height

        key_info={
            "char":char,
            "x1":x1,
            "y1":y1,
            "x2":x2,
            "y2":y2
        }
        keys.append(key_info)
    return keys

def draw_keyboard(frame, keys, hover_key_index=None):
    for i, key in enumerate(keys):
        x1 = key["x1"]
        y1 = key["y1"]
        x2 = key["x2"]
        y2 = key["y2"]
        char = key["char"]

        # if this key's index matches hovered index → highlight
        if hover_key_index == i:
            color = (0, 255, 0)
            thickness = 4
        else:
            color = (255, 255, 255)
            thickness = 2

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

        font = cv2.FONT_HERSHEY_SIMPLEX
        text_scale = 1
        text_thickness = 2
        text_size, _ = cv2.getTextSize(char, font, text_scale, text_thickness)
        text_width, text_height = text_size
        text_x = x1 + (x2 - x1 - text_width) // 2
        text_y = y1 + (y2 - y1 + text_height) // 2
        cv2.putText(frame, char, (text_x, text_y), font, text_scale, (255, 255, 255), text_thickness)

def draw_textbox(frame,text):
    h,w,_ = frame.shape
    box_x1=50
    box_y1=30
    box_x2=w-50
    box_y2=110

    cv2.rectangle(frame,(box_x1,box_y1),(box_x2,box_y2),(255,255,255),-1)
    cv2.rectangle(frame,(box_x1,box_y1),(box_x2,box_y2),(0,0,0),2)

    font=cv2.FONT_HERSHEY_SIMPLEX
    font_scale=1
    thickness=2

    text_x=box_x1+20
    text_y=box_y1+50

    cv2.putText(frame,text,(text_x,text_y),font,font_scale,(0,0,0),thickness)

mp_hands=mp.solutions.hands
hands=mp_hands.Hands(max_num_hands=1)
mp_draw=mp.solutions.drawing_utils

def count_extended_fingers(hand_landmarks, frame_width, frame_height):
    """
    Return (count, [thumb, index, middle, ring, pinky]) for which fingers are extended.
    Simple rules:
     - For thumb: compare x of tip vs pip (thumb opens sideways)
     - For other fingers: compare y of tip vs pip (tip above pip when finger extended)
    """
    tips_ids = [4, 8, 12, 16, 20]   # landmark indices for fingertip landmarks
    pip_ids =  [3, 6, 10, 14, 18]   # approximate pip joint indices for each finger

    extended = []
    for tip, pip in zip(tips_ids, pip_ids):
        tip_lm = hand_landmarks.landmark[tip]
        pip_lm = hand_landmarks.landmark[pip]

        if tip == 4:
            # Thumb: compare horizontal distance (thumb extends sideways)
            extended.append(abs(tip_lm.x - pip_lm.x) > 0.03)
        else:
            # Other fingers: tip y smaller than pip y when finger is extended (image coords)
            extended.append(tip_lm.y < pip_lm.y)

    return sum(extended), extended

def fingers_up(hand_landmarks):
    lm = hand_landmarks.landmark
    thumb_up  = lm[4].x < lm[3].x
    index_up  = lm[8].y < lm[6].y
    middle_up = lm[12].y < lm[10].y
    ring_up   = lm[16].y < lm[14].y
    pinky_up  = lm[20].y < lm[18].y
    return [thumb_up, index_up, middle_up, ring_up, pinky_up]


def main():
    cap= cv2.VideoCapture(0)
    cv2.namedWindow("Air Keyboard - Webcam Test", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Air Keyboard - Webcam Test", 500, 350)
    cv2.setWindowProperty(
        "Air Keyboard - Webcam Test",
        cv2.WND_PROP_TOPMOST,
        1
    )

    if not cap.isOpened():
        print("Error")
        return
    keys=None
    pinch_active=False ## True while pinch is being held
    last_hover_key = None
    pinch_frames = 0
    PINCH_FRAMES = 5   
    mode = "keyboard"           # current mode: "keyboard", "mouse"
    gesture_name = None         # currently-detected gesture name
    gesture_hold_frames = 0     # how long the same gesture has been held
    GESTURE_FRAMES = 5         # hold this many frames to switch modes
    screen_width, screen_height = pyautogui.size()
    prev_x, prev_y = pyautogui.position()
    smooth_factor = MOUSE_SMOOTHING

    pinch_start_time = None
    dragging = False

    Drag_Hold_Time = DRAG_HOLD_TIME
    pinch_start_threshold = PINCH_START_THRESHOLD
    pinch_end_threshold = PINCH_END_THRESHOLD
    right_clicked = False

    scroll_active = False
    prev_scroll_y = None
    scroll_sensitivity = SCROLL_SENSITIVITY
    scroll_threshold = SCROLL_THRESHOLD
    prev_index_pt=None
    prev_thumb_pt=None


    while True:
        success, frame= cap.read()
        if not success:
            print("Error in reading frame")
            return

        frame=cv2.flip(frame,1)
        frame_height, frame_width, _ = frame.shape
        rgb=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results=hands.process(rgb)
        index_x,index_y=None, None

        is_pinch=False
        index_x = index_y = None
        thumb_x = thumb_y = None

        if not results.multi_hand_landmarks:
            gesture_name = None
            gesture_hold_frames = 0


        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_finger_tip=hand_landmarks.landmark[8]
                thumb_tip=hand_landmarks.landmark[4]

                raw_index = (
                    int(index_finger_tip.x * frame_width),
                    int(index_finger_tip.y * frame_height)
                )
                raw_thumb = (
                    int(thumb_tip.x * frame_width),
                    int(thumb_tip.y * frame_height)
                )

                index_x, index_y = smooth_point(prev_index_pt, raw_index)
                thumb_x, thumb_y = smooth_point(prev_thumb_pt, raw_thumb)

                prev_index_pt = (index_x, index_y)
                prev_thumb_pt = (thumb_x, thumb_y)


                # detect how many fingers are extended and which ones
                finger_count, ext = count_extended_fingers(hand_landmarks, frame_width, frame_height)

                # map simple gestures from finger patterns
                detected_gesture = None
                if finger_count == 5:
                    detected_gesture = "palm"
                elif finger_count == 2 and ext[1] and ext[2]:
                    detected_gesture = "peace"

                # debounce the detected gesture across frames
                if detected_gesture == gesture_name:
                    gesture_hold_frames += 1
                else:
                    gesture_name = detected_gesture
                    gesture_hold_frames = 1

                # commit the mode switch when gesture held long enough
                if gesture_name is not None and gesture_hold_frames >= GESTURE_FRAMES:
                    if dragging:
                        pyautogui.mouseUp()
                        dragging = False
  
                    if gesture_name == "palm":
                        mode = "mouse"
                    elif gesture_name == "peace":
                        mode = "keyboard"
                    gesture_hold_frames = 0   # reset after switching

                if mode == "mouse":
                    fingers = fingers_up(hand_landmarks)
                    thumb_up, index_up, middle_up, ring_up, pinky_up = fingers

                    index_tip = hand_landmarks.landmark[8]
                    thumb_tip = hand_landmarks.landmark[4]
                    middle_tip = hand_landmarks.landmark[12]

                    x1, y1 = thumb_tip.x, thumb_tip.y
                    x2, y2 = index_tip.x, index_tip.y
                    x3, y3 = middle_tip.x, middle_tip.y

                    distance = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
                    mid_distance = ((x3 - x2)**2 + (y3 - y2)**2) ** 0.5
                    scroll_distance = ((x3 - x1)**2 + (y3 - y1)**2) ** 0.5

                    current_time = time.time()

                    if distance < pinch_start_threshold:
                        if pinch_start_time is None:
                            pinch_start_time = current_time
                        else:
                            held_time = current_time - pinch_start_time
                            if held_time > Drag_Hold_Time and not dragging:
                                pyautogui.mouseDown()
                                dragging = True

                    elif distance > pinch_end_threshold:
                        if pinch_start_time is not None:
                            if dragging:
                                pyautogui.mouseUp()
                                dragging = False
                            else:
                                click_duration = current_time - pinch_start_time
                                if click_duration < 0.4:
                                    pyautogui.leftClick()
                        pinch_start_time = None

                    if index_up and middle_up and not dragging:
                        if mid_distance < 0.032:
                            if not right_clicked:
                                pyautogui.rightClick()
                                right_clicked = True
                        else:
                            right_clicked = False
                    else:
                        right_clicked = False

                    if scroll_distance < scroll_threshold:
                        if not scroll_active:
                            scroll_active = True
                            prev_scroll_y = middle_tip.y

                        dy = middle_tip.y - prev_scroll_y
                        if abs(dy) > 0.002:
                            pyautogui.scroll(int(-dy * scroll_sensitivity))
                            prev_scroll_y = middle_tip.y
                    else:
                        scroll_active = False
                        prev_scroll_y = None    

                    x_norm = np.clip(index_tip.x, FRAME_MARGIN_NORM, 1 - FRAME_MARGIN_NORM)
                    y_norm = np.clip(index_tip.y, FRAME_MARGIN_NORM, 1 - FRAME_MARGIN_NORM)

                    mouse_x = np.interp(x_norm,
                                        (FRAME_MARGIN_NORM, 1 - FRAME_MARGIN_NORM),
                                        (0, screen_width))

                    mouse_y = np.interp(y_norm,
                                        (FRAME_MARGIN_NORM, 1 - FRAME_MARGIN_NORM),
                                        (0, screen_height))


                    margin = 20
                    mouse_x = max(margin, min(screen_width - margin, mouse_x))
                    mouse_y = max(margin, min(screen_height - margin, mouse_y))

                    smoothed_x = prev_x + MOUSE_SMOOTHING * (mouse_x - prev_x)
                    smoothed_y = prev_y + MOUSE_SMOOTHING * (mouse_y - prev_y)


                    pyautogui.moveTo(smoothed_x, smoothed_y)
                    prev_x, prev_y = smoothed_x, smoothed_y
                
                distance = ((index_x - thumb_x)**2 + (index_y - thumb_y)**2) ** 0.5

                if mode == "keyboard" and distance < 40:
                    is_pinch = True

                

        if keys is None:
            keys= build_keys(frame_width, frame_height)

        global typed_text

        hover_key = None
        if mode == "keyboard" and index_x is not None and index_y is not None:
            for i, key in enumerate(keys):
                if key["x1"] <= index_x <= key["x2"] and key["y1"] <= index_y <= key["y2"]:
                    hover_key = i
                    break


        if mode == "keyboard" and hover_key is not None and is_pinch:
            if hover_key == last_hover_key:
                pinch_frames += 1
            else:
                
                last_hover_key = hover_key
                pinch_frames = 1

            if pinch_frames >= PINCH_FRAMES and not pinch_active:
                char = keys[hover_key]["char"]

                if char =="<-":
                    if len(typed_text)>0:
                        typed_text=typed_text[:-1]
                elif char=="SPC":
                    typed_text += " "
                else:
                    typed_text += char
                    typed_text=typed_text[-MAX_CHARS:]

                print("Typed:", typed_text)
                pinch_active = True   
        else:
           
            pinch_frames = 0
            last_hover_key = hover_key if hover_key is not None else None
            if not is_pinch:
                pinch_active = False

        if mode=="keyboard":
            draw_keyboard(frame, keys, hover_key_index=hover_key)
        draw_textbox(frame, typed_text)

        cv2.putText(
        frame,
        f"MODE: {mode.upper()}",
        (60, 105),   # INSIDE textbox, bottom-left
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 255),
        2
        )


        if mode != "mouse":
            if index_x is not None and index_y is not None:
                cv2.circle(frame,(index_x,index_y),10,(0,255,0),-1)
            if thumb_x is not None and thumb_y is not None:
                cv2.circle(frame,(thumb_x,thumb_y),10,(0,0,255),-1)

        cv2.imshow("Air Keyboard - Webcam Test",frame)
        key=cv2.waitKey(1)
        if key==ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

