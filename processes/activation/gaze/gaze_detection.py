from multiprocessing.synchronize import Event as EventInstance

import time as t

from custom_lib.flag_pkg import FlagPkg
from custom_lib.eaxtension import LogE

import cv2
from GazeTracking.gaze_tracking import GazeTracking


def gaze_detection_process(flag_pkg: FlagPkg,
                           gazing_flag: EventInstance):
    PROCESS_NAME = "gaze"

    gaze = GazeTracking()
    webcam = cv2.VideoCapture(0, cv2.CAP_MSMF)
    if webcam.isOpened():
        t.sleep(2)
        flag_pkg.loading.clear()
    else:
        raise RuntimeError()

    while True:
        if flag_pkg.enable.is_set():
            ret, frame = webcam.read()
            if not ret or frame is None:
                LogE.e(PROCESS_NAME, "frame is empty.")
            else:
                gaze.refresh(frame)

                text = "None"
                if gaze.is_right():
                    text = "Looking right"
                elif gaze.is_left():
                    text = "Looking left"
                elif gaze.is_center():
                    text = "Looking center"
                elif gaze.is_blinking():
                    text = "blinking"
                print(f"gaze: {text}")

                if gaze.is_center() or gaze.is_blinking():  # 응시 방향 조건은 장치에서 재조정해야함.
                    gazing_flag.set()
                else:
                    gazing_flag.clear()