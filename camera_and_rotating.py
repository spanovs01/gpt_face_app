import cv2
import numpy as np
import time
from picamera2 import Picamera2

import rokilowlvlpy as roki

def rotation_uniform_rule(end_pos, start_pos, current_pos, tick_i, num_steps=200):
    delta = end_pos - start_pos
    target = start_pos + int(delta * tick_i / num_steps)
    return target

def rotation_exponential_smoothing_rule(end_pos, start_pos, current_pos, tick_i, num_steps=200):
    delta = end_pos - current_pos
    beta = 0.95
    target = int(beta * current_pos) + int((1 - beta) * delta)
    return target

def rotation_standard_rule(end_pos, start_pos, current_pos, tick_i, num_steps=200):
    delta = end_pos - current_pos
    p_const = 30
    target = current_pos + p_const if delta > 0 else current_pos - p_const
    return target

def rotation_tick(pos):
    ok, ret = sks.set_position(11, pos)
    if not ok:
        print(sks.get_error())
        exit()
    # time.sleep(0.01)
    return ret.value

def rotate(delta, start_pos, num_steps=200):
    end_pos = start_pos + delta
    end_pos = max(0, min(end_pos, 14000))
    current_pos = rotation_tick(start_pos)
    for i in range(num_steps):
        target_i = rotation_standard_rule(end_pos, start_pos, current_pos, i, num_steps=num_steps)
        current_pos = rotation_tick(target_i)
    return current_pos

def get_current_pos():
    ok, ret = sks.set_hold(11)
    if not ok:
        print(sks.get_error())
        exit()
    return ret.value
    
def Face_Detector(picamera, display=True):                      # TODO: threshold на близость человека к голове
    face_detector = cv2.CascadeClassifier("/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml")
    width = 320
    height = 240
    width_threshold = 50
    delta = 0
    start_pos = get_current_pos()
    current_pos = start_pos
    rotate_iter = 0
    num_steps = 100
    while True:
        frame = picamera.capture_array("lores")
        image = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_I420)
        faces = face_detector.detectMultiScale(image, 1.1, 3) # TODO: неточная модельб видит лица там где их нет
        # print(faces)

        if len(faces) > 0:
            bigest_face = [0, 0, 0, 0]
            for face in faces:
                if  bigest_face[2] < face[2]:
                    bigest_face = face
            if bigest_face[2] > width_threshold:
                (x, y, w, h) = bigest_face
                print(x,y,w,h)
                img_with_face = cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 5)
                bb_center_x = x + w // 2
                # if bb_center_x >= width // 2:
                #     delta = (bb_center_x - width // 2) / (width // 2)
                # else:
                #     delta = (-bb_center_x + width // 2) / (width // 2)
                delta = (bb_center_x - width // 2) / (width // 2)
                if abs(delta) < 0.2:
                    delta = 0
                print(delta)
                delta *= 5000
            else:
                delta = 0
                img_with_face = image
        else:
            delta = 0
            img_with_face = image

        end_pos = start_pos + delta
        end_pos = max(-7000, min(end_pos, 7000))
        start_pos = rotation_tick(start_pos)
        if abs(start_pos - end_pos) > 1000:
            # target_i = rotation_exponential_smoothing_rule(end_pos, start_pos, current_pos, rotate_iter, num_steps=num_steps)
            target_i = rotation_standard_rule(end_pos, start_pos, current_pos, rotate_iter, num_steps=num_steps)
            current_pos = rotation_tick(target_i)
            rotate_iter += 1
        if rotate_iter == num_steps:
            rotate_iter = 0

        if display:
            cv2.imshow("Detecting people", img_with_face)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # time.sleep(0.03)
    cv2.destroyAllWindows()
    
    
    
if __name__ == "__main__":
    mb = roki.create_motherboard("Test")
    sks = roki.protocols.SKServo(mb)

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(lores={"size": (320, 240)}, encode="lores")) # govniche - TODO rewrite loadcoeffs
    picam2.set_controls({"FrameDurationLimits": (16700, 16700)})
    picam2.set_controls({"AwbEnable": True})
    picam2.start()
    Face_Detector(picam2, True)
        