import json
import multiprocessing
import time
import serial

import cv2

controlX = 0
controlY = 0


def main():
    cam = cv2.VideoCapture(0)
    global controlX, controlY
    while True:
        iSee = False

        success, frame = cam.read()

        if success:
            h, w = frame.shape[0:2]
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            binary = cv2.inRange(hsv, (18, 60, 100), (32, 255, 255))
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            if len(contours) != 0:
                maxc = max(contours, key=cv2.contourArea)
                moments = cv2.moments(maxc)
                if moments["m00"] > 20:
                    cx = int(moments["m10"] / moments["m00"])
                    iSee = True
                    controlX = 2 * (cx - w / 2) / w
            if iSee:
                controlY = 0.6
                print(f"X: {controlX}, Y: {controlY}")
            else:
                controlY = 0
                controlX = 0
            time.sleep(0.05)


msg = {
    "speedA": 0,
    "speedB": 0
}

uart = serial.Serial("/dev/ttyUSB0", 9600)


def sender():
    global controlX, controlY
    while True:
        msg["speedA"] = controlY
        msg["speedB"] = controlX
        uart.write(json.dumps(msg, ensure_ascii=False).encode("utf-8"))
        time.sleep(1 / 10)


if __name__ == "__main__":
    multiprocessing.Process(target=sender, daemon=True).start()
    main()
