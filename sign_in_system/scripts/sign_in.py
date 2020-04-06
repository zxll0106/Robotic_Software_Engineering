#!/usr/bin/env python

'''
Copyright (c) 2016, Nadya Ampilogova
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

# Script for simulation
# Launch gazebo world prior to run this script

from __future__ import print_function
import sys
import rospy
import cv2
from std_msgs.msg import String
from std_msgs.msg import Int32
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from opencv_apps.msg import FaceArrayStamped
from opencv_apps.srv import FaceRecognitionTrain, FaceRecognitionTrainRequest
from sound_play.libsoundplay import SoundClient
import time
import Tkinter
import PIL.Image
import PIL.ImageTk



import os


class TakePhoto:
    def __init__(self):

        self.bridge = CvBridge()
        self.image_received = False

        # Connect image topic
        #img_topic = "/usb_cam/image_raw"
        img_topic = "/face_recognition/debug_image"
        self.image_sub = rospy.Subscriber(img_topic, Image, self.callback)
        rospy.Subscriber('/usb_cam/image_raw', Image, self.image_callback)

        self.window_width = 640
        self.window_height = 480
        self.image_width = int(self.window_width * 0.6)
        self.image_height = int(self.window_height * 0.6)
        self.imagepos_x = int(self.window_width * 0.2)
        self.imagepos_y = int(self.window_height * 0.1)
        self.top = Tkinter.Tk()
        self.top.wm_title("Sign_in System")
        self.top.geometry(str(self.window_width) + 'x' + str(self.window_height))
        self.canvas = Tkinter.Canvas(self.top, bg='white', width=self.image_width, height=self.image_height)
        self.canvas.place(x=self.imagepos_x, y=self.imagepos_y)
        self.picture=None
        self.Notag_picture=None
        self.lb1=Tkinter.Label(self.top,text='name: ')
        self.lb1.place(x=275, y=350, anchor='nw')
        self.lb3 = Tkinter.Label(self.top, text='sign_in recording ')
        self.lb3.place(x=520, y=50, anchor='nw')
        self.b = Tkinter.Button(self.top, text='sign in', width=10, height=2, command=self.button)
        self.b.place(x=260, y=370)

        self.name=''

        self.name_flag=True

        # Allow up to one second to connection
        rospy.sleep(1)

        rospy.Subscriber('/take_photo', String, self.take_photo)
        rospy.Subscriber('/face_recognition/output', FaceArrayStamped, self.name_callback)
        rospy.Subscriber('/sign_in_rename', Int32, self.rename_callback)

        self.pub = rospy.Publisher('/sign_in_name', String, queue_size=10)

    def callback(self, data):

        # Convert image to OpenCV format
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        self.image_received = True
        self.image = cv_image

        self.picture = self.tkImage(self.image,0.6)
        self.canvas.create_image(0, 0, anchor='nw', image=self.picture)
        #self.top.update_idletasks()
        self.top.update()
        self.top.after(0)

    def image_callback(self,data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        self.image_received = True
        self.Notag_image = cv_image




    def tkImage(self,frame,a):
        window_width = 640
        window_height = 480
        image_width = int(window_width * a)
        image_height = int(window_height * a)
        cvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        pilImage = PIL.Image.fromarray(cvimage)
        pilImage = pilImage.resize((image_width, image_height), PIL.Image.ANTIALIAS)
        tkImage = PIL.ImageTk.PhotoImage(image=pilImage)
        return tkImage


    def name_callback(self,msg):
        if msg.faces!={}:
            if self.name_flag==True:
                self.name=msg.faces[0].label
                rate = rospy.Rate(1)
                self.pub.publish(self.name)
                print(self.name)
                self.name_flag = False
                lb2 = Tkinter.Label(self.top, text=self.name)
                lb2.place(x=320, y=350, anchor='nw')



    def rename_callback(self,msg):
        if msg.data==0:
            self.name_flag=True

    def button(self):
        self.Notag_picture = self.tkImage(self.Notag_image, 0.15)
        timestr = time.strftime("%Y%m%d-%H%M%S-")
        timestr1=time.strftime("%Y.%m.%d %H:%M:%S")
        img_title = timestr + "photo.jpg"
        image1=self.Notag_image
        picture1=self.Notag_picture
        cv2.imwrite(img_title, image1)
        canvas = Tkinter.Canvas(self.top, bg='white', width=96, height=72)
        canvas.place(x=520, y=80)
        canvas.create_image(0, 0, anchor='nw', image=picture1)
        lb4 = Tkinter.Label(self.top, text="%s signed in on"%self.name)
        lb4.place(x=520, y=165, anchor='nw')
        lb5 = Tkinter.Label(self.top, text=timestr1)
        lb5.place(x=520, y=185, anchor='nw')

        # lb3 = Tkinter.Label(self.top, image=image1)
        # lb3.place()



    def take_picture(self, img_title):
        if self.image_received:
            # Save an image
            cv2.imwrite(img_title, self.image)
            return True
        else:
            return False

    def take_photo(self, msg):
        # print msg.data
        if msg.data == "take photo":
            # Take a photo
            # Use '_image_title' parameter from command line
            # Default value is 'photo.jpg'
            # img_title = rospy.get_param('~image_title', 'photo.jpg')
            timestr = time.strftime("%Y%m%d-%H%M%S-")
            img_title = timestr + "photo.jpg"

            if self.take_picture(img_title):
                rospy.loginfo("Saved image " + img_title)
            else:
                rospy.loginfo("No images received")


if __name__ == '__main__':
    # Initialize
    rospy.init_node('take_photo', anonymous=False)
    TP=TakePhoto()


    TP.top.mainloop()
    rospy.spin()





    # Sleep to give the last log messages time to be sent
    # rospy.sleep(1)