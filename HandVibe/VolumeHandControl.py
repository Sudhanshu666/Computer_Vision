import cv2 as cv
import time
import numpy as np
import HandTrackModule as htm
import math
import screen_brightness_control as sbc
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

capture = cv.VideoCapture(0)

cTime = 0
pTime = 0

def rescaleFrame(frame, scale):
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)

    dimensions = (width, height)

    return cv.resize(frame, dimensions, interpolation = cv.INTER_AREA)

detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()

currentVol = volume.GetMasterVolumeLevelScalar()

minVol = volRange[0]
maxVol = volRange[1]
volBar = np.interp(currentVol, [0, 1], [250, 700])
volPer = np.interp(currentVol, [0, 1], [0, 100])

currentB = sbc.get_brightness()
bBar= np.interp(currentB, [0, 100], [250, 700])

while True:
    isTrue, frame = capture.read()
    frame = cv.flip(frame, 1)
    frame = rescaleFrame(frame, 1.5)

    frame = detector.findHands(frame)
    lmList = detector.findPosition(frame, draw = False)
    #print(frame.shape)
    if len(lmList) != 0:
        #print(lmList[4], lmList[8])
        if lmList[0][1] > frame.shape[1] // 2:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1 + x2)//2, (y1 + y2)//2
        
            cv.circle(frame, (x1, y1), 12, (0,255,0), cv.FILLED)
            cv.circle(frame, (x2, y2), 12, (0,255,0), cv.FILLED)
            cv.line(frame, (x1, y1), (x2, y2), (0,255,0), 3)
            cv.circle(frame,(cx, cy), 12, (0,255,0), cv.FILLED)
            
            length = math.hypot(x2 - x1, y2 - y1)
            #print(length)            
            
            currentVol = volume.GetMasterVolumeLevelScalar()

            # Volume range 0 --> 1
            # Hand Range 20 --> 270
            # Volume Range -64 --> 0
            #                                     -64     0
            vol = np.interp(length, [20, 250], [minVol, maxVol])
            volBar = np.interp(currentVol, [0, 1], [250, 700])
            volPer = np.interp(currentVol, [0, 1], [0, 100])
            #print(vol)      
            volume.SetMasterVolumeLevel(vol, None)                        
        
        if lmList[0][1] < frame.shape[1] // 2:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1 + x2)//2, (y1 + y2)//2
        
            cv.circle(frame, (x1, y1), 12, (0,255,0), cv.FILLED)
            cv.circle(frame, (x2, y2), 12, (0,255,0), cv.FILLED)
            cv.line(frame, (x1, y1), (x2, y2), (0,255,0), 3)
            cv.circle(frame,(cx, cy), 12, (0,255,0), cv.FILLED)
            
            length = math.hypot(x2 - x1, y2 - y1)
            #print(length)
            
            currentB = sbc.get_brightness()            

            # Hand Range 20 --> 250
            # Brightness Range 0 --> 100
            #                                     -64     0
            blevel = np.interp(length, [20, 250], [0, 100])   
            bBar= np.interp(currentB, [0, 100], [250, 700])         
            blevel = int(blevel)

            sbc.set_brightness(blevel)            
            
        if length < 50:
            cv.circle(frame,(cx, cy), 12, (0,0,255), cv.FILLED)

    cv.putText(frame, 'Volume : ', (90, 80), cv.FONT_HERSHEY_PLAIN, 2, (255,0,0), 3)        
    cv.rectangle(frame, (250, 50), (700, 100), (255,0,0), 3)
    cv.rectangle(frame, (250, 50), (int(volBar), 100), (255,0,0), cv.FILLED)
    cv.putText(frame, f'{int(volPer)} %', (740, 90), cv.FONT_HERSHEY_PLAIN, 2, (255,0,0), 3)

    cv.putText(frame, 'Brightness : ', (30, 630), cv.FONT_HERSHEY_PLAIN, 2, (255,0,0), 3)
    cv.rectangle(frame, (250, 600), (700, 650), (255,0,0), 3)
    cv.rectangle(frame, (250, 600), (int(bBar), 650), (255,0,0), cv.FILLED)
    cv.putText(frame, f'{int(currentB[0])} %', (740, 640), cv.FONT_HERSHEY_PLAIN, 2, (255,0,0), 3)
    
    if volPer > 80:
        cv.putText(frame, 'Volume : ', (90, 80), cv.FONT_HERSHEY_PLAIN, 2, (0,0,255), 3)        
        cv.rectangle(frame, (250, 50), (700, 100), (0,0,255), 3)
        cv.rectangle(frame, (250, 50), (int(volBar), 100), (0,0,255), cv.FILLED)
        cv.putText(frame, f'{int(volPer)} %', (740, 90), cv.FONT_HERSHEY_PLAIN, 2, (0,0,255), 3)
    
    if currentB[0] > 80:
        cv.putText(frame, 'Brightness : ', (30, 630), cv.FONT_HERSHEY_PLAIN, 2, (0,0,255), 3)
        cv.rectangle(frame, (250, 600), (700, 650), (0,0,255), 3)
        cv.rectangle(frame, (250, 600), (int(bBar), 650), (0,0,255), cv.FILLED)
        cv.putText(frame, f'{int(currentB[0])} %', (740, 640), cv.FONT_HERSHEY_PLAIN, 2, (0,0,255), 3)

    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    
    cv.putText(frame, f'FPS : {int(fps)}', (20, 40), cv.FONT_HERSHEY_PLAIN, 2, (0,255,0), 3)
    
    cv.imshow('HandWibe', frame)
    
    if cv.waitKey(1) & 0xFF==ord('x'):
        break
capture.release
cv.destroyAllWindows