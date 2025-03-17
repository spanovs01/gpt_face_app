import cv2
import numpy as np
from picamera2 import Picamera2
    
def Face_Detector(picamera, display=True):                      # TODO: threshold на близость человека к голове
    face_detector = cv2.CascadeClassifier("/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml")
    while True:
        frame = picamera.capture_array("main")  
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_detector.detectMultiScale(image, 1.1, 3) # TODO: неточная модельб видит лица там где их нет
        print(faces)
        (x, y, w, h) = faces[0]
        print(x,y,w,h)
        img_with_face = cv2.rectangle(image, (x, y), (x+h, y+h), (0, 255, 0), 5)
        if display:
            cv2.imshow("Detecting people", img_with_face)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()
    
    
    
if __name__ == "__main__":
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'BGR888', "size": (1600, 1300)})) # govniche - TODO rewrite loadcoeffs
    picam2.set_controls({"FrameDurationLimits": (16700, 16700)})
    picam2.set_controls({"AwbEnable": True})
    picam2.start()
    while True:
        Face_Detector(picam2, True)
        