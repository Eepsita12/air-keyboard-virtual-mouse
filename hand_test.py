import cv2
import time
import mediapipe as mp
import pyautogui
mp_hands=mp.solutions.hands
mp_drawing=mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)


hands=mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

if not cap.isOpened():
    print("Camera not opened properly")

screen_width, screen_height= pyautogui.size()
prev_x, prev_y=pyautogui.position()
smooth_factor=0.2

pinch_start_time= None
dragging=False

Drag_Hold_Time= 0.18
pinch_start_threshold=0.04
pinch_end_threshold=0.06
right_clicked = False

scroll_active=False
prev_scroll_y=None
scroll_sensitivity=1000
scroll_threshold=0.03

control_enabled=True

def fingers_up(hand_landmarks):
    landmarks=hand_landmarks.landmark
    thumb_up = landmarks[4].x < landmarks[3].x  # these all says is fingertip above its lower joint?” → then that finger is up
    index_up  = landmarks[8].y  < landmarks[6].y
    middle_up = landmarks[12].y < landmarks[10].y
    ring_up   = landmarks[16].y < landmarks[14].y
    pinky_up  = landmarks[20].y < landmarks[18].y

    return [thumb_up, index_up, middle_up, ring_up, pinky_up]

cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Webcam", 500, 350)
cv2.setWindowProperty("Webcam", cv2.WND_PROP_TOPMOST, 1)


while True:
    success, frame= cap.read()
    frame=cv2.flip(frame,1)
    rgb_frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results=hands.process(rgb_frame)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )
            fingers= fingers_up(hand_landmarks)
            thumb_up, index_up, middle_up, ring_up, pinky_up = fingers

            if all(fingers):
                control_enabled=True
            elif not any(fingers):
                control_enabled=False

            if control_enabled:
                index_tip=hand_landmarks.landmark[8]
                thumb_tip=hand_landmarks.landmark[4]
                middle_tip=hand_landmarks.landmark[12]

                x1, y1= thumb_tip.x, thumb_tip.y
                x2, y2= index_tip.x, index_tip.y
                x3, y3= middle_tip.x, middle_tip.y

                distance= ((x2-x1)**2 + (y2-y1)**2) ** 0.5  #left click (index n thumb)
                mid_distance= ((x3-x2)**2 + (y3-y2)**2) ** 0.5
                scroll_distance= ((x3-x1)**2 + (y3-y1)**2) ** 0.5

                left_click_threshold=0.03
                right_cick_threshold=0.03

                current_time=time.time()

                if distance<pinch_start_threshold:
                    if pinch_start_time is None:
                        pinch_start_time=current_time
                    else:
                        held_time= current_time - pinch_start_time

                        if held_time>Drag_Hold_Time and not dragging:
                            pyautogui.mouseDown()
                            dragging = True

                elif distance>pinch_end_threshold:
                    if pinch_start_time is not None:
                        if dragging:
                            pyautogui.mouseUp()
                            dragging=False
                        else:
                            click_duration=current_time-pinch_start_time

                            if click_duration<0.4:
                                pyautogui.leftClick()

                    pinch_start_time= None

                else:
                    pass

                if index_up and middle_up and not thumb_up:                
                    if mid_distance<0.02:
                        if not right_clicked:
                            pyautogui.rightClick()
                            right_clicked=True
                    else:
                        right_clicked=False
                else:
                    right_clicked=False
                
                if scroll_distance<scroll_threshold:
                    if not scroll_active:
                        scroll_active=True
                        prev_scroll_y= y3

                    dy=y3-prev_scroll_y

                    if abs(dy)>0.005:
                        pyautogui.scroll(int(-dy*scroll_sensitivity))
                        prev_scroll_y=y3
                else:
                    scroll_active=False
                    prev_scroll_y=None
            
                x_norm= index_tip.x
                y_norm= index_tip.y

                if y_norm>0.9:
                    continue  

                mouse_x=int(x_norm*screen_width)
                mouse_y = int(y_norm * screen_height)

                smoothed_x= prev_x + smooth_factor * (mouse_x-prev_x)
                smoothed_y= prev_y + smooth_factor * (mouse_y-prev_y)

                pyautogui.moveTo(smoothed_x,smoothed_y)

                prev_x,prev_y=smoothed_x, smoothed_y
              
    cv2.imshow("Webcam",frame)
    key=cv2.waitKey(1)
    if key==ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
