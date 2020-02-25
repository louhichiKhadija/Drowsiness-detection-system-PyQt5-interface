#---------------------------------------------------------
# import the necessary packages
#---------------------------------------------------------
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import playsound
import argparse
import imutils
import time
import dlib
import cv2
#---------------------------------------------------------


class Drowsy:

	global COUNTER

	def __init__(self):
		self.COUNTER=0

	#function which is used to compute the ratio of distances between the 
	#vertical eye landmarks and the distances between the horizontal eye landmarks:
	##EAR = eye aspect ratio

	def eye_aspect_ratio(self,eye):
		# compute the euclidean distances between the two sets of
		# vertical eye landmarks (x, y)-coordinates
		A = dist.euclidean(eye[1], eye[5])
		B = dist.euclidean(eye[2], eye[4])
		
		# compute the euclidean distance between the horizontal
		# eye landmark (x, y)-coordinates
		C = dist.euclidean(eye[0], eye[3])
	
		# compute the eye aspect ratio
		ear = (A + B) / (2.0 * C)
	
		# return the eye aspect ratio
		return ear

	def Drowsiness_detector(self,frame,detector, predictor, lStart,lEnd, rStart,rEnd):
		# define two constants, one for the eye aspect ratio to indicate
		# blink and then a second constant for the number of consecutive
		# frames the eye must be below the threshold for to set off the
		# alarm
		
		EYE_AR_THRESH = 0.3
		EYE_AR_CONSEC_FRAMES = 48

		

		# loop over frames from the video stream
		#while True:
		# grab the frame from the threaded video file stream, resize
		# it, and convert it to grayscale
		# channels)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		
		# detect faces in the grayscale frame
		rects = detector(gray, 0)
		# loop over the face detections
		for rect in rects:
			# determine the facial landmarks for the face region, then
			# convert the facial landmark (x, y)-coordinates to a NumPy
			# array
			shape = predictor(gray, rect)
			shape = face_utils.shape_to_np(shape)
		
			# extract the left and right eye coordinates, then use the
			# coordinates to compute the eye aspect ratio for both eyes
			leftEye = shape[lStart:lEnd]
			rightEye = shape[rStart:rEnd]
			leftEAR = self.eye_aspect_ratio(leftEye)
			rightEAR = self.eye_aspect_ratio(rightEye)
		
			# average the eye aspect ratio together for both eyes
			ear = (leftEAR + rightEAR) / 2.0
			# compute the convex hull for the left and right eye, then
			# visualize each of the eyes
			leftEyeHull = cv2.convexHull(leftEye)
			rightEyeHull = cv2.convexHull(rightEye)
			cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
			cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

			# draw the computed eye aspect ratio on the frame to help
			# with debugging and setting the correct eye aspect ratio
			# thresholds and frame counters
			cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
				cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)



			# check to see if the eye aspect ratio is below the blink
			# threshold, and if so, increment the blink frame counter
			if ear < EYE_AR_THRESH:
				self.COUNTER += 1
		
				# if the eyes were closed for a sufficient number of
				# then sound the alarm
				if self.COUNTER >= EYE_AR_CONSEC_FRAMES:
					# if the alarm is not on, turn it on
					return "detect_drowsiness"
		
			# otherwise, the eye aspect ratio is not below the blink
			# threshold, so reset the counter and alarm
			else:
				self.COUNTER=0
				return "no_drowsiness"
