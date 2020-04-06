#!/usr/bin/env python

"""
    talkback.py - Version 1.1 2013-12-20

    Use the sound_play client to say back what is heard by the pocketsphinx recognizer.

"""

import rospy, os, sys
import time
from std_msgs.msg import String
from std_msgs.msg import Int32
from opencv_apps.msg import FaceArrayStamped
from sound_play.libsoundplay import SoundClient


class TalkBack:
    def __init__(self, script_path):
        rospy.init_node('talkback')

        rospy.on_shutdown(self.cleanup)

        # Create the sound client object
        self.soundhandle = SoundClient()
        self.sayCount = 0
        self.count=0
        self.faceFlag=False
        self.lmFlag=False


        rospy.Subscriber('/sign_in_name', String, self.name_callback)  # gai lm_data
        rospy.Subscriber('/lm_data', String, self.lm_callback)
        rospy.Subscriber("/face_detection/faces", FaceArrayStamped, self.face_callback)
        self.pub=rospy.Publisher('/sign_in_rename',Int32,queue_size=10)
        # self.pub1 = rospy.Publisher('/take_photo', String, queue_size=10)
        # self.pub2 = rospy.Publisher('/speech_face_recognition', String, queue_size=10)

    def name_callback(self,msg):
        print(1)
        if msg.data!= '':
            print(msg.data)
            self.soundhandle.say("hello,are you "+msg.data, volume=1.0)
            # time.sleep(4)
            # self.soundhandle.say("hello,are you " + msg.data, volume=1.0)
            self.lmFlag=True


    def face_callback(self, data):
        # Print the recognized words on the screen


        # Speak the recognized words in the selected voice

        if self.faceFlag:

            if self.count % 15 == 0:
                print(data.faces[0].face)

                if data.faces[0].face.x < 310:
                    self.soundhandle.say("move right " , volume=1.0)
                    self.sayCount=0
                elif data.faces[0].face.x > 330:
                    self.soundhandle.say("move left " , volume=1.0)
                    self.sayCount = 0
                elif data.faces[0].face.y < 230:
                    self.soundhandle.say("move down ", volume=1.0)
                    self.sayCount = 0
                elif data.faces[0].face.y > 250:
                    self.soundhandle.say(",move up " , volume=1.0)
                    self.sayCount = 0
                else:
                    self.soundhandle.say("do not move " , volume=1.0)
                    self.sayCount=self.sayCount+1
            self.count = self.count + 1
            if self.sayCount==5:
                time.sleep(1)
                self.soundhandle.say("now you can push the button,i will take photo for you ", volume=1.0)
                self.sayCount=0
                self.count=0
                self.faceFlag=False


    def lm_callback(self,msg):
        rospy.loginfo(msg.data)
        print(self.lmFlag)
        if self.lmFlag:
            if msg.data=='YES':
                self.soundhandle.say("Please stand at the center of the camera and follow my instructions  ", volume=1.0)
                time.sleep(5)
                self.faceFlag = True
            if msg.data.find('NO'):
                self.pub.publish(0)
            self.lmFlag=False



    def cleanup(self):
        self.soundhandle.stopAll()
        rospy.loginfo("Shutting down talkback node...")


if __name__ == "__main__":
    try:
        TalkBack(sys.path[0])
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("Talkback node terminated.")