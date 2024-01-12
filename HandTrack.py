import cv2 as cv
import mediapipe as mp
import time

cap = cv.VideoCapture(0)

mpHands= mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

cTime = 0
pTime = 0

while True:
    isTrue, frameori = cap.read()
    frame = cv.flip(frameori, 1)
    rgbframe = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    
    result = hands.process(rgbframe)
    #print(result.multi_hand_landmarks)
    
    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                #print(id, lm)
                h, w, c = frame.shape
                cx , cy = int(lm.x * w), int(lm.y * h)
                print(id, cx, cy)
                                
                if id == 4 or id == 8:
                    cv.circle(frame, (cx, cy), 12, (0,255,0), cv.FILLED)               
                
                
            mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)
            
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    
    cv.putText(frame, str(int(fps)), (10, 70), cv.FONT_HERSHEY_SIMPLEX, 3, (255,0,255), 3)
        
    cv.imshow('Webcam', frame)
    
    if cv.waitKey(1) & 0xFF==ord('x'):
        break
    
cap.release()
cv.destroyAllWindows()
    