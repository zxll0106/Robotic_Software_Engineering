#!/usr/bin/env python

from __future__ import print_function
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from opencv_apps.msg import FaceArrayStamped
from std_msgs.msg import Int32
from cv_bridge import CvBridge, CvBridgeError

import requests
import base64
import time
import urllib, urllib2
import ssl
import json
import base64


global token


class TakePhoto:
    def __init__(self):

        self.bridge = CvBridge()
        self.image_received = False
        self.pub1 = rospy.Publisher('/farewell_speech', Int32, queue_size=10)
        self.pub2 = rospy.Publisher('/farewell_age', String, queue_size=10)
        self.pub3 = rospy.Publisher('/farewell_sex', String, queue_size=10)
        self.img_title=''
        self.feature=''
        self.tag=True
        # Connect image topic
        # img_topic = "/camera/rgb/image_raw"
        img_topic = "/usb_cam/image_raw"
        self.image_sub = rospy.Subscriber(img_topic, Image, self.callback)
        rospy.Subscriber("/face_detection/faces", FaceArrayStamped, self.faceCallback)
        rospy.Subscriber('/farewell_reset', Int32, self.resetCallback)

        # Allow up to one second to connection
        rospy.sleep(1)




    def faceCallback(self,msg):
        if msg.faces != []:
            self.pub1.publish(1)
            print(1)
            if self.tag:
                self.take_photo()
                self.getFeature()
                self.tag=False

        else:
            print(0)
        # print(msg.faces)

    def resetCallback(self,msg):
        if msg.data==1:
            self.img_title = ''
            self.feature = ''
            self.tag = True


    def callback(self, data):

        # Convert image to OpenCV format
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        self.image_received = True
        self.image = cv_image

    def take_picture(self, img_title):
        if self.image_received:
            # Save an image
            cv2.imwrite(img_title, self.image)
            return True
        else:
            return False

    def take_photo(self):

        # Take a photo
        # Use '_image_title' parameter from command line
        # Default value is 'photo.jpg'
        # img_title = rospy.get_param('~image_title', 'photo.jpg')
        timestr = time.strftime("%Y%m%d-%H%M%S-")
        self.img_title = timestr + "photo.jpg"

        if self.take_picture(self.img_title):
            rospy.loginfo("Saved image " + self.img_title)
        else:
            rospy.loginfo("No images received")

    def getFeature(self):
        getToken()
        imgPath = "/home/zhaixiaolin/"+self.img_title
        result = json.loads(faceDetect(imgToBase64(imgPath)))['result']
        face_list = result['face_list'][0]
        location = face_list['location']
        age = face_list['age']
        beauty = face_list['beauty']
        expression = face_list['expression']['type']
        gender = face_list['gender']['type']
        self.feature=gender.encode("utf-8")+' '+str(age)
        print(self.feature)
        self.pub3.publish(str(gender.encode("utf-8")))
        self.pub2.publish(str(age))

def getToken():
    global token

    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=q8FBm39XVYE5AYNKahOUtA3j&client_secret=LMfY3Gejyer9wu4pF05ZZ270gVq4qlwf'
    request = urllib2.Request(host)
    request.add_header('Content-Type', 'application/json; charset=UTF-8')
    response = urllib2.urlopen(request)
    content = response.read()
    if (content):
        token = json.loads(content)['access_token']

def faceDetect(imgBase64):

    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
    request_url = request_url + "?access_token=" + token
    request = urllib2.Request(request_url)
    request.add_header('Content-Type', 'application/json')
    data = {"image": imgBase64, "image_type": "BASE64", "face_field": "age,beauty,expression,face_shape,gender"}
    response = urllib2.urlopen(request, urllib.urlencode(data))
    content = response.read()
    if content:
        return content

def imgToBase64(imgPath):
    with open(imgPath, "rb") as f:
        base64_data = base64.b64encode(f.read())
        return base64_data





if __name__ == '__main__':
    # Initialize
    rospy.init_node('take_photo', anonymous=False)
    TakePhoto()

    rospy.spin()
    # Sleep to give the last log messages time to be sent
    # rospy.sleep(1)