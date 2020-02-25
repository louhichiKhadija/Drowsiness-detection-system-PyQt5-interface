from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
import time
import sys
import interface
from interface.gui_interface import Ui_MainWindow

from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import playsound
import imutils
import dlib
import cv2
from imutils.video import FPS

import drowsiness_detector.Drowsiness_detector
from drowsiness_detector.Drowsiness_detector import *



class ThreadSignal(QObject):
    in_progress1 = pyqtSignal(str)
    in_progress2 = pyqtSignal(str)

class ThreadAlarme(QRunnable):
    def __init__(self,path):
        super().__init__()
        self.path=path

    def run(self):
        # play an alarm sound
        playsound.playsound(self.path)
    

class ThreadDrowsiness(QRunnable):
    def __init__(self):
        super().__init__()
        self.signal = ThreadSignal()
        self.alarme=ThreadAlarme("alarm.wav")
        self.threadpool = QThreadPool.globalInstance()
    
    #def sound_alarm(self,path):
        # play an alarm sound
        #playsound.playsound(path)

    def open_cam(self):
        # start the video stream thread
        print("[INFO] starting video stream thread...")
        vs = VideoStream(0).start()
        time.sleep(1.0)
        return vs


    def download_landmark(self):
        # initialize dlib's face detector (HOG-based) and then create
        # the facial landmark predictor
        print("[INFO] loading facial landmark predictor...")
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor("drowsiness_detector/shape_predictor_68_face_landmarks.dat")

        # grab the indexes of the facial landmarks for the left and
        # right eye, respectively
        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        return detector, predictor, lStart,lEnd, rStart,rEnd
    
    def run(self):

        # indicate if the alarm is going off
        ALARM_ON = False

        #load landmark model
        detector, predictor, lStart,lEnd, rStart,rEnd = self.download_landmark()

        #open camera
        vs=self.open_cam()

        #instantiate Drowsy class
        s=Drowsy()
        while True:
            frame = vs.read()
            
            dr=s.Drowsiness_detector(frame,detector, predictor, lStart,lEnd, rStart,rEnd)

            if dr== "detect_drowsiness" :
                self.signal.in_progress1.emit("<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; color:#ef2929;\">Drowsiness detected</span></p><p align=\"center\"><span style=\" font-size:20pt; color:#ef2929;\">To be safe</span></p><p align=\"center\"><span style=\" font-size:20pt; color:#ef2929;\">Please take a break</span></p></body></html>")
                self.signal.in_progress2.emit("image: url(:/phone/coffee.png);")
                if not ALARM_ON:
                    ALARM_ON = True
                
                    # check to see if an alarm file was supplied,
                    # and if so, start a thread to have the alarm
                    # sound played in the background
                    self.threadpool.start(self.alarme)
                    

            else:
                self.signal.in_progress1.emit("<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; color:#ffffff;\">Welcome</span></p><p align=\"center\"><span style=\" font-size:20pt; color:#eeeeec;\">Be safe .. Be happy</span></p></body></html>")
                self.signal.in_progress2.emit("image: url(:/phone/icon-smile.png);")
                ALARM_ON=False
        


class DemoBancTest(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.threadpool1 = QThreadPool.globalInstance()
        self.test()

 
    @pyqtSlot()
    def test(self):
        threadsecondaire = ThreadDrowsiness()
        threadsecondaire.signal.in_progress1.connect(self.label.setText)
        threadsecondaire.signal.in_progress2.connect(self.label_3.setStyleSheet)
      

        self.threadpool1.start(threadsecondaire)
       
 
    def closeEvent(self, event):
        # Wait for all threads to finish
        self.threadpool1.waitForDone()
        event.accept()

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    demobanctest = DemoBancTest()
    demobanctest.show()
    sys.exit(app.exec_())
